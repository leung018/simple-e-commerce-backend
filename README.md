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

Go to `http://localhost:8000/docs` to see the API swagger documentation and can try the API from there.

See makefile for more commands and more details.

## Potential Improvements
