from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from config import get_settings
from routers import projects, scenes, render, audio

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="AI-Powered Manim Video Generator API",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create directories if they don't exist
os.makedirs(settings.upload_dir, exist_ok=True)
os.makedirs(settings.output_dir, exist_ok=True)

# Mount static files for serving videos
app.mount("/outputs", StaticFiles(directory=settings.output_dir), name="outputs")
app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")

# Include routers
app.include_router(projects.router, prefix="/api/projects", tags=["Projects"])
app.include_router(scenes.router, prefix="/api/scenes", tags=["Scenes"])
app.include_router(render.router, prefix="/api/render", tags=["Render"])
app.include_router(audio.router, prefix="/api/audio", tags=["Audio"])


@app.get("/")
async def root():
    return {"message": "Manim Video Generator API", "status": "running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
