from django.contrib.auth.models import User
from django.conf.urls import url

from tastypie import fields
from tastypie.authorization import Authorization
from apikey.authentication import SciCloudApiKeyAuthentication

from .base import CloudResource, dispatch

from cloud.util.zip_packer import Packer, UnPacker

import json
import pickle


class CloudAccountResource(CloudResource):
    
    class Meta:
        resource_name = 'account'
        authorization = Authorization()
        authentication = SciCloudApiKeyAuthentication()
        list_allowed_methods = []
        detail_allowed_methods = []
    
    @dispatch("/")
    def create_hnd(self, request, **kwargs):
        return self.create_response(request, {})
    
    @dispatch
    def list_hnd(self, request, **kwargs):
        return self.create_response(request, {})
    
    @dispatch("/(?P<pk>\d+)/")
    def get_hnd(self, request, pk, **kwargs):
        return self.create_response(request, {})
    
    @dispatch("/(?P<pk>\d+)/activate/")
    def activate_hnd(self, request, pk,  **kwargs):
        return self.create_response(request, {})
    
    @dispatch("/(?P<pk>\d+)/deactivate/")
    def deactivate_hnd(self, request, pk, **kwargs):
        return self.create_response(request, {})
    

