from django.contrib.auth.models import User
from django.conf.urls import url

from tastypie import fields
from tastypie.authorization import Authorization
from apikey.authentication import SciCloudApiKeyAuthentication

from .base import CloudResource, dispatch

from cloud.util.zip_packer import Packer, UnPacker

import json
import pickle


class CloudRealtimeResource(CloudResource):
    
    class Meta:
        resource_name = 'realtime'
        authorization = Authorization()
        authentication = SciCloudApiKeyAuthentication()
        list_allowed_methods = []
        detail_allowed_methods = []

    @dispatch
    def request_hnd(self, request, **kwrags):
        return self.create_response(request, {})
    
    @dispatch
    def release_hnd(self, request, **kwrags):
        return self.create_response(request, {})
    
    @dispatch
    def list_hnd(self, request, **kwrags):
        return self.create_response(request, {})
    
    @dispatch("/change_max_duration/")
    def change_max_duration_hnd(self, request, **kwrags):
        return self.create_response(request, {})

