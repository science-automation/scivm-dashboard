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

import hmac
import time
import uuid
from django.conf import settings
from django.db import models
from tastypie.utils import now
from django.contrib.auth.models import User

try:
    from hashlib import sha1
except ImportError:
    import sha
    sha1 = sha.sha


class ApiAccess(models.Model):
    """A simple model for use with the ``CacheDBThrottle`` behaviors."""
    identifier = models.CharField(max_length=255)
    url = models.CharField(max_length=255, blank=True, default='')
    request_method = models.CharField(max_length=10, blank=True, default='')
    accessed = models.PositiveIntegerField()

    def __unicode__(self):
        return u"%s @ %s" % (self.identifier, self.accessed)

    def save(self, *args, **kwargs):
        self.accessed = int(time.time())
        return super(ApiAccess, self).save(*args, **kwargs)


class ApiKey(models.Model):
    user = models.ForeignKey(User)
    key = models.CharField(max_length=128, blank=True, default='', db_index=True)
    enabled = models.BooleanField(default=True)
    created = models.DateTimeField(default=now)
    description = models.CharField(max_length=256, blank=True, default='')

    def __unicode__(self):
        return u"%s for %s" % (self.key, self.user)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()

        return super(ApiKey, self).save(*args, **kwargs)

    def generate_key(self):
        # Get a random UUID.
        new_uuid = uuid.uuid4()
        # Hmac that beast.
        return hmac.new(str(new_uuid), digestmod=sha1).hexdigest()

    class Meta:
        abstract = getattr(settings, 'TASTYPIE_ABSTRACT_APIKEY', False)


def create_api_key(sender, **kwargs):
    """
    A signal for hooking up automatic ``ApiKey`` creation.
    """
    if kwargs.get('created') is True:
        ApiKey.objects.create(user=kwargs.get('instance'))
