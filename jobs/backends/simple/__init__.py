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

from django.conf import settings

from django.db.models.signals import post_save
from django.db import transaction
from django.dispatch import receiver

import logging
from celery.contrib.methods import task
import pickle
import cloud
from cloud.serialization import serialize, deserialize
import celery
import time
import random
import itertools
import datetime
import zlib
import pickle
import redis

logger = logging.getLogger("jobs.backends.simple")

ANY_STATUS = "_any_status_"

rcli = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)

@celery.task(name="simple.update_job_status")
def update_job_status(job_data, from_, to, extra_data=None):
    """ Tries to update status of job from <from_> to <to> and update other fields according to the <extra_data> as well. """
    from jobs.models import Job
    
    logger.info("status of Job %s is going to be updated" % job_data["pk"])
    
    kwargs = {"status": from_} if from_ is not ANY_STATUS else {}
    
    update_data = {"status": to, }
    update_data.update(extra_data if extra_data is not None else {})

    count = Job.objects.filter(pk=job_data["pk"], **kwargs).update(**update_data)
    if count != 1:
        logger.debug("Job %s is not in %s state or does not exist; cannot update status to %s" % (job_data["pk"], from_, to))
        return False

    #TODO some signal or similar would be good here
    logger.info("Job %s got %s status" % (job_data["pk"], to))
    return True


@celery.task(name="simple.enqueue_job")
def enqueue_job(job_data):
    """ Tries to update status of job to 'queued' and send job to execution handler on success. """
    from jobs.models import Job
    
    logger.info("Job %s is to be queued" % job_data["pk"])
    
    status_updated = update_job_status(job_data, from_=Job.WAITING, to=Job.QUEUED)
    if not status_updated:
        logger.error("Cannot move Job %s to queued state; gonna be a calm day" % (job_data["pk"], ))
        return False
    
    # pass job to execution handler
    execution_handler(job_data,)
    
    logger.info("Job %s is queued" % job_data["pk"])
    return True


@celery.task(name="simple.enqueue_jobs")
def enqueue_jobs(jobs_data):
    """ Tries to enqueue multiple jobs. """
    
    logger.info("Enquing multiple jobs started")

    # groupping enquing tasks
    group_action = celery.group(enqueue_job.s(job_data) for job_data in jobs_data).apply_async()
    
    # and wait for all of them
    group_action.join()  

    logger.info("Enqueing multiple jobs finished")
    return True


@celery.task(name="simple.enqueue_job_group")
def enqueue_group_job(jobs_data, group_id):
    """ Tries to enqueue jobs of a job group. """
    from jobs.models import Job, JobGroup
    
    logger.info("Jobs of joggroup %s are to be queued" % group_id)
    
    enqueue_jobs(jobs_data)
    
    logger.info("Jobs of jobgroup %s are queued" % (group_id, ))
    return True


@celery.task(name="simple.pass_job_to_execution_handler")
def execution_handler(job_data):
    """ Handles the processing of a job. 
        Steps:
            1. updates job status to processing 
            2. prepares job data sent to processing engine
            3. sends job to the processing engine and waits for results
            4. updates job according to results 
    """
    from jobs.models import Job, JobGroup
    from apikey.models import ApiKey
    from django.db.models import F
    
    logger.info("Execution handler got Job %s" % job_data["pk"])
    
    status_updated = update_job_status(job_data, from_=Job.QUEUED, to=Job.PROCESSING)
    if not status_updated:
        logger.error("Cannot move Job %s from queued state to processing state; what should happen now?" % job_data["pk"])
        return False
    
    try:
        payload = Job.objects.filter(pk=job_data["pk"]).values(*Job.JOB_DATA_FIELDS)[0]
    except IndexError:
        logger.critical("Cannot get payload of Job %s; does not exists; processing halts" % job_data["pk"])
        #TODO retry if restartable?
        #TODO state to stalling?
        return False
    try:
        api_secretkey = ApiKey.objects.filter(pk=payload["apikey_id"]).values("key")[0]["key"]
    except (IndexError, KeyError), e:
        logger.critical("Cannot get apikey secret for Job %s; processing halts" % job_data["pk"])
        #TODO retry if restartable?
        #TODO state to stalling?
        return False

    payload.update({
        "api_secretkey": api_secretkey,
        "server_url": settings.SCICLOUD_API_ROOT_URL,   
        "func_obj_pickled": bytes(payload["func_obj_pickled"]),
        "func_args_pickled": bytes(payload["func_args_pickled"]) if payload["func_args_pickled"] else None,
        "func_kwargs_pickled": bytes(payload["func_kwargs_pickled"]) if payload["func_kwargs_pickled"] else None,
    })
    global rcli
    rcli.rpush("noq.jobs.queued", zlib.compress(pickle.dumps(payload)))
    #cli.process_job2(payload)
    return True
    
@celery.task(name="simple.update_job_result")
def update_job_result(job_data, update):
    from jobs.models import Job, JobGroup
    from django.db.models import F
    logger.info("Update result handler got results for Job %s" % job_data["pk"])

    update["status"] = Job.ERROR if "exception" in update else Job.DONE
    update["finished_at"] = datetime.datetime.fromtimestamp(update["finished_at"])
    status_updated = update_job_status(job_data, from_=Job.PROCESSING, to=update["status"], extra_data=update)
    if not status_updated:
        logger.error("Cannot move Job %s from processing to %s state; results are dropped" % (job_data["pk"], update["status"]))
        return False
    
    if job_data["group_id"] is not None:
        counter_name = "failed_cnt" if update["status"] == Job.ERROR else "ok_cnt"
        logger.debug("Need to inc %s of JobGroup %s after executing %s" % (counter_name, job_data["group_id"], job_data["pk"]))
        count = JobGroup.objects.filter(pk=job_data["group_id"]).update(**{counter_name:F(counter_name)+1})
        if count != 1:
            logger.error("Cannot inc %s of JobGroup %s after executing Job %s" % (counter_name, job_data["group_id"], job_data["pk"]))
            return False
    
    logger.info("Update result handler has finished dealing with Job %s" % job_data["pk"])
    return True


@celery.task(name="simple.execute_job")
def process_job2(job_data):
    global c
    ret = c.do("execute_job", job_data)
    ret["finished_at"] = datetime.datetime.fromtimestamp(ret["finished_at"])
    return ret


@celery.task(name="simple.execute_job", queue="processing")
def process_job(job_data):
    """ Minimalist version of job execution worker. Not production ready and never will be :o """
    import pickle
    import sys
    import time
    import datetime

    logger.info("Job %s is going to be processed" % job_data["pk"])
    
    result = None
    exception = ""
    start =  time.time()
    try:
        func = pickle.loads(job_data["func_obj_pickled"])
        args = pickle.loads(job_data["func_args_pickled"]) if job_data["func_args_pickled"] else ()
        kwargs = pickle.loads(job_data["func_kwargs_pickled"]) if job_data["func_kwargs_pickled"] else {}
        result = func(*args, **kwargs)
        update = {'result_pickled': serialize(result)}
    except BaseException, e:
        import traceback
        traceback = ''.join(traceback.format_tb(sys.exc_info()[2]))
        update = {'exception': traceback + "\n" + str(e)}
    end = time.time()
    
    update["runtime"] = end-start
    update["finished_at"] = datetime.datetime.fromtimestamp(end)

    logger.info("Job %s has been processed" % job_data["pk"])
    return update

@celery.task(name="simple.wait_for_dependencies")
def wait_for_dependencies(jobs_data, owner_id, depends_on_desc, depends_on_errors, has_error, action):
    from jobs.models import Job, JIDS
     
    job_pks = [ job_data["pk"] for job_data in jobs_data ]
    logger.debug("Checking dependecies of jobs %s" % job_pks)
    
    dependent_on_jids = JIDS(depends_on_desc)
    statuses = Job.objects.for_jids(owner_id=owner_id, jids=dependent_on_jids).values("pk", "status", "owner_id", "jid")
    
    abort = False
    has_error = has_error or any(itertools.imap(lambda x: x["status"] in (Job.ERROR, Job.KILLED), statuses))
    
    if depends_on_errors == Job.ABORT:
        if len(statuses) != len(dependent_on_jids) or has_error:
            logger.debug("At least on of the dependencies of jobs %s is in bad state or missing and abort flag is set; must set stalled state" % job_pks)
            count = 0
            # this is a little bit slow way of doing this... #TODO
            for job_data in jobs_data:
                status_updated = update_job_status(job_data, from_=Job.WAITING, to=Job.STALLED)
                if not status_updated:
                    logger.error("Cannot move Job %s from waiting state to stalled state; sad" % job_data["pk"])
            return False
    
    # if we get here, we can safely ignore dependencies not having done status
    not_done_pks = [ entry['pk'] for entry in statuses if entry["status"] in (Job.WAITING, Job.QUEUED, Job.PROCESSING) ]
    not_done_jids = [ entry['jid'] for entry in statuses if entry["status"] in (Job.WAITING, Job.QUEUED, Job.PROCESSING) ]
    if not_done_pks:
        logger.debug("Still checking for %s" % not_done_pks)
        dependency_pks = not_done_pks
        countdown = random.randint(3,8)
        #FIXME retry?
        wait_for_dependencies.apply_async((jobs_data, owner_id, not_done_jids, depends_on_errors, has_error, action), countdown=countdown)
        return True

    logger.debug("All dependencies of jobs %s have been processed" % job_pks)
    logger.debug("Launching action %s" % action)
    action.apply_async(jobs_data)
    return True


def kill_job(job_data):
    from jobs.models import Job
    
    status_updated = update_job_status(job_data, from_=ANY_STATUS, to=Job.KILLED)
    if not status_updated:
        logger.error("Cannot move Job %s to killed state; bad for health" % job_data["pk"])
        return False
    # send some signal, kill running job etc #TODO
    return True


def delete_job(job_data, job_status, purge=False):
    from jobs.models import Job
    
    if job_status in Job.KILLABLE_STATES:
        logger.info("Job %s in killable state, let's kill it first" % job_data["pk"])
        kill_job(job_data)
    
    count = Job.objects.filter(pk=job_data["pk"]).update(is_deleted=True)
    if count != 1:
        logger.error("Cannot delete Job %s; ops ops ops" % job_data["pk"])
        return False
    
    #TODO blank non essential fields here
    
    # send some signal etc #TODO
    return True


def kill_jobgroup(jobgroup_id):
    pass


def delete_jobgroup(jobgroup_id):
    pass


class SimpleBackend(object):
    
    def __init__(self, *args, **kwargs):
        pass
    
    enqueue_job = staticmethod(enqueue_job)
    enqueue_jobs = staticmethod(enqueue_jobs)
    enqueue_group_job = staticmethod(enqueue_group_job)
    wait_for_dependencies = staticmethod(wait_for_dependencies)
    kill_job = staticmethod(kill_job)
    delete_job = staticmethod(delete_job)
    kill_jobgroup = staticmethod(kill_jobgroup)
    delete_jobgroup = staticmethod(delete_jobgroup)
    update_job_result = staticmethod(update_job_result)

