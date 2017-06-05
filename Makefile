.PHONY: all

all: test
	pytest

docker-test: test
	mv coverage.txt /shared