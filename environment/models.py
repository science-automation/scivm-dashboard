from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.utils.translation import ugettext as _
from django.db.models import Q
from django.core.cache import cache
from json_field import JSONField
from scivm import utils

class Environment(models.Model):
    uri = models.CharField(max_length=96, null=True, blank=True)
    name = models.CharField(max_length=96, null=True, blank=True)
    owner = models.ForeignKey(User, null=True, blank=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    properties = JSONField()
    capacity = JSONField()
    bootable = models.NullBooleanField(null=False, default=False)
    supportsSnapshots = models.NullBooleanField(null=False, default=True)
    snapshots = JSONField()
    guestinterface = models.CharField(max_length=96, null=True, blank=True)
    meters = JSONField()
    eventlog = JSONField()
    operations = JSONField()
