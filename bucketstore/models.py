from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.utils.translation import ugettext as _
from django.db.models import Q
from django.core.cache import cache
from json_field import JSONField
from scivm import utils

class BucketStore(models.Model):
    name = models.CharField(max_length=96, null=True, blank=True)
    owner = models.ForeignKey(User)
    description = models.TextField(default="", blank=True)
    created = models.DateTimeField(auto_now_add=True)

    # amazon ec2 access and secret key
    access_key = models.CharField(max_length=96, null=True, blank=True)
    access_secret_key = models.CharField(max_length=96, null=True, blank=True)
