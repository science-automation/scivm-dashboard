from django.contrib.auth.models import User
from django.conf.urls import url

from tastypie import fields
from tastypie.authorization import Authorization
from apikey.authentication import SciCloudApiKeyAuthentication

from .base import CloudResource, dispatch

from cloud.util.zip_packer import Packer, UnPacker
from jobs.jids import JIDS
from jobs.models import UserJobCounter, Job

from .forms import CronAddForm, CronLabelForm
from crons.models import Cron

import json
import pickle


class CloudCronResource(CloudResource):
    
    class Meta:
        resource_name = 'cron'
        authorization = Authorization()
        authentication = SciCloudApiKeyAuthentication()
        list_allowed_methods = []
        detail_allowed_methods = []
    
    @dispatch
    def register_hnd(self, request, **kwargs):
        """ Cron registration """
        try:
            # FIXME mabye it's not neccesary to unpack here; I did it just to have some kind of input valiation...
            func_obj_pickled = UnPacker(request.FILES["data"]).next()
            request.FILES["data"].seek(0)
        except Exception, e:
            logger.debug("cannot unpack cron data: %s" % str(e))
            raise ValidationError("cannot unpack cron data")
        
        depends_on = None
        if "depends_on" in request.FILES:
            depends_on = self.load_jids_from_file(request, "depends_on")
            if not UserJobCounter.is_allocated(request.user, depends_on.top()):
                return self.error_response(request, {"error": {"msg": "Sepcified dependency does not exist." , "code": 464, "retry": False}}, response_class=http.HttpRequest) 

        form = CronAddForm(request.POST)
        if not form.is_valid():
            return self.error_response(request, form.errors, response_class=http.HttpBadRequest) 
        
        cron = form.save(commit=False)
        
        # storing func/args/kwargs
        cron.func_obj_pickled = func_obj_pickled
        
        cron.owner = request.user
        cron.apikey_id = request.apikey.pk
        
        cron.depends_on = depends_on

        cron.save()
        
        #TODO
        #cron.backend.schedule_cron(cron.pk)
        return self.create_response(request, {})
    
    def get_cron_for_label(self, request):
        form = CronLabelForm(request.POST)
        if not form.is_valid():
            raise ValidationError("label field is required")
        label = form.cleaned_data["label"]
        try:
            return Cron.objects.get(owner=request.user, label=label)
        except Cron.DoesNotExist:
            return self.raise_response(request, {"error": {"msg": "Could not find requested Cron", "code": 481, "retry": False}}) 
        
    @dispatch
    def deregister_hnd(self, request, **kwargs):
        cron = self.get_cron_for_label(request)
        #TODO deregister here
        #cron.backend.deregister_cron(cron.pk)
        return self.create_response(request, {})
    
    @dispatch
    def run_hnd(self, request, **kwargs):
        """ Run cron instance of user specified by its label just now """
        cron = self.get_cron_for_label(request)
        #TODO run something here
        #cron.backend.run_cron(cron.pk)
        return self.create_response(request, {})
    
    @dispatch
    def list_hnd(self, request, **kwargs):
        """ List labels of user's cron instances """
        labels = Cron.objects.filter(owner=request.user).values_list("label", flat=True)
        return self.create_response(request, {"labels": labels})

    @dispatch
    def info_hnd(self, request, **kwargs):
        """ Get info about cron instance specified by its label """
        cron = self.get_cron_for_label(request)
        response = {
            "core_type": cron.core_type,
            "created": cron.created_at.strftime("%Y-%m-%d %H:%M:%S") if cron.created_at else None,
            "creator_host": cron.hostname,
            "func_name": cron.func_name,
            "label": cron.label,
            "last_jid": cron.lastjob.jid if cron.lastjob_id else None,
            "last_run": cron.lastrun_at.strftime("%Y-%m-%d %H:%M:%S") if cron.lastrun_at else None,
            "schedule": cron.cron_exp,
        }
        return self.create_response(request, response)
    

