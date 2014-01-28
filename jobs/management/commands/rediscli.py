import gevent
import redis
import logging

logger = logging.getLogger("redis")


class StrictRedis(redis.StrictRedis):
    
    def __init__(self, *args, **kwargs):
        self._connected_ev = gevent.event.Event()
        self._disconnected_ev = gevent.event.Event()
        self._evlock = gevent.lock.RLock()

        self._connected_ev.clear()
        self._disconnected_ev.set()
        self._watcher_coro = None

        super(StrictRedis, self).__init__(*args, **kwargs)
        
        self._watcher_coro = gevent.spawn(self._conn_watcher_coro)
    
    def execute_command(self, *args, **kwargs):
        if kwargs.pop("__nocheck", False):
            return super(StrictRedis, self).execute_command(*args, **kwargs)
            
        while True:
            self._connected_ev.wait()
            try:
                return super(StrictRedis, self).execute_command(*args, **kwargs)
            except redis.exceptions.ConnectionError:
                with self._evlock:
                    if self._connected_ev.is_set():
                        self._connected_ev.clear()
                        self._disconnected_ev.set()
    
    def _conn_watcher_coro(self):
        retry_count = 0
        timeout = 5
        retry_log = 5 
        while True:
            self._disconnected_ev.wait()
            try:
                self.execute_command("SET", "dummy", "dummy", __nocheck=True)
                self.execute_command("GET", "dummy", __nocheck=True)
                with self._evlock:
                    self._disconnected_ev.clear()
                    self._connected_ev.set()
                retry_count = 0
                logger.warning("redis is connected")
            except redis.exceptions.ConnectionError:
                if retry_count % retry_log == 0:
                    logger.warning("redis disconnected, couldn't reconnect in the last {0} secs".format(retry_count * timeout))
                retry_count += 1
                gevent.sleep(timeout)

    def __del__(self):
        if self._watcher_coro is not None:
            gevent.kill(self._watcher_coro)

