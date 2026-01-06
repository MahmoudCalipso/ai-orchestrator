.PHONY: help install setup run test clean docker-build docker-up docker-down lint format

help:
	@echo "AI Orchestrator - Make Commands"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make install       - Install dependencies"
	@echo "  make setup         - Run full setup"
	@echo ""
	@echo "Development:"
	@echo "  make run           - Start the orchestrator"
	@echo "  make run-dev       - Start with auto-reload"
	@echo "  make test          - Run tests"
	@echo "  make lint          - Run linters"
	@echo "  make format        - Format code"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build  - Build Docker image"
	@echo "  make docker-up     - Start Docker containers"
	@echo "  make docker-down   - Stop Docker containers"
	@echo "  make docker-logs   - View Docker logs"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean         - Clean temporary files"
	@echo "  make clean-all     - Clean everything including venv"

install:
	@echo "Installing dependencies..."
	pip install -r requirements.txt

setup:
	@echo "Running setup..."
	chmod +x setup.sh
	./setup.sh

run:
	@echo "Starting orchestrator..."
	chmod +x run.sh
	./run.sh

run-dev:
	@echo "Starting orchestrator in development mode..."
	chmod +x run.sh
	./run.sh --reload

test:
	@echo "Running tests..."
	pytest tests/ -v --cov=. --cov-report=html --cov-report=term

test-integration:
	@echo "Running integration tests..."
	pytest tests/ -v -m integration

lint:
	@echo "Running linters..."
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

format:
	@echo "Formatting code..."
	black .
	isort .

docker-build:
	@echo "Building Docker image..."
	docker-compose build

docker-up:
	@echo "Starting Docker containers..."
	docker-compose up -d

docker-down:
	@echo "Stopping Docker containers..."
	docker-compose down

docker-logs:
	@echo "Viewing Docker logs..."
	docker-compose logs -f

docker-restart:
	@echo "Restarting Docker containers..."
	docker-compose restart

clean:
	@echo "Cleaning temporary files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.coverage" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage

clean-all: clean
	@echo "Cleaning everything..."
	rm -rf venv
	rm -rf logs/*
	rm -rf cache/*

init-dirs:
	@echo "Creating directories..."
	mkdir -p models logs cache config

check-ollama:
	@echo "Checking Ollama..."
	@curl -s http://localhost:11434/api/tags > /dev/null && echo "✓ Ollama is running" || echo "✗ Ollama is not running"

pull-models:
	@echo "Pulling models..."
	ollama pull mistral
	ollama pull phi3
	@echo "Models pulled successfully"

health:
	@echo "Checking health..."
	@curl -s http://localhost:8080/health | python -m json.tool

status:
	@echo "Getting system status..."
	@curl -s http://localhost:8080/status -H "X-API-Key: dev-key-12345" | python -m json.tool

models:
	@echo "Listing models..."
	@curl -s http://localhost:8080/models -H "X-API-Key: dev-key-12345" | python -m json.tool

benchmark:
	@echo "Running benchmark..."
	python -c "import asyncio; from agents.test_agent import TestAgent; from core.orchestrator import Orchestrator; \
	async def run(): \
		orch = Orchestrator(); \
		await orch.initialize(); \
		agent = TestAgent(orch); \
		result = await agent.benchmark_performance(10); \
		print(result); \
		await orch.shutdown(); \
	asyncio.run(run())"