# Itkan Academy Backend
# Project Structure — itkan-Academy
```bash
itkan-Academy/
├─ .venv/
│
├─ backend/
│  ├─ __init__.py
│  ├─ main.py
│  ├─ alembic.ini
│  ├─ .env
│  ├─ requirements.txt
│  │
│  ├─ alembic/
│  │   └─ versions/
│  │       └─ env.py
│  │
│  ├─ app/
│  │   ├─ core/
│  │   │   ├─ __init__.py
│  │   │   ├─ config.py
│  │   │   ├─ security.py
│  │   │   ├─ lauth.py
│  │   │   ├─ authrization.py
│  │   │   └─ utils.py
│  │   │
│  │   ├─ db/
│  │   │   ├─ __init__.py
│  │   │   ├─ session.py
│  │   │   ├─ base.py
│  │   │   └─ init_db.py
│  │   │
│  │   ├─ api/
│  │   │   ├─ __init__.py
│  │   │   └─ v2/
│  │   │       ├─ __init__.py
│  │   │       ├─ role.py
│  │   │       ├─ users.py
│  │   │       ├─ permission.py
│  │   │       └─ permission_role.py
│  │   │
│  │   ├─ modules/
│  │   │   ├─ __init__.py
│  │   │   │
│  │   │   ├─ users/
│  │   │   │   ├─ __init__.py
│  │   │   │   ├─ models.py
│  │   │   │   ├─ schemas.py
│  │   │   │   ├─ crud.py
│  │   │   │   └─ router.py
│  │   │   │
│  │   │   ├─ branches/
│  │   │   │   ├─ __init__.py
│  │   │   │   ├─ models.py
│  │   │   │   ├─ schemas.py
│  │   │   │   ├─ crud.py
│  │   │   │   └─ router.py
│  │   │   │
│  │   │   ├─ exams/
│  │   │   │   ├─ __init__.py
│  │   │   │   ├─ models/ (exam.py, exam_question.py, exam_answer.py, exam_attempt.py)
│  │   │   │   ├─ schemas/ (exam.py, exam_question.py, exam_answer.py, exam_attempt.py)
│  │   │   │   ├─ crud/ (exam.py, exam_question.py, exam_answer.py, exam_attempt.py)
│  │   │   │   └─ router/ (exam.py, exam_question.py, exam_answer.py, exam_attempt.py)
│  │   │   │
│  │   │   ├─ audits/
│  │   │   │   ├─ __init__.py
│  │   │   │   ├─ models/ (audit_log.py, ...)
│  │   │   │   ├─ schemas/ (audit_log.py, ...)
│  │   │   │   ├─ crud/ (audit_log.py, ...)
│  │   │   │   └─ router/ (audit_log.py, ...)
│  │   │   │
│  │   │   ├─ permissions/
│  │   │   │   ├─ __init__.py
│  │   │   │   ├─ models/ (permission.py, permission_role.py)
│  │   │   │   ├─ schemas/ (permission.py, permission_role.py)
│  │   │   │   ├─ crud/ (permission.py, permission_role.py)
│  │   │   │   └─ router/ (permission.py, permission_role.py)
│  │   │   │
│  │   │   ├─ attendance/
│  │   │   │   ├─ __init__.py
│  │   │   │   ├─ models.py
│  │   │   │   ├─ schemas.py
│  │   │   │   ├─ crud.py
│  │   │   │   └─ router.py
│  │   │   │
│  │   │   ├─ roles/
│  │   │   │   ├─ __init__.py
│  │   │   │   ├─ models.py
│  │   │   │   ├─ schemas.py
│  │   │   │   ├─ crud.py
│  │   │   │   └─ router.py
│  │   │   │
│  │   │   ├─ classes/
│  │   │   │   ├─ __init__.py
│  │   │   │   ├─ models.py
│  │   │   │   ├─ schemas.py
│  │   │   │   ├─ crud.py
│  │   │   │   └─ router.py
│  │   │   │
│  │   │   ├─ notifications/
│  │   │   │   ├─ __init__.py
│  │   │   │   ├─ models.py
│  │   │   │   ├─ schemas.py
│  │   │   │   ├─ crud.py
│  │   │   │   └─ router.py
│  │   │   │
│  │   │   ├─ question_bank/
│  │   │   │   ├─ __init__.py
│  │   │   │   ├─ models.py
│  │   │   │   ├─ schemas.py
│  │   │   │   ├─ crud.py
│  │   │   │   └─ router.py
│  │   │   │
│  │   │   ├─ students/
│  │   │   │   ├─ __init__.py
│  │   │   │   ├─ models.py
│  │   │   │   ├─ schemas.py
│  │   │   │   ├─ crud.py
│  │   │   │   └─ router.py
│  │   │   │
│  │   │   ├─ staff/
│  │   │   │   ├─ __init__.py
│  │   │   │   ├─ models.py
│  │   │   │   ├─ schemas.py
│  │   │   │   ├─ crud.py
│  │   │   │   └─ router.py
│  │   │   │
│  │   │   ├─ evaluations/
│  │   │   │   ├─ __init__.py
│  │   │   │   ├─ models/ (daily_evaluation.py, ...)
│  │   │   │   ├─ schemas/ (daily_evaluation.py, ...)
│  │   │   │   ├─ crud/ (daily_evaluation.py, ...)
│  │   │   │   └─ router/ (daily_evaluation.py, ...)
│  │   │   │
│  │   │   ├─ financial/
│  │   │   │   ├─ __init__.py
│  │   │   │   ├─ models/ (invoice.py, payment.py)
│  │   │   │   ├─ schemas/ (invoice.py, payment.py)
│  │   │   │   ├─ crud/ (invoice.py, payment.py)
│  │   │   │   └─ router/ (invoice.py, payment.py)
│  │   │   │
│  │   │   └─ reports/
│  │   │       ├─ __init__.py
│  │   │       ├─ models/ (report_job.py, ...)
│  │   │       ├─ schemas/ (report_job.py, ...)
│  │   │       ├─ crud/ (report_job.py, ...)
│  │   │       └─ router/ (report_job.py, ...)
│  │   │
│  │   ├─ workers/
│  │   │   ├─ __init__.py
│  │   │   ├─ celery_app.py
│  │   │   └─ tasks/
│  │   │       ├─ __init__.py
│  │   │       ├─ email_tasks.py
│  │   │       ├─ report_tasks.py
│  │   │       └─ finance_tasks.py
│  │   │
│  │   ├─ services/
│  │   │   ├─ __init__.py
│  │   │   ├─ email_service.py
│  │   │   ├─ notification_service.py
│  │   │   └─ report_service.py
│  │   │
│  │   ├─ models/
│  │   │   └─ __init__.py
│  │   │
│  │   ├─ schemas/
│  │   │   └─ __init__.py
│  │   │
│  │   ├─ run.py
│  │   └─ tests/
│  │       ├─ __init__.py
│  │       └─ test_example.py
│
├─ .gitignore
└─ README.md
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
