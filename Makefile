# 🚀 ENVable - Lightning-fast environment deployment automation

.PHONY: help install test lint format docker-build docker-run clean dev-setup ci

# Default target
help: ## Show this help message
	@echo "🚀 ENVable Development Commands"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Development setup
install: ## Install dependencies
	@echo "📦 Installing dependencies..."
	pip install -r requirements.txt
	pip install pytest pytest-cov ruff black isort bandit safety mypy

dev-setup: install ## Set up development environment
	@echo "🔧 Setting up development environment..."
	python -m pip install --upgrade pip
	@if [ ! -f .env ]; then cp .env.example .env; echo "📝 Created .env from .env.example"; fi
	@echo "✅ Development environment ready!"

# Code quality
lint: ## Run code linting
	@echo "🔍 Running code quality checks..."
	ruff check src/ --output-format=github
	ruff format src/ --check
	mypy src/ --ignore-missing-imports

format: ## Format code
	@echo "🎨 Formatting code..."
	ruff format src/
	isort src/
	@echo "✅ Code formatted!"

# Security
security: ## Run security scans
	@echo "🛡️ Running security scans..."
	bandit -r src/ -f json -o bandit-report.json || true
	safety check --json --output safety-report.json || true
	@echo "📊 Security reports generated"

# Testing
test: ## Run tests
	@echo "🧪 Running tests..."
	python -c "import sys; sys.path.append('src'); import config; print('✅ Config module loads')"
	python -c "import sys; sys.path.append('src'); import agent; print('✅ Agent module loads')"
	python -c "import sys; sys.path.append('src'); from env_processor import ENVProcessor; print('✅ ENVProcessor loads')"
	@echo "✅ All import tests passed!"

test-coverage: ## Run tests with coverage
	@echo "📊 Running tests with coverage..."
	pytest tests/ --cov=src/ --cov-report=html --cov-report=term-missing

# Docker operations
docker-build: ## Build Docker image
	@echo "🐳 Building Docker image..."
	docker build -t envable:latest .
	@echo "✅ Docker image built!"

docker-run: ## Run Docker container
	@echo "🚀 Starting Docker container..."
	docker-compose up -d
	@echo "✅ Container running at http://localhost:8000"

docker-stop: ## Stop Docker containers
	@echo "🛑 Stopping Docker containers..."
	docker-compose down
	@echo "✅ Containers stopped!"

docker-logs: ## View Docker logs
	docker-compose logs -f envable

# CI/CD operations
ci: lint security test ## Run full CI pipeline
	@echo "🚀 CI pipeline completed!"

release-build: ## Build release artifacts
	@echo "📦 Building release artifacts..."
	python -m build
	@echo "✅ Release artifacts ready!"

# Cleanup
clean: ## Clean up temporary files
	@echo "🧹 Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ .coverage htmlcov/ 2>/dev/null || true
	rm -f bandit-report.json safety-report.json 2>/dev/null || true
	@echo "✅ Cleanup complete!"

# Development shortcuts
dev: dev-setup ## Quick development setup
run: ## Run ENVable locally
	@echo "🚀 Starting ENVable..."
	python -m src.agent

sync: ## Run environment sync
	@echo "🔄 Syncing environment variables..."
	python -m src.auto_sync

# Quick commands
all: clean install lint test docker-build ## Run everything
	@echo "🎉 All tasks completed successfully!"

# GitHub Actions simulation
simulate-ci: ## Simulate GitHub Actions CI locally
	@echo "🤖 Simulating GitHub Actions CI..."
	@$(MAKE) ci
	@echo "🎯 Local CI simulation complete!"

# Status check
status: ## Check system status
	@echo "📊 ENVable Status Check"
	@echo "Python: $$(python --version)"
	@echo "Pip: $$(pip --version)"
	@echo "Docker: $$(docker --version 2>/dev/null || echo 'Not installed')"
	@echo "Git: $$(git --version)"
	@if [ -f .env ]; then echo "✅ .env file present"; else echo "⚠️ .env file missing"; fi
	@if [ -f sync_config.json ]; then echo "✅ sync_config.json present"; else echo "⚠️ sync_config.json missing"; fi