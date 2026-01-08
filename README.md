# service-control

| Branch | Status |
|--------|-----------|
| develop | ![Build Status](https://codebuild.eu-central-1.amazonaws.com/badges?uuid=eyJlbmNyeXB0ZWREYXRhIjoiZk43RFNPWm5aNldBYmE3NU95MkFWNVg0aG5oMk1VRlhVcHNmdEVGOGFwc05zRW1lVG4zaU40dnBtSUFsd2dxd0tESlNYN1VkSS9pbkpFWDJ1ajQ0dkhrPSIsIml2UGFyYW1ldGVyU3BlYyI6IktHVHNJL21aN0NKKzg0V2YiLCJtYXRlcmlhbFNldFNlcmlhbCI6MX0%3D&branch=develop) |
| master | ![Build Status](https://codebuild.eu-central-1.amazonaws.com/badges?uuid=eyJlbmNyeXB0ZWREYXRhIjoiZk43RFNPWm5aNldBYmE3NU95MkFWNVg0aG5oMk1VRlhVcHNmdEVGOGFwc05zRW1lVG4zaU40dnBtSUFsd2dxd0tESlNYN1VkSS9pbkpFWDJ1ajQ0dkhrPSIsIml2UGFyYW1ldGVyU3BlYyI6IktHVHNJL21aN0NKKzg0V2YiLCJtYXRlcmlhbFNldFNlcmlhbCI6MX0%3D&branch=master) |

## Table of Content

- [Table of Content](#table-of-content)
- [Summary Of The Project](#summary-of-the-project)
- [Logging Standard Django Management Commands](#logging-standard-django-management-commands)
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
- [OTEL](#otel)
  - [Bootstrap](#bootstrap)
  - [Environment Variables](#environment-variables)
  - [Log Correlation](#log-correlation)
  - [Sampling](#sampling)
  - [Local Telemetry](#local-telemetry)
- [Importing Data from the BOD](#importing-data-from-the-bod)
- [Type Checking](#type-checking)
  - [Mypy](#mypy)
  - [Library Types](#library-types)
- [Deployment configuration](#deployment-configuration)

## Summary Of The Project

`service-control` provides and manages the verified permissions.  TBC

## Logging Standard Django Management Commands

This project uses a modified `manage.py` that supports redirecting the output of the standard
Django management commands to the logger. For this, simply add `--redirect-std-to-logger`, e.g.:

```bash
app/manage.py migrate --redirect-std-to-logger
```

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

All packages used in production are pinned to a major version. Automatically updating these packages
will use the latest minor (or patch) version available. Packages used for development, on the other
hand, are not pinned unless they need to be used with a specific version of a production package
(for example, boto3-stubs for boto3).

To update the packages to the latest minor/compatible versions, run:

```bash
pipenv update --dev
```

To see what major/incompatible releases would be available, run:

```bash
pipenv update --dev --outdated
```

To update packages to a new major release, run:

```bash
pipenv install logging-utilities~=5.0
```

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

## OTEL

[OpenTelemetry instrumentation](https://opentelemetry.io/docs/concepts/instrumentation/) can be done in many different ways, from fully automated zero-code instrumentation (otel-operator) to purely manual instrumentation.
Since we are kubernetes, the ideal solution would be to use the [otel-operator zero-code instrumentation](https://www.elastic.co/docs/solutions/observability/get-started/opentelemetry/use-cases/kubernetes/instrumenting-applications).

For reasons unclear (possibly related to how we do gevent monkey patching), zero-code auto-instrumentation does not work. Thus, we fall back to programmatic instrumentation as described in the [Python Opentelemetry Manual-Instrumentation Sample App](https://github.com/aws-observability/aws-otel-community/tree/master/sample-apps/python-manual-instrumentation-sample-app). We may revisit this once we figure out how to make auto-instrumentation work for this service.

To still use as less code as we can, we use the so called `OTEL programmatical instrumentation` approach. Unfortunately there are different understandings,
levels of integration and examples of this approach. We use the [method described here](https://github.com/open-telemetry/opentelemetry-python-contrib/tree/main/opentelemetry-instrumentation#programmatic-auto-instrumentation), since it provides the highest level of automatic instrumentation. I.e. we can use a initialize() method to automatically initialize all installed instrumentation libraries.

Other examples like these:

- [aws-otel-community](https://github.com/aws-observability/aws-otel-community/blob/master/sample-apps/python-manual-instrumentation-sample-app/app.py)
- [OTEL examples](https://opentelemetry.io/docs/zero-code/python/example/#programmatically-instrumented-server)

import the specific instrumentation libraries and initialize them with the instrument() method of each library.

It can be expected that documentations will improve and consolidate over time, as well that zero-code instrumentaton can be used in the future.

### Bootstrap

As mentioned above, all available and desired instrumentation libraries need to be installed first, i.e. added to the pipfile.
Well known libraries like django, request and botocore could be added manually. To get a better overview and add broader instrumentation
support, a otel bootstrap tool can be used to create a list of supported libraries for a given project.

Usage:

1. `edot-bootstrap --action=requirements` to get the list of libraries
2. Add all or the desired ones to the Pipfile.

Note: `edot-bootstrap` should be already installed via `infra-ansible-bgdi-dev`. If not, install it with `pipx install elastic-opentelemetry`.

### Environment Variables

The following env variables can be used to configure OTEL

| Env Variable                                              | Default                    | Description                                                                                                                                          |
| --------------------------------------------------------- | -------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| OTEL_EXPERIMENTAL_RESOURCE_DETECTORS                      |                            | OTEL resource detectors, adding resource attributes to the OTEL output. e.g. `os,process`                                                            |
| OTEL_EXPORTER_OTLP_ENDPOINT                               | http://localhost:4317      | The OTEL Exporter endpoint, e.g. `opentelemetry-kube-stack-gateway-collector.opentelemetry-operator-system:4317`                                     |
| OTEL_EXPORTER_OTLP_HEADERS                                |                            | A list of key=value headers added in outgoing data. https://opentelemetry.io/docs/languages/sdk-configuration/otlp-exporter/#header-configuration    |
| OTEL_EXPORTER_OTLP_INSECURE                               | false                      | If exporter ssl certificates should be checked or not.                                                                                               |
| OTEL_INSTRUMENTATION_HTTP_CAPTURE_HEADERS_SERVER_REQUEST  |                            | A comma separated list of request headers added in outgoing data. Regex supported. Use '.*' for all headers                                          |
| OTEL_INSTRUMENTATION_HTTP_CAPTURE_HEADERS_SERVER_RESPONSE |                            | A comma separated list of request headers added in outgoing data. Regex supported. Use '.*' for all headers                                          |
| OTEL_PYTHON_EXCLUDED_URLS                                 |                            | A comma separated list of url's to exclude, e.g. `checker`                                                                                           |
| OTEL_PYTHON_DJANGO_TRACED_REQUEST_ATTRS                   |                            | A comma separated list of attributes from the django request, e.g. `path_info,content_type`                                                          |
| OTEL_RESOURCE_ATTRIBUTES                                  |                            | A comma separated list of custom OTEL resource attributes, Must contain at least the service-name `service.name=service-shortlink`                   |
| OTEL_TRACES_SAMPLER                                       | parentbased_always_on      | Sampler to be used, see https://opentelemetry-python.readthedocs.io/en/latest/sdk/trace.sampling.html#module-opentelemetry.sdk.trace.sampling.       |
| OTEL_TRACES_SAMPLER_ARG                                   |                            | Optional additional arguments for sampler.                                                                                                           |
| OTEL_SDK_DISABLED                                         |                            | If set to "true", OTEL is disabled. See: https://opentelemetry.io/docs/specs/otel/configuration/sdk-environment-variables/#general-sdk-configuration |

### Log Correlation

The OpenTelemetry logging integration automatically injects tracing context into log statements. The following keys are injected into log record objects:

- otelSpanID
- otelTraceID
- otelTraceSampled

Note that although otelServiceName is injected, it will be empty. This is because the logging integration tries to read the service name from the trace provider, but our trace provider instance does not contain this resource attribute.

### Sampling

The python SDK supports ratio based [head sampling](https://opentelemetry.io/docs/concepts/sampling/#head-sampling). To enable, set

- OTEL_TRACES_SAMPLER=parentbased_traceidratio|traceidratio
- and OTEL_TRACES_SAMPLER_ARG=[0.0,1.0]

### Local Telemetry

Local telemetry can be tested by using one of the serve commands that use gunicorn, either 

```bash
make start-local-db
make gunicornserve
```

or

```bash
make start-local-db
make dockerrun
```

and visiting the Zipkin dashboard at [http://localhost:9411](http://localhost:9411).

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

## Deployment configuration

| **Environment Variable**    | **Default**                                   | **Description**                                                                                                                      |
| --------------------------- | --------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| `SECRET_KEY`                | `None`                                        | Django secret key.                                                                                                                   |
| `ALLOWED_HOSTS`             | `[]`                                          | list of host/domain names allowed to serve the app.                                                                                  |
| `DB_NAME`                   | `service_control`                             | Name of the primary PostgreSQL database.                                                                                             |
| `DB_USER`                   | `service_control`                             | Username for the primary PostgreSQL database.                                                                                        |
| `DB_PW`                     | `service_control`                             | Password for the primary PostgreSQL database.                                                                                        |
| `DB_HOST`                   | `service_control`                             | Host address for the primary PostgreSQL database.                                                                                    |
| `DB_PORT`                   | `5432`                                        | Port number for the primary PostgreSQL database.                                                                                     |
| `DB_NAME_TEST`              | `test_service_control`                        | Name of the PostgreSQL database used for testing.                                                                                    |
| `BOD_NAME`                  | `service_control`                             | Name of the secondary (bod) PostgreSQL database.                                                                                     |
| `BOD_USER`                  | `service_control`                             | Username for the bod PostgreSQL database.                                                                                            |
| `BOD_PW`                    | `service_control`                             | Password for the bod PostgreSQL database.                                                                                            |
| `BOD_HOST`                  | `service_control`                             | Host address for the bod PostgreSQL database.                                                                                        |
| `BOD_PORT`                  | `5432`                                        | Port number for the bod PostgreSQL database.                                                                                         |
| `DJANGO_STATIC_HOST`        | `''`                                          | Optional base URL.                                                                                                                   |
| `COGNITO_ENDPOINT_URL`      | `http://localhost:9229`                       | Base URL for AWS Cognito endpoint or local mock.                                                                                     |
| `COGNITO_POOL_ID`           | `local`                                       | Cognito user pool ID used for authentication.                                                                                        |
| `COGNITO_MANAGED_FLAG_NAME` | `dev:custom:managed_by_service`               | Cognito custom attribute name for service-managed users.                                                                             |
| `SHORT_ID_SIZE`             | `12`                                          | Default length of generated short IDs (nanoid).                                                                                      |
| `SHORT_ID_ALPHABET`         | `0123456789abcdefghijklmnopqrstuvwxyz`        | Character set used for nanoid short IDs.                                                                                             |
| `LOGGING_CFG`               | `config/logging-cfg-local.yaml`               | Path to YAML logging configuration file.                                                                                             |
| `LOG_ALLOWED_HEADERS`       | List of default headers                       | list of HTTP headers allowed in logs (overrides defaults).                                                                           |
| `HTTP_PORT`                 | `8000`                                        | Port on which the Gunicorn/Django app will listen.                                                                                   |
| `GUNICORN_WORKERS`          | `2`                                           | Number of worker processes Gunicorn will start.                                                                                      |
| `GUNICORN_WORKER_TMP_DIR`   | `None`                                        | Optional temporary directory for Gunicorn worker processes.                                                                          |
| `GUNICORN_KEEPALIVE`        | `2`                                           | The [`keepalive`](https://docs.gunicorn.org/en/stable/settings.html#keepalive) setting for persistent HTTP connections (in seconds). |
| `GUNICORN_TIMEOUT`          | Not explicitely set                           | The maximum time (in seconds) a worker can handle a request before timing out.                                                       |
