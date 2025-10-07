
# Green DevOps — FastAPI Baseline (GitHub Actions)

A **more complex Python app** to benchmark CI/CD energy/cost improvements.

## What this project includes
- **FastAPI** app with CRUD over an in-memory **SQLite** database via **SQLModel**.
- **Tests** using pytest + httpx (TestClient).
- **GitHub Actions baseline workflow** that measures:
  - install time/resources
  - test time/resources
  - uploads metrics as artifact.

This is intentionally realistic (web API + DB layer) but still lightweight and fast.

## Run locally
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q
```

## Endpoints
- `GET /health` → {"status":"ok"}
- `POST /items` → create item {name, price}
- `GET /items` → list items
- `GET /items/{item_id}` → fetch item by id

  ## API (v1)

Base path: `/api/v1`

- `POST /items` → create item (body: `{name, price>=0}`)  
  - 201, returns `ItemRead`
  - 409 if `name` not unique
- `GET /items/{id}` → fetch one
- `PATCH /items/{id}` → partial update (body: `{name?, price?}`)
  - 409 on unique-name violation
- `GET /items` → list with filters  
  - Query params:
    - `min_price` (>=0), `max_price` (>=0)
    - `q` (substring of name)
    - `limit` [1..200], `offset` [0..]
    - `order_by` in `{id,name,price}`, `direction` in `{asc,desc}`


## Next steps
Use this repo as your **baseline**. We'll then apply optimizations (caching, selective tests, minimal containers) and compare the metrics.

## Quality Gates
- **Lint:** Ruff, Black (check mode)
- **Type:** mypy (strict-ish)
- **Tests:** pytest with coverage; gate at **85%**
- **Property-based tests:** Hypothesis explores name/price domains
- **Performance:** pytest-benchmark producing `bench.json` artifact
- **Auth:** All `/api/v1/*` require `Authorization: Bearer <token>`; default token in dev/CI is `devtoken`, or fetch via `POST /auth/token`

## Observability
- **Prometheus**: `/metrics` exposes `http_requests_total`, `http_request_latency_seconds`, `http_requests_in_flight`.
- **Structured logs**: JSON via structlog, include `request_id`.
- **Request IDs**: responses include `X-Request-ID`.
- **Tracing**: OpenTelemetry configured to **console exporter** in dev/CI.

## Green Metrics
- **CodeCarbon** tracks CO₂e for `pip install` and test execution on CI.
- Artifacts: `metrics-optimized/emissions_install.csv`, `emissions_tests.csv`, and JSON summaries.

## Docker
```bash
docker build -t green-devops:local .
docker run -p 8000:8000 green-devops:local
# open http://localhost:8000/docs and http://localhost:8000/metrics

