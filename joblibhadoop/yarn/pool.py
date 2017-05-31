from .remotepool import RemotePool, RemoteWorker
from threading import Thread
from time import sleep
from knit import Knit


class YarnPool(RemotePool):

    def __init__(self, processes=None, port=0, authkey=None):
        super(YarnPool, self).__init__(processes=processes,
                                       port=port,
                                       authkey=authkey,
                                       workerscript=None)
        self.stopping = False
        self.k = Knit(autodetect=True)

        cmd = ('python remoteworker.py --port {} --key {}'
               .format(self.s.address[1], self.authkey))
        self.app_id = self.k.start(cmd,
                                   num_containers=self._processes,
                                   files=['remoteworker.py', ])
        self.t = Thread(target=self._monitor_appid)
        self.t.deamon = True
        self.t.start()

    def _start_remote_worker(self, pid):
        rw = RemoteWorker(pid)
        self._pool.append(rw)

    def _monitor_appid(self):
        while not self.stopping:
            try:
                status = self.k.status(self.app_id)
                yarn_state = status['app']['state']
                print("YARN application is {}".format(yarn_state))
            except:
                pass
            sleep(1)

    def terminate(self):
        self.stopping = True
        super(YarnPool, self).terminate()

        self.k.kill(self.app_id)
