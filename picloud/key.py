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

from tastypie.authorization import Authorization
from apikey.authentication import Authentication
from apikey.authentication import SciCloudApiKeyAuthentication

from .base import CloudResource, dispatch

from apikey.models import ApiKey


class CloudKeyResource(CloudResource):

    class Meta:
        resource_name = 'key'
        authorization = Authorization()
        authentication = SciCloudApiKeyAuthentication()
        list_allowed_methods = []
        detail_allowed_methods = []

    def _get_key(self, request, pk):
        try:
            return ApiKey.objects.filter(user=request.user).get(pk=pk)
        except ApiKey.DoesNotExist:
            return self.raise_response(request, {"error": {
                "msg": "The specified key was not found.",
                "code": "9492",  # FIXME
                "retry": False
            }})

    @dispatch("/")
    def create_hnd(self, request, **kwargs):
        key = ApiKey(user=request.user)
        key.save()
        return self.create_response(request, {
            "key": {
                "api_key": key.pk,
                "api_secretkey": key.key,
                "private_key": "XXXXXXXX",  # FIXME
            }
        })

    @dispatch
    def list_hnd(self, request, **kwargs):
        active_only = request.POST.get("active_only", True)
        qs = ApiKey.objects.filter(user=request.user)
        if active_only:
            qs = qs.filter(enabled=True)
        api_keys = list(qs.values_list("pk", flat=True))
        return self.create_response(request, {"api_keys": api_keys})

    @dispatch("/(?P<pk>\d+)/")
    def get_hnd(self, request, pk, **kwargs):
        key = self._get_key(request, pk)
        return self.create_response(request, {
            "key": {
                "api_key": key.pk,
                "api_secretkey": key.key,
                "private_key": "XXXXXXXX",  # FIXME
            }
        })

    @dispatch("/(?P<pk>\d+)/activate/")
    def activate_hnd(self, request, pk,  **kwargs):
        key = self._get_key(request, pk)
        key.enabled = True
        key.save()
        return self.create_response(request, {})

    @dispatch("/(?P<pk>\d+)/deactivate/")
    def deactivate_hnd(self, request, pk, **kwargs):
        key = self._get_key(request, pk)
        key.enabled = False
        key.save()
        return self.create_response(request, {})
