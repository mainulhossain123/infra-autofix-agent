.PHONY: help build up down logs clean test demo restart

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

build: ## Build all Docker images
	docker compose build

up: ## Start all services
	docker compose up -d

down: ## Stop all services
	docker compose down

logs: ## View logs from all services
	docker compose logs -f

logs-app: ## View app logs only
	docker compose logs -f app

logs-bot: ## View bot logs only
	docker compose logs -f bot

clean: ## Remove all containers, volumes, and images
	docker compose down -v --rmi all

restart: ## Restart all services
	docker compose restart

restart-app: ## Restart app service only
	docker compose restart app

test: ## Run tests
	docker compose exec app pytest tests/ -v

demo: ## Run demo scenarios
	@echo "Running demo scenarios..."
	bash scripts/demo.sh

psql: ## Connect to PostgreSQL database
	docker compose exec postgres psql -U remediation_user -d remediation_db

dev: ## Start services with build and follow logs
	docker compose up --build

status: ## Show status of all services
	docker compose ps
