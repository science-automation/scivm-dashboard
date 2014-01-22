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
from environment.models import Environment
from scivm import utils

class Image(models.Model):
    environments = models.ManyToManyField(Environment, related_name='included_images')
    image_id = models.CharField(max_length=96, null=True, blank=True)
    name = models.CharField(max_length=256, null=False, blank=False)
    owner = models.ForeignKey(User)
    description = models.TextField(default="", blank=True)
    created = models.DateTimeField(auto_now_add=True)
    lastmodified = models.DateTimeField(auto_now_add=True)
    public = models.BooleanField(null=False, default=False)
    base = models.BooleanField(null=False, default=False)
    size = models.BigIntegerField(null=True, blank=True)
