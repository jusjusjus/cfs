check: check.linting check.types check.units

check.units:
	CI=1 python -m pytest -x

check.types:
	mypy --ignore-missing-imports cfs

check.linting:
	flake8 cfs/ tests/

install.dev: install
	pip install -e .
	pip install -r requirements-dev.txt

install:
	pip install .
