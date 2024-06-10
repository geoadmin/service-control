SHELL = /bin/bash

.DEFAULT_GOAL := help

SERVICE_NAME := service-control

CURRENT_DIR := $(shell pwd)

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

# Commands
PIPENV_RUN := pipenv run
PYTHON := $(PIPENV_RUN) python3
YAPF := $(PIPENV_RUN) yapf
ISORT := $(PIPENV_RUN) isort
PYLINT := $(PIPENV_RUN) pylint

# Find all python files that are not inside a hidden directory (directory starting with .)
PYTHON_FILES := $(shell find $(APP_SRC_DIR) -type f -name "*.py" -print)

.PHONY: ci
ci:
	# Create virtual env with all packages for development using the Pipfile.lock
	pipenv sync --dev

.PHONY: setup
setup: $(SETTINGS_TIMESTAMP)
	# Create virtual env with all packages for development
	pipenv install --dev
	pipenv shell
	cp .env.default .env

.PHONY: format
format: ## Call yapf to make sure your code is easier to read and respects some conventions.
	$(YAPF) -p -i --style .style.yapf $(PYTHON_FILES)
	$(ISORT) $(PYTHON_FILES)

.PHONY: lint
lint: ## Run the code linting
	@echo "Run pylint..."
	$(PYLINT) $(PYTHON_FILES)

.PHONY: django-checks
django-checks: ## Run the django checks
	$(PYTHON) $(DJANGO_MANAGER) check --fail-level WARNING

.PHONY: django-check-migrations
django-check-migrations: ## Check the migrations
	@echo "Check for missing migration files"
	$(PYTHON) $(DJANGO_MANAGER) makemigrations --no-input --check


.PHONY: ci-check-format
ci-check-format: format
	@if [[ -n `git status --porcelain --untracked-files=no` ]]; then \
	 	>&2 echo "ERROR: the following files are not formatted correctly"; \
	 	>&2 echo "'git status --porcelain' reported changes in those files after a 'make format' :"; \
		>&2 git status --porcelain --untracked-files=no; \
		exit 1; \
	fi


# make sure that the code conforms to the style guide. Note that
# - the DJANGO_SETTINGS module must be made available to pylint
#   to support e.g. string model referencec (see
#   https://github.com/PyCQA/pylint-django#usage)
# - export of migrations for prometheus stats must be disabled,
#   otherwise it's attempted to connect to the db during linting
#   (which is not available)
.PHONY: lint
lint:
	@echo "Run pylint..."
	LOGGING_CFG=0 $(PYLINT) $(PYTHON_FILES)

.PHONY: django-checks
django-checks:
	$(PYTHON) $(DJANGO_MANAGER) check --fail-level WARNING


.PHONY: start-local-db
start-local-db: ## Run the local db as docker container
	docker compose up -d

# Running tests locally
.PHONY: test
test:
	# Collect static first to avoid warning in the test
	# $(PYTHON) $(DJANGO_MANAGER) collectstatic --noinput
	$(PYTHON) $(DJANGO_MANAGER) test --verbosity=2 --parallel 20 $(CI_TEST_OPT) $(TEST_DIR) $(APP_SRC_DIR)

.PHONY: help
help: ## Display this help
# automatically generate the help page based on the documentation after each make target
	@grep -E '^[.a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST)  | sort -k 1,1  | awk 'BEGIN {FS = ":" }; { print $$2":"$$3 }' | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
