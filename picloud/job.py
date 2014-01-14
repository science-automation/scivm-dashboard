from django.contrib.auth.models import User
from django.conf.urls import url

from tastypie import fields
from tastypie.authorization import Authorization
from apikey.authentication import SciCloudApiKeyAuthentication
from tastypie import http 
from tastypie.resources import ValidationError

from .base import CloudResource, CloudModelResource, dispatch, logger
from .forms import JobAddForm, JobAddMapForm

from jobs.models import Job, UserJobCounter, JobGroup
from jobs.jids import JIDS

from cloud.util.zip_packer import Packer, UnPacker
from cloud.serialization import serialize, deserialize

import json
import pickle
import logging
import zlib
import random


class CloudJobResource(CloudResource):
    
    class Meta:
        resource_name = 'job'
        authorization = Authorization()
        authentication = SciCloudApiKeyAuthentication()
        list_allowed_methods = []
        detail_allowed_methods = []
    
    
    @dispatch("/", methods=("POST",))
    def add_hnd(self, request, **kwargs):
        """ Job creation """
        try:
            # FIXME mabye it's not neccesary to unpack here; I did it just to have some kind of input valiation...
            func_obj_pickled, func_args_pickled, func_kwargs_pickled = (part  for part in UnPacker(request.FILES["data"]))
            request.FILES["data"].seek(0)
        except Exception, e:
            logger.debug("cannot unpack job data: %s" % str(e))
            raise ValidationError("cannot unpack job data")
        
        depends_on = None
        if "depends_on" in request.FILES:
            depends_on = self.load_jids_from_request(request, "depends_on")
            if not UserJobCounter.is_allocated(request.user, depends_on.top()):
                return self.error_response(request, {"error": {"msg": "Sepcified dependency does not exist." , "code": 464, "retry": False}}, response_class=http.HttpBadRequest) 

        form = JobAddForm(request.POST)
        if not form.is_valid():
            return self.error_response(request, form.errors, response_class=http.HttpBadRequest) 
        
        job = form.save(commit=False)
        
        # storing func/args/kwargs
        job.func_obj_pickled = func_obj_pickled
        job.func_args_pickled = func_args_pickled if func_args_pickled else None
        job.func_kwargs_pickled = func_kwargs_pickled if func_kwargs_pickled else None
        
        job.owner = request.user
        job.apikey_id = request.apikey.pk
        
        start, end = UserJobCounter.allocate(request.user, 1)
        job.job_type = job.CALL_JOB
        job.jid = start
        job.depends_on = depends_on

        job.save()
        
        # data to send to the queue about the job
        job_queue_data = job.get_queue_data()
        
        # partial task
        
        if job.depends_on:
            # launch event waiter and pass partial action
            action = Job.backend.enqueue_jobs.subtask()
            Job.backend.wait_for_dependencies.apply_async(((job_queue_data,), job.owner.pk, job.depends_on_desc, job.depends_on_errors, False, action))
        else:
            # apply data to partial task
            action = Job.backend.enqueue_job.subtask()
            action.apply_async((job_queue_data,))
        
        return self.create_response(request, {"jids": job.jids_desc})
    
    @dispatch
    def map_add_hnd(self, request, **kwargs):
        """ Map job creation """
        # validate map related inputs 
        map_form = JobAddMapForm(request.POST)
        if not map_form.is_valid():
            return self.error_response(request, map_form.errors, response_class=http.HttpBadRequest) 
        map_data = map_form.cleaned_data
        
        # Map job creation can span through multiple requests.
        # Map args come in batches, max ~500 args get serialized per request.
        # map_data['group_id']: pk of the already created map job if any
        if map_data["group_id"] is None:
            # first request, we need to create job group
            try:
                # [ <pickled-fuction>, <map-args-0>, <map-args-1>, ....] 
                data_parts = [ part for part in UnPacker(request.FILES["data"]) ]
                request.FILES["data"].seek(0)
            except Exception, e:
                logger.debug("cannot unpack job data: %s" % str(e))
                raise ValidationError("cannot unpack job data")
        
            
            form = JobAddForm(request.POST)
            if not form.is_valid():
                return self.error_response(request, form.errors, response_class=http.HttpBadRequest) 
            
            depends_on = None
            if "depends_on" in request.FILES:
                depends_on = self.load_jids_from_request(request, "depends_on")
                if not UserJobCounter.is_allocated(request.user, depends_on.top()):
                    return self.error_response(request, {"error": {"msg": "Sepcified dependency does not exist." , "code": 464, "retry": False}}, response_class=http.HttpResponse) 
            
            job_group = JobGroup()
            [ setattr(job_group, k, v) for (k,v) in form.cleaned_data.items() ]
            job_group.owner = request.user
            job_group.apikey_id = request.apikey.pk
            
            # storing func
            job_group.func_obj_pickled = data_parts.pop(0)
        
            # !! here we allocate jids for all children !!
            # use these jids in subsequent batches too
            start, end = UserJobCounter.allocate(request.user, map_data["map_len"])
            job_group.start_jid = start
            job_group.end_jid = end
            
            job_group.depends_on = depends_on
             
            job_group.save()
        else:
            # job group is created already, this is not the first batch of children
            # map_data['first_maparg_index']: index of the first arg in the payload
            try:
                # [ <map-args-idx0>, <map-args-idx1>, ....] 
                data_parts = [ part for part in UnPacker(request.FILES["data"]) ]
                request.FILES["data"].seek(0)
            except Exception, e:
                logger.debug("cannot unpack job data: %s" % str(e))
                raise ValidationError("cannot unpack job data")
            
            try:
                job_group = JobGroup.objects.get(owner=request.user, pk=map_data["group_id"])
            except Job.DoesNotExist:
                logger.debug("cannot get job for group_id: %s %s" % (map_data["group_id"], request.user))
                return self.error_response(request, {"error": {"msg": "Specified map job is not found", "code": "?", "retry": False}}, response_class=http.HttpBadRequest) #FIXME 
        
        # build jobs from current batch
        jobs = []
        for idx, func_args_pickled in enumerate(data_parts):
            job = job_group.clone_job()
            
            job.owner = request.user
            job.apikey_id = request.apikey.pk
            job.group = job_group
            job.job_type = Job.MAP_JOB #FIXME do we need diff type for parts of a map job?
            
            # storing func/args, no kwargs
            job.func_obj_pickled = job_group.func_obj_pickled
            job.func_args_pickled = func_args_pickled if func_args_pickled else None
        
            # do not let it to overrun the allocated jids;  let's be sure.
            assert map_data['first_maparg_index'] + idx < job_group.end_jid - job_group.start_jid + 1
            jid = map_data['first_maparg_index'] + idx + job_group.start_jid
            job.jid = jid
            
            jobs.append(job)
        
        # bulk create jobs
        Job.objects.bulk_create(jobs)
         
        if map_data['done']:
            # this was the last batch of children, let's enqueue job group
            
            # every group has a fake job entry
            fake_entry = job_group.clone_job()
            fake_entry.job_type = Job.MAP_JOB
            fake_entry.owner = request.user
            fake_entry.apikey_id = request.apikey.pk
            fake_entry.group = job_group
            
            # fake entries get the start jid and True in is_group_entry
            fake_entry.jid = job_group.start_jid 
            fake_entry.is_group_entry = True
            
            fake_entry.save()
            
            # data to send to the queue about the jobs
            children_data = Job.objects.for_group(job_group.pk).values(*Job.JOB_QUEUE_DATA_FIELDS)
            
            # partial task to launch if dependencies get resolved
            action = Job.backend.enqueue_group_job.subtask((job_group.pk,))

            if job_group.depends_on:
                # set up a an event listener and pass the partial task to it
                Job.backend.wait_for_dependencies.apply_async((list(children_data), job.owner.pk, job_group.depends_on_desc, job_group.depends_on_errors, False, action))
            else:
                # apply data to partial task
                action.apply_async((list(children_data),))
        
        return self.create_response(request, {"jids": job_group.jids_desc, 'group_id': job_group.pk})
    
    @dispatch
    def info_hnd(self, request, **kwargs):
        """ get info about a job """ 
        # load and validate jids
        jids = self.load_jids_from_request(request, "jids")
        if not UserJobCounter.is_allocated(request.user, jids.top()):
            return self.error_response(request, {"error": {"msg": "Could not find requested job.", "code": 454, "retry": False}}, response_class=http.HttpResponse) #FIXME 
         
        # use defaults if empty
        requested_info = request.GET.getlist("field", ("status", "stdout", "stderr", "runtime")) 
        
        # valid fields and collections
        info_fields = {
            'all': (
                'status', 
                'stdout', 'stderr', 'pilog', 'logging', 
                'exception', 
                'created', 'finished', 
                'parent_jid',
                'env', 'vol', 'code_version', 
                'function', 'args', 'kwargs', 'func_body', 
                'label', 
                'memory_failcnt', 'memory_max_usage', 'memory_usage',
                'cputime_system', 'cputime_user', 
                'cpu_percentage_system', 'cpu_percentage_user',
                'disk_usage',
                'ports',
                'creator_api_key', 'creator_hostname',
                'runtime', 'max_runtime', 
                'profile',
            ),
            'attributes': (
                'code_version', 'core_type', 'cores', 'creator_api_key',
                'creator_hostname', 'env', 'function', 'label', 'max_runtime', 
                'parent_jid', 'vol'
            ),
            'cpu_percentage': (
                'cpu_percentage_system', 'cpu_percentage_user',
            ),
            'cputime': (    
                'cputime_system', 'cputime_user', 
            ),
            'memory': (
                'memory_failcnt', 'memory_max_usage', 'memory_usage',
            )
        }
        
        # necessary fields to put into the response
        requested_fields = set()

        # check if requested field name is a collection and whether is valid or not
        for fname in set(requested_info):
            if fname in info_fields:
                requested_fields.update(info_fields[fname])
            elif fname in info_fields["all"]:
                requested_fields.add(fname)

        response_data = {"info": {}, "language": "python"}
        jobs = Job.objects.for_jids(request.user.pk, jids)
        
        # build response dict
        for job in jobs:
            data = {}
            for field in requested_fields:
                data[field] = getattr(job, "get_%s_info" % field)()
            response_data["info"][job.jid] = data
        
        return self.create_response(request, response_data)
    
    @dispatch
    def result_serialized_hnd(self, request, **kwargs):
        jids = self.load_jids_from_request(request, "jids")
        if not UserJobCounter.is_allocated(request.user, jids.top()):
            return self.error_response(request, {"error": {"msg": "Could not find requested job.", "code": 454, "retry": False}}, response_class=http.HttpResponse) #FIXME 

        #FIXME this handler should give back only jobs with "done" status and shouldn't accept jid of job what not in done "state"
        jobs_data = Job.objects.for_jids(request.user.pk, jids).values("status", "result_pickled", "language", "language_version") 
        
        # repsonse has two parts: a json and some kind of binary "multipart" data
        raw_data = []
        response_data = {"interpretation": [], "language": "python"}

        # boundary for the multipart part
        boundary = "========" + "".join([ str(random.randint(0,9)) for i in xrange(0, 152) ])  + "==" #FIXME performance++
        
        for job in jobs_data:
            if job["status"] != Job.DONE:
                return self.error_response(request, {"error": {"msg": "No result for requested job(s).", "code": "?", "retry": False}}, response_class=http.HttpResponse) #FIXME 
            # it's all pickled all the way down
            response_data["interpretation"].append({"datatype": "python_pickle", "language": job["language"], "_version": job["language_version"] })
            raw_data.append(boundary + bytes(job["result_pickled"]))
        
        response = json.dumps(response_data) + "boundary=%s\n" % boundary + "".join(raw_data)
        return http.HttpResponse(response, content_type="application/json")
    
    @dispatch
    def result_serialized_global_hnd(self, request, **kwargs):
        """ ????? """
        jids = self.load_jids_from_request(request, "jids")
        if not UserJobCounter.is_allocated(request.user, jids.top()):
            return self.error_response(request, {"error": {"msg": "Could not find requested job.", "code": 454, "retry": False}}, response_class=http.HttpResponse) #FIXME 
        return self.create_response(request, {})
    
    @dispatch
    def kill_hnd(self, request, **kwargs):
        jids = self.load_jids_from_request(request, "jids")
        if not UserJobCounter.is_allocated(request.user, jids.top()):
            return self.error_response(request, {"error": {"msg": "Could not find requested job.", "code": 454, "retry": False}}, response_class=http.HttpResponse) #FIXME 
        
        for job in Job.objects.for_jids(request.user.pk, jids).filter(status__in=Job.KILLABLE_STATES):
            #FIXME slow as hell
            job.kill()
        
        return self.create_response(request, {})
    
    @dispatch
    def delete_hnd(self, request, **kwargs):
        jids = self.load_jids_from_request(request, "jids")
        if not UserJobCounter.is_allocated(request.user, jids.top()):
            return self.error_response(request, {"error": {"msg": "Could not find requested job.", "code": 454, "retry": False}}, response_class=http.HttpResponse) #FIXME 
        
        for job in Job.objects.for_jids(request.user.pk, jids):
            #FIXME slow as hell
            job.delete(purge=False)
        
        return self.create_response(request, {})
    
    @dispatch
    def bucketmap_hnd(self, request, **kwargs):
        """ see cloud client bucket.py """
        jids = self.load_jids_from_request(request, "jids")
        if not UserJobCounter.is_allocated(request.user, jids.top()):
            return self.error_response(request, {"error": {"msg": "Could not find requested job.", "code": 454, "retry": False}}, response_class=http.HttpResponse) #FIXME 
        return self.create_response(request, {})
    
    @dispatch
    def filemap_hnd(self, request, **kwargs):
        """ see cloud client files.py """
        jids = self.load_jids_from_request(request, "jids")
        if not UserJobCounter.is_allocated(request.user, jids.top()):
            return self.error_response(request, {"error": {"msg": "Could not find requested job.", "code": 454, "retry": False}}, response_class=http.HttpResponse) #FIXME 
        return self.create_response(request, {})

