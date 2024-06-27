SHELL := /bin/bash
BIN_DIR ?= venv/bin/

venv:
	python3 -m venv venv && \
	source venv/bin/activate && \
	pip install -r requirements.txt -r requirements-dev.txt
run-db: # Run it first before starting the server or running tests. However, you may need to wait a moment for the database to be ready. Therefore, it hasn't been added as a prerequisite for the run-server or test targets.
	docker compose up -d
clean-db:
	docker compose down -v
test:
	${BIN_DIR}pytest
run-server:
	export POSTGRES_DB=dev_db && \
	${PATH_PREFIX}uvicorn app.main:app --reload
format-check:
	${BIN_DIR}black . --check
format:
	${BIN_DIR}black .
lint:
	${BIN_DIR}mypy . --check-untyped-defs