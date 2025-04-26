FROM python:3.11-slim as builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y --no-install-recommends gcc python3-dev

# Create and activate virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip

COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

FROM python:3.11-slim

WORKDIR /app

RUN groupadd -r appuser && useradd -r -g appuser appuser \
    && chown appuser:appuser /app

# Copy virtual environment from builder stage
COPY --from=builder --chown=appuser:appuser /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY --from=builder --chown=appuser:appuser /app/wheels /wheels
COPY --chown=appuser:appuser . .

RUN pip install --no-cache-dir /wheels/* \
    && rm -rf /wheels

USER appuser

EXPOSE 8000

ENV PYTHONPATH=/app \
    HOST=0.0.0.0 \
    PORT=8000 \
    DEBUG=false

CMD ["python", "-c", "from app.patches.bcrypt_patch import patch_bcrypt; patch_bcrypt(); import uvicorn; uvicorn.run('main:app', host='0.0.0.0', port=8000, proxy_headers=True)"]

