# ===== AsyncFlow Makefile =====
up:
	docker compose up --build

down:
	docker compose down -v

logs:
	docker compose logs -f

restart:
	docker compose down -v && docker compose up --build

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +

# quality
lint:
	uv run ruff check .
format:
	uv run ruff format .
typecheck:
	uv run mypy .

test:
	uv run pytest

qa: format lint typecheck test