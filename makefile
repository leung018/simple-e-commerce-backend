SHELL := /bin/bash
PATH_PREFIX := venv/bin/

venv:
	python3 -m venv venv && \
	source venv/bin/activate && \
	pip install -r requirements.txt -r requirements-dev.txt
test:
	${PATH_PREFIX}pytest