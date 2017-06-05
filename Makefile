.PHONY: all

all: test
	pytest

docker-test: test
	mv .coverage /shared