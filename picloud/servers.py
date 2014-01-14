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
        """ Returns a list of urls for available api servers """
        # TODO it's hardcoded in settings for now
        return self.create_response(request, {"servers": [ settings.SCICLOUD_API_ROOT_URL, ]})
