.PHONY: setup dev clean test lint format check help

help:
	@echo "GRC - Glorified Rectangle Creator"
	@echo ""
	@echo "Usage:"
	@echo "  make setup    Create virtual environment and install dependencies (using UV)"
	@echo "  make dev      Start the GRC application"
	@echo "  make lint     Run Ruff linter to check code"
	@echo "  make format   Run Ruff formatter to format code"
	@echo "  make check    Run both lint and format check"
	@echo "  make test     Run the test suite"
	@echo "  make clean    Remove virtual environment and cache files"
	@echo "  make help     Show this help message"

setup:
	@echo "Setting up environment with UV..."
	@uv venv
	@uv pip install -e ".[dev]"
	@echo "Setup complete. Run 'make dev' to start the application."

dev:
	@uv run python -m grc.main

lint:
	@echo "Running Ruff linter..."
	@uv run ruff check src/ tests/

format:
	@echo "Running Ruff formatter..."
	@uv run ruff format src/ tests/

check: lint
	@echo "Checking formatting..."
	@uv run ruff format --check src/ tests/

clean:
	@echo "Cleaning up..."
	@rm -rf .venv venv/ __pycache__/ .pytest_cache/ .mypy_cache/ .ruff_cache/ *.egg-info
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@echo "Clean complete."

test:
	@uv run pytest tests/ -v
