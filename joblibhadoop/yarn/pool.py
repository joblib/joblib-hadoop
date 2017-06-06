"""Yarn pool module."""

import os
import os.path
import shutil
import socket
import tempfile
from threading import Thread
from time import sleep
from multiprocessing.util import debug
from knit import Knit
from .remotepool import RemotePool, RemoteWorker
from ..resources import conda_environment_filename

JOBLIB_YARN_WORKER = 'joblib-yarn-worker'
JOBLIB_YARN_CONDA_ENV = 'conda_env'

TEMP_DIR = os.environ.get('JOBLIB_TEMP_FOLDER', tempfile.gettempdir())
CONDA_ENV_CREATE_COMMAND = 'conda env create -q -p {} --file={}'
CONDA_ENV_INSTALL_COMMAND = 'conda install -y -q -p /tmp/{} {}'


def create_conda_env(*extra_packages):
    """Create a conda environment to pass to Knit"""
    # Create conda environment
    if os.path.isfile(os.path.join(TEMP_DIR, JOBLIB_YARN_CONDA_ENV + '.zip')):
        return

    os.system(CONDA_ENV_CREATE_COMMAND.format(
        os.path.join(TEMP_DIR, JOBLIB_YARN_CONDA_ENV),
        conda_environment_filename()))
    if len(*extra_packages):
        os.system(CONDA_ENV_INSTALL_COMMAND.format(' '.join(*extra_packages)))
    # Archive conda environment
    shutil.make_archive(os.path.join(TEMP_DIR, JOBLIB_YARN_CONDA_ENV), 'zip',
                        root_dir=TEMP_DIR,
                        base_dir=JOBLIB_YARN_CONDA_ENV)


class YarnPool(RemotePool):
    """The Yarn Pool mananger."""

    def __init__(self, processes=None, port=0, authkey=None):
        super(YarnPool, self).__init__(processes=processes,
                                       port=port,
                                       authkey=authkey,
                                       workerscript=JOBLIB_YARN_WORKER)
        self.stopping = False
        self.knit = Knit(autodetect=True)
        create_conda_env([])
        cmd = ('$PYTHON_BIN $CONDA_PREFIX/bin/{} --host {} --port {} --key {}'
               .format(JOBLIB_YARN_WORKER,
                       socket.gethostname(),
                       self.server.address[1],
                       self.authkey))
        self.app_id = self.knit.start(
            cmd, num_containers=self._processes,
            env='{}.zip'.format(os.path.join(TEMP_DIR, JOBLIB_YARN_CONDA_ENV)))
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
