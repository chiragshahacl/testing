# Authentication Service

---

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Built with](https://img.shields.io/badge/Built_with-Cookiecutter_Django_Rest-F7B633.svg)](https://github.com/agconti/cookiecutter-django-rest)

This is a RESTful API authentication service built using Python/Django. The purpose of this service is to provide secure and easy-to-use authentication for any web or mobile application.

## Features

- User login with username and password
- User logout
- JWT based authentication
- Permission group management

## 📔 Documentation

Open your browser at http://127.0.0.1:7004/authentication/docs (or equivalent, using your Docker host), you will see an automatic, interactive, API documentation.

## Prerequisites

To install the authentication service locally, you will need the fallowing pakages installed:

<details>
<summary>Python</summary>

If you do not have Python installed on your system, install it manually from [Python's official website](https://www.python.org/downloads/). Additionally, you check the `pyproject.toml` file to determine the exact version of Python required for the project.

</details>

<details>
<summary>Poetry</summary>

You can follow the steps at [Poetry's doc](https://python-poetry.org/docs/), or install by using:

```shell
curl -sSL https://install.python-poetry.org | python3 -
```

</details>

<details>
  <summary>PostgreSQL</summary>

There are two simples way to have a postgreSQL instance running locally.

### Docker Image

```shell
docker network create tucana
docker run --name postgres_container -p 5432:5432 --network tucana -e POSTGRES_PASSWORD=cantguessthis -d postgres
```

### Local Installation

1. Install homebrew:

```shell
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

2. Check if it’s up to date and that it’s healthy:

```shell
brew update
brew doctor
```

3. Install postgreSQL:

```shell
brew install postgresql@15
```

4. Start posgreSQL service:

```shell
brew services start postgresql@15
```

Wait a few seconds, then confirm that it’s running:

```shell
brew services list
```

_**Note**: If it says “command not found” or “Unknown command”, you’ll need to add the Postgres app to your PATH in your shell file.
For example, if you are using .zshrc:_

```shell
echo 'export PATH="/Applications/Postgres.app/Contents/Versions/latest/bin:$PATH"' >> ~/.zshrc
```

</details>

## Installation

```shell
./build.sh
poetry run python create_db.py
poetry run python manage.py migrate
poetry run python manage.py runserver
```

_**Note**: Please note that the build script generates a `.env` file in the root folder, which contains the necessary environment
variables for running the project. While these variables have default values set, some of them may need to be updated to
reflect your local environment. Therefore, it is recommended that you check the `.env` file and modify the relevant
variables as needed before running the project._

## Configuration

Before you can start using the authentication service, you will need to create an admin user. To do so, execute:

```shell
poetry run python manage.py createsuperuser
```

To create internal tokens to be used in other applications you can use:

```
poetry run python manage.py create_internal_token --duration-days 10
```

To create system user you can use the following command in your local machine 

_**Note**: group shall be the comma seprated values from the list [ clinical, tech, organization, admin]_

```shell
poetry run python manage.py create_system_user --email {EMAIL} --groups clinical,tech --password {PASSWORD} --first_name {FIRSTNAME} --last_name {LASTNAME}
```

## Running locally

To start the server execute the following command:

```shell
poetry run python -m gunicorn authentication.asgi:application
```

## Docker

It is possible to start the service locally by running a Docker container. Start the dev server for local development:

```bash
docker-compose up
```

_**Note**: a script checks the availability of the PostgreSQL container before starting the server.
This helps to ensure that the container is ready for use before the server starts.
Please note that it may take a few seconds for the service to become available until PostgreSQL is ready._

## API Documentation

The API documentation for the authentication service can be found [insert link to documentation here].
