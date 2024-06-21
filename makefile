SHELL := /bin/bash
BIN_DIR ?= venv/bin/

venv:
	python3 -m venv venv && \
	source venv/bin/activate && \
	pip install -r requirements.txt -r requirements-dev.txt
test:
	${BIN_DIR}pytest
format-check:
	${BIN_DIR}black . --check
format:
	${BIN_DIR}black .
lint:
	${BIN_DIR}mypy . --check-untyped-defs