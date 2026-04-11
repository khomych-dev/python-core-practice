FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN useradd -m -d /app -s /bin/bash appuser

WORKDIR /app

RUN chown -R appuser:appuser /app
USER appuser

COPY --chown=appuser:appuser requirements.txt .

RUN uv pip install --system --no-cache -r requirements.txt

COPY --chown=appuser:appuser . .

EXPOSE 8000

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
