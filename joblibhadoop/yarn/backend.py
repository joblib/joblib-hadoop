from joblib._parallel_backends import ThreadingBackend
from joblib.my_exceptions import WorkerInterrupt
from .pool import YarnPool


class YarnBackend(ThreadingBackend):
    """The YARN backend class."""

    def effective_n_jobs(self, n_jobs):
        """Return the number of effective jobs running in the backend."""
        # TODO: add support -1, -2 etc.
        if n_jobs < 0:
            raise ValueError('n_jobs < 0 is not implemented yet')

        return n_jobs

    def initialize(self, n_jobs, poolargs):
        """Initialize the backend."""
        self._pool = YarnPool(n_jobs)
        return n_jobs

    def get_exceptions(self):
        """Return the list of interrupt supported by the backend."""
        # We are using multiprocessing, we also want to capture
        # KeyboardInterrupts
        return [KeyboardInterrupt, WorkerInterrupt]
