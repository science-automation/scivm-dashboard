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

from django.conf.urls import patterns, url

urlpatterns = patterns('apikey.views',
    url(r'^$', 'index'),
    url(r'^add/$', 'add_apikey'),
    url(r'^edit/(?P<apikey_id>.*)/$', 'edit_apikey'),
    url(r'^enable/(?P<apikey_id>.*)/$', 'enable_apikey'),
    url(r'^disable/(?P<apikey_id>.*)/$', 'disable_apikey'),
    url(r'^remove/(?P<apikey_id>.*)/$', 'remove_apikey'),
)
