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

from django.conf.urls import patterns, include, url
from tastypie.api import Api
from django.contrib import admin
admin.autodiscover()

from crons.api import CronResource
from jobs.api import JobResource
from volume.api import VolumeResource
from bucketfile.api import BucketFileResource
from bucketstore.api import BucketStoreResource
from provider.api import ProviderResource
from environment.api import EnvironmentResource
from image.api import ImageResource
from picloud.urls import cloud_api

v1_api = Api(api_name='v1')
v1_api.register(CronResource())
v1_api.register(JobResource())
v1_api.register(VolumeResource())
v1_api.register(BucketFileResource())
v1_api.register(BucketStoreResource())
v1_api.register(ProviderResource())
v1_api.register(EnvironmentResource())
v1_api.register(ImageResource())


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
    url(r'^bucketfile/', include('bucketfile.urls')),
    url(r'^bucketstore/', include('bucketstore.urls')),
    url(r'^provider/', include('provider.urls')),
    url(r'^payment/', include('payment.urls')),
    url(r'^start/', include('start.urls')),
    url(r'^settings/', include('settings.urls')),
    url(r'^crons/', include('crons.urls')),
    url(r'^environment/', include('environment.urls')),
    url(r'^image/', include('image.urls')),
)
