# service-control

| Branch | Status |
|--------|-----------|
| develop | ![Build Status](https://codebuild.eu-central-1.amazonaws.com/badges?uuid=eyJlbmNyeXB0ZWREYXRhIjoiZk43RFNPWm5aNldBYmE3NU95MkFWNVg0aG5oMk1VRlhVcHNmdEVGOGFwc05zRW1lVG4zaU40dnBtSUFsd2dxd0tESlNYN1VkSS9pbkpFWDJ1ajQ0dkhrPSIsIml2UGFyYW1ldGVyU3BlYyI6IktHVHNJL21aN0NKKzg0V2YiLCJtYXRlcmlhbFNldFNlcmlhbCI6MX0%3D&branch=develop) |
| master | ![Build Status](https://codebuild.eu-central-1.amazonaws.com/badges?uuid=eyJlbmNyeXB0ZWREYXRhIjoiZk43RFNPWm5aNldBYmE3NU95MkFWNVg0aG5oMk1VRlhVcHNmdEVGOGFwc05zRW1lVG4zaU40dnBtSUFsd2dxd0tESlNYN1VkSS9pbkpFWDJ1ajQ0dkhrPSIsIml2UGFyYW1ldGVyU3BlYyI6IktHVHNJL21aN0NKKzg0V2YiLCJtYXRlcmlhbFNldFNlcmlhbCI6MX0%3D&branch=master) |

## Table of Content

- [Table of Content](#table-of-content)
- [Summary Of The Project](#summary-of-the-project)
- [Local Development](#local-development)
  - [Dependencies](#dependencies)
  - [Setup](#setup)
  - [Updating Packages](#updating-packages)
  - [Running Tests In Parallel](#running-tests-in-parallel)
  - [Visual Studio Code Integration](#visual-studio-code-integration)
    - [Debug from Visual Studio Code](#debug-from-visual-studio-code)
    - [Run Tests From Within Visual Studio Code](#run-tests-from-within-visual-studio-code)
- [Cognito](#cognito)
  - [Local Cognito](#local-cognito)
- [Importing Data from the BOD](#importing-data-from-the-bod)
- [Type Checking](#type-checking)
  - [Mypy](#mypy)
  - [Library Types](#library-types)

## Summary Of The Project

`service-control` provides and manages the verified permissions.  TBC

## Local Development

### Dependencies

Prerequisites on host for development and build:

- python version 3.12
- [pipenv](https://pipenv-fork.readthedocs.io/en/latest/install.html)
- `docker` and `docker compose`

### Setup

To create and activate a virtual Python environment with all dependencies installed:

```bash
make setup
```

To start the local postgres container, run this:

```bash
make start-local-db
```

You may want to do an initial sync of your database by applying the most recent Django migrations with

```bash
app/manage.py migrate
```

### Updating Packages

All packages used in production are pinned to a minor version. Automatically updating these packages
will use the latest minor (or patch) version. Packages used for development, on the other hand, are
not pinned unless they need to be used with a specific version of a production package
(for example, boto3-stubs for boto3).

To update the packages to the latest minor or patch version, run:

```bash
pipenv lock
pipenv sync --dev
```

To update packages to a new major release, modify the version in the Pipfile, then run the command
above.

### Running Tests In Parallel

Run tests with, for example, 16 workers:

```bash
pytest -n 16
```

### Visual Studio Code Integration

There are some possibilities to debug this codebase from within visual studio code.

#### Debug from Visual Studio Code

In order to debug the service from within vs code, you need to create a launch-configuration. Create
a folder `.vscode` in the root folder if it doesn't exist and put a file `launch.json` with this content
in it:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python Debugger: Attach",
      "type": "debugpy",
      "request": "attach",
      "justMyCode": false,
      "connect": {
        "host": "localhost",
        "port": 5678
      }
    }
  ]
}
```

Alternatively, create the file via menu "Run" > "Add Configuration" by choosing

- Debugger: Python Debugger
- Debug Configration: Remote Attach
- Hostname: `localhost`
- Port number: `5678`

Now you can start the server with `make serve-debug`.
The bootup will wait with the execution until the debugger is attached, which can most easily done by hitting F5.

#### Run Tests From Within Visual Studio Code

The unit tests can also be invoked inside vs code directly (beaker icon).
To do this you need to have the following settings either in
`.vscode/settings.json` or in your workspace settings:

```json
  "python.testing.pytestArgs": [
    "app"
  ],
  "python.testing.unittestEnabled": false,
  "python.testing.pytestEnabled": true,
```

You can also create this file interactively via menu "Python: Configure Tests"
in the Command Palette (Ctrl+Shift+P).

For the automatic test discovery to work, make sure that vs code has the Python
interpreter of your venv selected (`.venv/bin/python`).
You can change the Python interpreter via menu "Python: Select Interpreter"
in the Command Palette.

## Cognito

This project uses Amazon Cognito user identity and access management. It uses a custom user attribute to
mark users managed_by_service by this service.

To synchronize all local users with cognito, run:

```bash
app/manage.py cognito_sync
```

### Local Cognito

For local testing the connection to cognito, [cognito-local](https://github.com/jagregory/cognito-local) is used.
`cognito-local` stores all of its data as simple JSON files in its volume (`.volumes/cognito/db/`).

You can also use the AWS CLI together with `cognito-local` by specifying the local endpoint, for example:

```bash
aws --endpoint $COGNITO_ENDPOINT_URL cognito-idp list-users --user-pool-id $COGNITO_POOL_ID
```

## Importing Data from the BOD

The "Betriebsobjekte Datenbank" (BOD) is a central database for running and configuring the map
viewer and some of its services. It contains metadata and translations on the individual layers
and configurations for display and serving the data through our services such as Web Map Service
(WMS), Web Map Tiling Service (WMTS) and our current api (mf-chsdi3/api3).

You can import a BOD dump and migrate its data:

```bash
make setup-bod
make import-bod file=dump.sql
app/manage.py bod_sync
```

To generate more BOD models, run:

```bash
app/manage.py inspectdb --database=bod
```

The BOD models are unmanaged, meaning Django does not manage any migrations for these models.
However, migrations are still needed during tests to set up the test BOD. To achieve this, it is
necessary to create migrations for the models and dynamically adjust the `managed` flag based on
whether the tests or the server is running (`django.conf.settings.TESTING`). Since these migrations
are only for testing purposes, the previous migration file can be removed and recreated:


```bash
rm app/bod/migrations/0001_initial.py
app/manage.py makemigrations bod
```

Afterward, the `managed` flag needs to be set to `django.conf.settings.TESTING` in both the models
and the migrations.

## Type Checking

### Mypy

Type checking can be done by either calling `mypy` or the make target: 

```sh
make type-check
```

This will check all files in the repository.

### Library Types

For type-checking, the external library [mypy](https://mypy.readthedocs.io) is being used. See the [type hints cheat sheet](https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html) for help on getting the types right.

Some 3rd party libraries need to have explicit type stubs installed for the type checker
to work. Some of them can be found in [typeshed](https://github.com/python/typeshed). Sometimes dedicated
packages exist, as is the case with [django-stubs](https://pypi.org/project/django-stubs/).

If there aren't any type hints available, they can also be auto-generated with [stubgen](https://mypy.readthedocs.io/en/stable/stubgen.html)
