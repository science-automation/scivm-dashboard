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

import celery
from django.core.cache import cache
from django.conf import settings
from django.utils.translation import ugettext as _
from environment.models import Environment
from exceptions import RecoveryThresholdError
import utils
import hashlib

@celery.task
def import_image(repo_name=None):
#    if not repo_name:
#        raise StandardError('You must specify a repo name')
#    hosts = Host.objects.filter(enabled=True)
#    for h in hosts:
#        import_image_to_host.subtask((h, repo_name)).apply_async()
    return True

@celery.task
def build_image(path=None, tag=None):
#    if not path:
#        raise StandardError('You must specify a path')
#    hosts = Host.objects.filter(enabled=True)
#    for h in hosts:
    return True
