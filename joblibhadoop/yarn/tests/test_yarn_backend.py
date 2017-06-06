"""Test the yarn parallel backend."""

import os
from math import sqrt

import pytest

from joblib import (Parallel, delayed,
                    register_parallel_backend, parallel_backend)
from joblibhadoop.yarn import YarnBackend
from joblibhadoop.yarn.backend import __interrupts__

__NAMENODE = os.environ['JOBLIB_HDFS_NAMENODE']


skip_localhost = pytest.mark.skipif(__NAMENODE == 'localhost',
                                    reason="Cannot use nodemanager from "
                                           "localhost")


def test_supported_interrupt():
    """Verify the list of supported interrupts is correct."""
    register_parallel_backend('yarn', YarnBackend)

    backend = YarnBackend()
    assert backend.get_exceptions() == __interrupts__


def test_parallel_invalid_njobs_raises_value_error():
    """Check that calling parallel with wrong n_jobs raise an exception."""
    register_parallel_backend('yarn', YarnBackend)

    with pytest.raises(ValueError) as excinfo:
        with parallel_backend('yarn'):
            result = Parallel(verbose=100)(
                delayed(sqrt)(i**2) for i in range(100))
    assert 'n_jobs < 0 is not implemented yet' in str(excinfo.value)

    with pytest.raises(ValueError) as excinfo:
        with parallel_backend('yarn', n_jobs=0):
            result = Parallel(verbose=100)(
                delayed(sqrt)(i**2) for i in range(100))
    assert 'n_jobs == 0 in Parallel has no meaning' in str(excinfo.value)


@skip_localhost
def test_parallel_backend_njobs():
    """Check that calling parallel with Yarn backend works."""
    register_parallel_backend('yarn', YarnBackend)

    # Run in parallel using Yarn backend
    with parallel_backend('yarn', n_jobs=5):
        result = Parallel(verbose=100)(
            delayed(sqrt)(i**2) for i in range(100))

    assert [sqrt(x**2) for x in range(100)] == result
