# Garage Management API

An advanced asynchronous backend service for modern auto repair shops. Designed to handle complex repair histories, AI-driven analytics, and real-time billing.

---

## Key Features

* **Strict Entity Tracking**
  Reliable car identification and repair history tracking strictly by license plates to prevent data mismatch.

* **AI-Powered Insights**
  Automated extraction of repair data (parts, labor, costs) from raw mechanic notes using OpenAI, with cost tracing via Langfuse.

* **Event-Driven Billing**
  Integration with Stripe webhooks for payment processing.

* **Real-Time Notifications**
  WebSockets implementation to instantly notify shop managers when a repair invoice is paid.

* **Background Processing**
  Redis + Arq-powered background workers for heavy tasks.

* **Production-Ready Infrastructure**
  Fully containerized with Docker, including health checks, Prometheus metrics, and Grafana dashboards.

---

## Tech Stack

* **Framework:** FastAPI (Python 3.12)
* **Database:** PostgreSQL 15 + Asyncpg + SQLAlchemy 2.0 (Repository Pattern)
* **Caching & Queues:** Redis + Arq
* **Integrations:** Stripe API, OpenAI API, Langfuse
* **Testing:** Pytest (Asyncio, Integration + Unit tests)
* **DevOps:** Docker Compose, GitHub Actions (CI/CD)

---

## Quick Start (Docker)

### 1. Clone the repository

```bash
git clone https://github.com/khomych-dev/garage-management-api.git
cd garage-management-api
```

### 2. Configure environment

Copy the example environment file and provide your API keys:

```bash
cp .env.example .env
```

### 3. Run the project

```bash
docker compose up -d
```

**Local Environment (After startup):**
* API: `http://localhost:8000`
* Docs (Swagger): `http://localhost:8000/docs`

**Live Production:**
* API: `https://khomych-dev.online`
* Docs (Swagger): `https://khomych-dev.online/docs`

---

## Testing

The project focuses on testing critical business flows (e.g., repair history integrity, authentication, billing logic).

```bash
uv run pytest -v
```

---

## Author

**Anatolii Khomych**
* **GitHub:** [@khomych-dev](https://github.com/khomych-dev)
