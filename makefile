check: check.linting check.types

check.types:
	mypy --ignore-missing-imports edfpy

check.linting:
	flake8

install.dev: install
	pip install -e .
	pip install -r requirements-dev.txt

install:
	pip install .
