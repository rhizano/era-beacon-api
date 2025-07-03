from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes import auth, beacons, presence_logs

# Create FastAPI application
app = FastAPI(
    title=settings.project_name,
    description="API for tracking user presence via BLE Beacons, including user authentication and beacon/presence log management.",
    version="1.0.0",
    openapi_url=f"{settings.api_v1_str}/openapi.json",
    docs_url=f"{settings.api_v1_str}/docs",
    redoc_url=f"{settings.api_v1_str}/redoc"
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix=settings.api_v1_str)
app.include_router(beacons.router, prefix=settings.api_v1_str)
app.include_router(presence_logs.router, prefix=settings.api_v1_str)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "BLE Beacon Presence Tracking API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
