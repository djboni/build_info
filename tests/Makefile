#!/usr/bin/python3
# Build Info - https://github.com/djboni/build_info
# MIT License - Copyright (c) 2021 Djones A. Boni

COVERAGE_OMIT = --omit="./*"

all: compilations tests

tests:
	python3 -m unittest

compilations:
	cd example && make clean all
	cd test_generated_code && make clean all

coverage:
	coverage run --branch -m unittest
	coverage report $(COVERAGE_OMIT) --show-missing --skip-empty

clean:
	cd example && make clean
	cd test_generated_code && make clean
	find .. -type d -name __pycache__ | xargs rm -fr
	rm -f .coverage
