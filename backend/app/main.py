# app/main.py
from fastapi import FastAPI
from app.core.config import settings
from app.modules.users.router import router as users_router

app = FastAPI(title=settings.APP_NAME)


app.include_router(users_router, prefix="/api/v1/users", tags=["users"])


@app.on_event("startup")
async def startup_event():
    print("🚀 Mohamed Abdrabou — Hello from Itkan Academy.")


@app.on_event("shutdown")
async def shutdown_event():
    print("🛑 Mohamed Abdrabou — Goodbye from Itkan Academy.")


@app.get("/test", tags=["test1"])
async def test():
    return {"status": "ok"}


# Include routers from modules later
# from app.modules.users.router import router as users_router
# app.include_router(users_router, prefix="/api/v1/users", tags=["users"])
