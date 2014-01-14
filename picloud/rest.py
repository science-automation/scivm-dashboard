from django.contrib.auth.models import User
from django.conf.urls import url

from tastypie import fields
from tastypie.authorization import Authorization
from apikey.authentication import SciCloudApiKeyAuthentication

from .base import CloudResource, dispatch

from cloud.util.zip_packer import Packer, UnPacker

import json
import pickle


class CloudRestResource(CloudResource):
    
    class Meta:
        resource_name = 'rest'
        authorization = Authorization()
        authentication = SciCloudApiKeyAuthentication()
        list_allowed_methods = []
        detail_allowed_methods = []

    @dispatch
    def register_hnd(self, request, **kwrags):
        return self.create_response(request, {})
    
    @dispatch
    def deregister_hnd(self, request, **kwrags):
        return self.create_response(request, {})
    
    @dispatch
    def list_hnd(self, request, **kwrags):
        return self.create_response(request, {})
    
    @dispatch
    def info_hnd(self, request, **kwrags):
        return self.create_response(request, {})
    
    @dispatch("/invoke/(?P<pk>\d+)/")
    def invoke_hnd(self, request, **kwrags):
        return self.create_response(request, {})
    
    @dispatch("/invoke/(?P<pk>\d+)/map/")
    def invoke_map_hnd(self, request, **kwrags):
        return self.create_response(request, {})
    

