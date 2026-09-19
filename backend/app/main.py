"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import v1_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""
    # Startup
    print("🚀 Starting AI Listing Automation Platform...")
    print(f"📡 Database: {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else 'configured'}")
    print(f"🔑 Debug mode: {settings.DEBUG}")
    yield
    # Shutdown
    print("🛑 Shutting down...")
    from app.core.database import engine
    await engine.dispose()


app = FastAPI(
    title="AI Multi-Marketplace Seller Listing Automation",
    description="Create products once, AI generates marketplace-specific listings for Amazon, Flipkart, and Meesho.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register custom exception handlers
register_exception_handlers(app)

# Mount API router
app.include_router(v1_router)


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "1.0.0"}
