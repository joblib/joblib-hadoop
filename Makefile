.PHONY: all test docker-test docker-pytest docker-hdfs-clear docker-stop docker-all

all: test

# Only for local testing
test:
	pytest

install:
	pip install setuptools
	pip install -r requirements.txt . --upgrade

run-examples:
	cd docker && \
		docker-compose run --rm -e JOBLIB_HDFS_NAMENODE=namenode joblib-hadoop-client make docker-examples

run-all:
	cd docker && \
		docker-compose run --rm -e JOBLIB_HDFS_NAMENODE=namenode joblib-hadoop-client make docker-all

run-container:
	cd docker && \
		docker-compose run --rm -e JOBLIB_HDFS_NAMENODE=namenode joblib-hadoop-client bash

# Start the Hadoop cluster
docker-start:
	cd docker && docker-compose up

# Gently stop/remove a running Hadoop cluster
docker-stop:
	cd docker && docker-compose stop
	cd docker && docker-compose rm -f

# Launch the test suite in the joblib-hadoop client docker container.
# For the moment, this is the only way for testing the YARN backend
# automatically.
docker-test:
	cd docker && \
		docker-compose run --rm -e JOBLIB_HDFS_NAMENODE=namenode joblib-hadoop-client make docker-pytest

# Examples runner helpers
hdfs-example:
	python examples/joblib_hdfs_multiply.py

# The YARN example only works if access to the hadoop cluster is not done via
# localhost (e.g use it from the .
yarn-example:
	python examples/joblib_yarn_parallel.py

examples: hdfs-example yarn-example

# The following targets can only be used from inside the joblib-hadoop-client 
# docker container.
# Run this each time the joblib-hadoop-client container is started in
# interactive mode.

# The coverage is moved from the container to the host in order to be used
# later by codecov: we need this trick since the YARN backend can only be tested
# from the container.
docker-pytest: install hdfs-clear test

docker-examples: install examples

docker-all: install examples hdfs-clear test

# Pytest creates the Memory cache test results in /user/test in the hdfs
# cluster, this target ensures we start from a fresh setup.
hdfs-clear:
	hdfs dfs -rm -f -r /user/test
