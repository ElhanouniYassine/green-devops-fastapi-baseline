
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

## Next steps
Use this repo as your **baseline**. We'll then apply optimizations (caching, selective tests, minimal containers) and compare the metrics.
