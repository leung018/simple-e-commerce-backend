SHELL := /bin/bash
BIN_DIR ?= venv/bin/

venv:
	python3 -m venv venv && \
	source venv/bin/activate && \
	pip install -r requirements.txt -r requirements-dev.txt
run-db:
	docker compose up -d
clean-db:
	docker compose down -v
test: # run-db first in local development. Don't add run-db directly here becasue no need for github action
	${BIN_DIR}pytest
run-server: run-db
	${PATH_PREFIX}uvicorn app.main:app --reload
format-check:
	${BIN_DIR}black . --check
format:
	${BIN_DIR}black .
lint:
	${BIN_DIR}mypy . --check-untyped-defs