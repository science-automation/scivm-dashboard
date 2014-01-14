from django.contrib.auth.models import User
from django.conf.urls import url

from tastypie import fields
from tastypie.authorization import Authorization
from apikey.authentication import SciCloudApiKeyAuthentication

from .base import CloudResource, dispatch

from cloud.util.zip_packer import Packer, UnPacker

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
    def list_hnd(self, request, **kwrags):
        return self.create_response(request, {})
    
    @dispatch
    def create_hnd(self, request, **kwrags):
        return self.create_response(request, {})
    
    @dispatch
    def mkdir_hnd(self, request, pk, **kwrags):
        return self.create_response(request, {})
    
    @dispatch
    def sync_initiate_hnd(self, request, **kwrags):
        return self.create_response(request, {})
    
    @dispatch
    def sync_terminate_hnd(self, request, **kwrags):
        return self.create_response(request, {})
    
    @dispatch
    def delete_hnd(self, request, pk, **kwrags):
        return self.create_response(request, {})
    
    @dispatch
    def check_release_hnd(self, request, pk, **kwrags):
        return self.create_response(request, {})
    
    @dispatch
    def ls_hnd(self, request, pk, **kwrags):
        return self.create_response(request, {})
    
    @dispatch
    def rm_hnd(self, request, pk, **kwrags):
        return self.create_response(request, {})
    

