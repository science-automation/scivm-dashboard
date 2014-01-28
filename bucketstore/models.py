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
from json_field import JSONField
from scivm import utils

class BucketStore(models.Model):
    name = models.CharField(max_length=96, null=True, blank=True)
    owner = models.ForeignKey(User)
    description = models.TextField(default="", blank=True)
    created = models.DateTimeField(auto_now_add=True)

    # amazon ec2 access and secret key
    access_key = models.CharField(max_length=96, null=True, blank=True)
    access_secret_key = models.CharField(max_length=96, null=True, blank=True)
