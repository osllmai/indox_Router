FROM python:3.11-slim as builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y --no-install-recommends gcc python3-dev

COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

FROM python:3.11-slim

WORKDIR /app

RUN groupadd -r appuser && useradd -r -g appuser appuser \
    && chown appuser:appuser /app

COPY --from=builder --chown=appuser:appuser /app/wheels /wheels
COPY --chown=appuser:appuser . .

RUN pip install --no-cache /wheels/* \
    && rm -rf /wheels

USER appuser

EXPOSE 8000

ENV PYTHONPATH=/app \
    HOST=0.0.0.0 \
    PORT=8000 \
    DEBUG=false

CMD ["python", "-c", "from app.patches.bcrypt_patch import patch_bcrypt; patch_bcrypt(); import uvicorn; uvicorn.run('main:app', host='0.0.0.0', port=8000, proxy_headers=True)"]

