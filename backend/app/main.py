from fastapi import FastAPI
from app.core.config import settings

# Import routers from modules
from app.modules.users.router import router as users_router
from app.modules.branches.router import router as branches_router
from app.modules.exams.router import router as exams_router
from app.modules.financial.router import router as financial_router
from app.modules.reports.router import router as reports_router

app = FastAPI(title=settings.APP_NAME)

# Include routers
app.include_router(users_router, prefix="/api/v1/users", tags=["users"])
app.include_router(branches_router, prefix="/api/v1/branches", tags=["branches"])
app.include_router(exams_router, prefix="/api/v1/exams", tags=["exams"])
app.include_router(financial_router, prefix="/api/v1/financial", tags=["financial"])
app.include_router(reports_router, prefix="/api/v1/reports", tags=["reports"])


# Startup event
@app.on_event("startup")
async def startup_event():
    print("🚀 Mohamed Abdrabou — Hello from Itkan Academy.")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    print("🛑 Mohamed Abdrabou — Goodbye from Itkan Academy.")


# Test endpoint
@app.get("/test", tags=["test"])
async def test():
    return {"status": "ok"}
