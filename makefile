SHELL := /bin/sh
CURRENT_DIR = $(shell pwd)

format:
	@black -l 120 -t py37 -S ./app

test:
	@python3 -m unittest discover -s tests -p test_*.py

coverage:
	@mkdir -p local
	@coverage run --rcfile .coveragerc -m unittest discover -s tests -p test_*.py
	@coverage html --skip-covered --rcfile .coveragerc
	@coverage report --skip-covered --rcfile .coveragerc
	@echo
	@echo "Coverage:" "file://"$(CURRENT_DIR)"/local/htmlcov/index.html"