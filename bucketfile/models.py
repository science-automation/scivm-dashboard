from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.utils.translation import ugettext as _
from django.db.models import Q
from django.core.cache import cache
from json_field import JSONField
from bucketstore.models import BucketStore
from scivm import utils

class BucketFile(models.Model):
#    bucket_id = models.ForeignKey('BucketStore')
    owner = models.ForeignKey(User)    
    name = models.CharField(max_length=96, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    lastmodified = models.DateTimeField(auto_now_add=True)
    size = models.BigIntegerField(null=True, blank=True)
    public = models.BooleanField(null=False, default=False)
