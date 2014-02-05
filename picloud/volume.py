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

from scicloud.util.zip_packer import Packer, UnPacker

import json
import pickle


class CloudVolumeResource(CloudResource):
    
    class Meta:
        resource_name = 'volume'
        authorization = Authorization()
        authentication = SciCloudApiKeyAuthentication()
        list_allowed_methods = []
        detail_allowed_methods = []
    
    @dispatch
    def list_hnd(self, request, **kwargs):
        return self.create_response(request, {})
    
    @dispatch
    def create_hnd(self, request, **kwargs):
        return self.create_response(request, {})
    
    @dispatch
    def mkdir_hnd(self, request, pk, **kwargs):
        return self.create_response(request, {})
    
    @dispatch
    def sync_initiate_hnd(self, request, **kwargs):
        return self.create_response(request, {})
    
    @dispatch
    def sync_terminate_hnd(self, request, **kwargs):
        return self.create_response(request, {})
    
    @dispatch
    def delete_hnd(self, request, pk, **kwargs):
        return self.create_response(request, {})
    
    @dispatch
    def check_release_hnd(self, request, pk, **kwargs):
        return self.create_response(request, {})
    
    @dispatch
    def ls_hnd(self, request, pk, **kwargs):
        return self.create_response(request, {})
    
    @dispatch
    def rm_hnd(self, request, pk, **kwargs):
        return self.create_response(request, {})
    

