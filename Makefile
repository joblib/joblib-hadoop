.PHONY: all test docker-test docker-hdfs-clear docker-compose-stop

all: test

# Only for local testing
test:
	pytest

# For testing within a docker container.
# Use with:
# $ docker-compose run --rm --name testnode -e NAMENODE=namenode nodemanager make docker-test
docker-test: docker-hdfs-clear test
	mv .coverage /shared

docker-hdfs-clear:
	hdfs dfs -rm -f -r /user/test

docker-compose-stop:
	cd docker && docker-compose stop
	cd docker && docker-compose rm -f
