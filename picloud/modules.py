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
from django.conf import settings

from tastypie import fields
from tastypie.authorization import Authorization
from tastypie.authentication import Authentication
from apikey.authentication import SciCloudApiKeyAuthentication

from .base import CloudResource, dispatch

from scicloud.util.zip_packer import Packer, UnPacker

import json
import pickle
import zerorpc

from .backends.conf import MODMAN_AS_SERVICE, MODMAN_SERVICE_ENDPOINT
if MODMAN_AS_SERVICE:
    _backend = zerorpc.Client(MODMAN_SERVICE_ENDPOINT)
else:
    from .backends.modman_service import Service
    _backend = Service()


class CloudPackageResource(CloudResource):
    BACKEND_TIMEOUT = 10

    class Meta:
        resource_name = 'package'
        authorization = Authorization()
        authentication = SciCloudApiKeyAuthentication()
        list_allowed_methods = []
        detail_allowed_methods = []

    @dispatch
    def list_hnd(self, request, **kwargs):
        """ Returns a list of package names to ignore (for dependency manager, client side) 
            Client expects a list under the key "packages" in the response.
        """
        # FIXME send user_id ? environment ?!
        packages_to_ignore = _backend.packages_to_ignore(timeout=self.BACKEND_TIMEOUT) 
        return self.create_response(request, {"packages": packages_to_ignore })


class CloudModuleResource(CloudResource):
    BACKEND_TIMEOUT = 10

    class Meta:
        resource_name = 'module'
        authorization = Authorization()
        authentication = SciCloudApiKeyAuthentication()
        list_allowed_methods = []
        detail_allowed_methods = []
    
    @dispatch
    def check_hnd(self, request, **kwargs):
        """ Compares the imported modules of the client to the modules we have in the environment of the user. 
            Returns what modules the client should upload.
            
            Incoming data format:
                
                [ ["<module1-rel-path>", <module1-timestamp, <module1-is-archive>"], ... ]
            
            Client expects the same kind of list under the key "modules" in the response.
        """
        # load json input
        module_descs_in = self.load_json_from_file(request, "data")        
        
        # get list of modules to upload from backend 
        response = _backend.check_modules(request.user.pk, module_descs_in, timeout=self.BACKEND_TIMEOUT)

        # FIXME when should we send ap_version?
        return self.create_response(request, { "modules": response["modules_to_upload"]})
    
    @dispatch
    def add_hnd(self, request, **kwargs):
        """ Stores the modules sent by the client and creates a new environment version for the user
            
            Incoming data:
                1. [ ["<module1-rel-path>", <module1-timestamp, <module1-is-archive>"], ... ]
                2. A tar file with all modules

            Client expects an environment version under the key "ap_version".
        """
        source = UnPacker(request.FILES["data"])
        
        module_descs_in = json.loads(source.next())
        tarfile_raw = bytes(source.next())
        
        response = _backend.add_modules(request.user.pk, module_descs_in, tarfile_raw, timeout=self.BACKEND_TIMEOUT)
        return self.create_response(request, {"ap_version": response["ap_version"]})
