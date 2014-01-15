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
