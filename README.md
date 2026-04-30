# Garage Management API 🚀

An advanced, asynchronous backend service for modern auto repair shops. Built to handle complex repair histories, AI-driven analytics, and real-time billing seamlessly.

## 🌟 Key Features

* **Strict Entity Tracking:** Reliable car identification and repair history tracking strictly by license plates to prevent data mismatch.
* **AI-Powered Insights:** Automated extraction of repair data (parts, labor, costs) from raw mechanic notes using OpenAI, with cost tracing via Langfuse.
* **Event-Driven Billing:** Integration with Stripe webhooks for payment processing.
* **Real-Time Notifications:** WebSockets implementation to instantly notify shop managers when a repair invoice is paid.
* **Background Processing:** Redis & Arq-powered background workers for heavy tasks.
* **Production-Ready Infrastructure:** Fully containerized with Docker, complete with health checks, Prometheus metrics, and Grafana dashboards.

## 🛠 Tech Stack

* **Framework:** FastAPI (Python 3.12)
* **Database:** PostgreSQL 15 + Asyncpg + SQLAlchemy 2.0 (Repository Pattern)
* **Caching & Queues:** Redis + Arq
* **Integrations:** Stripe API, OpenAI API, Langfuse
* **Testing:** Pytest (Asyncio, Integration Tests)
* **DevOps:** Docker Compose, GitHub Actions (CI/CD)

## 🚦 Quick Start (Docker)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/khomych-dev/garage-management-api.git
   cd garage-management-api
   ```

2. **Configure Environment:**
    Copy the example environment file and fill in your actual API keys.
    ```bash
    cp .env.example .env
    ```

3. **Launch the Infrastructure:**
    ```bash
    docker compose up -d
    ```
    The API will be available at http://localhost:8000.
    API Documentation (Swagger UI) at http://localhost:8000/docs.

## 🧪 Testing

The project maintains pragmatic test coverage focusing on critical business paths (e.g., cascade deletions in repair history, secure authentication).
```bash
uv run pytest -v
```

## 👨‍💻 Author

**Anatolii Khomych**
* GitHub: [@khomych-dev](https://github.com/khomych-dev)
