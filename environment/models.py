from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.utils.translation import ugettext as _
from django.db.models import Q
from django.core.cache import cache
from json_field import JSONField
from scivm import utils

class Environment(models.Model):
    name = models.CharField(max_length=96, null=True, blank=True)
    owner = models.ForeignKey(User, unique=True)
    description = models.TextField(default="", blank=True)
    created = models.DateTimeField(auto_now_add=True)
    public = models.BooleanField(null=False, default=False)
