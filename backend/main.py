"""
AI Video Creator Agent - Backend Server
FastAPI server for video generation workflow
"""

import os
import uuid
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Optional, List

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from dotenv import load_dotenv

from routes.video import router as video_router
from routes.status import router as status_router

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="AI Video Creator Agent",
    description="Generate videos from text prompts using AI",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "./output"))
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/output", StaticFiles(directory=str(OUTPUT_DIR)), name="output")

# Mount frontend static files
FRONTEND_DIR = Path(__file__).parent.parent / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="frontend")

# Include routers
app.include_router(video_router, prefix="/api", tags=["Video"])
app.include_router(status_router, prefix="/api", tags=["Status"])

@app.get("/")
async def root():
    """Serve the frontend application"""
    # Try to serve from relative frontend path
    frontend_path = Path(__file__).parent.parent / "frontend" / "index.html"
    if frontend_path.exists():
        return FileResponse(str(frontend_path))
    
    # Fallback to JSON response
    return {
        "status": "online",
        "service": "AI Video Creator Agent",
        "version": "1.0.0",
        "message": "Frontend not found. Please ensure frontend files are in the frontend/ directory."
    }

@app.get("/health")
async def health_check():
    """Health check for monitoring"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=True
    )
