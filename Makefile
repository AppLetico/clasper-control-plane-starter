.PHONY: dev test

# Prefer venv uvicorn so "make dev" works without activating the venv.
UVICORN := $(if $(wildcard .venv/bin/uvicorn),.venv/bin/uvicorn,uvicorn)

dev:
	set -a && . ./.env && set +a && PYTHONPATH=src $(UVICORN) control_plane.main:app --reload --port $${CONTROL_PLANE_PORT:-9001}

test:
	python3 -m pytest
