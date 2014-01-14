from django.contrib.auth.models import User
from django.conf.urls import url
from django.conf import settings

from tastypie import fields
from tastypie.authorization import Authorization
from tastypie.authentication import Authentication
from apikey.authentication import SciCloudApiKeyAuthentication

from .base import CloudResource, dispatch

from cloud.util.zip_packer import Packer, UnPacker

import json
import pickle


class CloudServerResource(CloudResource):

    class Meta:
        resource_name = 'servers'
        authorization = Authorization()
        authentication = Authentication()
        list_allowed_methods = []
        detail_allowed_methods = []
    
    @dispatch
    def list_hnd(self, request, **kwargs):
        return self.create_response(request, {"servers": [ settings.SCICLOUD_API_ROOT_URL, ]})


class CloudPackageResource(CloudResource):

    class Meta:
        resource_name = 'package'
        authorization = Authorization()
        authentication = SciCloudApiKeyAuthentication()
        list_allowed_methods = []
        detail_allowed_methods = []
    
    @dispatch
    def list_hnd(self, request, **kwargs):
        return self.create_response(request, {"packages": []})


class CloudModuleResource(CloudResource):

    class Meta:
        resource_name = 'module'
        authorization = Authorization()
        authentication = SciCloudApiKeyAuthentication()
        list_allowed_methods = []
        detail_allowed_methods = []

    @dispatch
    def check_hnd(self, request, **kwargs):
        #ret = {"ap_version": "9wc1e9b6bd8346e586d5db417ba7dd5cc4f95a8a", "modules": [[ "asciitable/basic.py", 1386464223, False], ["asciitable/ipac.py", 1386464221, False]]}
        return self.create_response(request, {"modules": []})
    
    @dispatch
    def add_hnd(self, request, **kwargs):
        return self.create_response(request, {"modules": []})

