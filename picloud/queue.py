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

from django.contrib.auth.models import User
from django.conf.urls import url

from tastypie import fields
from tastypie.authorization import Authorization
from apikey.authentication import SciCloudApiKeyAuthentication

from .base import CloudResource, dispatch

from cloud.util.zip_packer import Packer, UnPacker

import json
import pickle


class CloudQueueResource(CloudResource):
    
    class Meta:
        resource_name = 'queue'
        authorization = Authorization()
        authentication = SciCloudApiKeyAuthentication()
        list_allowed_methods = []
        detail_allowed_methods = []
    
    @dispatch("/", methods=["GET", "POST"])
    def list_or_create_hnd(self, request, **kwargs):
        return self.create_response(request, {})
    
    @dispatch("/(?P<name>\w+)/")
    def info_hnd(self, request, name, **kwargs):
        return self.create_response(request, {})
    
    @dispatch("/(?P<name>\w+)/count/")
    def count_hnd(self, request, name, **kwargs):
        return self.create_response(request, {})

    @dispatch("/(?P<name>\w+)/exists/")
    def exists_hnd(self, request, name, **kwargs):
        return self.create_response(request, {})
    
    @dispatch("/(?P<name>\w+)/delete/")
    def delete_hnd(self, request, name, **kwargs):
        return self.create_response(request, {})
    
    @dispatch("/(?P<name>\w+)/push/")
    def push_hnd(self, request, name, **kwargs):
        return self.create_response(request, {})
    
    @dispatch("/(?P<name>\w+)/pop/")
    def pop_hnd(self, request, name, **kwargs):
        return self.create_response(request, {})
    
    @dispatch("/(?P<name>\w+)/pop_tickets/")
    def pop_tickets_hnd(self, request, name, **kwargs):
        return self.create_response(request, {})

    @dispatch("/(?P<name>\w+)/ack/")
    def ack_hnd(self, request, name, **kwargs):
        return self.create_response(request, {})

    @dispatch("/(?P<name>\w+)/update_deadline/")
    def update_deadline_hnd(self, request, name, **kwargs):
        return self.create_response(request, {})
    
    @dispatch("/(?P<name>\w+)/attach/")
    def attach_hnd(self, request, name, **kwargs):
        return self.create_response(request, {})

    @dispatch("/(?P<name>\w+)/detach/")
    def detach_hnd(self, request, name, **kwargs):
        return self.create_response(request, {})
    

