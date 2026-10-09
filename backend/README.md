# Kisan BhavSaathi — Backend Service

**Role:** Core REST API service for Kisan BhavSaathi (SIH 2026).  
**Tech Stack:** Python 3.11+ / FastAPI / Uvicorn / Pydantic v2 / SQLAlchemy 2.0 / PostgreSQL (psycopg2-binary) / Pytest.  
**Current Milestone:** Step 4B.3 — Alembic Setup & Initial Migration Generation Only.

---

## 1. Directory Structure

```text
backend/
├── alembic/                  # Alembic database migrations directory
│   ├── env.py                # Alembic environment configured with Base.metadata & app settings
│   ├── script.py.mako        # Migration script template
│   └── versions/             # Migration revisions
│       └── 711f7a9575e0_initial_relational_schema.py
├── alembic.ini               # Alembic configuration file (no hardcoded secrets)
├── app/
│   ├── __init__.py           # Package marker
│   ├── main.py               # Application entry point, lifespan, CORS, and root routes
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py         # Environment-based settings (CORS, DATABASE_URL, pool settings)
│   │   ├── database.py       # SQLAlchemy 2.0 Engine, SessionLocal, get_db, and connectivity check
│   │   └── logging.py        # Centralized application logging setup
│   ├── models/               # SQLAlchemy 2.0 Domain ORM models (20 tables, 22 enums)
│   │   ├── __init__.py       # Re-exports Base, enums, and all 20 domain models
│   │   ├── base.py           # DeclarativeBase, UUIDPrimaryKeyMixin, TimestampMixin
│   │   ├── crop.py           # Crop, Lot, SaleIntent
│   │   ├── enums.py          # 22 canonical StrEnum classes with __pg_enum_name__
│   │   ├── fpo.py            # FPO, FPOMembership
│   │   ├── market.py         # MarketPrice, PricePrediction, PincodeCoordinate
│   │   ├── matching.py       # BuyerDemand, Match, Offer, Negotiation
│   │   ├── order.py          # Order, OrderLotAllocation, Logistics, PaymentRecord, Grievance
│   │   └── user.py           # User, FarmerProfile, BuyerProfile
│   └── api/
│       ├── __init__.py
│       └── v1/
│           ├── __init__.py
│           ├── health.py     # GET /health endpoint definition
│           └── router.py     # Version 1 central API router aggregator
├── tests/
│   ├── __init__.py
│   ├── conftest.py           # Pytest test fixtures (TestClient)
│   ├── test_base_and_enums.py # Tests for DeclarativeBase, UUID/timestamp mixins, and 22 enums
│   ├── test_database.py      # Tests for database settings, engine pool, and session lifecycle
│   ├── test_health.py        # Automated tests for health endpoint, startup, and CORS
│   ├── test_migrations.py    # Tests for Alembic configuration, script directory, and initial revision
│   └── test_models.py        # Offline metadata, constraint, and relationship tests for 20 models
├── .env.example              # Environment variables template with placeholder DATABASE_URL
├── .gitignore                # Git ignore rules for virtualenvs, bytecode, and .env
├── pytest.ini                # Pytest configuration with pythonpath set to '.'
├── requirements.txt          # Production, database, and testing dependency manifest
└── README.md                 # Setup, configuration, and execution instructions
```

---

## 2. Prerequisites (Windows)

- **Python 3.11 or newer** installed.
- **PostgreSQL 14+** installed and running locally on Windows (e.g., standard PostgreSQL service on port `5432`).
  - Verify Python version:
    ```powershell
    python --version
    ```
  - Verify PostgreSQL Windows service:
    ```powershell
    Get-Service -Name *postgres*
    ```

---

## 3. Local Environment Setup

### 3.1 Create and Activate a Virtual Environment
From the `backend/` directory in PowerShell:

```powershell
# Navigate into backend directory
cd backend

# Create virtual environment named '.venv'
python -m venv .venv

# Activate the virtual environment on Windows
.\.venv\Scripts\Activate.ps1
```

> *Tip: If PowerShell blocks script execution, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in your terminal session.*

### 3.2 Install Dependencies
Install all required packages (including FastAPI, SQLAlchemy 2.0, and psycopg2-binary):

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

---

## 4. Configuration (.env)

1. Copy the provided `.env.example` template to `.env`:
   ```powershell
   Copy-Item .env.example .env
   ```
2. Open `.env` and set your database connection parameters:
   ```dotenv
   # Local PostgreSQL database URL
   DATABASE_URL="postgresql+psycopg2://postgres:YOUR_PASSWORD@localhost:5432/kisan_bhavsaathi_dev"
   
   # Connection Pool Settings
   DB_POOL_SIZE=5
   DB_MAX_OVERFLOW=10
   DB_POOL_TIMEOUT=30
   DB_POOL_RECYCLE=1800
   DB_POOL_PRE_PING=True
   ```

> **Security Rule:** Never commit `.env` or production passwords to version control. The repository `.gitignore` automatically excludes `.env` files.

---

## 5. PostgreSQL Connectivity Check

You can explicitly test connectivity to your local PostgreSQL server without starting the full web application:

```powershell
python -m app.core.database
```

- If PostgreSQL is reachable, it reports:
  ```json
  {
    "connected": true,
    "database_url": "postgresql+psycopg2://postgres:***@localhost:5432/kisan_bhavsaathi_dev",
    "dialect": "postgresql",
    "latency_ms": 3.45,
    "message": "PostgreSQL connection successfully verified."
  }
  ```
- If PostgreSQL is unreachable or credentials are not yet set, it reports a sanitized error message **without leaking passwords**.
- Note: Importing the FastAPI app (`app.main`) does **not** require a running database server.

---

## 6. Running the Application

### Option A: Direct Python Execution
```powershell
python -m app.main
```

### Option B: Using Uvicorn Directly (with Hot-Reload)
```powershell
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Once running:
- **Interactive OpenAPI Documentation:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Root Health Check:** [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)
- **API v1 Health Check:** [http://127.0.0.1:8000/api/v1/health](http://127.0.0.1:8000/api/v1/health)

---

## 7. Database Migrations (Alembic)

Kisan BhavSaathi uses **Alembic** to manage PostgreSQL database migrations. The database URL is dynamically loaded from the application settings (`DATABASE_URL`), ensuring secrets are never hardcoded.

### 7.1 Inspecting Migrations
From `backend/`:

```powershell
# View latest revision head
python -m alembic heads

# View migration history
python -m alembic history --verbose

# Generate offline SQL preview without connecting to the database
python -m alembic upgrade head --sql
```

### 7.2 Safe Migration Workflow
- Migrations define all 20 core tables, 22 native PostgreSQL ENUM types, and table CHECK/UNIQUE/FK constraints.
- Financial and audit records enforce `ondelete="RESTRICT"` to prevent accidental cascading deletion.
- **Safety Boundary:** During Step 4B.3, migration files are generated and tested offline. Applying migrations (`alembic upgrade head`) to `kisan_bhavsaathi_dev` or `kisan_bhavsaathi_test` occurs in subsequent execution steps.

---

## 8. Running Automated Tests

Run the full offline test suite using `pytest`:

```powershell
python -m pytest -v
```

All unit tests run completely offline without requiring a running PostgreSQL server or SQLite:
- `tests/test_health.py`: Health endpoint, startup lifecycle, and CORS origin verification.
- `tests/test_database.py`: Configuration defaults, password masking, connection pooling, and session cleanup.
- `tests/test_base_and_enums.py`: DeclarativeBase, UUIDPrimaryKeyMixin, TimestampMixin, and all 22 canonical enums.
- `tests/test_models.py`: Discovery of 20 domain tables, check constraints (`chk_lot_ownership`), JSONB columns, and relationship mappings.
- `tests/test_migrations.py`: Alembic configuration discovery, script directory resolution, and initial revision validity.

---

## 9. Scope Boundaries for Step 4B.3

This milestone provides **Alembic Setup & Initial Migration Generation Only**:
- ✅ Alembic infrastructure (`alembic.ini`, `alembic/env.py`, `alembic/script.py.mako`, `alembic/versions/`).
- ✅ Initial revision script covering all 20 tables, 22 native enums, and foreign-key/check constraints.
- ✅ Dynamic application settings integration with masked secrets.
- ✅ Offline test coverage for migration metadata and Alembic discovery.
- ❌ **Strictly out of scope for this step:** Connecting to PostgreSQL, applying migrations (`alembic upgrade`), altering databases, or executing SQL.
