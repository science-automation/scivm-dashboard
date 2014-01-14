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
