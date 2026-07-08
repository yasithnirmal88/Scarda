# Solar AIM

Intelligent monitoring system for utility-scale solar power plants.

## Project Structure

```
backend/
├── app/
│   ├── api/endpoints/     # REST API route handlers
│   ├── api/router.py      # Central API router
│   ├── api/deps.py        # Shared dependencies
│   ├── auth/              # JWT, roles, permissions
│   ├── core/              # Config, security, logging
│   ├── database/          # Session, Base, init
│   ├── middleware/        # Auth, error handler, request logger
│   ├── models/            # SQLAlchemy ORM models
│   ├── providers/         # Data provider pattern
│   │   ├── base_provider.py   # IDataProvider interface
│   │   ├── fake_provider.py   # Hardcoded placeholder data
│   │   └── huawei/            # Future Huawei integration
│   ├── repositories/      # CRUD data access layer
│   ├── schemas/           # Pydantic request/response schemas
│   ├── services/          # Business logic (placeholder)
│   └── utils/             # Enums, constants, helpers
├── alembic/               # Database migrations
├── requirements.txt
└── Dockerfile
```

## Architecture

### Clean Architecture Layers

- **API Layer** — FastAPI routers with placeholder endpoints
- **Service Layer** — Business logic (stubbed)
- **Repository Layer** — SQLAlchemy data access (CRUD only)
- **Provider Layer** — External data source abstraction

### Data Provider Pattern

```python
class IDataProvider(ABC):
    async def get_current_readings(self) -> dict: ...
    async def get_weather(self) -> dict: ...
    async def get_historical_readings(self, start, end) -> list: ...
    async def get_historical_weather(self, start, end) -> list: ...
    async def health_check(self) -> dict: ...
```

- `FakeDataProvider` — returns hardcoded JSON
- Future `HuaweiDataProvider` — will connect to Huawei Smart Logger

The rest of the application depends only on `IDataProvider`. Swapping providers requires zero changes outside the provider layer.

### Authentication

JWT-based with three roles:

| Role      | Permissions                          |
|-----------|--------------------------------------|
| Admin     | Full system access                   |
| Engineer  | Operations and maintenance           |
| Manager   | Reports and monitoring               |

## How to Run

### Using Docker (recommended)

```bash
docker compose up --build
```

Backend API: http://localhost:8000  
API Docs: http://localhost:8000/docs

### Running Locally

```bash
cd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Database Migrations (Alembic)

```bash
alembic revision --autogenerate -m "description"
alembic upgrade head
```

## Environment Variables

See `.env.example`:

| Variable                  | Description                  | Default                                |
|---------------------------|------------------------------|----------------------------------------|
| `APP_NAME`                | Application name             | Solar AIM                              |
| `DEBUG`                   | Debug mode                   | false                                  |
| `DATABASE_URL`            | PostgreSQL connection string | postgresql://postgres:postgres@localhost:5432/solar_aim |
| `SECRET_KEY`              | JWT signing key              | change-me-in-production                |
| `ALGORITHM`               | JWT algorithm                | HS256                                  |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration         | 30                                     |

## Future Huawei Integration

When API credentials are obtained:

1. Create `HuaweiDataProvider` in `app/providers/huawei/`
2. Implement the `IDataProvider` interface
3. Swap the provider in the service layer

No other part of the codebase needs modification.
