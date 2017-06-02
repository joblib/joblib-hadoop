"""Example showing how to use joblib-hadoop with an YARN cluster"""

from math import sqrt
from joblib import (Parallel, delayed,
                    register_parallel_backend, parallel_backend)
from joblibhadoop.yarn import YarnBackend

if __name__ == '__main__':
    register_parallel_backend('yarn', YarnBackend)

    # Run in parallel using Yarn backend
    with parallel_backend('yarn', n_jobs=5):
        print(Parallel(verbose=100)(
            delayed(sqrt)(i**2) for i in range(100)))

    # Should be executed in parallel locally
    print(Parallel(verbose=100, n_jobs=5)(
        delayed(sqrt)(i**2) for i in range(100))
