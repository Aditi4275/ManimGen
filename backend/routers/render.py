from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

from services.render_service import render_scene, compile_project
from .scenes import scenes_db, SceneStatus, Scene
from .projects import projects_db

router = APIRouter()

# Render jobs storage
render_jobs: dict = {}


class RenderJob(BaseModel):
    id: str
    scene_id: Optional[str] = None
    project_id: Optional[str] = None
    status: str
    progress: int = 0
    output_url: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime


class RenderResponse(BaseModel):
    success: bool
    data: Optional[RenderJob] = None
    message: Optional[str] = None


async def process_render(job_id: str, scene_id: str):
    """Background task to render a scene."""
    job = render_jobs[job_id]
    scene = scenes_db[scene_id]
    
    try:
        job["status"] = "rendering"
        job["progress"] = 10
        scene["status"] = SceneStatus.rendering
        
        # Call render service
        result = await render_scene(scene["code"], scene_id)
        
        job["progress"] = 100
        job["status"] = "completed"
        job["output_url"] = result["video_url"]
        
        scene["video_url"] = result["video_url"]
        scene["thumbnail_url"] = result.get("thumbnail_url")
        scene["duration_seconds"] = result.get("duration", 5.0)
        scene["status"] = SceneStatus.completed
        scene["updated_at"] = datetime.utcnow()
        
    except Exception as e:
        job["status"] = "failed"
        job["error_message"] = str(e)
        scene["status"] = SceneStatus.failed
        scene["error_message"] = str(e)
        scene["updated_at"] = datetime.utcnow()


@router.post("/scene/{scene_id}", response_model=RenderResponse)
async def render_single_scene(scene_id: str, background_tasks: BackgroundTasks):
    """Start rendering a single scene."""
    if scene_id not in scenes_db:
        raise HTTPException(status_code=404, detail="Scene not found")
    
    scene = scenes_db[scene_id]
    
    if not scene.get("code"):
        raise HTTPException(status_code=400, detail="Scene has no code to render")
    
    job_id = str(uuid.uuid4())
    now = datetime.utcnow()
    
    job = {
        "id": job_id,
        "scene_id": scene_id,
        "project_id": scene["project_id"],
        "status": "pending",
        "progress": 0,
        "output_url": None,
        "error_message": None,
        "created_at": now
    }
    
    render_jobs[job_id] = job
    
    # Start background render task
    background_tasks.add_task(process_render, job_id, scene_id)
    
    return RenderResponse(
        success=True,
        data=RenderJob(**job),
        message="Render job started"
    )


@router.get("/job/{job_id}", response_model=RenderResponse)
async def get_render_status(job_id: str):
    """Get the status of a render job."""
    if job_id not in render_jobs:
        raise HTTPException(status_code=404, detail="Render job not found")
    
    return RenderResponse(
        success=True,
        data=RenderJob(**render_jobs[job_id])
    )


async def process_export(job_id: str, project_id: str):
    """Background task to export a complete project."""
    job = render_jobs[job_id]
    project = projects_db[project_id]
    
    try:
        job["status"] = "compiling"
        job["progress"] = 10
        
        # Get all completed scenes
        scene_ids = project.get("scenes", [])
        scenes = [scenes_db[sid] for sid in scene_ids if sid in scenes_db]
        scenes.sort(key=lambda s: s["order_index"])
        
        # Compile all scenes
        result = await compile_project(
            scenes=scenes,
            project_id=project_id,
            audio_url=project.get("audio_url")
        )
        
        job["progress"] = 100
        job["status"] = "completed"
        job["output_url"] = result["video_url"]
        
    except Exception as e:
        job["status"] = "failed"
        job["error_message"] = str(e)


@router.post("/export/{project_id}", response_model=RenderResponse)
async def export_project(project_id: str, background_tasks: BackgroundTasks):
    """Export all scenes as a compiled video."""
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = projects_db[project_id]
    scene_ids = project.get("scenes", [])
    
    if not scene_ids:
        raise HTTPException(status_code=400, detail="Project has no scenes")
    
    # Check all scenes are rendered
    for sid in scene_ids:
        if sid in scenes_db:
            scene = scenes_db[sid]
            if scene["status"] != SceneStatus.completed:
                raise HTTPException(
                    status_code=400,
                    detail=f"Scene {sid} is not rendered yet"
                )
    
    job_id = str(uuid.uuid4())
    now = datetime.utcnow()
    
    job = {
        "id": job_id,
        "scene_id": None,
        "project_id": project_id,
        "status": "pending",
        "progress": 0,
        "output_url": None,
        "error_message": None,
        "created_at": now
    }
    
    render_jobs[job_id] = job
    
    background_tasks.add_task(process_export, job_id, project_id)
    
    return RenderResponse(
        success=True,
        data=RenderJob(**job),
        message="Export job started"
    )


async def process_render_all_and_combine(job_id: str, project_id: str):
    """Background task to render all scenes and combine them into one video."""
    job = render_jobs[job_id]
    project = projects_db[project_id]
    
    try:
        scene_ids = project.get("scenes", [])
        scenes = [scenes_db[sid] for sid in scene_ids if sid in scenes_db]
        scenes.sort(key=lambda s: s["order_index"])
        
        total_scenes = len(scenes)
        
        # Phase 1: Render each scene (80% of progress)
        for i, scene in enumerate(scenes):
            scene_id = scene["id"]
            
            job["status"] = f"Rendering scene {i+1}/{total_scenes}"
            job["progress"] = int((i / total_scenes) * 80)
            
            if scene["status"] != SceneStatus.completed or not scene.get("video_url"):
                # Render this scene
                scene["status"] = SceneStatus.rendering
                
                try:
                    result = await render_scene(scene["code"], scene_id)
                    scene["video_url"] = result["video_url"]
                    scene["thumbnail_url"] = result.get("thumbnail_url")
                    scene["duration_seconds"] = result.get("duration", 5.0)
                    scene["status"] = SceneStatus.completed
                    scene["updated_at"] = datetime.utcnow()
                except Exception as e:
                    scene["status"] = SceneStatus.failed
                    scene["error_message"] = str(e)
                    raise Exception(f"Failed to render scene {i+1}: {str(e)}")
        
        # Phase 2: Combine all scenes (remaining 20%)
        job["status"] = "Combining scenes"
        job["progress"] = 85
        
        result = await compile_project(
            scenes=scenes,
            project_id=project_id,
            audio_url=project.get("audio_url")
        )
        
        job["progress"] = 100
        job["status"] = "completed"
        job["output_url"] = result["video_url"]
        
    except Exception as e:
        job["status"] = "failed"
        job["error_message"] = str(e)


@router.post("/render-all/{project_id}", response_model=RenderResponse)
async def render_all_and_combine(project_id: str, background_tasks: BackgroundTasks):
    """
    Render all scenes in a project and combine them into a single video.
    This is an all-in-one operation that:
    1. Renders each scene that hasn't been rendered yet
    2. Combines all rendered scenes into one video
    """
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = projects_db[project_id]
    scene_ids = project.get("scenes", [])
    
    if not scene_ids:
        raise HTTPException(status_code=400, detail="Project has no scenes to render")
    
    # Check all scenes have code
    for sid in scene_ids:
        if sid in scenes_db:
            scene = scenes_db[sid]
            if not scene.get("code"):
                raise HTTPException(
                    status_code=400,
                    detail=f"Scene '{scene.get('prompt', sid)}' has no code"
                )
    
    job_id = str(uuid.uuid4())
    now = datetime.utcnow()
    
    job = {
        "id": job_id,
        "scene_id": None,
        "project_id": project_id,
        "status": "pending",
        "progress": 0,
        "output_url": None,
        "error_message": None,
        "created_at": now
    }
    
    render_jobs[job_id] = job
    
    background_tasks.add_task(process_render_all_and_combine, job_id, project_id)
    
    return RenderResponse(
        success=True,
        data=RenderJob(**job),
        message=f"Started rendering {len(scene_ids)} scenes"
    )
