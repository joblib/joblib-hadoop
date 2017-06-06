"""Yarn pool module."""

import socket
from threading import Thread
from time import sleep
from multiprocessing.util import debug
from knit import Knit
from .remotepool import RemotePool, RemoteWorker


class YarnPool(RemotePool):
    """The Yarn Pool mananger."""

    def __init__(self, processes=None, port=0, authkey=None):
        super(YarnPool, self).__init__(processes=processes,
                                       port=port,
                                       authkey=authkey,
                                       workerscript=None)
        self.stopping = False
        self.knit = Knit(autodetect=True)

        cmd = ('joblib-yarn-worker '
               '--host {} --port {} --key {}'
               .format(socket.gethostname(),
                       self.server.address[1],
                       self.authkey))
        self.app_id = self.knit.start(cmd,
                                      num_containers=self._processes)
        self.thread = Thread(target=self._monitor_appid)
        self.thread.deamon = True
        self.thread.start()

    def _start_remote_worker(self, pid):
        remote_worker = RemoteWorker(pid)
        self._pool.append(remote_worker)

    def _monitor_appid(self):
        while not self.stopping:
            status = self.knit.status()
            yarn_state = status['app']['state']
            debug("YARN application is {}".format(yarn_state))
            sleep(1)

    def terminate(self):
        self.stopping = True
        super(YarnPool, self).terminate()
        self.knit.kill()
