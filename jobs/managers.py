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

from django.db import models
import collections


class NotDeletedManagerMixin(object):
    """ Excludes objects with is_deleted flag"""

    def get_queryset(self):
        return super(NotDeletedManagerMixin, self).get_queryset().filter(is_deleted=False)


class JobManager(models.Manager):
    
    def for_jids(self, owner_id, jids):
        jids = list(jids) if isinstance(jids, collections.Iterable) else (jids, )
        return self.filter(owner_id=owner_id, jid__in=jids, is_group_entry=False)
    
    def for_group(self, group_id):
        return self.filter(group__pk=group_id, is_group_entry=False)


class JobNotDeletedManager(NotDeletedManagerMixin, JobManager):
    """ Excludes jobs with is_deleted flag"""
    pass


class JobGroupManager(models.Manager):
    pass


class JobGroupNotDeletedManager(NotDeletedManagerMixin, JobGroupManager):
    """ Excludes jobgroups with is_deleted flag"""
    pass
