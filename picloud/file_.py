from django.contrib.auth.models import User
from django.conf.urls import url

from tastypie import fields
from tastypie.authorization import Authorization
from apikey.authentication import SciCloudApiKeyAuthentication

from .base import CloudResource, dispatch

from cloud.util.zip_packer import Packer, UnPacker

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
    

