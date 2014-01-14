from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.utils.translation import ugettext as _
from django.db.models import Q
from django.core.cache import cache
from scivm import utils
from jobs.models import Job, JobTemplate


class Cron(JobTemplate):
    # most of the fields come from the base class
    
    class Meta:
        unique_together = (("owner", "label"),)

    cron_exp = models.CharField(max_length=96, blank=False)
    lastjob = models.ForeignKey(Job, null=True, blank=True)
    
    @property
    def lastrun_at(self):
        return  self.lastjob.created_at if self.lastjob_id else None #FIXME started_at ?

