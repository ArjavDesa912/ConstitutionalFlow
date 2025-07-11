
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from src.core.config import settings
from src.core.database import create_tables
from src.api.routes import constitutional, tasks, feedback, annotators

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Adaptive Constitutional AI Platform with Intelligent Human Feedback Orchestration",
    version="1.0.0",
    debug=settings.DEBUG
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(constitutional.router, prefix="/api", tags=["Constitutional"])
app.include_router(tasks.router, prefix="/api", tags=["Tasks"])
app.include_router(feedback.router, prefix="/api", tags=["Feedback"])
app.include_router(annotators.router, prefix="/api", tags=["Annotators"])

@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup"""
    try:
        create_tables()
        print("Database tables created successfully")
    except Exception as e:
        print(f"Error creating database tables: {e}")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to ConstitutionalFlow",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Basic health check - can be enhanced with database connectivity check
        return {
            "status": "healthy",
            "timestamp": "2024-01-01T00:00:00Z",
            "version": "1.0.0"
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Health check failed: {str(e)}")

@app.get("/api/docs")
async def get_api_docs():
    """Get API documentation"""
    return {
        "message": "API documentation available at /docs",
        "swagger_ui": "/docs",
        "redoc": "/redoc"
    }
