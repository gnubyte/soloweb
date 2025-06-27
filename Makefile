.PHONY: help install install-dev test test-cov lint format clean build dist upload upload-github docs

help: ## Show this help message
	@echo "Soloweb - Production-Grade Async Web Framework"
	@echo "=============================================="
	@echo ""
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install the package in development mode
	pip install -e .

install-dev: ## Install development dependencies
	pip install -e ".[dev]"

test: ## Run tests
	PYTHONPATH=. python3 tests/test_soloweb.py

test-cov: ## Run tests with coverage
	python -m pytest tests/ -v --cov=soloweb --cov-report=html --cov-report=term-missing

lint: ## Run linting checks
	flake8 soloweb/ tests/ example_app.py
	mypy soloweb/

format: ## Format code with black and isort
	black soloweb/ tests/ example_app.py setup.py
	isort soloweb/ tests/ example_app.py setup.py

clean: ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

build: clean ## Build the package
	python3 setup.py sdist bdist_wheel

dist: build ## Create distribution packages
	@echo "Distribution packages created in dist/"

upload: dist ## Upload to PyPI (requires twine)
	twine upload dist/*

upload-test: dist ## Upload to TestPyPI
	twine upload --repository testpypi dist/*

upload-github: ## Upload to GitHub releases (requires GitHub CLI)
	@echo "Uploading to GitHub releases..."
	@if ! command -v gh &> /dev/null; then \
		echo "GitHub CLI (gh) is not installed. Please install it first:"; \
		echo "  macOS: brew install gh"; \
		echo "  Ubuntu: sudo apt install gh"; \
		echo "  Or visit: https://cli.github.com/"; \
		exit 1; \
	fi
	@if ! gh auth status &> /dev/null; then \
		echo "GitHub CLI is not authenticated. Please run: gh auth login"; \
		exit 1; \
	fi
	./upload_release.sh

docs: ## Build documentation
	cd docs && make html

check: format lint test ## Run all checks (format, lint, test)

release: check build upload ## Full release process

release-github: check build upload-github ## Full GitHub release process

example: ## Run the example application
	PYTHONPATH=. python3 example_app.py

cli-test: ## Test the CLI
	soloweb --version
	soloweb --help

version: ## Show current version
	@python3 -c "import soloweb; print(soloweb.__version__)"

bump-version: ## Bump version (usage: make bump-version VERSION=1.1.0)
	@if [ -z "$(VERSION)" ]; then \
		echo "Usage: make bump-version VERSION=1.1.0"; \
		exit 1; \
	fi
	@echo "Bumping version to $(VERSION)..."
	@sed -i '' 's/__version__ = ".*"/__version__ = "$(VERSION)"/' soloweb/__init__.py
	@echo "Version bumped to $(VERSION)"
	@echo "Don't forget to update CHANGELOG.md and commit the changes!" 