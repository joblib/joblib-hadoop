"""Test the yarn parallel backend."""

import os
import os.path
import shutil
from math import sqrt

import pytest
from pytest import mark

from joblib import (Parallel, delayed,
                    register_parallel_backend, parallel_backend)
from joblibhadoop.yarn import YarnBackend
from joblibhadoop.yarn.backend import JOBLIB_YARN_INTERRUPTS
from joblibhadoop.yarn.pool import (create_conda_env,
                                    TEMP_DIR, JOBLIB_YARN_DEFAULT_CONDA_ENV)

JOBLIB_HDFS_NAMENODE = os.environ['JOBLIB_HDFS_NAMENODE']


skip_localhost = pytest.mark.skipif(JOBLIB_HDFS_NAMENODE == 'localhost',
                                    reason="Cannot use nodemanager from "
                                           "localhost")


@mark.parametrize('packages', [[], ['pandas']])
def test_create_conda_env(packages):
    """Test conda env creation works as expected."""
    env = JOBLIB_YARN_DEFAULT_CONDA_ENV
    env_dir = os.path.join(TEMP_DIR, env)
    env_file = env_dir + '.zip'

    create_conda_env(env, False, *packages)

    assert os.path.isdir(env_dir)
    assert os.path.isfile(env_file)

    create_conda_env(env, True, *packages)

    assert os.path.isdir(env_dir)
    assert os.path.isfile(env_file)

    create_conda_env(env, False, *packages)

    assert os.path.isdir(env_dir)
    assert os.path.isfile(env_file)

    shutil.rmtree(env_dir, ignore_errors=True)
    os.remove(env_file)


def test_supported_interrupt():
    """Verify the list of supported interrupts is correct."""
    register_parallel_backend('yarn', YarnBackend)

    backend = YarnBackend()
    assert backend.get_exceptions() == JOBLIB_YARN_INTERRUPTS


def test_parallel_invalid_njobs_raises_value_error():
    """Check that calling parallel with wrong n_jobs raise an exception."""
    register_parallel_backend('yarn', YarnBackend)

    with pytest.raises(ValueError) as excinfo:
        with parallel_backend('yarn'):
            Parallel(verbose=100)(delayed(sqrt)(i**2) for i in range(100))
    assert 'n_jobs < 0 is not implemented yet' in str(excinfo.value)

    with pytest.raises(ValueError) as excinfo:
        with parallel_backend('yarn', n_jobs=0):
            Parallel(verbose=100)(delayed(sqrt)(i**2) for i in range(100))
    assert 'n_jobs == 0 in Parallel has no meaning' in str(excinfo.value)


@skip_localhost
def test_parallel_backend_njobs():
    """Check that calling parallel with Yarn backend works."""
    register_parallel_backend('yarn', YarnBackend)

    # Run in parallel using Yarn backend
    with parallel_backend('yarn', n_jobs=5, packages=['scikit-learn']):
        result = Parallel(verbose=100)(
            delayed(sqrt)(i**2) for i in range(100))

    assert [sqrt(x**2) for x in range(100)] == result
