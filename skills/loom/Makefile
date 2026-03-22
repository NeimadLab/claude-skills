.PHONY: install dev lint test clean

install:  ## Install Loom in the current environment
	pip install -e .

dev:  ## Install with dev dependencies
	pip install -e ".[dev]"

lint:  ## Run linter
	ruff check src/ tests/
	ruff format --check src/ tests/

format:  ## Auto-format code
	ruff format src/ tests/

test:  ## Run tests
	pytest tests/ -v

test-unit:  ## Run unit tests only
	pytest tests/unit/ -v

clean:  ## Clean build artifacts
	rm -rf build/ dist/ *.egg-info src/*.egg-info .ruff_cache .pytest_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
