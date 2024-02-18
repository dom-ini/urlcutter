.DEFAULT_GOAL := all

bandit:
	poetry run bandit -r . -x ./app/static
toml_sort:
	poetry run toml-sort pyproject.toml --all --in-place
flake8:
	poetry run flake8 .
isort:
	poetry run isort .
black:
	poetry run black .
lint: black flake8 isort toml_sort
