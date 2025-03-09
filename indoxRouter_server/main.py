"""
IndoxRouter Server

This is the main entry point for the IndoxRouter server application.
The server provides a FastAPI-based API for accessing various AI providers and models.
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers import auth, chat, completion, embedding, image, model
from app.core.config import settings

app = FastAPI(
    title="IndoxRouter Server",
    description="A unified API for various AI providers",
    version="0.2.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1", tags=["Authentication"])
app.include_router(model.router, prefix="/api/v1", tags=["Models"])
app.include_router(chat.router, prefix="/api/v1", tags=["Chat"])
app.include_router(completion.router, prefix="/api/v1", tags=["Completion"])
app.include_router(embedding.router, prefix="/api/v1", tags=["Embedding"])
app.include_router(image.router, prefix="/api/v1", tags=["Image"])


@app.on_event("startup")
async def startup():
    """Initialize services on startup."""
    # Initialize database and services
    pass


@app.on_event("shutdown")
async def shutdown():
    """Clean up resources on shutdown."""
    # Cleanup resources
    pass


@app.get("/", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "message": "IndoxRouter Server is running"}


def run_server():
    """Run the server using uvicorn."""
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )


if __name__ == "__main__":
    run_server()
