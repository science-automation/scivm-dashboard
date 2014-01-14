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
