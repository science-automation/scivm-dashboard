import zerorpc
import gevent
import sys
import traceback

import pickle

import time
import random
import cloud
from cloud.serialization import serialize, deserialize

BROKER_ENDPOINT = 'tcp://127.0.0.1:10000'

class JobAgentWorker(object):
    def __init__(self, obj, endpoint):
        self._obj = obj
        self._broker = zerorpc.Client(endpoint)

    def run(self):
        PID = str(os.getpid())
        while True:
            try:
                print 'agent is registering'
                work_queue = self._broker.worker_register(timeout=None)
                print 'agent is registered, waiting for work order...'
                self.worker_loop(work_queue)
            except zerorpc.LostRemote:
                print>>sys.stderr, 'lost the connection to the broker...'

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
                result = method(*args)
                self._broker.worker_postresult(request_id, 'OK', result)
            except Exception as e:
                error = self._print_traceback()
                self._broker.worker_postresult(request_id, 'ERR', error)
        except Exception as e:
            print>>sys.stderr, 'exception:', e,\
                    'unable to process work order:',\
                    request_id, method_name, args

    def worker_loop(self, work_queue):
        for work_order in work_queue:
            gevent.spawn(self._async_task, *work_order)


class Commands(object):
    
    def execute_job(self, job_data):
        print "Job %s is going to be processed" % job_data["pk"]
        
        result = None
        exception = ""
        gevent.sleep(0.05)
        start =  time.time()
        print job_data
        #gevent.sleep(random.randint(1,5))
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
        update["finished_at"] = end #datetime.datetime.fromtimestamp(end)
        
        print "Job %s has been processed" % job_data["pk"]
        return update
        

if __name__ == "__main__":
    worker = JobAgentWorker(Commands(), BROKER_ENDPOINT)
    worker.run()

