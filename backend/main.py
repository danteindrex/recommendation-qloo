from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from app.core.config import settings
from app.core.database import init_db
from app.api.routes import cultural, analytics, admin, websocket, cultural_intelligence, enterprise, privacy_admin, cultural_intelligence_mock
from app.services.kafka_service import kafka_service
from app.services.stream_processor import stream_processor
from app.services.notification_service import notification_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    # Validate required Gemini API key
    if not settings.GOOGLE_GEMINI_API_KEY:
        raise Exception("GOOGLE_GEMINI_API_KEY is required. Please set your Gemini API key in the .env file.")
    
    print(f"✅ Gemini API key configured successfully")
    
    await init_db()
    
    # Start real-time processing services
    try:
        await kafka_service.start()
        await stream_processor.start()
        await notification_service.start()
    except Exception as e:
        print(f"Warning: Failed to start real-time services: {e}")
    
    yield
    
    # Shutdown
    try:
        await kafka_service.stop()
        await stream_processor.stop()
        await notification_service.stop()
    except Exception as e:
        print(f"Warning: Error stopping real-time services: {e}")


app = FastAPI(
    title="CulturalOS API",
    description="Cultural Intelligence Platform API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
# app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])  # Disabled authentication
app.include_router(cultural.router, prefix="/api/cultural", tags=["cultural"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(cultural_intelligence.router, prefix="/api/cultural-intelligence", tags=["cultural-intelligence"])
app.include_router(cultural_intelligence_mock.router, prefix="/api/cultural-mock", tags=["cultural-intelligence-mock"])
app.include_router(enterprise.router, prefix="/api/enterprise", tags=["enterprise"])
app.include_router(privacy_admin.router, prefix="/api/privacy-admin", tags=["privacy-admin"])

app.include_router(websocket.router, prefix="/ws", tags=["websocket"])


@app.get("/")
async def root():
    return {"message": "CulturalOS API is running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    )