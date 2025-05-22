# Variables
CHECKFILES = ./app ./tests
PY_WARN = PYTHONDEVMODE=1

# Help
help:
	@echo "Project Development Makefile"
	@echo
	@echo "Usage: make <target>"
	@echo "Targets:"
	@echo "    setup               Install dependencies and pre-commit hooks"
	@echo "    style               Run ruff format and check"
	@echo "    test [path=dir]     Run tests with coverage"
	@echo
	@echo "Examples:"
	@echo "    make setup"
	@echo "    make style"
	@echo "    make test"
	@echo "    make test path=tests/test_settings.py"


# Environment Setup with Hooks
setup:
	@set -e; \
	echo "Setting up the environment..."; \
	if ! command -v uv > /dev/null; then \
		echo "'uv' is not installed. Installing..."; \
		pip install uv; \
	fi; \
	pip install --upgrade pip; \
	uv sync; \
	echo "Installing pre-commit hooks..."; \
	mkdir -p .git/hooks; \
	echo '#!/bin/bash' > .git/hooks/pre-commit; \
	echo 'set -e' >> .git/hooks/pre-commit; \
	echo 'uv run ruff format --check . || (echo "Whoa there! Your code is uglier than my first Hello World program. Fix it, please..." && exit 1)' >> .git/hooks/pre-commit; \
	echo 'uv run ruff check . || (echo "Oof, your code smells like a wet sock. Clean it up!" && exit 1)' >> .git/hooks/pre-commit; \
	echo 'uv run mypy . || (echo "Type errors? Seriously? Its like you forgot Python even has types. Oh wait..." && exit 1)' >> .git/hooks/pre-commit; \
	echo 'exit 0' >> .git/hooks/pre-commit; \
	chmod +x .git/hooks/pre-commit; \
	echo "Pre-commit hooks installed successfully!"; \
	echo "Setup complete! To activate the environment, use: source .venv/bin/activate"


# Run Tests
test:
	@set -e; \
	echo "Starting tests... Buckle up!"; \
	echo "Running tests with coverage..."; \
	$(PY_WARN) uv run coverage run -m pytest $(path) || (echo "Tests failed like a bad soufflé. Check your errors and try again." && exit 1); \
	echo "Generating coverage report..."; \
	uv run coverage report --omit="tests/**/*.py,app/telemetry/classes.py" --show-missing --skip-covered --fail-under=98 || (echo "Uh oh! Coverage is below 98%. Write more tests or hire an intern." && exit 1); \
	echo "Validating the tests coverage..."; \
	uv run coverage report --include="tests/**/test_*.py" --show-missing --skip-covered --fail-under=100 || (echo "Uh oh! Test coverage is below 100%. Make sure all lines of the tests are covered." && exit 1); \
	echo "Checking for lint issues with ruff..."; \
	uv run ruff check $(CHECKFILES) || (echo "Your code's looking a bit... *ruff*. Fix those lint issues!" && exit 1); \
	echo "Checking code formatting..."; \
	uv run ruff format --check $(CHECKFILES) || (echo "Your formatting is as wild as a 3AM coding spree. Tidy it up!" && exit 1); \
	echo "Running mypy for type checks..."; \
	uv run mypy $(CHECKFILES) || (echo "Types are all over the place. Did you forget type hints existed?" && exit 1); \
	rm -f .coverage; \
	echo "All tests passed! You have the Gandalf approve! 🧙"


# Run styling
style:
	@echo "Formatting code with ruff..."
	@uv run ruff format $(CHECKFILES)
	@echo "Checking code with ruff and attempting to fix..."
	@uv run ruff check $(CHECKFILES) --fix
