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
