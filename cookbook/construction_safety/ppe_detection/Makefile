# Makefile for PPE Detection Docker Operations
# Usage: make <target>

.PHONY: help build build-dev build-prod start start-dev start-prod stop logs backup restore clean test lint format type-check ci-test deploy install-dev install-hooks

# Default target
.DEFAULT_GOAL := help

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)PPE Detection - Docker Management$(NC)"
	@echo "=================================="
	@echo ""
	@echo "$(GREEN)Available targets:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""

# Setup and Configuration
setup: ## Initial setup - copy .env.example to .env
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "$(GREEN)✓ Created .env file from .env.example$(NC)"; \
		echo "$(YELLOW)⚠ Please edit .env with your configuration$(NC)"; \
	else \
		echo "$(YELLOW)⚠ .env file already exists$(NC)"; \
	fi

check-env: ## Check if .env file exists
	@if [ ! -f .env ]; then \
		echo "$(YELLOW)⚠ .env file not found. Run 'make setup' first$(NC)"; \
		exit 1; \
	fi

# Build targets
build: build-prod ## Build production images (default)

build-dev: ## Build development images
	@echo "$(BLUE)Building development images...$(NC)"
	./scripts/docker/build.sh dev

build-prod: ## Build production images
	@echo "$(BLUE)Building production images...$(NC)"
	./scripts/docker/build.sh production

build-no-cache: ## Build production images without cache
	@echo "$(BLUE)Building production images without cache...$(NC)"
	./scripts/docker/build.sh production --no-cache

# Start targets
start: start-prod ## Start production services (default)

start-dev: check-env ## Start development services
	@echo "$(BLUE)Starting development services...$(NC)"
	./scripts/docker/start.sh dev

start-prod: check-env ## Start production services
	@echo "$(BLUE)Starting production services...$(NC)"
	./scripts/docker/start.sh production

start-monitoring: check-env ## Start services with monitoring (Prometheus & Grafana)
	@echo "$(BLUE)Starting services with monitoring...$(NC)"
	docker-compose --profile monitoring up -d

start-dev-tools: check-env ## Start development tools (PGAdmin, Redis Commander, etc.)
	@echo "$(BLUE)Starting development tools...$(NC)"
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml --profile dev-tools up -d

# Stop targets
stop: ## Stop all services
	@echo "$(BLUE)Stopping services...$(NC)"
	./scripts/docker/stop.sh

stop-volumes: ## Stop services and remove volumes (WARNING: deletes data)
	@echo "$(YELLOW)⚠ This will remove all volumes (databases, caches, etc.)$(NC)"
	./scripts/docker/stop.sh --volumes

# Logs
logs: ## View logs for all services
	./scripts/docker/logs.sh

logs-app: ## View logs for app service
	./scripts/docker/logs.sh app

logs-db: ## View logs for database service
	./scripts/docker/logs.sh db

logs-redis: ## View logs for Redis service
	./scripts/docker/logs.sh redis

logs-celery: ## View logs for Celery worker
	./scripts/docker/logs.sh celery_worker

logs-nginx: ## View logs for Nginx service
	./scripts/docker/logs.sh nginx

# Status and monitoring
ps: ## Show status of all services
	@docker-compose ps

stats: ## Show resource usage statistics
	@docker stats --no-stream

health: ## Check health of all services
	@docker-compose ps | grep -E "(healthy|unhealthy|starting)"

# Database operations
db-shell: ## Access PostgreSQL shell
	@docker-compose exec db psql -U postgres ppe_detection

db-backup: ## Backup database
	@docker-compose exec db pg_dump -U postgres ppe_detection | gzip > backup_$(shell date +%Y%m%d_%H%M%S).sql.gz
	@echo "$(GREEN)✓ Database backup created$(NC)"

db-migrate: ## Run database migrations
	@docker-compose exec app alembic upgrade head

db-migrate-create: ## Create new migration
	@read -p "Migration description: " desc; \
	docker-compose exec app alembic revision --autogenerate -m "$$desc"

# Application shell access
shell-app: ## Access app container shell
	@docker-compose exec app bash

shell-db: ## Access database container shell
	@docker-compose exec db bash

shell-redis: ## Access Redis container shell
	@docker-compose exec redis sh

# Backup and restore
backup: ## Backup all data (database, Redis, files)
	@echo "$(BLUE)Creating backup...$(NC)"
	./scripts/docker/backup.sh

restore: ## Restore from backup (Usage: make restore BACKUP_DIR=./backups/xxx)
	@if [ -z "$(BACKUP_DIR)" ]; then \
		echo "$(YELLOW)Usage: make restore BACKUP_DIR=./backups/ppe_detection_backup_XXXXXX$(NC)"; \
		exit 1; \
	fi
	@echo "$(BLUE)Restoring from backup...$(NC)"
	./scripts/docker/restore.sh $(BACKUP_DIR)

# Cleaning
clean: ## Remove stopped containers
	@docker-compose down --remove-orphans
	@echo "$(GREEN)✓ Removed stopped containers$(NC)"

clean-images: ## Remove unused images
	@docker image prune -f
	@echo "$(GREEN)✓ Removed unused images$(NC)"

clean-volumes: ## Remove unused volumes (WARNING: may delete data)
	@docker volume prune -f
	@echo "$(GREEN)✓ Removed unused volumes$(NC)"

clean-all: stop ## Stop services and clean everything (WARNING: deletes all data)
	@echo "$(YELLOW)⚠ This will remove all containers, images, and volumes$(NC)"
	@read -p "Are you sure? (yes/no): " confirm; \
	if [ "$$confirm" = "yes" ]; then \
		docker-compose down -v --rmi all --remove-orphans; \
		echo "$(GREEN)✓ Cleaned everything$(NC)"; \
	else \
		echo "Cancelled"; \
	fi

# Testing
test: ## Run tests in app container
	@docker-compose exec app pytest

test-coverage: ## Run tests with coverage report
	@docker-compose exec app pytest --cov=src --cov-report=html

# CI/CD Commands (can run locally or in CI)
install-dev: ## Install development dependencies
	@echo "$(BLUE)Installing development dependencies...$(NC)"
	pip install -e ".[dev]"
	@echo "$(GREEN)✓ Development dependencies installed$(NC)"

install-hooks: install-dev ## Install pre-commit hooks
	@echo "$(BLUE)Installing pre-commit hooks...$(NC)"
	pip install pre-commit
	pre-commit install
	pre-commit install --hook-type commit-msg
	@echo "$(GREEN)✓ Pre-commit hooks installed$(NC)"

lint: ## Run all linters (ruff, black check)
	@echo "$(BLUE)Running linters...$(NC)"
	@echo "Checking with Ruff..."
	ruff check src tests
	@echo "Checking formatting with Black..."
	black --check --diff src tests
	@echo "$(GREEN)✓ Linting complete$(NC)"

format: ## Format code with black and isort
	@echo "$(BLUE)Formatting code...$(NC)"
	black src tests
	isort src tests
	@echo "$(GREEN)✓ Code formatted$(NC)"

type-check: ## Run type checking with mypy
	@echo "$(BLUE)Running type checks...$(NC)"
	mypy src --install-types --non-interactive --ignore-missing-imports
	@echo "$(GREEN)✓ Type checking complete$(NC)"

ci-test: ## Run tests locally as CI would (no Docker)
	@echo "$(BLUE)Running tests (CI mode)...$(NC)"
	pytest tests/ -v --cov=src --cov-report=xml --cov-report=term-missing --cov-report=html
	@echo "$(GREEN)✓ Tests complete$(NC)"

security-check: ## Run security checks
	@echo "$(BLUE)Running security checks...$(NC)"
	@echo "Checking dependencies with Safety..."
	safety check || true
	@echo "Checking code with Bandit..."
	bandit -r src || true
	@echo "$(GREEN)✓ Security check complete$(NC)"

pre-commit-all: ## Run all pre-commit hooks on all files
	@echo "$(BLUE)Running pre-commit on all files...$(NC)"
	pre-commit run --all-files
	@echo "$(GREEN)✓ Pre-commit complete$(NC)"

ci-full: lint type-check ci-test security-check ## Run all CI checks locally
	@echo "$(GREEN)✓ All CI checks passed!$(NC)"

deploy: ## Deploy application (requires configuration)
	@echo "$(BLUE)Deploying application...$(NC)"
	@echo "$(YELLOW)Note: Configure deployment target in CI/CD or environment$(NC)"
	# Add deployment commands here

# Scaling
scale-app: ## Scale app service (Usage: make scale-app REPLICAS=3)
	@if [ -z "$(REPLICAS)" ]; then \
		echo "$(YELLOW)Usage: make scale-app REPLICAS=3$(NC)"; \
		exit 1; \
	fi
	@docker-compose up -d --scale app=$(REPLICAS)
	@echo "$(GREEN)✓ Scaled app service to $(REPLICAS) replicas$(NC)"

scale-celery: ## Scale Celery worker (Usage: make scale-celery REPLICAS=3)
	@if [ -z "$(REPLICAS)" ]; then \
		echo "$(YELLOW)Usage: make scale-celery REPLICAS=3$(NC)"; \
		exit 1; \
	fi
	@docker-compose up -d --scale celery_worker=$(REPLICAS)
	@echo "$(GREEN)✓ Scaled Celery worker to $(REPLICAS) replicas$(NC)"

# Development helpers
dev-rebuild: ## Rebuild and restart development environment
	@$(MAKE) build-dev
	@$(MAKE) start-dev

prod-rebuild: ## Rebuild and restart production environment
	@$(MAKE) build-no-cache
	@$(MAKE) start-prod

restart: ## Restart all services
	@docker-compose restart

restart-app: ## Restart only app service
	@docker-compose restart app

# Quick commands
up: start ## Alias for start

down: stop ## Alias for stop

# Installation and first-time setup
install: setup build-prod ## Complete first-time installation
	@echo ""
	@echo "$(GREEN)✓ Installation complete!$(NC)"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Edit .env with your configuration"
	@echo "  2. Run: make start"
	@echo "  3. Access API at http://localhost:8000"
	@echo ""

install-dev: setup build-dev ## Complete first-time development installation
	@echo ""
	@echo "$(GREEN)✓ Development installation complete!$(NC)"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Edit .env with your configuration"
	@echo "  2. Run: make start-dev"
	@echo "  3. Access API at http://localhost:8000"
	@echo ""

# Update
update: ## Pull latest changes and rebuild
	@git pull
	@$(MAKE) build-no-cache
	@$(MAKE) restart
	@echo "$(GREEN)✓ Update complete!$(NC)"

# Documentation
docs: ## Open deployment documentation
	@if command -v xdg-open > /dev/null; then \
		xdg-open docs/DOCKER_DEPLOYMENT.md; \
	elif command -v open > /dev/null; then \
		open docs/DOCKER_DEPLOYMENT.md; \
	else \
		cat docs/DOCKER_DEPLOYMENT.md; \
	fi
