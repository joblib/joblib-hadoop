"""Test the yarn parallel backend."""

import os
from math import sqrt

import pytest

from joblib import (Parallel, delayed,
                    register_parallel_backend, parallel_backend)
from joblibhadoop.yarn import YarnBackend

__namenode__ = os.environ['NAMENODE']


skip_localhost = pytest.mark.skipif(__namenode__ == 'localhost',
                                    reason="Cannot use nodemanager from "
                                           "localhost")


@skip_localhost
def test_simple_parallel_backend():
    """Check that calling parallel with Yarn backend works."""
    register_parallel_backend('yarn', YarnBackend)

    # Run in parallel using Yarn backend
    with parallel_backend('yarn'):
        result = Parallel(verbose=100)(
            delayed(sqrt)(i**2) for i in range(100))

    assert [sqrt(x**2) for x in range(100)] == result


@skip_localhost
def test_parallel_backend_njobs():
    """Check that calling parallel with Yarn backend works."""
    register_parallel_backend('yarn', YarnBackend)

    # Run in parallel using Yarn backend
    with parallel_backend('yarn', n_jobs=5):
        result = Parallel(verbose=100)(
            delayed(sqrt)(i**2) for i in range(100))

    assert [sqrt(x**2) for x in range(100)] == result
