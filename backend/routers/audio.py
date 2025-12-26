from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid
import os
import aiofiles

from config import get_settings
from .projects import projects_db

router = APIRouter()
settings = get_settings()


class AudioUpload(BaseModel):
    id: str
    project_id: str
    filename: str
    url: str
    duration_seconds: Optional[float] = None
    created_at: datetime


class AudioResponse(BaseModel):
    success: bool
    data: Optional[AudioUpload] = None
    message: Optional[str] = None


class TTSRequest(BaseModel):
    project_id: str
    text: str
    voice: str = "default"


@router.post("/upload/{project_id}", response_model=AudioResponse)
async def upload_audio(project_id: str, file: UploadFile = File(...)):
    """Upload an audio file for a project."""
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Validate file type
    allowed_types = ["audio/mpeg", "audio/wav", "audio/mp3", "audio/x-wav"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: MP3, WAV"
        )
    
    # Generate unique filename
    file_ext = os.path.splitext(file.filename)[1] or ".mp3"
    audio_id = str(uuid.uuid4())
    filename = f"{audio_id}{file_ext}"
    filepath = os.path.join(settings.upload_dir, filename)
    
    # Save file
    async with aiofiles.open(filepath, 'wb') as f:
        content = await file.read()
        await f.write(content)
    
    # Update project
    audio_url = f"/uploads/{filename}"
    projects_db[project_id]["audio_url"] = audio_url
    projects_db[project_id]["updated_at"] = datetime.utcnow()
    
    audio_data = {
        "id": audio_id,
        "project_id": project_id,
        "filename": file.filename,
        "url": audio_url,
        "duration_seconds": None,  # Could be calculated
        "created_at": datetime.utcnow()
    }
    
    return AudioResponse(
        success=True,
        data=AudioUpload(**audio_data),
        message="Audio uploaded successfully"
    )


@router.delete("/{project_id}")
async def delete_audio(project_id: str):
    """Remove audio from a project."""
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = projects_db[project_id]
    audio_url = project.get("audio_url")
    
    if audio_url:
        # Delete file
        filepath = os.path.join(settings.upload_dir, os.path.basename(audio_url))
        if os.path.exists(filepath):
            os.remove(filepath)
    
    project["audio_url"] = None
    project["updated_at"] = datetime.utcnow()
    
    return {"success": True, "message": "Audio removed successfully"}


@router.post("/tts", response_model=AudioResponse)
async def generate_tts(request: TTSRequest):
    """Generate text-to-speech audio (placeholder for TTS integration)."""
    if request.project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # TODO: Integrate with a TTS service (Google Cloud TTS, ElevenLabs, etc.)
    # For now, return a placeholder response
    raise HTTPException(
        status_code=501,
        detail="TTS feature coming soon. Please upload an audio file instead."
    )
