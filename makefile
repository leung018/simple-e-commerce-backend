SHELL := /bin/bash
VENV_BIN_PATH := venv/bin/

venv:
	python3 -m venv venv && \
	source venv/bin/activate && \
	pip install -r requirements.txt -r requirements-dev.txt
test:
	${VENV_BIN_PATH}pytest
format-check:
	${VENV_BIN_PATH}black . --check
format:
	${VENV_BIN_PATH}black .
lint:
	${VENV_BIN_PATH}mypy . --check-untyped-defs