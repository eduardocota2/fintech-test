SHELL := /bin/sh
COMPOSE := docker compose -f docker-compose.yml --env-file .env

.PHONY: help compose-up compose-down compose-ps compose-logs db-up db-down db-reset migrate

help:
	@echo "Available targets:"
	@echo "  compose-up            Build and start full stack"
	@echo "  compose-down          Stop full stack"
	@echo "  compose-ps            Show compose services"
	@echo "  compose-logs          Tail all compose logs"
	@echo "  db-up                 Start only postgres (delegates to backend/Makefile)"
	@echo "  db-down               Stop compose stack (delegates to backend/Makefile)"
	@echo "  db-reset              Reset postgres volume (delegates to backend/Makefile)"
	@echo "  migrate               Run alembic migration service"

compose-up:
	$(COMPOSE) up --build -d

compose-down:
	$(COMPOSE) down

compose-ps:
	$(COMPOSE) ps

compose-logs:
	$(COMPOSE) logs -f

db-up:
	$(MAKE) -C backend db-up

db-down:
	$(MAKE) -C backend db-down

db-reset:
	$(MAKE) -C backend db-reset

migrate:
	$(COMPOSE) up migrate
