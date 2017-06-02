"""Example showing how to use joblib-hadoop with an YARN cluster"""

from math import sqrt
from joblib import (Parallel, delayed,
                    register_parallel_backend, parallel_backend)
from joblibhadoop.yarn import YarnBackend

if __name__ == '__main__':
    register_parallel_backend('yarn', YarnBackend)
    with parallel_backend('yarn', n_jobs=1):
        Parallel(verbose=100)(
            delayed(sqrt)(i**2) for i in range(100))
