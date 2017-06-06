.PHONY: all test docker-test docker-pytest docker-hdfs-clear docker-compose-stop

all: test

# Only for local testing
test:
	pytest

# This is a helper target for gently stop/remove a running cluster
docker-compose-stop:
	cd docker && docker-compose stop
	cd docker && docker-compose rm -f

# Launch the test suite in the joblib-hadoop client docker container.
# For the moment, this is the only way for testing the YARN backend
# automatically.
docker-test:
	cd docker && docker-compose run --rm -e JOBLIB_HDFS_NAMENODE=namenode joblib-hadoop-client make docker-pytest

# Examples runner helpers
docker-hdfs-example:
	cd docker && docker-compose run --rm joblib-hadoop-client python examples/joblib_hdfs_multiply.py

docker-yarn-example:
	cd docker && docker-compose run --rm joblib-hadoop-client python examples/joblib_yarn_parallel.py

docker-gridsearchcv-example:
	cd docker && docker-compose run --rm joblib-hadoop-client python examples/gridsearchcv.py

# The following targets are only for testing from inside a docker container.

# The coverage is moved from the container to the host in order to be used
# later by codecov: we need this trick since the YARN backend can only be tested
# from the container.
docker-pytest: docker-hdfs-clear test
	mv .coverage /shared

# Pytest creates the Memory cache test results in /user/test in the hdfs
# cluster, this target ensures we start from a fresh setup.
docker-hdfs-clear:
	hdfs dfs -rm -f -r /user/test
