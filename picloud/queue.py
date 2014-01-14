from django.contrib.auth.models import User
from django.conf.urls import url

from tastypie import fields
from tastypie.authorization import Authorization
from apikey.authentication import SciCloudApiKeyAuthentication

from .base import CloudResource, dispatch

from cloud.util.zip_packer import Packer, UnPacker

import json
import pickle


class CloudQueueResource(CloudResource):
    
    class Meta:
        resource_name = 'queue'
        authorization = Authorization()
        authentication = SciCloudApiKeyAuthentication()
        list_allowed_methods = []
        detail_allowed_methods = []
    
    @dispatch("/", methods=["GET", "POST"])
    def list_or_create_hnd(self, request, **kwrags):
        return self.create_response(request, {})
    
    @dispatch("/(?P<name>\w+)/")
    def info_hnd(self, request, name, **kwrags):
        return self.create_response(request, {})
    
    @dispatch("/(?P<name>\w+)/count/")
    def count_hnd(self, request, name, **kwrags):
        return self.create_response(request, {})

    @dispatch("/(?P<name>\w+)/exists/")
    def exists_hnd(self, request, name, **kwrags):
        return self.create_response(request, {})
    
    @dispatch("/(?P<name>\w+)/delete/")
    def delete_hnd(self, request, name, **kwrags):
        return self.create_response(request, {})
    
    @dispatch("/(?P<name>\w+)/push/")
    def push_hnd(self, request, name, **kwrags):
        return self.create_response(request, {})
    
    @dispatch("/(?P<name>\w+)/pop/")
    def pop_hnd(self, request, name, **kwrags):
        return self.create_response(request, {})
    
    @dispatch("/(?P<name>\w+)/pop_tickets/")
    def pop_tickets_hnd(self, request, name, **kwrags):
        return self.create_response(request, {})

    @dispatch("/(?P<name>\w+)/ack/")
    def ack_hnd(self, request, name, **kwrags):
        return self.create_response(request, {})

    @dispatch("/(?P<name>\w+)/update_deadline/")
    def update_deadline_hnd(self, request, name, **kwrags):
        return self.create_response(request, {})
    
    @dispatch("/(?P<name>\w+)/attach/")
    def attach_hnd(self, request, name, **kwrags):
        return self.create_response(request, {})

    @dispatch("/(?P<name>\w+)/detach/")
    def detach_hnd(self, request, name, **kwrags):
        return self.create_response(request, {})
    

