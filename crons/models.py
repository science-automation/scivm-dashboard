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

