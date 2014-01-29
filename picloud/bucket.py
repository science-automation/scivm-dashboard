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

from tastypie.authorization import Authorization
from apikey.authentication import SciCloudApiKeyAuthentication

from .base import CloudResource, dispatch
from tastypie import http 

import json
import pickle

import boto


class S3(object):
    
    def __init__(self, access_key, secret_key, root_bucket_name, debug=None):
        self._access_key = access_key
        self._secret_key = secret_key
        self._conn = boto.connect_s3(self._access_key, self._secret_key, debug=debug)
        self._root_bucket_name = root_bucket_name

    def get_bucket(self):
        return boto.s3.bucket.Bucket(connection=self._conn, name=self._root_bucket_name)
    
    def get_key(self, user, name):
        bucket = self.get_bucket()
        eff_name = self.prefix_with_user_dir(user, name)
        key = bucket.lookup(eff_name)
        return key

    def prefix_with_user_dir(self, user, name):
        #FIXME
        return name
    
    def public_url_folder(self, user):
        #FIXME prefixed with https://s3.amazonaws.com/ by cli
        #TODO
        return "?"


s3 = S3(settings.SCICLOUD_S3_ACCESS_KEY, 
        settings.SCICLOUD_S3_SECRET_KEY, 
        settings.SCICLOUD_S3_ROOT_BUCKET, 
        settings.SCICLOUD_S3_DEBUG_LEVEL
)


class CloudBucketResource(CloudResource):
    
    class Meta:
        resource_name = 'bucket'
        authorization = Authorization()
        authentication = SciCloudApiKeyAuthentication()
        list_allowed_methods = []
        detail_allowed_methods = []
   
    def _file_not_found(self, request):
        return self.error_response(request, {"error": {
                "msg": "The specified file was not found.", 
                "code": "492", 
                "retry": False
                }}, response_class=http.HttpResponse) 

    @dispatch 
    def new_hnd(self, request, **kwargs):
        """
        return self.create_response(request, {
            "ticket": {
                "AWSAccessKeyId": "AKIAJCY7JV52WD4MJSNQ", 
                "acl": "private", 
                "key": "Wdzvw6doCTYgeFJstoKvEdxDUMi0Rd1x43F1cJpj/mi.mi", 
                "signature": "oGFA/pGeHrcJW/qe/MzwE4Mnues=", 
                "policy": "eyJjb25kaXRpb25zIjogW3siYnVja2V0IjogInBpLXVzZXItYnVja2V0cyJ9LCB7ImtleSI6ICJXZHp2dzZkb0NUWWdlRkpzdG9LdkVkeERVTWkwUmQxeDQzRjFjSnBqL21pLm1pIn0sIHsiYWNsIjogInByaXZhdGUifSwgWyJzdGFydHMtd2l0aCIsICIkQ29udGVudC1UeXBlIiwgIiJdLCBbInN0YXJ0cy13aXRoIiwgIiRDb250ZW50LU1ENSIsICIiXV0sICJleHBpcmF0aW9uIjogIjIwMTQtMDEtMjhUMjA6Mzc6MjFaIn0=", 
                "Content-Type": "binary/octet-stream"
            }, 
            "params": {
                "action": "https://pi-user-buckets.s3-external-1.amazonaws.com/"
            }
        })
        """
        return self.create_response(request, {})

    @dispatch 
    def list_hnd(self, request, **kwargs):
        prefix = request.POST.get("prefix", None)
        marker = request.POST.get("marker", None)
        #max_keys = max([ min([int(request.POST.get("max_keys", 1000)), 1000]), 1)
        delimiter = request.POST.get("delimiter", None)
        
        return self.create_response(request, {"files": [], "truncated": True or False}) #FIXME
    
    @dispatch 
    def get_hnd(self, request, **kwargs):
        return self.create_response(request, {})
    
    @dispatch 
    def exists_hnd(self, request, **kwargs):
        """ Checks if key given by name exists or not
            Returns True or False under the key name 'exists'.
        """
        name = request.POST["name"]
        key = s3.get_key(request.user, name)
        return self.create_response(request, {"exists": key is not None})
    
    @dispatch 
    def info_hnd(self, request, **kwargs):
        """ Information about key given by "name".
            Data comes form a PATCH request to s3.
        """
        name = request.POST["name"]
        
        key = s3.get_key(request.user, name)
        if key is None: 
            return self._file_not_found(request)

        resp = {
            "content-disposition": key.content_disposition, 
            "content-encoding": key.content_encoding, 
            "md5sum": key.etag, #FIXME md5 must be stored somewhere else
            "last-modified": key.last_modified, 
            "cache-control": key.cache_control, 
            "content-type": key.content_type, 
            "public": False, #FIXME from where this info comes from?
            "size": key.size
        }
        return self.create_response(request, resp)
    
    @dispatch 
    def md5_hnd(self, request, **kwargs):
        name = request.POST["name"]
        
        key = s3.get_key(request.user, name)
        if key is None: 
            return self._file_not_found(request)
        
        #TODO etag is not good for this; maybe its stored somewhere else

        return self.create_response(request, {"md5sum": key.etag}) #FIXME
    
    @dispatch 
    def remove_hnd(self, request, **kwargs):
        name = request.POST["name"]
        
        key = s3.get_key(request.user, name)
        if key is None: 
            return self._file_not_found(request)
        
        #TODO

        return self.create_response(request, {"removed": True or False}) #FIXME
    
    @dispatch("/is_public/")
    def is_public_hnd(self, request, **kwargs):
        name = request.POST["name"]
        
        key = s3.get_key(request.user, name)
        if key is None: 
            return self._file_not_found(request)
        
        #TODO

        return self.create_response(request, {"status": True or False}) #FIXME

    @dispatch("/make_public/")
    def make_public_hnd(self, request, **kwargs):
        name = request.POST["name"]
        reset_headers = bool(request.POST["reset_headers"])
        headers = [ (key[3:], value) for key,value in request.POST.items() if key.startswith("bh_") ]
        
        key = s3.get_key(request.user, name)
        if key is None: 
            return self._file_not_found(request)
        
        #TODO

        return self.create_response(request, {"url": "?"}) #FIXME prefixed with https://s3.amazonaws.com/ by cli
    
    @dispatch("/make_private/")
    def make_private_hnd(self, request, **kwargs):
        name = request.POST["name"]
        
        key = s3.get_key(request.user, name)
        if key is None: 
            return self._file_not_found(request)
        
        #TODO

        return self.create_response(request, {"status": True or False}) #FIXME
    
    @dispatch("/public_url_folder/")
    def public_url_folder_hnd(self, request, **kwargs):
        """ Gives back the url of the user's public s3 folder """
        url = s3.public_url_folder(request.user)
        return self.create_response(request, {"url": url}) 

