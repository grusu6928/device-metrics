.PHONY: help setup test lint format run-receiver run-consumer docker-build docker-up docker-down migrate install-hooks ci check commitlint security-scan

help:
	@echo "Device Metrics Microservice - Available commands:"
	@echo "  make setup          - Set up development environment"
	@echo "  make install-hooks - Install pre-commit hooks"
	@echo "  make test           - Run tests"
	@echo "  make lint           - Run linters"
	@echo "  make format         - Auto-format code"
	@echo "  make ci             - Run all CI checks (lint, test, security)"
	@echo "  make check          - Run all checks before commit (lint + test)"
	@echo "  make commitlint     - Validate commit messages"
	@echo "  make security-scan  - Run security scans (Trivy, Bandit)"
	@echo "  make run-receiver   - Start FastAPI receiver"
	@echo "  make run-consumer   - Start Kafka consumer"
	@echo "  make docker-up      - Start infrastructure services"
	@echo "  make docker-down    - Stop infrastructure services"
	@echo "  make migrate        - Run database migrations"
	@echo "  make docker-build   - Build Docker image"

setup:
	bash scripts/setup.sh

test:
	@echo "Running tests (same as CI)..."
	@export DATABASE_URL="$${DATABASE_URL:-sqlite:///./test.db}" && pytest tests/ -v --cov=src --cov-report=term

install-hooks:
	pre-commit install
	pre-commit install --hook-type commit-msg

lint:
	pre-commit run --all-files

format:
	black src tests
	isort src tests

run-receiver:
	uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

run-consumer:
	python -m src.consumer.main

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

migrate:
	alembic upgrade head

migrate-create:
	@read -p "Migration message: " msg; \
	alembic revision --autogenerate -m "$$msg"

docker-build:
	docker build -t device-metrics:latest .

# CI/CD Checks
ci: lint test security-scan
	@echo "✅ All CI checks passed!"

check: lint test
	@echo "✅ All pre-commit checks passed!"

commitlint:
	@echo "Validating commit messages..."
	@if [ -z "$$(git rev-parse --verify HEAD 2>/dev/null)" ]; then \
		echo "No commits to validate"; \
	else \
		base=$$(git merge-base HEAD origin/main 2>/dev/null || git rev-list --max-parents=0 HEAD | head -1); \
		head=$$(git rev-parse HEAD); \
		for commit in $$(git rev-list $$base..$$head); do \
			commit_subject=$$(git log -1 --format=%s $$commit); \
			echo "Validating commit: $$(echo $$commit | cut -c1-7)"; \
			tmp_file=$$(mktemp); \
			echo "$$commit_subject" > "$$tmp_file"; \
			pre-commit run --hook-stage commit-msg --commit-msg-filename "$$tmp_file" conventional-pre-commit || { \
				echo "❌ Commit $$(echo $$commit | cut -c1-7) does not follow conventional commit format"; \
				echo "Message: $$commit_subject"; \
				rm -f "$$tmp_file"; \
				exit 1; \
			}; \
			rm -f "$$tmp_file"; \
		done; \
		echo "✅ All commits follow conventional commit format"; \
	fi

security-scan:
	@echo "Running security scans..."
	@if command -v trivy >/dev/null 2>&1; then \
		echo "Running Trivy scan..."; \
		trivy fs --severity HIGH,CRITICAL . || true; \
	else \
		echo "⚠️  Trivy not installed. Install with: brew install trivy (macOS) or see https://aquasecurity.github.io/trivy/"; \
	fi
	@if command -v bandit >/dev/null 2>&1; then \
		echo "Running Bandit scan..."; \
		pip install bandit >/dev/null 2>&1 || true; \
		bandit -r src -f json -o bandit-report.json || true; \
		echo "Bandit scan complete. See bandit-report.json"; \
	else \
		echo "⚠️  Bandit not installed. Install with: pip install bandit"; \
	fi

# Enhanced linting (matches CI)
lint-ci:
	@echo "Running CI-style linting..."
	python -m pip install --upgrade pip >/dev/null 2>&1 || true
	pip install flake8 black isort mypy >/dev/null 2>&1 || true
	@echo "Linting with flake8..."
	flake8 src tests --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 src tests --count --exit-zero --max-complexity=10 --max-line-length=100 --statistics
	@echo "Type checking with mypy..."
	mypy src --ignore-missing-imports || true
	@echo "Checking code formatting with black..."
	black --check src tests
	@echo "Checking import sorting with isort..."
	isort --check-only src tests
	@echo "✅ Linting complete!"

# Test with coverage (matches CI exactly)
test-ci:
	@echo "Running tests with coverage (CI mode)..."
	@export DATABASE_URL="$${DATABASE_URL:-sqlite:///./test.db}" && pytest tests/ -v --cov=src --cov-report=xml --cov-report=term --cov-report=html
	@echo "✅ Tests complete! Coverage report in htmlcov/index.html"
