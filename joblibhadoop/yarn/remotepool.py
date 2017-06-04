"""Remote workers pool manager module."""

import string
import random
import socket
from time import sleep
from threading import Thread
from multiprocessing.util import debug
from multiprocessing.pool import Pool
from multiprocessing.managers import BaseManager

import subprocess


class QueueManager(BaseManager):
    """Message queue manager."""
    pass


class RemoteWorker(object):
    """The RemoteWorker object.

    A stub used to mimic the state of a local multiprocessing worker.
    """
    exitcode = None
    connected = False
    proc = None

    def __init__(self, pid):
        self.pid = pid

    def set_connected(self):
        """Change to connected state."""
        self.connected = True

    def set_exitcode(self, exitcode):
        """Set exit code and switch to disconnect state."""
        self.exitcode = exitcode
        self.connected = False


class RemotePool(Pool):
    """The RemotePool object.

    This object extends a multiprocessing.Pool by exposing its inqueue and
    outqueue using a BaseManager.
    RemoteWorkers connect to this pool via the BaseManager and
    then use the queues to execute tasks
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

        self.mgr = QueueManager(address=('', port),
                                authkey=self.authkey.encode())
        self.server = self.mgr.get_server()

        self.thread = Thread(target=self.server.serve_forever)
        self.thread.daemon = True
        self.thread.start()

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

    def _start_remote_worker(self, pid):
        remote_worker = RemoteWorker(pid)
        debug('starting remote worker %d', pid)

        args = ['python', self.workerscript]
        args.append('--host')
        args.append(socket.gethostname())
        args.append('--port')
        args.append(str(self.server.address[1]))
        args.append('--workerid')
        args.append(str(pid))
        args.append('--key')
        args.append(self.authkey.decode())

        remote_worker.proc = subprocess.Popen(args)
        self._pool.append(remote_worker)

    def terminate(self):
        """Stop this Pool.

        It will send a sentinel to the remote workers and waits
        at most 10 seconds for all objects to be dereferenced.
        """
        super(RemotePool, self).terminate()

        # wait until all remote objects are dereferenced
        for _ in range(100):
            if self.server.number_of_objects(None) == 0:
                break

            debug('waiting for objects to be dereferenced')
            sleep(0.1)

    def __reduce__(self):
        pass
