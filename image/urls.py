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

urlpatterns = patterns('image.views',
    url(r'^$', 'index'),
    url(r'^add/$', 'add_image'),
    url(r'^favorite/(?P<image_id>.*)/$', 'favorite_image'),
    url(r'^unfavorite/(?P<image_id>.*)/$', 'unfavorite_image'),
    url(r'^clone/(?P<image_id>.*)/$', 'clone_image'),
    url(r'^share/(?P<image_id>.*)/$', 'share_image'),
    url(r'^edit/(?P<image_id>.*)/$', 'edit_image'),
    url(r'^modify/(?P<image_id>.*)/$', 'modify_image'),
    url(r'^remove/(?P<image_id>.*)/$', 'remove_image'),
    url(r'^public/(?P<image_id>.*)/$', 'public_image'),
    url(r'^private/(?P<image_id>.*)/$', 'private_image'),
    url(r'^import/$', 'import_image'),
    url(r'^import/$', 'build_image'),
)
