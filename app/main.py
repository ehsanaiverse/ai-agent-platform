import os
import sys
from pathlib import Path

# Ensure project root directory is on sys.path for direct execution (python app/main.py)
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.middleware.request_logger import RequestLoggerMiddleware
from app.api.routers import api_router
from app.core.config import settings
from app.core.logger import setup_logging
from app.exceptions.handlers import register_exception_handlers

setup_logging()

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    version="1.0.0",
)

# CORS middleware for cross-origin client compatibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging middleware
app.add_middleware(RequestLoggerMiddleware)

# Register global exception handlers
register_exception_handlers(app)

# Register application API routers
app.include_router(api_router)

@app.get("/")
async def root():
    return {
        "status": "online",
        "message": "Welcome to AI Agent Platform",
        "version": "1.0.0",
    }


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )