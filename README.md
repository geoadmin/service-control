# service-control

| Branch | Status |
|--------|-----------|
| develop | ![Build Status](https://codebuild.eu-central-1.amazonaws.com/badges?uuid=eyJlbmNyeXB0ZWREYXRhIjoiZk43RFNPWm5aNldBYmE3NU95MkFWNVg0aG5oMk1VRlhVcHNmdEVGOGFwc05zRW1lVG4zaU40dnBtSUFsd2dxd0tESlNYN1VkSS9pbkpFWDJ1ajQ0dkhrPSIsIml2UGFyYW1ldGVyU3BlYyI6IktHVHNJL21aN0NKKzg0V2YiLCJtYXRlcmlhbFNldFNlcmlhbCI6MX0%3D&branch=develop) |
| master | ![Build Status](https://codebuild.eu-central-1.amazonaws.com/badges?uuid=eyJlbmNyeXB0ZWREYXRhIjoiZk43RFNPWm5aNldBYmE3NU95MkFWNVg0aG5oMk1VRlhVcHNmdEVGOGFwc05zRW1lVG4zaU40dnBtSUFsd2dxd0tESlNYN1VkSS9pbkpFWDJ1ajQ0dkhrPSIsIml2UGFyYW1ldGVyU3BlYyI6IktHVHNJL21aN0NKKzg0V2YiLCJtYXRlcmlhbFNldFNlcmlhbCI6MX0%3D&branch=master) |


## Table of Content

- [Table of Content](#table-of-content)
- [Summary of the project](#summary-of-the-project)
- [Local development](#local-development)
  - [Dependencies](#dependencies)
  - [Setup](#setup)
- [Local Development](#local-development-1)
  - [vs code Integration](#vs-code-integration)
    - [Debug from vs code](#debug-from-vs-code)
    - [Attach debugger to the tests](#attach-debugger-to-the-tests)
    - [Run tests from within vs code](#run-tests-from-within-vs-code)

## Summary of the project

`service-control` provides and manages the verified permissions.  TBC

## Local development

### Dependencies

Prerequisites on host for development and build:

- python version 3.12
- [pipenv](https://pipenv-fork.readthedocs.io/en/latest/install.html)
- `docker` and `docker compose`

### Setup

Copy the `.env.dist` file to `.env` on your local machine:

```bash
cp .env.dist .env
```

Initialize the local python environment with pipenv:

```bash
pipenv sync -d
```

and start the local postgres container

```bash
docker compose up
```

## Local Development

### vs code Integration

There are some possibilities to debug this codebase from within visual studio code.

#### Debug from vs code

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

Now you can start the server with `make serve-debug`. The bootup will wait with the execution until 
the debugger is attached, which can most easily done by hitting f5.

#### Attach debugger to the tests

The same process described above can be used to debug tests. Simply run `make test-debug`, they will
then wait until the debugger is attached.

#### Run tests from within vs code

The unit tests can also be invoked inside vs code directly. To do this you need to have following
settings locally to your workspace:

```json
  "python.testing.pytestArgs": [
    "app"
  ],
  "python.testing.unittestEnabled": false,
  "python.testing.pytestEnabled": true,
  "python.testing.debugPort": 5678
```

They can either be in `.vscode/settings.json` or in your workspace settings. Now the tests can be
run and debugged with the testing tab of vscode (beaker icon).
