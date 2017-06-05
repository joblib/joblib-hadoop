.PHONY: all

all: test

# Only for local testing
test:
	pytest

# For testing within a docker container.
# Use with:
# $ docker-compose run --rm --name testnode -e NAMENODE=namenode nodemanager make docker-test
docker-test: test
	mv .coverage /shared