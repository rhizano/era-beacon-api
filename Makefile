.PHONY: help install dev test clean docker-build docker-up docker-down migrate

help:
	@echo "Available commands:"
	@echo "  install     - Install dependencies"
	@echo "  dev         - Run development server"
	@echo "  test        - Run tests"
	@echo "  clean       - Clean cache files"
	@echo "  docker-build - Build Docker image"
	@echo "  docker-up   - Start services with Docker Compose"
	@echo "  docker-down - Stop Docker Compose services"
	@echo "  migrate     - Run database migrations"

install:
	pip install -r requirements.txt

dev:
	python run_dev.py

test:
	pytest

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +

docker-build:
	docker build -t era-beacon-api .

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

migrate:
	alembic upgrade head

create-migration:
	alembic revision --autogenerate -m "$(message)"
