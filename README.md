# Garage Management API

An advanced asynchronous backend service for modern auto repair shops. Designed to handle complex repair histories, AI-driven analytics, and secure real-time billing.

---

## Key Features & Architecture

* **AI-Powered Insights & Zero-Hallucination**
  Automated extraction of repair data (parts, labor, costs) from raw mechanic notes using OpenAI Structured Outputs. Strict validation filters reject irrelevant inputs to prevent AI hallucinations from polluting the database. Cost tracking and prompt management are handled via Langfuse.

* **Event-Driven Billing & Idempotency**
  Stripe webhook integration for payment processing. Includes cryptographic signature verification to reject malicious requests and idempotency handling to prevent duplicate database writes.

* **Secure Real-Time Notifications**
  JWT-secured WebSockets notify shop managers instantly when invoices are paid. Uses controlled broadcast channels to prevent client-side spam and unauthorized message access.

* **Strict Entity Tracking**
  Vehicle identification and repair history tracking based strictly on license plates using fail-closed validation models.

* **Background Processing**
  Redis + Arq workers for non-blocking execution of heavy background tasks.

* **Production-Ready Infrastructure**
  Fully containerized via Docker, with strict environment configuration through `.env` files and readiness for monitoring and observability tooling.

---

## Tech Stack

* **Framework:** FastAPI (Python 3.12)
* **Database:** PostgreSQL 15 + Asyncpg + SQLAlchemy 2.0 (Repository Pattern)
* **Caching & Queues:** Redis + Arq
* **Integrations:** Stripe API, OpenAI API, Langfuse
* **Security:** JWT Authentication, OAuth2PasswordBearer, PyJWT
* **Testing:** Pytest (Asyncio, Unit & Integration tests)
* **DevOps:** Docker Compose, GitHub Actions (CI/CD)

---

## Quick Start (Docker)

### 1. Clone the repository

```bash
git clone https://github.com/khomych-dev/garage-management-api.git
cd garage-management-api
```

---

### 2. Configure environment

Copy example environment file and set required variables:

```bash
cp .env.example .env
```

---

### 3. Run the project

```bash
docker compose up -d
```

---

## Local Environment

After startup:

* API: `http://localhost:8000`
* Docs (Swagger): `http://localhost:8000/docs`

---

## Production

* API: `https://khomych-dev.online`
* Docs (Swagger): `https://khomych-dev.online/docs`

---

## Testing

Focus is on critical business flows:

* repair history integrity
* authentication
* billing correctness

```bash
uv run pytest -v
```

---

## Author

* **Anatolii Khomych**
* **GitHub:** [@khomych-dev](https://github.com/khomych-dev)
