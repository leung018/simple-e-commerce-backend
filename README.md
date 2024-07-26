# simple e-commerce backend

## Project Manual

### Prerequisites

#### Python 3.12

I use pyenv and choose the version specified in the `.python-version` file. You can use your favorite way to set up the python environment.

#### Docker & Docker Compose

Use docker to run the postgres database.

### How To Run

1. Install the dependencies

```bash
make venv
```

Noted that every command in the `makefile` won't need to activate the virtual environment because it use the path to the virtual environment directly.

2. Start the database

```bash
make run-db
```

3. Import seed data for products

```bash
make import-products
```

4. Run the application

```bash
make run-server
```

Go to http://localhost:8000/docs to see the API swagger documentation and can try the API from there.

See makefile for more commands and more details.

## Potential Improvements

### Divide unit test and integration test

In current project, all tests use the real implementation. If the size of the project grows, it is better to divide the tests into unit tests and integration tests.

The tests in `test/repositories` can be considered as integration tests to interact with database directly while tests from other directories may use fake implementations of the repositories to test. One test of OrderService is also targeting the handling of race condition and prefer using real implementation of the repository and this test can be considered as integration test too.

Moreover, some function call related to bcrypt in library is quite slow. Can also consider to move the bcrypt related function to a separate module and test that module in integration test, while using fake implementation of that module in unit tests.
