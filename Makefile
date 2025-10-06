.PHONY: help devops-up devops-down devops-check devops-logs devops-restart
.PHONY: test-backend test-frontend test-all lint-backend lint-frontend lint-all
.PHONY: build-backend build-frontend build-all
.PHONY: k8s-deploy k8s-status k8s-logs k8s-rollback
.PHONY: metrics-export billing-run clean

.DEFAULT_GOAL := help

##@ General

help: ## Display this help message
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Development

devops-up: ## Start all services (docker-compose)
	@echo "🚀 Starting DocuChat services..."
	cd infra && docker-compose up -d
	@echo ""
	@echo "✅ Services started successfully!"
	@echo ""
	@echo "📍 Access URLs:"
	@echo "   Frontend:   http://localhost:3000"
	@echo "   Backend:    http://localhost:8000"
	@echo "   API Docs:   http://localhost:8000/docs"
	@echo "   Prometheus: http://localhost:9090"
	@echo "   Grafana:    http://localhost:3001 (admin/admin)"
	@echo ""
	@echo "💡 Tip: Run 'make devops-logs' to see logs"

devops-down: ## Stop all services
	@echo "🛑 Stopping DocuChat services..."
	cd infra && docker-compose down
	@echo "✅ Services stopped"

devops-restart: ## Restart all services
	@echo "🔄 Restarting DocuChat services..."
	cd infra && docker-compose restart
	@echo "✅ Services restarted"

devops-check: ## Check health of all services
	@echo "🏥 Checking service health..."
	@echo ""
	@printf "Backend:    "
	@curl -sf http://localhost:8000/api/v1/health > /dev/null && echo "✅ Healthy" || echo "❌ Unhealthy"
	@printf "Metrics:    "
	@curl -sf http://localhost:8000/api/v1/metrics > /dev/null && echo "✅ Available" || echo "❌ Unavailable"
	@printf "Prometheus: "
	@curl -sf http://localhost:9090/-/healthy > /dev/null && echo "✅ Healthy" || echo "❌ Unhealthy"
	@printf "Grafana:    "
	@curl -sf http://localhost:3001/api/health > /dev/null && echo "✅ Healthy" || echo "❌ Unhealthy"

devops-logs: ## Show logs from all services
	cd infra && docker-compose logs -f

devops-logs-backend: ## Show backend logs only
	cd infra && docker-compose logs -f backend

devops-logs-frontend: ## Show frontend logs only
	cd infra && docker-compose logs -f frontend

##@ Testing

test-backend: ## Run backend tests
	@echo "🧪 Running backend tests..."
	cd backend && pytest tests/ -v --cov=app --cov-report=term-missing

test-frontend: ## Run frontend tests
	@echo "🧪 Running frontend tests..."
	cd frontend && pnpm test

test-all: test-backend test-frontend ## Run all tests
	@echo "✅ All tests completed"

##@ Linting

lint-backend: ## Lint backend code
	@echo "🔍 Linting backend code..."
	cd backend && ruff check app/
	cd backend && ruff format --check app/

lint-frontend: ## Lint frontend code
	@echo "🔍 Linting frontend code..."
	cd frontend && pnpm exec tsc --noEmit

lint-all: lint-backend lint-frontend ## Lint all code
	@echo "✅ Linting completed"

format-backend: ## Format backend code
	@echo "✨ Formatting backend code..."
	cd backend && ruff format app/

##@ Building

build-backend: ## Build backend Docker image
	@echo "🏗️  Building backend Docker image..."
	docker build -t docuchat/backend:local backend/
	@echo "✅ Backend image built: docuchat/backend:local"

build-frontend: ## Build frontend Docker image
	@echo "🏗️  Building frontend Docker image..."
	docker build -t docuchat/frontend:local frontend/
	@echo "✅ Frontend image built: docuchat/frontend:local"

build-all: build-backend build-frontend ## Build all Docker images
	@echo "✅ All images built"

##@ Kubernetes

k8s-deploy: ## Deploy to Kubernetes using Helm
	@echo "🚀 Deploying to Kubernetes..."
	helm upgrade --install docuchat ./infra/chart \
		--namespace docuchat-prod \
		--create-namespace \
		-f infra/chart/values.yaml
	@echo "✅ Deployment completed"

k8s-status: ## Check Kubernetes deployment status
	@echo "📊 Kubernetes deployment status:"
	@echo ""
	kubectl get pods -n docuchat-prod
	@echo ""
	kubectl get svc -n docuchat-prod
	@echo ""
	kubectl get ingress -n docuchat-prod

k8s-logs: ## Show logs from Kubernetes pods
	@echo "📝 Backend logs:"
	kubectl logs -l app.kubernetes.io/component=backend -n docuchat-prod --tail=50

k8s-logs-follow: ## Follow logs from backend pods
	kubectl logs -l app.kubernetes.io/component=backend -n docuchat-prod -f

k8s-rollback: ## Rollback to previous Helm release
	@echo "⏪ Rolling back to previous release..."
	helm rollback docuchat -n docuchat-prod
	@echo "✅ Rollback completed"

k8s-port-forward-backend: ## Port-forward to backend service
	@echo "🔌 Port-forwarding backend to localhost:8000..."
	kubectl port-forward -n docuchat-prod svc/docuchat-backend 8000:8000

k8s-port-forward-grafana: ## Port-forward to Grafana
	@echo "🔌 Port-forwarding Grafana to localhost:3001..."
	kubectl port-forward -n docuchat-prod svc/docuchat-grafana 3001:3000

##@ Monitoring

metrics-export: ## Export current metrics
	@echo "📊 Exporting metrics..."
	@mkdir -p exports
	@curl -s http://localhost:8000/api/v1/metrics > exports/metrics_$(shell date +%Y%m%d_%H%M%S).txt
	@echo "✅ Metrics exported to exports/"

metrics-show: ## Show current metrics
	@curl -s http://localhost:8000/api/v1/metrics | grep -E "^(openai|ml|http|rag)" | head -20

prometheus-open: ## Open Prometheus UI in browser
	@echo "🔍 Opening Prometheus..."
	@open http://localhost:9090 2>/dev/null || xdg-open http://localhost:9090 2>/dev/null || echo "Open http://localhost:9090 in your browser"

grafana-open: ## Open Grafana UI in browser
	@echo "📊 Opening Grafana..."
	@open http://localhost:3001 2>/dev/null || xdg-open http://localhost:3001 2>/dev/null || echo "Open http://localhost:3001 in your browser (admin/admin)"

##@ Billing

billing-run: ## Manually run billing job
	@echo "💰 Running billing job..."
	kubectl create job --from=cronjob/docuchat-billing manual-billing-$(shell date +%s) -n docuchat-prod
	@echo "✅ Billing job created. Check logs with: kubectl logs -l job-name=manual-billing-* -n docuchat-prod"

billing-logs: ## Show billing job logs
	@kubectl logs -l app.kubernetes.io/component=billing -n docuchat-prod --tail=100

##@ Database

db-backup: ## Create database backup
	@echo "💾 Creating database backup..."
	@mkdir -p backups
	@kubectl exec -it deployment/postgresql -n docuchat-prod -- pg_dump -U docuchat docuchat > backups/docuchat_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "✅ Backup created in backups/"

db-restore: ## Restore database from backup (requires BACKUP_FILE variable)
	@if [ -z "$(BACKUP_FILE)" ]; then \
		echo "❌ Error: BACKUP_FILE not specified"; \
		echo "Usage: make db-restore BACKUP_FILE=backups/docuchat_20251006.sql"; \
		exit 1; \
	fi
	@echo "⚠️  WARNING: This will restore the database from $(BACKUP_FILE)"
	@echo "Press Ctrl+C to cancel, or Enter to continue..."
	@read
	@kubectl exec -i deployment/postgresql -n docuchat-prod -- psql -U docuchat docuchat < $(BACKUP_FILE)
	@echo "✅ Database restored"

db-shell: ## Open PostgreSQL shell
	@echo "🐘 Opening PostgreSQL shell..."
	kubectl exec -it deployment/postgresql -n docuchat-prod -- psql -U docuchat docuchat

##@ Utilities

clean: ## Clean temporary files and caches
	@echo "🧹 Cleaning temporary files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "node_modules" -prune -o -type d -name ".next" -exec rm -rf {} + 2>/dev/null || true
	rm -rf backend/htmlcov backend/.coverage 2>/dev/null || true
	@echo "✅ Cleanup completed"

install-backend: ## Install backend dependencies
	@echo "📦 Installing backend dependencies..."
	cd backend && pip install -r requirements.txt

install-frontend: ## Install frontend dependencies
	@echo "📦 Installing frontend dependencies..."
	cd frontend && pnpm install

setup-dev: install-backend install-frontend ## Setup development environment
	@echo "✅ Development environment setup completed"

##@ Documentation

docs-serve: ## Serve documentation locally
	@echo "📚 Serving documentation..."
	@echo "Backend docs: http://localhost:8000/docs"
	@echo "Redoc: http://localhost:8000/redoc"

##@ CI/CD

ci-test: lint-all test-all ## Run CI tests locally
	@echo "✅ CI tests completed successfully"

ci-build: build-all ## Build images for CI
	@echo "✅ CI build completed"

##@ Quick Actions

quick-start: devops-up devops-check ## Quick start (up + check)
	@echo ""
	@echo "🎉 DocuChat is ready!"

quick-stop: devops-down clean ## Quick stop (down + clean)
	@echo "✅ DocuChat stopped and cleaned"

version: ## Show version information
	@echo "DocuChat Version Information:"
	@echo ""
	@echo "Backend:"
	@cd backend && python -c "import app; print(f'  Version: 1.0.0')" 2>/dev/null || echo "  Version: 1.0.0"
	@echo ""
	@echo "Frontend:"
	@cd frontend && node -e "console.log('  Version: 1.0.0')" 2>/dev/null || echo "  Version: 1.0.0"
	@echo ""
	@echo "Infrastructure:"
	@echo "  Helm Chart: $(shell grep '^version:' infra/chart/Chart.yaml | awk '{print $$2}')"
