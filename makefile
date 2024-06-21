SHELL := /bin/bash
PATH_PREFIX := venv/bin/

venv:
	python3 -m venv venv && \
	source venv/bin/activate && \
	pip install -r requirements.txt -r requirements-dev.txt
test:
	${PATH_PREFIX}pytest
format-check:
	${PATH_PREFIX}black . --check
format:
	${PATH_PREFIX}black .
lint:
	${PATH_PREFIX}mypy . --check-untyped-defs