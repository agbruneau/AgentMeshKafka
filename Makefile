# =============================================================================
# kafka-eda-lab - Makefile
# Simulation EDA avec Apache Kafka
# =============================================================================

.PHONY: all build clean test test-integration test-load \
        up down reset logs status health \
        dashboard grafana jaeger kafka-ui prometheus \
        topics help

# -----------------------------------------------------------------------------
# Variables
# -----------------------------------------------------------------------------
GO := go
BINARY_DIR := bin
SERVICES := quotation souscription reclamation dashboard simulator

# Docker
DOCKER_COMPOSE := docker-compose
COMPOSE_FILE := docker-compose.yml

# URLs
DASHBOARD_URL := http://localhost:8080
GRAFANA_URL := http://localhost:3000
JAEGER_URL := http://localhost:16686
KAFKA_UI_URL := http://localhost:8090
PROMETHEUS_URL := http://localhost:9090

# =============================================================================
# BUILD
# =============================================================================

all: build ## Build tous les services

build: ## Compile tous les services Go
	@echo ============================================
	@echo  Building all services...
	@echo ============================================
	@if not exist $(BINARY_DIR) mkdir $(BINARY_DIR)
	@$(GO) build -o $(BINARY_DIR)/dashboard.exe ./cmd/dashboard 2>nul && echo [OK] dashboard || echo [SKIP] dashboard
	@$(GO) build -o $(BINARY_DIR)/quotation.exe ./cmd/quotation 2>nul && echo [OK] quotation || echo [SKIP] quotation
	@$(GO) build -o $(BINARY_DIR)/souscription.exe ./cmd/souscription 2>nul && echo [OK] souscription || echo [SKIP] souscription
	@$(GO) build -o $(BINARY_DIR)/reclamation.exe ./cmd/reclamation 2>nul && echo [OK] reclamation || echo [SKIP] reclamation
	@$(GO) build -o $(BINARY_DIR)/simulator.exe ./cmd/simulator 2>nul && echo [OK] simulator || echo [SKIP] simulator
	@echo ============================================
	@echo  Build complete.
	@echo ============================================

clean: ## Nettoie les binaires et fichiers temporaires
	@echo Cleaning...
	@if exist $(BINARY_DIR) rmdir /s /q $(BINARY_DIR)
	@if exist *.db del /q *.db
	@echo Clean complete.

# =============================================================================
# DOCKER
# =============================================================================

up: ## Demarre l'environnement Docker Compose
	@echo ============================================
	@echo  Starting kafka-eda-lab...
	@echo ============================================
	$(DOCKER_COMPOSE) up -d
	@echo ============================================
	@echo  Environment started.
	@echo  Run 'make status' to check services.
	@echo ============================================

down: ## Arrete l'environnement Docker Compose
	@echo Stopping kafka-eda-lab...
	$(DOCKER_COMPOSE) down
	@echo Environment stopped.

reset: ## Reinitialise completement (supprime les volumes)
	@echo ============================================
	@echo  Resetting kafka-eda-lab...
	@echo ============================================
	$(DOCKER_COMPOSE) down -v --remove-orphans
	@timeout /t 2 /nobreak >nul
	$(DOCKER_COMPOSE) up -d
	@echo ============================================
	@echo  Environment reset complete.
	@echo ============================================

logs: ## Affiche les logs de tous les services
	$(DOCKER_COMPOSE) logs -f

logs-kafka: ## Affiche les logs Kafka uniquement
	$(DOCKER_COMPOSE) logs -f kafka

status: ## Affiche l'etat des conteneurs
	@echo ============================================
	@echo  Container Status
	@echo ============================================
	$(DOCKER_COMPOSE) ps

# =============================================================================
# TESTS
# =============================================================================

test: ## Lance les tests unitaires
	@echo Running unit tests...
	$(GO) test -v ./internal/...

test-integration: ## Lance les tests d'integration
	@echo Running integration tests...
	$(GO) test -v -tags=integration ./tests/integration/...

test-integration-quotation: ## Tests d'integration Quotation
	@echo Running Quotation integration tests...
	$(GO) test -v -tags=integration ./tests/integration/quotation_test.go

test-integration-phase2: ## Tests d'integration Phase 2
	@echo Running Phase 2 integration tests...
	$(GO) test -v -tags=integration ./tests/integration/phase2_test.go

test-load: ## Lance les tests de charge (k6)
	@echo Running load tests...
	@echo [TODO] k6 run tests/load/

test-cover: ## Lance les tests avec couverture
	@echo Running tests with coverage...
	$(GO) test -coverprofile=coverage.out ./internal/...
	$(GO) tool cover -html=coverage.out -o coverage.html
	@echo Coverage report: coverage.html

# =============================================================================
# HEALTH & DIAGNOSTICS
# =============================================================================

health: ## Verifie la sante de tous les services
	@echo ============================================
	@echo  Health Check - kafka-eda-lab
	@echo ============================================
	@powershell -ExecutionPolicy Bypass -File scripts/health-check.ps1
	@echo ============================================

topics: ## Liste les topics Kafka
	@echo Listing Kafka topics...
	$(DOCKER_COMPOSE) exec kafka kafka-topics.sh --bootstrap-server localhost:9092 --list

# =============================================================================
# OUTILS - Ouvrir dans le navigateur
# =============================================================================

dashboard: ## Ouvre le Dashboard dans le navigateur
	@echo Opening Dashboard...
	@start $(DASHBOARD_URL)

grafana: ## Ouvre Grafana dans le navigateur
	@echo Opening Grafana...
	@start $(GRAFANA_URL)

jaeger: ## Ouvre Jaeger dans le navigateur
	@echo Opening Jaeger...
	@start $(JAEGER_URL)

kafka-ui: ## Ouvre Kafka UI dans le navigateur
	@echo Opening Kafka UI...
	@start $(KAFKA_UI_URL)

prometheus: ## Ouvre Prometheus dans le navigateur
	@echo Opening Prometheus...
	@start $(PROMETHEUS_URL)

# =============================================================================
# HELP
# =============================================================================

help: ## Affiche cette aide
	@echo.
	@echo  ============================================
	@echo   kafka-eda-lab - Commandes disponibles
	@echo  ============================================
	@echo.
	@echo  BUILD:
	@echo    make build            Compile tous les services Go
	@echo    make clean            Nettoie les binaires
	@echo.
	@echo  DOCKER:
	@echo    make up               Demarre l'environnement
	@echo    make down             Arrete l'environnement
	@echo    make reset            Reinitialise completement
	@echo    make logs             Affiche les logs (tous)
	@echo    make logs-kafka       Affiche les logs Kafka
	@echo    make status           Affiche l'etat des conteneurs
	@echo.
	@echo  TESTS:
	@echo    make test             Tests unitaires
	@echo    make test-integration Tests d'integration
	@echo    make test-load        Tests de charge
	@echo    make test-cover       Tests avec couverture
	@echo.
	@echo  DIAGNOSTICS:
	@echo    make health           Verifie la sante des services
	@echo    make topics           Liste les topics Kafka
	@echo.
	@echo  OUTILS (ouvre le navigateur):
	@echo    make dashboard        http://localhost:8080
	@echo    make grafana          http://localhost:3000
	@echo    make jaeger           http://localhost:16686
	@echo    make kafka-ui         http://localhost:8090
	@echo    make prometheus       http://localhost:9090
	@echo.
	@echo  ============================================
	@echo.
