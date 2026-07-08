# Solar AIM

Solar AIM is an intelligent monitoring system for utility-scale solar power plants.

## Project Structure

```
solar-aim/
├── backend/                    # FastAPI Python backend
│   ├── app/
│   │   ├── api/                # REST API endpoints
│   │   ├── auth/               # JWT authentication
│   │   ├── core/               # Configuration and security
│   │   ├── database/           # SQLAlchemy setup
│   │   ├── middleware/          # Auth middleware
│   │   ├── models/             # SQLAlchemy models
│   │   ├── providers/          # Data provider pattern
│   │   │   └── huawei/         # Future Huawei API integration
│   │   ├── repositories/       # Data access layer
│   │   ├── schemas/            # Pydantic schemas
│   │   ├── services/           # Business logic layer
│   │   └── utils/              # Utility functions
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                   # React + TypeScript frontend
│   ├── src/
│   │   ├── components/         # Reusable UI components
│   │   ├── contexts/           # React contexts
│   │   ├── hooks/              # Custom hooks
│   │   ├── layouts/            # Page layouts
│   │   ├── pages/              # Route pages
│   │   ├── routes/             # Router configuration
│   │   ├── services/           # API client
│   │   ├── types/              # TypeScript types
│   │   └── utils/              # Constants and helpers
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── .env.example
```

## Running the Project

### Prerequisites

- Docker and Docker Compose
- Node.js 20+ (for local frontend development)
- Python 3.12+ (for local backend development)

### Using Docker (recommended)

```bash
docker-compose up --build
```

- Backend API: http://localhost:8000
- Frontend: http://localhost:3000

### Running Locally

#### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Architecture

### Clean Architecture Layers

- **API Layer** - FastAPI routers with placeholder endpoints
- **Service Layer** - Business logic (to be implemented)
- **Repository Layer** - SQLAlchemy data access
- **Provider Layer** - External data source abstraction

### Data Provider Pattern

The system uses an abstract `IDataProvider` interface:

```python
class IDataProvider(ABC):
    async def get_current_readings(self) -> dict: ...
    async def get_weather(self) -> dict: ...
    async def get_historical_data(self, start, end) -> list: ...
```

- `FakeDataProvider` returns hardcoded placeholder data
- Future `HuaweiDataProvider` (in `providers/huawei/`) will connect to Huawei Smart Logger APIs

### Authentication

JWT-based authentication with three roles:
- **Admin** - Full system access
- **Engineer** - Operations and maintenance
- **Manager** - Reports and monitoring

## Future Integration

When Huawei Smart Logger APIs become available:
1. Implement `HuaweiDataProvider` in `app/providers/huawei/`
2. Register it in the service layer
3. Replace `FakeDataProvider` with the real provider
