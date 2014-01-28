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

def app_name(context):
    return { 'APP_NAME': getattr(settings, 'APP_NAME', 'Unknown')}

def app_revision(context):
    return { 'APP_REVISION': getattr(settings, 'APP_REVISION', 'Unknown')}

def google_analytics_code(context):
    return { 'GOOGLE_ANALYTICS_CODE': getattr(settings, 'GOOGLE_ANALYTICS_CODE', None)}

def managed_platform(context):
    return { 'MANAGED': getattr(settings, 'MANAGED', None)}
