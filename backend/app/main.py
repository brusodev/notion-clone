from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis import Redis
import logging
from app.core.config import settings
from app.core.database import Base, engine
from app.api.v1 import auth, workspaces, pages, blocks, invitations, search, comments

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup event: Create database tables
@app.on_event("startup")
async def startup_event():
    """Create database tables on startup"""
    logger.info("=" * 60)
    logger.info("Starting Notion Clone API")
    logger.info("=" * 60)

    try:
        logger.info("Initializing models...")
        # Import all models to ensure they are registered with Base.metadata
        from app.models import (
            user, workspace, workspace_member, page, page_version, page_favorite, block, invitation,
            comment, comment_reaction, comment_mention, comment_attachment
        )
        # Note: Using Alembic migrations instead of create_all for better control
        # Base.metadata.create_all(bind=engine)
        logger.info("✓ Models initialized successfully!")
    except Exception as e:
        logger.error(f"✗ Error initializing models: {e}")
        raise

    logger.info("=" * 60)

# Initialize Redis client for token blacklist
try:
    redis_client = Redis.from_url(settings.REDIS_URL, decode_responses=True)
    redis_client.ping()
    auth.redis_client = redis_client
    logger.info("Redis connection established")
except Exception as e:
    logger.warning(f"Redis connection failed: {e}. Token blacklist will be disabled.")
    auth.redis_client = None

# Include routers
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(workspaces.router, prefix=f"{settings.API_V1_STR}/workspaces", tags=["workspaces"])
app.include_router(pages.router, prefix=f"{settings.API_V1_STR}/pages", tags=["pages"])
app.include_router(blocks.router, prefix=f"{settings.API_V1_STR}/blocks", tags=["blocks"])
app.include_router(invitations.router, prefix=f"{settings.API_V1_STR}/invitations", tags=["invitations"])
app.include_router(search.router, prefix=f"{settings.API_V1_STR}/search", tags=["search"])
app.include_router(comments.router, prefix=f"{settings.API_V1_STR}/comments", tags=["comments"])


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "project": settings.PROJECT_NAME
    }


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Notion Clone API",
        "version": settings.VERSION,
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
