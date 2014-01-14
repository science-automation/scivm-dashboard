import zerorpc
import gevent
import gevent.queue
import sys
import bisect


JOBSERVER_ENDPOINT = 'tcp://127.0.0.1:10000'


class Worker(object):
    def __init__(self, worker_id):
        self._id = worker_id
        self._nb_concur_rq = 1
        self._pending_rqs = set()
        self._work_queue = gevent.queue.Queue()

    def __str__(self):
        return 'worker #{0} {1}/{2} rqs'.format(self._id,
                len(self._pending_rqs), self._nb_concur_rq)

    @property
    def id(self):
        return self._id

    @property
    def work_queue(self):
        return self._work_queue

    @property
    def pending_requests(self):
        return self._pending_rqs

    def post_request(self, rq_id, method, args):
        self._pending_rqs.add(rq_id)
        self._work_queue.put((rq_id, method, args))

    def resolve_request(self, rq_id):
        self._pending_rqs.remove(rq_id)


class JobServer(zerorpc.Server):

    def __init__(self):
        super(JobServer, self).__init__()
        self._next_worker_id = 0
        self._workers = dict()
        self._workers_ready_for_work = gevent.queue.Queue()
        self._next_request_id = 0
        self._pending_requests = dict()

    def _status_loop(self):
        while True:
            gevent.sleep(2)
            print '-- broker status - {0} worker(s), {1} pending request(s) {2} jobs'.format(
                    len(self._workers), len(self._pending_requests), self._next_request_id)
            for worker in self._workers.itervalues():
                print '--- ', worker

    def run(self):
        status_coro = gevent.spawn(self._status_loop)
        try:
            return zerorpc.Server.run(self)
        finally:
            status_coro.kill()

    @zerorpc.stream
    def worker_register(self):
        worker = Worker(self._next_worker_id)
        self._next_worker_id += 1
        self._workers[worker.id] = worker
        try:
            print 'new worker registered:', worker
            self._workers_ready_for_work.put(worker)
            for work_order in worker.work_queue:
                yield work_order
        except Exception as e:
            print>>sys.stderr, 'lost worker', worker, e
            for rq_id in worker.pending_requests:
                async_result = self._pending_requests[rq_id]
                async_result.set_exception(e)
        finally:
            del self._workers[worker.id]

    def worker_postresult(self, request_id, status, result):
        if request_id not in self._pending_requests:
            raise Exception('Request {0} was abandonned'.format(request_id))
        async_result = self._pending_requests[request_id]
        if status == 'OK':
            async_result.set(result)
        else:
            async_result.set_exception(zerorpc.RemoteError(*result))

    def do(self, method, *args):
        rq_id = self._next_request_id
        self._next_request_id += 1

        async_result = gevent.event.AsyncResult()
        self._pending_requests[rq_id] = async_result
        try:
            for worker in self._workers_ready_for_work:
                if worker.id in self._workers and worker.accepts_more_work:
                    break

            worker.post_request(rq_id, method, args)
            if worker.accepts_more_work:
                self._workers_ready_for_work.put(worker)

            return async_result.get()
        finally:
            worker.resolve_request(rq_id)
            del self._pending_requests[rq_id]
            if worker.accepts_more_work:
                self._workers_ready_for_work.put(worker)


broker = JobServer()
broker.bind(JOBSERVER_ENDPOINT)
print 'jobserver is waiting for workers and requests...'
broker.run()
