from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.utils.translation import ugettext as _
from django.db.models import Q
from django.core.cache import cache
from json_field import JSONField
from scivm import utils

class Bucket(models.Model):
    name = models.CharField(max_length=96, null=True, blank=True)
    owner = models.ForeignKey(User, null=True, blank=True)
    description = models.TextField(default="", blank=True)
    created = models.DateTimeField(auto_now_add=True)

    # amazon ec2 access and secret key
    access_key = models.CharField(max_length=96, null=True, blank=True)
    access_secret_key = models.CharField(max_length=96, null=True, blank=True)


class BucketFile(models.Model):
    bucket_id = models.ForeignKey('Bucket')
    owner = models.ForeignKey(User, unique=True)    
    name = models.CharField(max_length=96, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    lastmodified = models.DateTimeField(auto_now_add=True)
    size = models.BigIntegerField(null=True, blank=True)
    public = models.BooleanField(null=False, default=False)
