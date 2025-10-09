# syntax=docker/dockerfile:1.7
FROM python:3.11-slim AS builder
WORKDIR /app
ENV PIP_NO_CACHE_DIR=1
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --prefix=/install -r requirements.txt
COPY src ./src

FROM python:3.11-slim
# Non-root user
RUN useradd -m -u 10001 appuser
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
# copy only installed packages and app code
COPY --from=builder /install /usr/local
COPY src ./src
USER appuser
EXPOSE 8000
CMD ["uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
