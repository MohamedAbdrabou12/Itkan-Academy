# Itkan Academy Backend

# Project Structure (start point)
```bash

itkan-backend/
├─ .venv/                              # Virtual environment folder
├─ .env                                # Environment variables file
├─ requirements.txt                    # Python dependencies list
├─ alembic/                            # Database migrations folder
│  └─ versions/                        # Individual migration versions
│
├─ app/
│  ├─ __init__.py                      # Marks this directory as a Python package
│  ├─ main.py                          # Entry point for running the FastAPI server
│  │
│  ├─ core/                            # Core settings and global configurations
│  │  ├─ __init__.py
│  │  ├─ config.py                     # Environment and app configuration
│  │  ├─ security.py                   # JWT authentication and password hashing
│  │  ├─ logging_config.py             # Logging setup and configuration
│  │  └─ utils.py                      # General utility functions
│  │
│  ├─ db/                              # Database management layer
│  │  ├─ __init__.py
│  │  ├─ session.py                    # SQLAlchemy engine and session setup
│  │  ├─ base.py                       # Base model import for Alembic autogeneration
│  │  └─ init_db.py                    # Initialize database with seed data
│  │
│  ├─ api/                             # REST API endpoints
│  │  ├─ __init__.py
│  │  └─ v1/                           # API version 1 routes
│  │     ├─ __init__.py
│  │     ├─ deps.py                    # Shared dependencies (e.g., DB session, auth)
│  │     ├─ users.py                   # User-related API routes
│  │     ├─ branches.py                # Branch-related API routes
│  │     ├─ exams.py                   # Exam-related API routes
│  │     ├─ finance.py                 # Financial-related API routes
│  │     └─ reports.py                 # Report-related API routes
│  │
│  ├─ modules/                         # Business logic (each module in its own folder)
│  │  ├─ __init__.py
│  │  ├─ users/
│  │  │  ├─ __init__.py
│  │  │  ├─ models.py                  # SQLAlchemy models for users
│  │  │  ├─ schemas.py                 # Pydantic schemas for users
│  │  │  ├─ crud.py                    # CRUD operations for users
│  │  │  ├─ service.py                 # User-related business logic (auth, roles, etc.)
│  │  │  └─ router.py                  # Connect user module endpoints to the API
│  │  │
│  │  ├─ branches/
│  │  │  ├─ __init__.py
│  │  │  ├─ models.py                  # Branch models
│  │  │  ├─ schemas.py                 # Branch schemas
│  │  │  ├─ crud.py                    # Branch CRUD operations
│  │  │  ├─ service.py                 # Branch-specific business logic
│  │  │  └─ router.py                  # Branch endpoints router
│  │  │
│  │  ├─ exams/
│  │  │  ├─ __init__.py
│  │  │  ├─ models.py                  # Exam models
│  │  │  ├─ schemas.py                 # Exam schemas
│  │  │  ├─ crud.py                    # Exam CRUD operations
│  │  │  ├─ service.py                 # Exam-specific logic
│  │  │  └─ router.py                  # Exam endpoints router
│  │  │
│  │  ├─ financial/
│  │  │  ├─ __init__.py
│  │  │  ├─ models.py                  # Financial models
│  │  │  ├─ schemas.py                 # Financial schemas
│  │  │  ├─ crud.py                    # Financial CRUD operations
│  │  │  ├─ service.py                 # Financial-related logic
│  │  │  └─ router.py                  # Financial endpoints router
│  │  │
│  │  └─ reports/
│  │      ├─ __init__.py
│  │      ├─ models.py                 # Report models
│  │      ├─ schemas.py                # Report schemas
│  │      ├─ crud.py                   # Report CRUD operations
│  │      ├─ service.py                # Report generation logic
│  │      └─ router.py                 # Report endpoints router
│  │
│  ├─ workers/                         # Background tasks (Celery workers)
│  │  ├─ __init__.py
│  │  ├─ celery_app.py                 # Celery setup and Redis integration
│  │  └─ tasks/
│  │     ├─ __init__.py
│  │     ├─ email_tasks.py             # Email sending background tasks
│  │     ├─ report_tasks.py            # Report generation tasks
│  │     └─ finance_tasks.py           # Asynchronous financial processing tasks
│  │
│  ├─ services/                        # Shared reusable services
│  │  ├─ __init__.py
│  │  ├─ email_service.py              # General email sending service
│  │  ├─ notification_service.py       # Notification handling service
│  │  └─ report_service.py             # Common report generation service
│  │
│  ├─ models/                          # Global shared models (if needed)
│  │  └─ __init__.py
│  │
│  ├─ schemas/                         # Shared Pydantic schemas
│  │  └─ __init__.py
│  │
│  └─ tests/                           # Unit tests
│      ├─ __init__.py
│      └─ test_example.py              # Example test file
│
└─ README.md                           # Project documentation file
```


## Project Setup

Follow these steps after cloning the repository:

1. Clone the repository
```bash
git clone <repo_url>
cd <repo_folder>


2.Create and activate a virtual environment

Linux/macOS: 
$: python3 -m venv .venv
$: source .venv/bin/activate

Windows:
$:python -m venv .venv
$: .venv\Scripts\activate

3.Install dependencies
$: pip install -r requirements.txt

4.Create a .env file
Add your database configuration:

```POSTGRES_USER=<your_db_user>
POSTGRES_PASSWORD=<your_db_password>
POSTGRES_DB=<your_db_name>
POSTGRES_HOST=<your_db_host>
POSTGRES_PORT=<your_db_port>
DATABASE_URL=postgresql://<user>:<password>@<host>:<port>/<db>

5.Run Alembic migrations
$: alembic upgrade head

6.Start the FastAPI server
$: uvicorn app.main:app --reload


Open Swagger UI
Navigate to http://127.0.0.1:8000/docs
 to explore and test the API.
```
Additional Notes

Make sure PostgreSQL server is running and accessible from your .env configuration.

All modules are structured to allow easy addition of new endpoints and business logic.

Background tasks (Celery) require Redis to be running for asynchronous processing.

Unit tests can be run using:
```bash
 pytest app/tests
```
>> Note: Always activate the virtual environment before running commands to ensure dependencies are used from .venv.
