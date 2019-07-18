SHELL := /bin/sh


format:
	black -l 120 -t py37 -S ./app
