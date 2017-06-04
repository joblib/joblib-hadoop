.PHONY: all

all: coverage

test:
	pytest
	
coverage: test
	codecov