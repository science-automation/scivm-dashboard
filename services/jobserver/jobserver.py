import zerorpc
import gevent
from gevent import monkey
monkey.patch_all()

import gevent.queue
import sys
import bisect
import redis
import pickle
import zlib

JOBSERVER_ENDPOINT = 'tcp://127.0.0.1:10000'


class Worker(object):
    def __init__(self, jobserver, worker_id):
        self._jobserver = jobserver
        self._id = worker_id
        self._pending_rqs = set()
        self._next_request_id = 0
        self._command_queue = gevent.queue.Queue()
        self._fetch_coro = None
        self._cur_job_pk = None
    
    def __str__(self):
        return 'worker #{0} cur job: {1} pending: {2} rqs'.format(self._id, self._cur_job_pk, len(self._pending_rqs))

    @property
    def id(self):
        return self._id

    @property
    def command_queue(self):
        return self._command_queue

    @property
    def pending_requests(self):
        return self._pending_rqs

    def post_request(self, rq_id, method, args):
        self._pending_rqs.add(rq_id)
        self._command_queue.put((rq_id, method, args))

    def resolve_request(self, rq_id):
        self._pending_rqs.remove(rq_id)
    
    def start_fetching(self):
        if self._fetch_coro is not None:
            return
        print "worker {0} starts to fetch jobs...".format(self.id,)
        self._fetch_coro = gevent.spawn(self.fetch_loop)

    def stop_fetching(self):
        if self._fetch_coro is not None:
            self._fetch_coro.kill()
            print "worker {0} stops to fetch jobs...".format(self.id,)

    def fetch_loop(self):
        while True:
            queue, data = self._jobserver.pop_from_job_queue()
            data = pickle.loads(zlib.decompress(data))
            self._cur_job_pk = data["pk"]
            try:
                result = self._jobserver._execute_job(self, data)
                self._jobserver.push_to_jobresult_queue(result)
            except Exception, e:
                print "worker {0} got exception...".format(self.id,)
                print e
            self._cur_job_pk = None


class JobServer(zerorpc.Server):

    def __init__(self):
        super(JobServer, self).__init__()
        self._workers = dict()
        self._next_request_id = 0
        self._pending_requests = dict()
        self.rcli = redis.StrictRedis(host="localhost", port=6379, db=0)
    
    def pop_from_job_queue(self):
        return self.rcli.blpop("noq.jobs.queued")
    
    def push_to_jobresult_queue(self, result):
        return self.rcli.rpush("noq.jobs.finished", zlib.compress(pickle.dumps(result)))

    def _status_loop(self):
        while True:
            gevent.sleep(2)
            print '-- broker status - {0} worker(s), {1} pending request(s)'.format(len(self._workers), len(self._pending_requests))
            for worker in self._workers.itervalues():
                print '--- ', worker
    
    def run(self):
        status_coro = gevent.spawn(self._status_loop)
        try:
            return zerorpc.Server.run(self)
        finally:
            status_coro.kill()
            for worker in self._workers.values():
                worker.stop_fetching()
    
    def worker_hello(self, worker_id):
        print 'worker says hello', worker_id
        
    @zerorpc.stream
    def worker_register(self, worker_id):
        new = False
        if worker_id not in self._workers:
            worker = self._workers[worker_id] = Worker(self, worker_id)
            print 'new worker registered:', worker
        else:
            worker = self._workers[worker_id]
            print 'existing worker came back:', worker

        try:
            worker.start_fetching()
            for command in worker.command_queue:
                yield command
        except Exception as e:
            print 'lost worker', worker, e
            for rq_id in worker.pending_requests:
                async_result = self._pending_requests[rq_id]
                async_result.set_exception(e)
        finally:
            worker.stop_fetching()
            del self._workers[worker.id]
    
    def worker_postresult(self, request_id, status, result):
        if request_id not in self._pending_requests:
            result["abandoned"] = True
            self.push_to_jobresult_queue(result)
            raise Exception('Request {0} is timed out'.format(request_id))
        async_result = self._pending_requests[request_id]
        if status == 'OK':
            async_result.set(result)
        else:
            # this should not happen #FIXME this means that worker is buggy
            async_result.set_exception(zerorpc.RemoteError(*result))
    
    def _execute_job(self, worker, *args):
        rq_id = self._next_request_id
        self._next_request_id += 1
        
        async_result = gevent.event.AsyncResult()
        self._pending_requests[rq_id] = async_result
        
        try:
           worker.post_request(rq_id, "execute_job", args)
           return async_result.get()
        finally:
            worker.resolve_request(rq_id)
            del self._pending_requests[rq_id]
    
    def do(self, worker_id, method, *args):
        try:
           worker = self._workers[worker_id]
        except KeyError, e:
            raise Exception('Worker not found'.format(worker_id))
        try:
            async_result = self._do(worker, method, *args)
            return async_result.get()
        finally:
            worker.resolve_request(rq_id)
            del self._pending_requests[rq_id]


broker = JobServer()
broker.bind(JOBSERVER_ENDPOINT)


print 'jobserver is waiting for workers and requests...'
broker.run()
