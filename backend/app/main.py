from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1 import api_router


# Create FastAPI app instance
app = FastAPI(
    title=settings.APP_NAME,
    version="2.0",
    description="Itkan Academy API — powered by Mohamed Abdrabou",
)

# Add CORS middleware (if frontend will call this API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
    ],  # you can add specific origins in production as  ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API v2 router
app.include_router(api_router, prefix="/api/v1")


# Main application entry point
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
