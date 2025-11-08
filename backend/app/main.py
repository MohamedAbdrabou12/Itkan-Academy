from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_router
from app.core.config import settings
from app.core.middleware import BranchScopeMiddleware
from fastapi_pagination import add_pagination


# Create FastAPI app instance
app = FastAPI(
    title="Itkan Academy",
    version="1.0",
    description="Itkan Academy API — powered by Mohamed Abdrabou",
)

add_pagination(app)


# Add CORS middleware (if frontend will call this API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add BranchScopeMiddleware BEFORE registering API routers
app.add_middleware(BranchScopeMiddleware)

# Include API v1 router
app.include_router(api_router, prefix="/api/v1")


# Main application startup event
@app.on_event("startup")
async def on_startup():
    print("🚀 Mohamed Abdrabou — Itkan Academy API started successfully.")


# Application shutdown event
@app.on_event("shutdown")
async def on_shutdown():
    print("🛑 Mohamed Abdrabou — Itkan Academy API stopped.")


# Health check endpoint
@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "ok", "app": settings.APP_NAME}


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    return {"message": "Welcome to Itkan Academy API 👋"}
