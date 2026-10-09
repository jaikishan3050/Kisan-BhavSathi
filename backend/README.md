# Kisan BhavSaathi — Backend Service

**Role:** Core REST API service for Kisan BhavSaathi (SIH 2026).  
**Tech Stack:** Python 3.11+ / FastAPI / Uvicorn / Pydantic v2 / Pytest.  
**Current Milestone:** Step 3 — Backend Foundation Only.

---

## 1. Directory Structure

```text
backend/
├── app/
│   ├── __init__.py           # Package marker
│   ├── main.py               # Application entry point, lifespan, CORS, and root routes
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py         # Environment-based settings and CORS configuration
│   │   └── logging.py        # Centralized application logging setup
│   └── api/
│       ├── __init__.py
│       └── v1/
│           ├── __init__.py
│           ├── health.py     # GET /health endpoint definition
│           └── router.py     # Version 1 central API router aggregator
├── tests/
│   ├── __init__.py
│   ├── conftest.py           # Pytest test fixtures (TestClient)
│   └── test_health.py        # Automated tests for health endpoint, startup, and CORS
├── .env.example              # Environment variables template (no secrets)
├── pytest.ini                # Pytest configuration with pythonpath set to '.'
├── requirements.txt          # Production and testing dependency manifest
└── README.md                 # Setup, configuration, and execution instructions
```

---

## 2. Prerequisites (Windows)

- **Python 3.11 or newer** installed.
- Verify your Python version in PowerShell:
  ```powershell
  python --version
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
Install the required packages using pip:

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
2. Open `.env` and review active settings.

### Key Settings:
- `PROJECT_NAME`: Display name for the API documentation.
- `ENVIRONMENT`: Set to `development`, `staging`, or `production`.
- `DEBUG`: Set to `True` for hot-reloading and detailed errors during local development.
- `HOST`: Bind host address (default: `127.0.0.1`).
- `PORT`: Bind port (default: `8000`).
- `LOG_LEVEL`: Log severity threshold (`DEBUG`, `INFO`, `WARNING`, `ERROR`).
- `CORS_ORIGINS`: Comma-separated list of allowed origins.
  - **Local Development Default:** `http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173`
  - **Production Requirement:** Must be explicitly set to the production domains of the web admin portal and mobile client. Wildcard `*` is strictly discouraged for production.

---

## 5. Running the Application

### Option A: Direct Python Execution
```powershell
python -m app.main
```

### Option B: Using Uvicorn Directly (with Hot-Reload)
```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Once running, the following endpoints are available:
- **Interactive Swagger Documentation:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc Documentation:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **Root Health Check:** [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)
- **Version 1 Health Check:** [http://127.0.0.1:8000/api/v1/health](http://127.0.0.1:8000/api/v1/health)
- **Root Metadata Index:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## 6. Running Automated Tests

Run the test suite using `pytest`:

```powershell
# From the backend directory
pytest
```

To run with verbose output and test names:
```powershell
pytest -v
```

All 5 test cases should pass:
1. `test_root_health_endpoint`
2. `test_api_v1_health_endpoint`
3. `test_root_index_endpoint`
4. `test_cors_headers_on_health`
5. `test_cors_headers_rejected_origin`

---

## 7. Scope Boundaries for Step 3

This module constitutes **Step 3: Backend Foundation Only**:
- ✅ FastAPI skeleton, Pydantic settings, application logging, CORS, `/health` endpoint, and automated tests.
- ❌ **Out of scope for this step:** Database models, Alembic migrations, JWT authentication, user accounts, and business domains. These are scheduled sequentially for Steps 4 through 11.
