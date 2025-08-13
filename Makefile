# Makitox Platform Makefile
.PHONY: start install test docker clean help

# Default target
.DEFAULT_GOAL := help

# Colors for output
CYAN = \033[36m
GREEN = \033[32m
YELLOW = \033[33m
RED = \033[31m
NC = \033[0m # No Color

help: ## Show this help message
	@echo "$(CYAN)🌟 Makitox Platform Commands$(NC)"
	@echo "================================"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-15s$(NC) %s\n", $$1, $$2}'

start: ## Start the Makitox platform server
	@echo "$(CYAN)🚀 Starting Makitox Platform...$(NC)"
	@python server.py

install: ## Install dependencies
	@echo "$(CYAN)📦 Installing dependencies...$(NC)"
	@pip install -r api/requirements.txt
	@echo "$(GREEN)✅ Dependencies installed$(NC)"

test: ## Run integration tests
	@echo "$(CYAN)🧪 Running integration tests...$(NC)"
	@python api/test_integration.py

status: ## Check server status
	@curl -s http://localhost:8000/api/status | python -m json.tool

dev: ## Start in development mode
	@echo "$(CYAN)💻 Starting development server...$(NC)"
	@python start.py

restart: ## Restart the server (stop and start)
	@echo "$(YELLOW)🔄 Restarting server...$(NC)"
	@pkill -f "python server.py" || true
	@sleep 2
	@$(MAKE) start

quick: ## Quick start (install + start)
	@$(MAKE) install
	@$(MAKE) start

urls: ## Show all available URLs
	@echo "$(CYAN)📍 Makitox Platform URLs:$(NC)"
	@echo "$(GREEN)🌐 Website:     $(NC)http://localhost:8000"
	@echo "$(GREEN)🔌 API:         $(NC)http://localhost:8000/api"
	@echo "$(GREEN)📊 Gold Prices: $(NC)http://localhost:8000/api/gold-prices/yearly"
	@echo "$(GREEN)💊 Health:      $(NC)http://localhost:8000/api/status"
	@echo "$(GREEN)📚 API Docs:    $(NC)http://localhost:8000/docs"