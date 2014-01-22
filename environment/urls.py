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

urlpatterns = patterns('environment.views',
    url(r'^$', 'index'),
    url(r'^add/$', 'add_environment'),
    url(r'^favorite/(?P<environment_id>.*)/$', 'favorite_environment'),
    url(r'^unfavorite/(?P<environment_id>.*)/$', 'unfavorite_environment'),
    url(r'^clone/(?P<environment_id>.*)/$', 'clone_environment'),
    url(r'^share/(?P<environment_id>.*)/$', 'share_environment'),
    url(r'^edit/(?P<environment_id>.*)/$', 'edit_environment'),
    url(r'^modify/(?P<environment_id>.*)/$', 'modify_environment'),
    url(r'^remove/(?P<environment_id>.*)/$', 'remove_environment'),
    url(r'^public/(?P<environment_id>.*)/$', 'public_environment'),
    url(r'^private/(?P<environment_id>.*)/$', 'private_environment'),
    url(r'^attach_image/(?P<environment_id>.*)/(?P<image_id>.*)$', 'attach_image'),
    url(r'^unattach_image/(?P<environment_id>.*)/(?P<image_id>.*)$', 'unattach_image'),
)
