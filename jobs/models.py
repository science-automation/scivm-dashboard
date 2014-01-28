# Copyright 2014 Science Automation
#
# This file is part of Science VM.
#
# Science VM is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# Science VM is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Science VM. If not, see <http://www.gnu.org/licenses/>.

from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.utils.translation import ugettext as _
from django.db.models import Q, F
from django.core.cache import cache
from scivm import utils
from json_field import JSONField

from .jids import JIDS
from .managers import JobGroupManager, JobManager, JobGroupNotDeletedManager, JobNotDeletedManager

import time
import base64
import pickle
import zlib
import collections


def get_job_backend():
    from .backends import get_backend
    # import all backend, default is the first
    entry = settings.JOB_BACKENDS
    return get_backend(entry["backend"])(**entry["config"])
__job_backend__ = get_job_backend()


class UserJobCounter(models.Model):
    """ Job counter for user (jid sequence allocator) """
    MAX_TRIES = 10

    user = models.ForeignKey(User, unique=True)
    counter = models.PositiveIntegerField(default=0)
    
    @classmethod
    def is_allocated(cls, user, jid):
        try:
            obj = cls.objects.get(user=user)
            return obj.counter >= jid
        except cls.DoesNotExist:
            return False

    @classmethod
    def allocate(cls, user, count=1):
        # get or create counter for user
        obj, created = cls.objects.get_or_create(user=user)
        
        tried = 0
        changed = 0
        
        # try again if allocation fails
        while tried < cls.MAX_TRIES:
            changed = cls.objects.filter(user=user, counter=obj.counter).update(counter = F('counter') + count)
            if changed == 1:
                # good, counter should be now obj.counter + count                
                return obj.counter+1, obj.counter+count
            
            # wait some before executing next try
            time.sleep(0.01)
            tried += 1
        
        raise Exception("cannot allocate %s jobs for %s" % (count, user))


class JobTemplate(models.Model):
    
    # all action should go through the backend
    backend = __job_backend__

    class Meta:
        abstract = True
    
    JOB_CLONE_ATTRS = (
            'owner_id', 'apikey_id', 'hostname', 
            'label', 'cloud_version', 'ap_version',
            'language', 'language_version', 'mod_versions',
            'func_name', 'func_obj_pickled', 'fast_serialization', 
            'cores', 'core_type',
            'depends_on_errors', 'depends_on_desc',
            'restartable', 'max_runtime', 'priority',
            'profile', 'process_id', 'kill_process'
    )
    
    C1, C2, F2, M1, S1 = "c1", "c2", "f2", "m1", "s1"
    CORE_TYPE_DICT = {
        C1: _("C1"),
        C2: _("C2"),
        F2: _("F2"),
        M1: _("M2"),
        S1: _("S1"),
    }
    CORE_CHOICES = ((1, "1"), (2, "2"), (4, "4"), (8, "8"), (16, "16")) 
    
    ABORT, IGNORE = "abort", "ignore"
    DEPENDS_ON_ERROR_DICT = {
        ABORT: _("abort"),
        IGNORE: _("ignore"),
    }

    owner = models.ForeignKey(User)
    apikey_id = models.PositiveIntegerField()
    hostname = models.CharField(max_length=96, default="", blank=True)
    
    label = models.CharField(max_length=96, default="", blank=True)
    
    cloud_version = models.CharField(max_length=25)
    ap_version = models.CharField(max_length=96, default="", blank=True)

    language = models.CharField(max_length=96)
    language_version = models.TextField(default="")
    mod_versions = JSONField(default={}, blank=True)
    
    func_name = models.TextField()
    func_obj_pickled = models.BinaryField()
    
    fast_serialization = models.IntegerField(default=0)
    
    core_type = models.CharField(max_length=2, choices=CORE_TYPE_DICT.items(), default=C1, blank=True)
    cores = models.IntegerField(choices=CORE_CHOICES, default=1)
    
    # !! see depends_on property below 
    depends_on_desc = JSONField(null=True) 
    depends_on_errors = models.CharField(choices=DEPENDS_ON_ERROR_DICT.items(), default=ABORT, max_length=16)
    
    restartable = models.BooleanField(default=True)
    max_runtime = models.IntegerField(null=True, blank=True) # in minutes, time to kill if not finished
    priority = models.IntegerField(default=5)
    
    profile = models.BooleanField(default=False)
    process_id = models.IntegerField() # ???
    kill_process = models.BooleanField() # do not reuse interpreter process after finishing... or something like that
    
    # -- from picloud web interface --
    # environment
    # voulmes
    # dependent_on_by

    created_at = models.DateTimeField(auto_now_add=True)
    
    @property
    def jids_desc(self):
        raise NotImplementedError

    @property
    def jids(self):
        return JIDS(self.jids_desc)
    
    def get_jid_display(self):
        raise NotImplementedError
    
    @property
    def depends_on(self):
        if self.depends_on_desc is not None:
            return JIDS(self.depends_on_desc)
        return None
    
    @depends_on.setter
    def depends_on(self, jids_or_desc):
        if jids_or_desc is None:
            desc = None
        else:
            desc = JIDS(jids_or_desc).serialize() if not isinstance(jids_or_desc, JIDS) else jids_or_desc.serialize()
        self.depends_on_desc = desc
    
    @property
    def func_obj(self):
        if self.func_obj_pickled is None:
            return None
        return pickle.loads(self.func_obj_pickled)
    
    def clone_job(self):
        obj = Job()
        for attr in self.JOB_CLONE_ATTRS:
            setattr(obj, attr, getattr(self, attr))
        return obj


class JobGroup(JobTemplate):
    """ Represents a map job of a user """
    
    # filter out "is_deleted" objects by default
    objects = JobGroupNotDeletedManager()
    is_deleted = models.BooleanField(default=False, db_index=True)
    
    # the original manager without filtering
    allobjects = JobGroupManager()
    
    class Meta:
        pass
    
    start_jid = models.PositiveIntegerField()
    end_jid = models.PositiveIntegerField()

    ok_cnt = models.PositiveIntegerField(default=0)
    failed_cnt = models.PositiveIntegerField(default=0)
    
    @property
    def job_cnt(self):
        return self.end_jid - self.start_jid + 1

    @property
    def jids_desc(self):
        return ['xrange', self.start_jid, 1, self.job_cnt]

    def get_jid_display(self):
        return "map[%s,%s]"  % (self.start_jid, self.end_jid)
    
    def get_status_display(self):
        return "%s/%s/%s" % (self.ok_cnt, self.failed_cnt, self.job_cnt)

    def kill(self):
        return self.backend.kill_jobgroup(self.pk)
    
    def delete(self, *args, **kwargs):
        # really delete it?
        if kwargs.get('purge', False):
            kwargs.pop("purge")
            return super(JobGroup, self).delete(*args, **kwargs)
        # send to backend
        return self.backend.delete_jobgroup(self.pk)


class Job(JobTemplate):
    """ Represents a job of a user """
    
    # filter out "is_deleted" objects by default
    objects = JobNotDeletedManager()
    is_deleted = models.BooleanField(default=False, db_index=True)
    
    # the original manager without filtering
    allobjects = JobManager()
    
    class Meta:
        ordering = ('jid', )
        unique_together = (('owner', 'jid', 'is_group_entry'))
    
    WAITING, QUEUED, PROCESSING = "waiting", "queued", "processing"
    DONE, ERROR, KILLED, STALLED = "done", "error", "killed", "stalled"
    
    KILLABLE_STATES = (WAITING, QUEUED, PROCESSING)
    END_STATES = (DONE, ERROR, STALLED)

    STATUS_DICT = {
        WAITING: _("waiting"),
        QUEUED: _("queued"),
        PROCESSING: _("processing"),
        DONE: _("done"),
        ERROR: _("error"),
        KILLED: _("killed"),
        STALLED: _("stalled"),
    }

    CALL_JOB, MAP_JOB, CRON_JOB = "call", "map", "cron"
    FILEMAP_MAPPER_JOB, FILEMAP_REDUCER_JOB = "filemap_mapper", "fielmap_reducer"
    JOBTYPE_DICT = {
        CALL_JOB: _("call"),
        MAP_JOB: _("map"),
        CRON_JOB: _("cron"),
        FILEMAP_MAPPER_JOB: _("filemap_mapper"),
        FILEMAP_REDUCER_JOB: _("filemap_reducer"),
    }
    
    # it's better to use strings, values become less cryptic 
    status = models.CharField(choices=STATUS_DICT.items(), max_length=16, default=WAITING, db_index=True)
    
    # it's better to use strings, values become less cryptic 
    job_type = models.CharField(choices=JOBTYPE_DICT.items(), max_length=16, db_index=True)
    jid = models.PositiveIntegerField(db_index=True)
    
    group = models.ForeignKey(JobGroup, null=True, blank=True)
    is_group_entry = models.BooleanField(default=False, db_index=True)

    func_args_pickled = models.BinaryField(blank=True, default=None, null=True)
    func_kwargs_pickled = models.BinaryField(blank=True, default=None, null=True)

    finished_at = models.DateTimeField(null=True, blank=True)
    # FIXME max_digits and decimal_places
    runtime = models.DecimalField(max_digits=14, decimal_places=6, null=True, blank=True)
    
    # user_cpu_time, user_sys_time, peak_memory, 
    # peak_swap, mem_alloc_fails, listening_ports
    
    exception = models.TextField(default="", blank=True)
    result_pickled = models.BinaryField(null=True, blank=True)

    # FIXME logs should be somewehere else... ?
    stdout = models.TextField(default="", blank=True) 
    stderr = models.TextField(default="", blank=True)  
    logging = models.TextField(default="", blank=True)  
    pilog = models.TextField(default="", blank=True) 
    syslog = models.TextField(default="", blank=True) 
    #profiling_info = models.TextField(default="", blank=True)
    
    @property
    def jids_desc(self):
        return self.jid

    def get_jid_display(self):
        if self.is_group_entry:
            return self.group.get_jid_display()
        return self.jid
    
    def get_status_display(self):
        if self.is_group_entry:
            return self.group.get_status_display()
        return self.STATUS_DICT[self.status]
    
    @property
    def func_args(self):
        if self.func_args_pickled is None:
            return ()
        return pickle.loads(self.func_args_pickled)
    
    @property
    def func_kwargs(self):
        if self.func_kwargs_pickled is None:
            return {}
        return pickle.loads(self.func_kwargs_pickled)
    
    @property
    def result(self):
        if self.result_pickled is None:
            return None
        return pickle.loads(self.result_pickled)
    
    def kill(self):
        return self.backend.kill_job(job_data=self.get_queue_data())
    
    def delete(self, *args, **kwargs):
        # really delete it?
        if kwargs.get('purge', True):
            kwargs.pop("purge")
            return super(Job, self).delete(*args, **kwargs)
        # send to backend
        return self.backend.delete_job(self.get_queue_data(), self.status)
    
    get_creator_api_key_info = lambda self: self.apikey_id
    get_creator_hostname_info = lambda self: self.hostname
    get_status_info = lambda self: self.get_status_display()
    get_stdout_info = lambda self: '' #FIXME
    get_stderr_info = lambda self: '' #FIXME
    get_pilog_info = lambda self: '' #FIXME
    get_logging_info = lambda self: '' #FIXME
    get_exception_info = lambda self: self.exception if self.exception else None
    get_max_runtime_info = lambda self: self.max_runtime
    get_runtime_info = lambda self: None #FIXME
    get_created_info = lambda self: self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None 
    get_finished_info = lambda self: self.finished_at.strftime("%Y-%m-%d %H:%M:%S") if self.finished_at else None 
    get_vol_info = lambda self: [] #FIXME
    get_env_info = lambda self: None #FIXME
    get_function_info = lambda self: self.func_name
    get_label_info = lambda self: self.label
    get_parent_jid_info = lambda self: None #FIXME
    get_disk_usage_info = lambda self: None #FIXME
    get_func_body_info = lambda self: base64.encodestring(bytes(self.func_obj_pickled))
    get_args_info = lambda self: base64.encodestring(bytes(self.func_args_pickled))
    get_kwargs_info = lambda self: base64.encodestring(bytes(self.func_kwargs_pickled))
    get_memory_failcnt_info = lambda self: None #FIXME
    get_memory_max_usage_info = lambda self: None #FIXME
    get_memory_usage_info = lambda self: None #FIXME
    get_cputime_user_info = lambda self: None #FIXME
    get_cputime_system_info = lambda self: None #FIXME
    get_cpu_percentage_user_info = lambda self: None #FIXME
    get_cpu_percentage_system_info = lambda self: None #FIXME
    get_ports_info = lambda self: None #FIXME
    get_profile_info = lambda self: None #FIXME
    get_code_version_info = lambda self: self.ap_version
    
    # data about job sent to queue
    JOB_QUEUE_DATA_FIELDS = (
        'pk', 'group_id', 
        'owner_id', 'jid', 
        'depends_on_desc', 'job_type',
    )
    
    # data aboutjob sent to execution engine
    JOB_DATA_FIELDS = (
        'pk', 'group_id', 
        'owner_id', 'hostname', 'apikey_id',
        'jid', 'job_type', 'ap_version', 
        'depends_on_desc',
        'cores', 'core_type', 
        'func_name', 'func_obj_pickled', 'func_args_pickled', 'func_kwargs_pickled', 
        'max_runtime', 'restartable', 'profile', 'fast_serialization', 
    )
        
    def get_job_data(self):
        ret =  {k: getattr(self, k) for k in self.JOB_DATA_FIELDS}
        for name in ('func_obj_pickled', 'func_args_pickled', 'func_kwargs_pickled'):
            ret[name]= bytes(ret[name]) if ret[name] is not None else None
        return ret
    
    def get_queue_data(self):
        ret =  {k: getattr(self, k) for k in self.JOB_QUEUE_DATA_FIELDS}
        return ret
