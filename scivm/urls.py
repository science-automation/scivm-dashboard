# Copyright 2013 Evan Hazlett and contributors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from django.conf.urls import patterns, include, url
from tastypie.api import Api
from django.contrib import admin
admin.autodiscover()

from crons.api import CronResource
from jobs.api import JobResource
from volume.api import VolumeResource
from bucket.api import BucketResource
from environment.api import EnvironmentResource
from picloud.urls import cloud_api

v1_api = Api(api_name='v1')
v1_api.register(CronResource())
v1_api.register(JobResource())
v1_api.register(VolumeResource())
v1_api.register(BucketResource())
v1_api.register(EnvironmentResource())


urlpatterns = patterns('',
    url(r'^$', 'scivm.views.index', name='index'),
    url(r'^api/login', 'accounts.views.api_login', name='api_login'),
    url(r'^api/', include(v1_api.urls)),
    url(r'^api/', include(cloud_api.urls)),
    url(r'^accounts/', include('accounts.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^jobs/', include('jobs.urls')),
    url(r'^apikey/', include('apikey.urls')),
    url(r'^support/', include('support.urls')),
    url(r'^volume/', include('volume.urls')),
    url(r'^bucket/', include('bucket.urls')),
    url(r'^payment/', include('payment.urls')),
    url(r'^start/', include('start.urls')),
    url(r'^settings/', include('settings.urls')),
    url(r'^crons/', include('crons.urls')),
    url(r'^environment/', include('environment.urls')),
)
