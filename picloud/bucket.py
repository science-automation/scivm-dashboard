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

from django.conf import settings
from django.utils.timezone import utc

from tastypie.authorization import Authorization
from apikey.authentication import SciCloudApiKeyAuthentication

from .base import CloudResource, dispatch
from tastypie import http

import json
import itertools
import datetime
import boto
import boto.gs
import boto.gs.bucket
import boto.s3.bucket

import base64
import hmac
from hashlib import sha1 as sha
from email.utils import formatdate
from urlparse import urlparse


class Store(object):

    # List of Query String Arguments of Interest
    special_params = [
        'acl', 'location', 'logging', 'partNumber', 'policy', 'requestPayment',
        'torrent', 'versioning', 'versionId', 'versions', 'website', 'uploads',
        'uploadId', 'response-content-type', 'response-content-language',
        'response-expires', 'response-cache-control', 'delete', 'lifecycle',
        'response-content-disposition', 'response-content-encoding'
    ]

    def __init__(self, type_, access_key, secret_key, root_bucket_name,
                 client_access_key, client_secret_key, debug=None):
        self._type = type_
        self._root_bucket_name = root_bucket_name

        self._access_key = access_key
        self._secret_key = secret_key

        self._cli_access_key = client_access_key
        self._cli_secret_key = client_secret_key

        self._upload_expiration_kwargs = {"hours": 8}

        connect_method = getattr(boto, "connect_" + type_)
        self._conn = connect_method(
            self._access_key,
            self._secret_key,
            debug=debug
        )

        self._BUCKET = {
            "s3": boto.s3.bucket.Bucket,
            "gs": boto.gs.bucket.Bucket
        }[type_]

        self._AUTH_HEADER = {
            "s3": "AWS",
            "gs": "GOOG1"
        }[type_]

    @property
    def service_base_url(self):
        return self._conn.DefaultHost

    @property
    def client_access_key(self):
        return self._cli_access_key

    @property
    def root_url(self):
        return "https://{0}/{1}".format(self.service_base_url, self.root_bucket_name)

    @property
    def root_bucket_name(self):
        return self._root_bucket_name

    def get_bucket(self):
        return self._BUCKET(connection=self._conn, name=self._root_bucket_name)

    def get_key(self, user, name):
        bucket = self.get_bucket()
        eff_name = self.prefix_with_user_dir(user, name)
        key = bucket.lookup(eff_name, headers={})
        return key

    def is_public(self, key):
        if self._type == "s3":
            acl = key.get_acl()
            for g in acl.acl.grants:
                if g.type == "Group" and  \
                   g.uri == "http://acs.amazonaws.com/groups/global/AllUsers" and \
                   g.permission == "READ":
                    return True
            return False
        else:
            return "private" not in key.cache_control

    def url_for_key(self, key, public=True):
        return "{0}/{1}".format(self.root_url, key.key)

    def prefix_with_user_dir(self, user, name):
        return "{0}/{1}".format(user.pk, name)

    def public_url_folder(self, user):
        # prefixed with https://s3.amazonaws.com/ by cli
        prefix = self.prefix_with_user_dir(user, "")
        return "{0}/{1}".format(self.root_bucket_name, prefix)

    def get_upload_policy(self, key):
        now = datetime.datetime.utcnow().replace(tzinfo=utc)
        exp_date = now + datetime.timedelta(**self._upload_expiration_kwargs)
        expiration = exp_date.strftime("%Y-%m-%dT%H:%M:%SZ")

        policy = {
            "conditions": [
                {"bucket": self._root_bucket_name},
                {"key": key},
                {"acl": "private"},
                ["starts-with", "$Content-Type", ""],
                ["starts-with", "$Content-MD5", ""]
            ],
            "expiration": expiration,
        }
        policy_encoded = json.dumps(policy).encode("utf-8")
        return policy_encoded.encode("base64").replace('\n', '')

    def get_policy_signature(self, encoded_policy):
        signature = hmac.new(self._cli_secret_key, encoded_policy, sha).digest()
        return signature.encode("base64").replace('\n', '')

    def get_auth_signature(self, method, url, headers):
        if not 'date' in headers and not 'x-amz-date' in headers:
            headers['date'] = formatdate(timeval=None, localtime=False, usegmt=True)
        canonical_string = self.get_canonical_string(url, headers, method)
        h = hmac.new(self._cli_secret_key, canonical_string, digestmod=sha)
        signature = base64.encodestring(h.digest()).strip()
        return '{0} {1}:{2}'.format(self._AUTH_HEADER,
                                    self._cli_access_key,
                                    signature)

    def get_canonical_string(self, url, headers, method):
        # from python-requests-aws package
        parsedurl = urlparse(url)
        objectkey = parsedurl.path[1:]
        query_args = sorted(parsedurl.query.split('&'))

        bucket = parsedurl.netloc[:-len(self.service_base_url)]
        if len(bucket) > 1:
            # remove last dot
            bucket = bucket[:-1]

        interesting_headers = {
            'content-md5': '',
            'content-type': '',
            'date': ''}
        for key in headers:
            lk = key.lower()
            try:
                lk = lk.decode('utf-8')
            except:
                pass
            if headers[key] and (lk in interesting_headers.keys() or
               lk.startswith('x-amz-')):
                interesting_headers[lk] = headers[key].strip()

        # If x-amz-date is used it supersedes the date header.
        if 'x-amz-date' in interesting_headers:
            interesting_headers['date'] = ''

        buf = '%s\n' % method
        for key in sorted(interesting_headers.keys()):
            val = interesting_headers[key]
            if key.startswith('x-amz-'):
                buf += '%s:%s\n' % (key, val)
            else:
                buf += '%s\n' % val

        # append the bucket if it exists
        if bucket != '':
            buf += '/%s' % bucket

        # add the objectkey. even if it doesn't exist, add the slash
        buf += '/%s' % objectkey

        params_found = False

        # handle special query string arguments
        for q in query_args:
            k = q.split('=')[0]
            if k in self.special_params:
                if params_found:
                    buf += '&%s' % q
                else:
                    buf += '?%s' % q
                params_found = True
        return buf


store = Store(
    settings.SCICLOUD_BUCKET_TYPE,
    settings.SCICLOUD_BUCKET_ACCESS_KEY,
    settings.SCICLOUD_BUCKET_SECRET_KEY,
    settings.SCICLOUD_BUCKET_NAME,
    settings.SCICLOUD_BUCKET_CLIENT_ACCESS_KEY,
    settings.SCICLOUD_BUCKET_CLIENT_SECRET_KEY,
    settings.SCICLOUD_BUCKET_DEBUG_LEVEL
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
        name = request.POST["name"]
        hex_md5 = request.POST['hex-md5']
        content_type = request.POST.get("content-type", "binary/octet-stream")
        content_encoding = request.POST.get('content-encoding', "")

        key = store.prefix_with_user_dir(request.user, name)

        policy_encoded = store.get_upload_policy(key)
        signature = store.get_policy_signature(policy_encoded)

        ticket = {
            "AWSAccessKeyId": store.client_access_key,
            "acl": "private",
            "key": key,
            "signature": signature,
            "policy": policy_encoded,
            "Content-Type": content_type,
            "Content-MD5": hex_md5,
        }
        if content_encoding:
            ticket["Content-Encoding"] = content_encoding

        response = {
            "ticket": ticket,
            "params": {
                "action": store.root_url,
            }
        }
        return self.create_response(request, response)

    @dispatch
    def list_hnd(self, request, **kwargs):
        """ Lists the files user has in the bucket.

            Follows the s3 bucket listing conventions. (perfix, marker, delimiter)
        """
        prefix = request.POST.get("prefix", "")
        marker = request.POST.get("marker", "")
        delimiter = request.POST.get("delimiter", "")

        max_keys = int(request.POST.get("max_keys", 1000))
        max_keys = max((1, max_keys))  # >= 1
        max_keys = min((1000, max_keys))  # <= 1000

        bucket = store.get_bucket()

        # prefix "prefix" with user dir
        eff_prefix = store.prefix_with_user_dir(request.user, prefix)

        # get list iterator from s3
        file_iter = bucket.list(prefix=eff_prefix, delimiter=delimiter,
                                marker=marker, headers=None,
                                encoding_type=None)

        # convert to list, try to get +1 item to be able
        # to determine if the results are truncated
        files = [key.key.split("/", 1)[1]
                 for key in itertools.islice(file_iter, 0, max_keys+1)]

        # if max_keys is less then there are more results
        # -> truncated = True
        truncated = len(files) > max_keys
        if truncated:
            # return 1 item less
            files = files[:-1]

        return self.create_response(request, {
            "files": files,
            "truncated": truncated
        })

    @dispatch
    def get_hnd(self, request, **kwargs):
        name = request.POST["name"]
        key = store.get_key(request.user, name)
        if key is None:
            return self._file_not_found(request)

        ticket = {}
        auth = store.get_auth_signature("GET", store.root_url + key.key, ticket)
        ticket["Authorization"] = auth
        response = {
            "ticket": ticket,
            "params": {
                "action": store.root_url + key.key,
                "bucket": store.root_bucket_name,
                "size": key.size,
            }
        }
        return self.create_response(request, response)

    @dispatch
    def exists_hnd(self, request, **kwargs):
        name = request.POST["name"]
        key = store.get_key(request.user, name)
        return self.create_response(request, {"exists": key is not None})

    @dispatch
    def info_hnd(self, request, **kwargs):
        name = request.POST["name"]

        key = store.get_key(request.user, name)
        if key is None:
            return self._file_not_found(request)

        status = store.is_public(key)
        resp = {
            "content-disposition": key.content_disposition,
            "content-encoding": key.content_encoding,
            "md5sum": key.etag[1:-1],
            "last-modified": key.last_modified,
            "cache-control": key.cache_control,
            "content-type": key.content_type,
            "public": status,
            "size": key.size
        }
        return self.create_response(request, resp)

    @dispatch
    def md5_hnd(self, request, **kwargs):
        name = request.POST["name"]

        key = store.get_key(request.user, name)
        if key is None:
            return self._file_not_found(request)

        md5sum = key.etag[1:-1]
        return self.create_response(request, {"md5sum": md5sum})

    @dispatch
    def remove_hnd(self, request, **kwargs):
        names = [store.prefix_with_user_dir(request.user, name)
                 for name in request.POST.getlist("name")]

        bucket = store.get_bucket()
        ret = bucket.delete_keys(names)
        if ret.errors:
            raise  # FIXME what to do
        return self.create_response(request, {"removed": True})

    @dispatch("/is_public/")
    def is_public_hnd(self, request, **kwargs):
        name = request.POST["name"]

        key = store.get_key(request.user, name)
        if key is None:
            return self._file_not_found(request)

        resp = {"status": store.is_public(key)}
        if resp["status"]:
            resp["url"] = store.url_for_key(key, public=True)
        return self.create_response(request, resp)

    @dispatch("/make_public/")
    def make_public_hnd(self, request, **kwargs):
        name = request.POST["name"]
        reset_headers = bool(request.POST.get("reset_headers", False))
        headers = [(key[3:], value) for key, value in request.POST.items()
                   if key.startswith("bh_")]

        key = store.get_key(request.user, name)
        if key is None:
            return self._file_not_found(request)

        key.set_canned_acl("public-read", headers=headers)
        url = store.url_for_key(key, public=True)
        return self.create_response(request, {"url": url})

    @dispatch("/make_private/")
    def make_private_hnd(self, request, **kwargs):
        name = request.POST["name"]

        key = store.get_key(request.user, name)
        if key is None:
            return self._file_not_found(request)

        key.set_canned_acl("private")
        status = True
        return self.create_response(request, {"status": status})

    @dispatch("/public_url_folder/")
    def public_url_folder_hnd(self, request, **kwargs):
        url = store.public_url_folder(request.user)
        return self.create_response(request, {"url": url})
