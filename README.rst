Joblib-hadoop
=============

|Travis| |Codecov|

.. |Travis| image:: https://travis-ci.org/joblib/joblib-hadoop.svg?branch=master
    :target: https://travis-ci.org/joblib/joblib-hadoop

.. |Codecov| image:: https://codecov.io/gh/joblib/joblib-hadoop/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/joblib/joblib-hadoop

This package provides parallel and store backends for joblib that can be use on
a Hadoop cluster.

If you don't know joblib already, user documentation is located on
https://pythonhosted.org/joblib

Joblib-hadoop supports Python 2.7, 3.4 and 3.5.

Getting the latest code
=======================

To get the latest code use git::

    git clone git://github.com/joblib/joblib-hadoop.git

Installing joblib-hadoop
========================

We recommend using
`Python Anaconda 3 distribution <https://www.continuum.io/Downloads>`_ for
full support of the HDFS store backends.

1. Create an Anaconda environment (use python 2.7, 3.4 or 3.5) and activate it:

..  code-block:: bash

    $ conda create -n joblibhadoop-env python==3.5 libhdfs3 -c conda-forge
    $ . activate joblibhadoop-env

We recommend using anaconda because it provides a pre-built version of
libhdfs3. See build_libhdfs3_ if you want to install it using pip.

2. From the `joblibhadoop-env` environment, perform installation using pip:

..  code-block:: bash

    $ cd joblib-hadoop
    $ pip install -r requirements.txt .


Using joblib-hadoop on a Hadoop cluster
=======================================

1. Use a HDFS storage backend with Joblib memory to cache results (replace
'namenode' with the name of the HDFS namenode):

..  code-block:: python

  import numpy as np
  from joblib import Memory
  from joblibhadoop.hdfs import register_hdfs_store_backend

  if __name__ == '__main__':
      register_hdfs_store_backend()

      mem = Memory(location='joblib_cache_hdfs',
                   backend='hdfs', host='namenode', port=8020, user='test',
                   verbose=100, compress=True)

      multiply = mem.cache(np.multiply)
      array1 = np.arange(10000)
      array2 = np.arange(10000)

      result = multiply(array1, array2)

      # Second call should return the cached result
      result = multiply(array1, array2)
      print(result)

2. Use a YARN backend with Joblib parallel to parallelize computations:

..  code-block:: python

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
          delayed(sqrt)(i**2) for i in range(100)))

The YARN parallel backend example only works on a host where Hadoop is installed and 
correctly configured.


All examples are available in the `examples <examples>`_ directory.

Developping with joblibhadoop
=============================

Prerequisites
-------------

In order to run the test suite, you need to setup a local hadoop cluster. This
can be achieved very easily using the docker and docker-compose recipes given
in the `docker <docker>`_ directory:

1. `Install docker-engine <https://docs.docker.com/engine/installation/>`_:

You have to be able to run the hello-world container:

..  code-block:: bash

    $ docker run hello-world

2. Install docker-compose with pip:

..  code-block:: bash

    $ pip install docker-compose


3. Start your hadoop cluster using docker-compose:

..  code-block:: bash

    $ cd joblib-hadoop/docker
    $ docker-compose up

Running the test suite
----------------------

The test suite can be launched from another container of the Hadoop
nodemanager. This is achieved very easily using docker-compose.

1. Ensure your hadoop cluster is already started:

..  code-block:: bash

   $ cd joblib-hadoop/docker
   $ docker-compose up -d
   $ docker-compose ps

Your containers should be in the state *Up*.

2. You can start pytest from a nodemanager container instance:

..  code-block:: bash

   $ docker-compose run --rm -e NAMENODE=namenode nodemanager pytest

or locally:

..  code-block:: bash

   $ pytest

3. After changes in the code, the nodemanager image needs to be rebuild:

..  code-block:: bash

   $ docker-compose build --no-cache nodemanager


.. _build_libhdfs3:

Building and installing the hdfs3 package by hand
=================================================

For the moment hdfs3 cannot be directly installed using pip : the reason is
because hdfs3 depends on a C++ based library that is not available in the
Linux distros and that one needs to build by hand first.

The following notes are specific to Ubuntu 16.04 but can also be adapted to
Fedora (packages names are slightly different).

1. Clone libhdfs3 from github:

..  code-block:: bash

    $ sudo mkdir /opt/hdfs3
    $ sudo chown <login>:<login> /opt/hdfs3
    $ cd /opt/hdfs3
    $ git clone git@github.com:Pivotal-Data-Attic/pivotalrd-libhdfs3.git libhdfs3


2. Install required packages

..  code-block:: bash

    $ sudo apt-get install cmake cmake-curses-gui libxml2-dev libprotobuf-dev \
    libkrb5-dev uuid-dev libgsasl7-dev protobuf-compiler protobuf-c-compiler \
    build-essential -y


3. Use CMake to configure and build

..  code-block:: bash

   $ cd /opt/hdfs3/libhdfs3
   $ mkdir build
   $ cd build
   $ ../bootstrap
   $ make
   $ make install


4. Add the following to your **~/.bashrc** environment file:

::

   export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/opt/hdfs3/libhdfs3/dist

5. reload your environment:

..  code-block:: bash

   $ source ~/.bashrc

6. Use **pip** to install *hdfs3* (use `sudo` if needed):

..  code-block:: bash

   $ pip install hdfs3
