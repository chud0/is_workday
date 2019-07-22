SHELL := /bin/sh


format:
	black -l 120 -t py37 -S ./app

test:
	@python3 -m unittest discover -s tests -p test_*.py
