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

from tastypie import fields
from tastypie.resources import ModelResource
from tastypie.authorization import Authorization
from apikey.authentication import (MultiApiKeyAuthentication,
    SessionAuthentication, MultiAuthentication)
from django.contrib.auth.models import User
from tastypie.bundle import Bundle
from django.conf.urls import url
from jobs.models import Job

class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'

class JobResource(ModelResource):
    owner = fields.ForeignKey(UserResource, 'user', null=True, blank=True)

    class Meta:
        queryset = Job.objects.all()
        resource_name = 'job'
        authorization = Authorization()
        authentication = MultiAuthentication(
            MultiApiKeyAuthentication(), SessionAuthentication())
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']
