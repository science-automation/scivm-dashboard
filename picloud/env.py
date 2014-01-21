from django.contrib.auth.models import User
from django.conf.urls import url

from tastypie import fields
from tastypie.authorization import Authorization
from apikey.authentication import SciCloudApiKeyAuthentication

from .base import CloudResource, dispatch

from cloud.util.zip_packer import Packer, UnPacker

from environment.models import Environment
from image.models import Image

import json
import pickle


class CloudEnvironmentResource(CloudResource):
    
    class Meta:
        resource_name = 'environment'
        authorization = Authorization()
        authentication = SciCloudApiKeyAuthentication()
        list_allowed_methods = []
        detail_allowed_methods = []
    
    @dispatch
    def list_hnd(self, request, **kwargs):
        return self.create_response(request, {})
    
    @dispatch("/list_bases/")
    def list_bases_hnd(self, request, **kwargs):
        return self.create_response(request, {})
    
    @dispatch
    def create_hnd(self, request, **kwargs):
        return self.create_response(request, {})
    
    @dispatch
    def edit_info_hnd(self, request, **kwargs):
        return self.create_response(request, {})
    
    @dispatch
    def modify_hnd(self, request, **kwargs):
        return self.create_response(request, {})

    @dispatch
    def save_hnd(self, request, **kwargs):
        return self.create_response(request, {})
    
    @dispatch
    def save_shutdown_hnd(self, request, **kwargs):
        return self.create_response(request, {})
    
    @dispatch
    def shutdown_hnd(self, request, **kwargs):
        return self.create_response(request, {})
    
    @dispatch
    def clone_hnd(self, request, **kwargs):
        return self.create_response(request, {})

    @dispatch
    def delete_hnd(self, request, **kwargs):
        return self.create_response(request, {})
    

