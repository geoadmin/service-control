SHELL = /bin/bash

.DEFAULT_GOAL := help

SERVICE_NAME := service-control

CURRENT_DIR := $(shell pwd)

# Docker metadata
GIT_HASH = `git rev-parse HEAD`
GIT_HASH_SHORT = `git rev-parse --short HEAD`
GIT_BRANCH = `git symbolic-ref HEAD --short 2>/dev/null`
GIT_DIRTY = `git status --porcelain`
GIT_TAG = `git describe --tags || echo "no version info"`
AUTHOR = $(USER)

# Imports the environment variables
## TODO if we call the file .env, then it'll be read by pipenv too
## which is good for running migrate
# ifneq ("$(wildcard .env)","")
# include .env
# export
# else
# include .env
# export
# endif

# Django specific
APP_SRC_DIR := app
DJANGO_MANAGER := $(CURRENT_DIR)/$(APP_SRC_DIR)/manage.py
DJANGO_MANAGER_DEBUG := -m debugpy --listen localhost:5678 --wait-for-client $(CURRENT_DIR)/$(APP_SRC_DIR)/manage.py

# Commands
PIPENV_RUN := pipenv run
PYTHON := $(PIPENV_RUN) python3
TEST := $(PIPENV_RUN) pytest
YAPF := $(PIPENV_RUN) yapf
ISORT := $(PIPENV_RUN) isort
PYLINT := $(PIPENV_RUN) pylint
MYPY := $(PIPENV_RUN) mypy
PSQL := PGPASSWORD=postgres psql -h localhost -p 15433 -U postgres
PGRESTORE := PGPASSWORD=postgres pg_restore -h localhost -p 15433 -U postgres

# Find all python files that are not inside a hidden directory (directory starting with .)
PYTHON_FILES := $(shell find $(APP_SRC_DIR) -type f -name "*.py" -print)

# Docker variables
DOCKER_REGISTRY = 974517877189.dkr.ecr.eu-central-1.amazonaws.com
DOCKER_IMG_LOCAL_TAG := $(DOCKER_REGISTRY)/$(SERVICE_NAME):local-$(USER)-$(GIT_HASH_SHORT)

# AWS variables
AWS_DEFAULT_REGION = eu-central-1

.PHONY: ci
ci:
	# Create virtual env with all packages for development using the Pipfile.lock
	pipenv sync --dev

.PHONY: setup
setup: $(SETTINGS_TIMESTAMP) ## Create virtualenv with all packages for development
	pipenv install --dev
	cp .env.default .env
	pipenv shell

.PHONY: format
format: ## Call yapf to make sure your code is easier to read and respects some conventions.
	$(YAPF) -p -i --style .style.yapf $(PYTHON_FILES)
	$(ISORT) $(PYTHON_FILES)


.PHONY: django-checks
django-checks: ## Run the django checks
	$(PYTHON) $(DJANGO_MANAGER) check --fail-level WARNING

.PHONY: django-check-migrations
django-check-migrations: ## Check the migrations
	@echo "Check for missing migration files"
	$(PYTHON) $(DJANGO_MANAGER) makemigrations --no-input --check


.PHONY: ci-check-format
ci-check-format: format ## Check the format (CI)
	@if [[ -n `git status --porcelain --untracked-files=no` ]]; then \
	 	>&2 echo "ERROR: the following files are not formatted correctly"; \
	 	>&2 echo "'git status --porcelain' reported changes in those files after a 'make format' :"; \
		>&2 git status --porcelain --untracked-files=no; \
		exit 1; \
	fi

.PHONY: serve
serve: ## Serve the application locally
	$(PYTHON) $(DJANGO_MANAGER) runserver

.PHONY: serve-debug
serve-debug: ## Serve the application locally for debugging
	$(PYTHON) $(DJANGO_MANAGER_DEBUG) runserver

.PHONY: dockerlogin
dockerlogin: ## Login to the AWS Docker Registry (ECR)
	aws --profile swisstopo-bgdi-builder ecr get-login-password --region $(AWS_DEFAULT_REGION) | docker login --username AWS --password-stdin $(DOCKER_REGISTRY)


.PHONY: dockerbuild
dockerbuild: ## Create a docker image
	docker build \
		--build-arg GIT_HASH="$(GIT_HASH)" \
		--build-arg GIT_BRANCH="$(GIT_BRANCH)" \
		--build-arg GIT_DIRTY="$(GIT_DIRTY)" \
		--build-arg VERSION="$(GIT_TAG)" \
		--build-arg HTTP_PORT="$(HTTP_PORT)" \
		--build-arg AUTHOR="$(AUTHOR)" -t $(DOCKER_IMG_LOCAL_TAG) .


.PHONY: dockerpush
dockerpush: dockerbuild ## Push to the docker registry
	docker push $(DOCKER_IMG_LOCAL_TAG)


.PHONY: dockerrun
dockerrun: clean_logs dockerbuild $(LOGS_DIR) ## Run the locally built docker image
	docker run \
		-it -p $(HTTP_PORT):8080 \
		--env-file=${PWD}/${ENV_FILE} \
		--env LOGS_DIR=/logs \
		--env SCRIPT_NAME=$(ROUTE_PREFIX) \
		--mount type=bind,source="${LOGS_DIR}",target=/logs \
		$(DOCKER_IMG_LOCAL_TAG)


# make sure that the code conforms to the style guide. Note that
# - the DJANGO_SETTINGS module must be made available to pylint
#   to support e.g. string model referencec (see
#   https://github.com/PyCQA/pylint-django#usage)
# - export of migrations for prometheus stats must be disabled,
#   otherwise it's attempted to connect to the db during linting
#   (which is not available)
.PHONY: lint
lint: ## Run the linter on the code base
	@echo "Run pylint..."
	LOGGING_CFG=0 $(PYLINT) $(PYTHON_FILES)

.PHONY: type-check
type-check: ## Run the type-checker mypy
	$(MYPY) app/

.PHONY: start-local-db
start-local-db: ## Run the local db as docker container
	docker compose up -d

.PHONY: test
test: ## Run tests locally
	$(TEST)

.PHONY: setup-bod
setup-bod: ## Set up the bod locally
	$(PSQL) -c 'CREATE ROLE "pgkogis";'
	$(PSQL) -c 'CREATE ROLE "www-data";'
	$(PSQL) -c 'CREATE ROLE "bod_admin";'
	$(PSQL) -c 'CREATE ROLE "rdsadmin";'

.PHONY: import-bod
import-bod: ## Import the bod locally
	$(PSQL) -c 'DROP DATABASE IF EXISTS bod_master;'
	$(PSQL) -c 'CREATE DATABASE bod_master;'
	$(PGRESTORE) -d bod_master $(file) --v

.PHONY: help
help: ## Display this help
# automatically generate the help page based on the documentation after each make target
# from https://gist.github.com/prwhite/8168133
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m\033[0m\n"} /^[$$()% a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)
