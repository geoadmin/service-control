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
