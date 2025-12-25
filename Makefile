.PHONY: help install install-dev test lint format clean build upload docs

# Default target
help:
	@echo "PyDevToolkit MagicCLI - Available commands:"
	@echo ""
	@echo "Installation & Setup:"
	@echo "  install      Install the package in development mode"
	@echo "  install-dev  Install with development dependencies"
	@echo ""
	@echo "Testing & Quality:"
	@echo "  test         Run the test suite"
	@echo "  lint         Run code linting and formatting checks"
	@echo "  format       Format code with black and isort"
	@echo "  check-all    Run all checks (format, lint, test)"
	@echo ""
	@echo "Building & Publishing:"
	@echo "  clean        Clean build artifacts"
	@echo "  build        Build the package"
	@echo "  upload       Upload to PyPI (requires credentials)"
	@echo "  upload-test  Upload to Test PyPI"
	@echo ""
	@echo "Version Management:"
	@echo "  bump-major   Bump major version (X.0.0)"
	@echo "  bump-minor   Bump minor version (x.X.0)"
	@echo "  bump-patch   Bump patch version (x.x.X)"
	@echo "  release-*    Bump version, commit, tag, and push"
	@echo ""
	@echo "Development:"
	@echo "  run          Run the application directly"
	@echo "  docs         Generate documentation"
	@echo "  audit        Run security audit"
	@echo ""

# Installation
install:
	pip install -e .

install-dev:
	pip install -e ".[dev,test]"
	pre-commit install

# Testing
test:
	python -m pytest tests/ -v --cov=src --cov-report=term-missing

test-integration:
	python -m pytest tests/integration/ -v

test-unit:
	python -m pytest tests/unit/ -v

# Code quality
lint:
	flake8 src/ tests/
	mypy src/
	bandit -r src/
	safety check

format:
	black src/ tests/
	isort src/ tests/

format-check:
	black --check src/ tests/
	isort --check-only src/ tests/

# Cleaning
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

# Building and distribution
build: clean
	python -m build

upload: build
	python -m twine upload dist/*

upload-test: build
	python -m twine upload --repository testpypi dist/*

# Version management
bump-major:
	python scripts/bump_version.py major

bump-minor:
	python scripts/bump_version.py minor

bump-patch:
	python scripts/bump_version.py patch

release-major: bump-major
	git add .
	git commit -m "Bump version to $(shell python -c "import re; print(re.search(r'version = \"([^\"]+)\"', open('pyproject.toml').read()).group(1))")"
	git tag v$(shell python -c "import re; print(re.search(r'version = \"([^\"]+)\"', open('pyproject.toml').read()).group(1))")
	git push && git push --tags

release-minor: bump-minor
	git add .
	git commit -m "Bump version to $(shell python -c "import re; print(re.search(r'version = \"([^\"]+)\"', open('pyproject.toml').read()).group(1))")"
	git tag v$(shell python -c "import re; print(re.search(r'version = \"([^\"]+)\"', open('pyproject.toml').read()).group(1))")
	git push && git push --tags

release-patch: bump-patch
	git add .
	git commit -m "Bump version to $(shell python -c "import re; print(re.search(r'version = \"([^\"]+)\"', open('pyproject.toml').read()).group(1))")"
	git tag v$(shell python -c "import re; print(re.search(r'version = \"([^\"]+)\"', open('pyproject.toml').read()).group(1))")
	git push && git push --tags

# Documentation
docs:
	@echo "Documentation generation not yet implemented"
	@echo "Consider adding Sphinx with RDT theme"

# Development helpers
run:
	python src/main.py

dev:
	python -m src.main

# Security audit
audit:
	safety check
	bandit -r src/

# All checks (used in CI)
check-all: format-check lint test
	@echo "All checks passed!"