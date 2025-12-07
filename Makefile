.PHONY: help setup test lint format run-receiver run-consumer docker-build docker-up docker-down migrate install-hooks

help:
	@echo "Device Metrics Microservice - Available commands:"
	@echo "  make setup          - Set up development environment"
	@echo "  make install-hooks - Install pre-commit hooks"
	@echo "  make test           - Run tests"
	@echo "  make lint           - Run linters"
	@echo "  make format         - Auto-format code"
	@echo "  make run-receiver   - Start FastAPI receiver"
	@echo "  make run-consumer   - Start Kafka consumer"
	@echo "  make docker-up      - Start infrastructure services"
	@echo "  make docker-down    - Stop infrastructure services"
	@echo "  make migrate        - Run database migrations"
	@echo "  make docker-build   - Build Docker image"

setup:
	bash scripts/setup.sh

test:
	pytest tests/ -v --cov=src --cov-report=term

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
