.PHONY: dev test

dev:
	set -a && . ./.env && set +a && PYTHONPATH=src uvicorn control_plane.main:app --reload --port $${CONTROL_PLANE_PORT:-9001}

test:
	pytest
