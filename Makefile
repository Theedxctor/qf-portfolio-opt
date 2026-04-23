# Makefile for QF Portfolio Optimization

.PHONY: lint format type-check clean-code

# Format code according to standards
format:
	isort .
	black .

# Check for style violations
lint:
	flake8 . --count --exclude=venv,postgres_data --select=E9,F63,F7,F82 --show-source --statistics
	flake8 . --count --exclude=venv,postgres_data --exit-zero --max-complexity=10 --max-line-length=127 --ignore=E203,W503 --statistics

# Check static types
type-check:
	mypy . --ignore-missing-imports --explicit-package-bases --exclude venv

# Run everything at once
clean-code: format lint type-check