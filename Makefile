# ----- Config -----
PY := python
PKG := src
APP := src.app.main:app
TOKEN ?= devtoken

# ----- Dev -----
.PHONY: install run test lint type cov bench fmt fmt-check precommit

install:
	$(PY) -m pip install --upgrade pip
	pip install -r requirements.txt

run:
	API_TOKEN=$(TOKEN) uvicorn $(APP) --reload

test:
	API_TOKEN=$(TOKEN) pytest -q

cov:
	API_TOKEN=$(TOKEN) pytest --cov=$(PKG) --cov-report=term-missing

bench:
	API_TOKEN=$(TOKEN) pytest -k test_perf_create_and_list --benchmark-json=bench.json

lint:
	ruff check .

fmt:
	black .

fmt-check:
	black --check .
	ruff check --output-format=github .

type:
	mypy $(PKG)

precommit:
	pre-commit run --all-files

# ----- Containers / Observability -----
.PHONY: docker-build compose-up compose-down compose-restart

docker-build:
	docker build -t green-devops:local .

compose-up:
	docker compose up --build

compose-down:
	docker compose down -v

compose-restart:
	docker compose down -v && docker compose up --build -d

# ----- CI sim (local) -----
.PHONY: emissions-install emissions-tests

emissions-install:
	$(PY) tools/run_with_emissions.py --label install --outdir metrics-optimized -- pip install -r requirements.txt

emissions-tests:
	API_TOKEN=$(TOKEN) $(PY) tools/run_with_emissions.py --label tests --outdir metrics-optimized -- pytest -q
