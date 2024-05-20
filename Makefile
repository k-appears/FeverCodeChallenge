help:             ## Show this help.
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'


PHONY += build
build:            ## Build the application.
	poetry install

PHONY += dev-build
dev-build: build  ## Build the application for development.
	poetry run pre-commit install -f


PHONY += run-standalone
run-standalone:              ## Run the application
	poetry run uvicorn app.main:app --reload --port 8000


PHONY += run-dependencies
run-dependencies:              ## Run dependencies
	docker compose up -d redis mock-event-service

PHONY += run
run:              ## Run the application
	docker compose up --build

PHONY += test
test:             ## Run tests.
	poetry run pytest -W error::UserWarning -W ignore::DeprecationWarning -vv

PHONY += test-coverage
test-coverage:    ## Run tests with code coverage report in HTML.
	poetry run coverage run -m pytest
	poetry run coverage html

PHONY += test-coverage-ci
test-coverage-ci: ## Run tests with code coverage report in terminal.
	poetry run coverage run -m pytest
	poetry run coverage report

PHONY += lint
lint:             ## Lint files.
	poetry run black .
	poetry run flake8
	poetry run mypy .
