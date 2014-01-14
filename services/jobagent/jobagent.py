import zerorpc
import zerorpc.context
import gevent
import sys
import traceback

import pickle

import time
import random
import cloud
from cloud.serialization import serialize, deserialize
import zmq
import os
import logging
logging.basicConfig()
logging.getLogger().setLevel(logging.INFO) 


class SuperClient(zerorpc.Client):
    
    def __init__(self, *args, **kwargs):
        super(SuperClient, self).__init__(*args, **kwargs)
        #self._events._socket.setsockopt(zmq.SNDHWM, 1)


class JobAgentWorker(object):
    BROKER_ENDPOINT = 'tcp://127.0.0.1:10000'
    
    def __init__(self, obj):
        self._obj = obj
        self.broker = SuperClient(self.BROKER_ENDPOINT, context=zerorpc.context.Context())
        self.c = 0

    def run(self):
        PID = str(os.getpid())
        tries = 0
        try:
            while True:
                if tries > 0:
                   gevent.sleep(max(tries, 10) * 3)
                try:
                    print 'agent try to say hello', PID
                    self.broker.worker_hello(PID, timeout=15)
                    print 'broker is up'
                except zerorpc.exceptions.TimeoutExpired, e:
                    print>>sys.stderr, 'agent hello timed out'
                    tries += 1
                    continue
                tries = 0
                try:
                    print 'agent is registering', PID
                    work_queue = self.broker.worker_register(PID, timeout=None)
                    print 'agent is registered, waiting for work order...'
                    self.worker_loop(work_queue)
                except zerorpc.LostRemote:
                    print>>sys.stderr, 'lost the connection to the broker...'
        except Exception, e:
            print e

    def _print_traceback(self):
        exc_infos = list(sys.exc_info())
        traceback.print_exception(*exc_infos, file=sys.stderr)
        exc_type, exc_value, exc_traceback = exc_infos
        human_traceback = traceback.format_exc()
        name = exc_type.__name__
        human_msg = str(exc_value)
        return (name, human_msg, human_traceback)

    def _async_task(self, request_id, method_name, args):
        try:
            method = getattr(self._obj, method_name)
            error = None
            try:
                #print "post before", request_id
                result = method(*args)
                self.broker.worker_postresult(request_id, 'OK', result)
                #print "post after", request_id
            except Exception, e:
                print "exc", e
                error = self._print_traceback()
                self.broker.worker_postresult(request_id, 'ERR', error)
                print "post after", request_id
        except Exception, e:
            print>>sys.stderr, 'exception:', e,\
                    'unable to process work order:',\
                    request_id, method_name, args
    
    def worker_loop(self, work_queue):
        for work_order in work_queue:
            gevent.spawn(self._async_task, *work_order)


class Commands(object):
    
    def execute_job(self, job_data):
        print "executing job {0}".format(job_data["pk"])

        result = None
        exception = ""
        start = time.time()
        
        try:
            func = pickle.loads(job_data["func_obj_pickled"])
            args = pickle.loads(job_data["func_args_pickled"]) if job_data["func_args_pickled"] else ()
            kwargs = pickle.loads(job_data["func_kwargs_pickled"]) if job_data["func_kwargs_pickled"] else {}
            result = func(*args, **kwargs)
            update = {'result_pickled': serialize(result)}
        except BaseException, e:
            import traceback
            print e
            traceback = ''.join(traceback.format_tb(sys.exc_info()[2]))
            update = {'exception': traceback + "\n" + str(e)}
        finally:
            end = time.time()

        update["pk"] = job_data["pk"]
        update["group_id"] = job_data["group_id"]
        update["runtime"] = end-start
        update["finished_at"] = end

        print "finished job {0}".format(job_data["pk"])
        return update
        

if __name__ == "__main__":
    worker = JobAgentWorker(Commands())
    worker.run()

