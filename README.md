# Scanpy Analysis Platform

Web-based single-cell RNA-seq analysis platform using Scanpy.

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Quick Start](#2-quick-start)
3. [Project Structure](#3-project-structure)
4. [Development Commands](#4-development-commands)
5. [Tech Stack](#5-tech-stack)

---

## 1. Prerequisites

| Requirement | Version |
|-------------|---------|
| Python | 3.10+ |
| Docker & Docker Compose | Latest |
| Git | Latest |

---

## 2. Quick Start

### Step 1: Start Services

```bash
docker-compose up -d
```

### Step 2: Setup Python Environment

```bash
cd backend
python3.10 -m venv venv
source venv/bin/activate    # Linux/Mac
pip install -r requirements.txt
cp .env.example .env
```

### Step 3: Initialize Database

```bash
python init_db.py
python test_db.py
```

### Step 4: Run Development Server

```bash
# Terminal 1: API server
uvicorn app.main:app --reload

# Terminal 2: Celery worker
celery -A app.core.celery_app worker --loglevel=info
```

> **API documentation:** http://localhost:8000/docs

---

## 3. Project Structure

```
scanpy-platform/
├── backend/              # FastAPI application
│   ├── app/
│   │   ├── api/          # REST endpoints
│   │   ├── models/       # Database models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/     # Business logic
│   │   ├── tasks/        # Celery tasks
│   │   └── core/         # Configuration
│   └── venv/             # Virtual environment
├── data/
│   ├── jobs/             # Job data
│   └── test_data/        # Sample datasets
└── docker-compose.yml
```

---

## 4. Development Commands

```bash
# Daily startup
docker-compose up -d
source backend/venv/bin/activate

# Daily shutdown
docker-compose down
deactivate

# Database access
docker exec -it scanpy-postgres psql -U scanpy_user -d scanpy_db

# View logs
docker-compose logs -f postgres
docker-compose logs -f redis
```

---

## 5. Tech Stack

| Component | Technology |
|-----------|-----------|
| API framework | FastAPI |
| Async tasks | Celery |
| Database | PostgreSQL |
| Task queue | Redis |
| Analysis | Scanpy |

---

## Security Notice

**This is a development/demo configuration.**

Default credentials are intentionally simple for ease of testing:
- Database password: `scanpy_pass`
- No authentication enabled

**For production use:**
1. Review `SECURITY.md` for hardening guidelines
2. Change all default passwords
3. Enable authentication
4. Restrict network access
5. Use HTTPS/TLS

See `.env.example` for configuration options.