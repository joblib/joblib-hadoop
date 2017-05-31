import random
import string
from time import sleep
from threading import Thread
from multiprocessing.pool import Pool
from multiprocessing.managers import BaseManager
from multiprocessing.util import debug

import subprocess


class QueueManager(BaseManager):
    pass


class RemoteWorker(object):
    """The RemoteWorker object.

    A stub used to mimic the state of a local multiprocessing worker.
    """
    exitcode = None
    connected = False

    def __init__(self, pid):
        self.pid = pid

    def set_connected(self):
        self.connected = True

    def set_exitcode(self, exitcode):
        self.exitcode = exitcode
        self.connected = False


class RemotePool(Pool):
    """The RemotePool object.

    This object extends a multiprocessing.Pool by exposing its inqueue and
    outqueue using a BaseManager.
    RemoteWorkers to connect to this pool by connecting to the BaseManager and
    then using the queues execute tasks
    """
    def __init__(self, processes=None, port=0, authkey=None,
                 workerscript='remoteworker.py'):
        """ Construct a new RemotePool.

        @param processes: Number of Python processes to be spawned
        @param port: The port number where upon the BaseManager should bind.
        If port == 0, a free port is selected.
        @param authkey: The key used to check the validity of incoming
        connections
        @param workerscript: The script which starts a worker
        """

        if authkey is None:
            options = string.ascii_letters + string.digits
            self.authkey = ''.join([random.choice(options) for _ in range(32)])
        else:
            self.authkey = authkey

        QueueManager.register('get_inqueue', callable=lambda: self._inqueue)
        QueueManager.register('get_outqueue', callable=lambda: self._outqueue)
        QueueManager.register('add_worker', callable=self._add_worker)
        QueueManager.register('remove_worker', callable=self._remove_worker)

        m = QueueManager(address=('', port), authkey=self.authkey.encode())
        self.s = m.get_server()

        self.t = Thread(target=self.s.serve_forever)
        self.t.daemon = True
        self.t.start()

        self.worker_index = 0
        self.workerscript = workerscript
        super(RemotePool, self).__init__(processes=processes)

    def _add_worker(self, pid):
        for worker in self._pool:
            if worker.pid == pid:
                worker.set_connected()
                break

        # didn't find a worker with this pid,
        # assigning it to the first without a pid
        else:
            for worker in self._pool:
                if worker.pid is None:
                    worker.pid = pid
                    worker.set_connected()
                    break

    def _remove_worker(self, pid, exitcode):
        for worker in self._pool:
            if worker.pid == pid:
                worker.set_exitcode(exitcode)
                break

    def _repopulate_pool(self):
        for _ in range(self._processes - len(self._pool)):
            self.worker_index += 1
            self._start_remote_worker(self.worker_index)
            print('added worker')

    def _start_remote_worker(self, pid):
        rw = RemoteWorker(pid)
        print('starting remote worker %d', pid)

        args = ['python', self.workerscript]
        args.append('--port')
        args.append(str(self.s.address[1]))
        args.append('--workerid')
        args.append(str(pid))
        args.append('--key')
        args.append(self.authkey)

        rw.proc = subprocess.Popen(args)
        self._pool.append(rw)

    def terminate(self):
        """Stop this Pool.

        It will send a sentinel to the remote workers and waits
        at most 10 seconds for all objects to be dereferenced.
        """
        super(RemotePool, self).terminate()

        # wait until all remote objects are dereferenced
        for _ in range(100):
            if self.s.number_of_objects(None) == 0:
                break

            print('waiting for objects to be dereferenced')
            sleep(0.1)
