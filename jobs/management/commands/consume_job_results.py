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

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from optparse import make_option

from jobs.models import Job
import redis
import zlib
import pickle
from django.conf import settings

class Command(BaseCommand):
    help = 'Consum custom job result queue'

    def handle(self, *args, **options):
        rcli = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)
        while True:
            queue, data = rcli.blpop("noq.jobs.finished")
            try:
                update =  pickle.loads(zlib.decompress(data))
                print update
                job_data = {"pk": update.pop("pk"), "group_id": update.pop("group_id") }
                print job_data, update
                Job.backend.update_job_result.apply_async((job_data, update))
            except Exception, e:
                print e
