"""
IndoxRouter Server

This is the main entry point for the IndoxRouter server application.
The server provides a FastAPI-based API for accessing various AI providers and models.
It connects to an external website database to validate API keys.
"""

# Try to load encrypted environment variables if available
try:
    import sys
    import os

    # Add the parent directory to path to find load_encrypted_env.py
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    import load_encrypted_env

    load_encrypted_env.load()
except ImportError:
    # If the module is not found, continue without it
    print(
        "Note: load_encrypted_env module not found. Using standard environment variables."
    )
except Exception as e:
    # If there's an error loading the encrypted env, log it but continue
    print(f"Warning: Could not load encrypted environment variables: {e}")

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers import auth, chat, completion, embedding, image, model
from app.core.config import settings
from app.db.database import init_db
from app.resources import Chat, Completions, Embeddings, Images

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
    # Initialize connection to the external website database
    if settings.DATABASE_URL:
        if init_db():
            print(
                f"Successfully connected to external website database at {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else settings.DATABASE_URL}"
            )
        else:
            print("Error: Failed to connect to external website database.")
            import sys

            sys.exit(1)
    else:
        print(
            "Error: DATABASE_URL not set. Connection to external website database is required."
        )
        import sys

        sys.exit(1)


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
        reload=False,
    )


if __name__ == "__main__":
    run_server()
