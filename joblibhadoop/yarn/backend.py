"""Yarn backend for joblib."""

from joblib._parallel_backends import ThreadingBackend
from joblib.my_exceptions import WorkerInterrupt
from .pool import YarnPool


__interrupts__ = [KeyboardInterrupt, WorkerInterrupt]


class YarnBackend(ThreadingBackend):
    """The YARN backend class."""

    def __init__(self, packages=[]):
        """Constructor"""
        self.packages = packages
        self._pool = None
        self.parallel = None


    def effective_n_jobs(self, n_jobs):
        """Return the number of effective jobs running in the backend."""
        if n_jobs == 0:
            raise ValueError('n_jobs == 0 in Parallel has no meaning')
        if n_jobs < 0:
            # TODO: add support -1, -2 etc.
            raise ValueError('n_jobs < 0 is not implemented yet')

        return n_jobs

    def configure(self, n_jobs, parallel=None, **backend_args):
        """Initialize the backend."""
        n_jobs = self.effective_n_jobs(n_jobs)
        self._pool = YarnPool(processes=n_jobs, packages=self.packages)
        self.parallel = parallel
        return n_jobs

    def get_exceptions(self):
        """Return the list of interrupt supported by the backend."""
        # We are using multiprocessing, we also want to capture
        # KeyboardInterrupts
        return __interrupts__
