📘 Itkan Academy Backend
🧱 Project Structure (start point)
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
│  │  ├─ users/
│  │  │  ├─ __init__.py
│  │  │  ├─ models.py                  # SQLAlchemy models for users
│  │  │  ├─ schemas.py                 # Pydantic schemas for users
│  │  │  ├─ crud.py                    # CRUD operations for users
│  │  │  ├─ service.py                 # User-related business logic
│  │  │  └─ router.py                  # Connect user module endpoints
│  │  ├─ branches/
│  │  │  ├─ __init__.py
│  │  │  ├─ models.py                  # Branch models
│  │  │  ├─ schemas.py                 # Branch schemas
│  │  │  ├─ crud.py                    # Branch CRUD operations
│  │  │  ├─ service.py                 # Branch-specific logic
│  │  │  └─ router.py                  # Branch endpoints router
│  │  ├─ exams/
│  │  │  ├─ __init__.py
│  │  │  ├─ models.py                  # Exam models
│  │  │  ├─ schemas.py                 # Exam schemas
│  │  │  ├─ crud.py                    # Exam CRUD operations
│  │  │  ├─ service.py                 # Exam-specific logic
│  │  │  └─ router.py                  # Exam endpoints router
│  │  ├─ financial/
│  │  │  ├─ __init__.py
│  │  │  ├─ models.py                  # Financial models
│  │  │  ├─ schemas.py                 # Financial schemas
│  │  │  ├─ crud.py                    # Financial CRUD operations
│  │  │  ├─ service.py                 # Financial logic
│  │  │  └─ router.py                  # Financial endpoints router
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
│  │     └─ finance_tasks.py           # Asynchronous financial tasks
│  │
│  ├─ services/                        # Shared reusable services
│  │  ├─ __init__.py
│  │  ├─ email_service.py              # Email sending service
│  │  ├─ notification_service.py       # Notification handling service
│  │  └─ report_service.py             # Report generation service
│  │
│  ├─ tests/                           # Unit tests
│  │  ├─ __init__.py
│  │  └─ test_example.py               # Example test file
│
└─ README.md                           # Project documentation file
```


⚙️ Project Setup

```bash
# 1. Clone the repository
git clone <repo_url>
cd <repo_folder>

# 2. Create and activate a virtual environment

# Linux/macOS
python3 -m venv .venv
source .venv/bin/activate

# Windows
python -m venv .venv
.venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create a .env file with database credentials
POSTGRES_USER=<your_db_user>
POSTGRES_PASSWORD=<your_db_password>
POSTGRES_DB=<your_db_name>
POSTGRES_HOST=<your_db_host>
POSTGRES_PORT=<your_db_port>
DATABASE_URL=postgresql://<user>:<password>@<host>:<port>/<db>

# 5. Run Alembic migrations
alembic upgrade head

# 6. Start the FastAPI server manually
uvicorn app.main:app --reload

# OR use the shortcut script (run.py)
python run.py

# 7. Open Swagger UI
# Visit:
http://127.0.0.1:8000/docs
```

🧾 Notes

Windows users: automatically uses --loop asyncio since uvloop isn’t supported.

Linux/macOS users: runs with uvloop (faster).

Always activate your virtual environment before running commands.

Ensure PostgreSQL is running and credentials in .env are valid.

Celery background tasks require Redis to be active.

Run tests with:

```bash
pytest app/tests
```