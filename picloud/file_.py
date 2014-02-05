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


class CloudFileResource(CloudResource):
    
    class Meta:
        resource_name = 'file'
        authorization = Authorization()
        authentication = SciCloudApiKeyAuthentication()
        list_allowed_methods = []
        detail_allowed_methods = []
    
    @dispatch
    def new_hnd(self, request, **kwargs):
        return self.create_response(request, {})
    
    @dispatch
    def put_hnd(self, request, **kwargs):
        return self.create_response(request, {})
    
    @dispatch
    def list_hnd(self, request, **kwargs):
        return self.create_response(request, {})
    
    @dispatch
    def get_hnd(self, request, **kwargs):
        return self.create_response(request, {})
    
    @dispatch
    def exists_hnd(self, request, **kwargs):
        return self.create_response(request, {})

    @dispatch
    def md5_hnd(self, request, **kwargs):
        return self.create_response(request, {})
    
    @dispatch
    def delete_hnd(self, request, **kwargs):
        return self.create_response(request, {})
    

