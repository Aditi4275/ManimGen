from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum
import uuid

from services.llm_service import generate_manim_code, get_multi_scene_codes
from .projects import projects_db

router = APIRouter()


class SceneStatus(str, Enum):
    pending = "pending"
    generating = "generating"
    rendering = "rendering"
    completed = "completed"
    failed = "failed"


class SceneCreate(BaseModel):
    project_id: str
    prompt: str


class SceneUpdate(BaseModel):
    prompt: Optional[str] = None
    code: Optional[str] = None
    order_index: Optional[int] = None


class Scene(BaseModel):
    id: str
    project_id: str
    prompt: str
    code: Optional[str] = None
    video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    duration_seconds: float = 0
    order_index: int
    status: SceneStatus
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class SceneResponse(BaseModel):
    success: bool
    data: Optional[Scene] = None
    message: Optional[str] = None


# In-memory scenes storage
scenes_db: dict = {}


@router.post("/", response_model=SceneResponse)
async def create_scene(scene: SceneCreate):
    """Create a new scene and generate Manim code."""
    if scene.project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    
    scene_id = str(uuid.uuid4())
    now = datetime.utcnow()
    
    project = projects_db[scene.project_id]
    order_index = len(project.get("scenes", []))
    
    new_scene = {
        "id": scene_id,
        "project_id": scene.project_id,
        "prompt": scene.prompt,
        "code": None,
        "video_url": None,
        "thumbnail_url": None,
        "duration_seconds": 0,
        "order_index": order_index,
        "status": SceneStatus.generating,
        "error_message": None,
        "created_at": now,
        "updated_at": now
    }
    
    scenes_db[scene_id] = new_scene
    project["scenes"].append(scene_id)
    project["scene_count"] = len(project["scenes"])
    
    # Generate Manim code using LLM
    try:
        generated_code = await generate_manim_code(scene.prompt)
        new_scene["code"] = generated_code
        new_scene["status"] = SceneStatus.pending
        new_scene["updated_at"] = datetime.utcnow()
    except Exception as e:
        new_scene["status"] = SceneStatus.failed
        new_scene["error_message"] = str(e)
        new_scene["updated_at"] = datetime.utcnow()
    
    return SceneResponse(
        success=True,
        data=Scene(**new_scene),
        message="Scene created successfully"
    )


@router.get("/project/{project_id}", response_model=dict)
async def list_scenes(project_id: str):
    """List all scenes for a project."""
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = projects_db[project_id]
    scene_ids = project.get("scenes", [])
    
    scenes = [
        Scene(**scenes_db[sid])
        for sid in scene_ids
        if sid in scenes_db
    ]
    
    # Sort by order_index
    scenes.sort(key=lambda s: s.order_index)
    
    return {"success": True, "data": scenes}


@router.get("/{scene_id}", response_model=SceneResponse)
async def get_scene(scene_id: str):
    """Get a specific scene."""
    if scene_id not in scenes_db:
        raise HTTPException(status_code=404, detail="Scene not found")
    
    return SceneResponse(
        success=True,
        data=Scene(**scenes_db[scene_id])
    )


@router.put("/{scene_id}", response_model=SceneResponse)
async def update_scene(scene_id: str, update: SceneUpdate):
    """Update a scene."""
    if scene_id not in scenes_db:
        raise HTTPException(status_code=404, detail="Scene not found")
    
    scene = scenes_db[scene_id]
    
    if update.prompt is not None:
        scene["prompt"] = update.prompt
    if update.code is not None:
        scene["code"] = update.code
    if update.order_index is not None:
        scene["order_index"] = update.order_index
    
    scene["updated_at"] = datetime.utcnow()
    
    return SceneResponse(
        success=True,
        data=Scene(**scene),
        message="Scene updated successfully"
    )


@router.delete("/{scene_id}")
async def delete_scene(scene_id: str):
    """Delete a scene."""
    if scene_id not in scenes_db:
        raise HTTPException(status_code=404, detail="Scene not found")
    
    scene = scenes_db[scene_id]
    project_id = scene["project_id"]
    
    if project_id in projects_db:
        project = projects_db[project_id]
        if scene_id in project.get("scenes", []):
            project["scenes"].remove(scene_id)
            project["scene_count"] = len(project["scenes"])
    
    del scenes_db[scene_id]
    return {"success": True, "message": "Scene deleted successfully"}


@router.post("/{scene_id}/regenerate", response_model=SceneResponse)
async def regenerate_scene(scene_id: str, new_prompt: Optional[str] = None):
    """Regenerate a scene with a new or existing prompt."""
    if scene_id not in scenes_db:
        raise HTTPException(status_code=404, detail="Scene not found")
    
    scene = scenes_db[scene_id]
    prompt = new_prompt or scene["prompt"]
    
    scene["status"] = SceneStatus.generating
    scene["updated_at"] = datetime.utcnow()
    
    try:
        generated_code = await generate_manim_code(prompt)
        scene["code"] = generated_code
        scene["prompt"] = prompt
        scene["status"] = SceneStatus.pending
        scene["video_url"] = None
        scene["thumbnail_url"] = None
        scene["error_message"] = None
        scene["updated_at"] = datetime.utcnow()
    except Exception as e:
        scene["status"] = SceneStatus.failed
        scene["error_message"] = str(e)
        scene["updated_at"] = datetime.utcnow()
    
    return SceneResponse(
        success=True,
        data=Scene(**scene),
        message="Scene regenerated successfully"
    )


class MultiSceneCreate(BaseModel):
    project_id: str
    prompt: str
    num_scenes: int = 5  # Default to 5 scenes for ~30 second video


class MultiSceneResponse(BaseModel):
    success: bool
    data: Optional[List[Scene]] = None
    message: Optional[str] = None


@router.post("/multi", response_model=MultiSceneResponse)
async def create_multi_scenes(request: MultiSceneCreate):
    """
    Create multiple scenes from a single prompt.
    Generates a sequence of related scenes for a ~30 second video.
    """
    if request.project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = projects_db[request.project_id]
    
    # Generate multiple scene codes
    scene_data = get_multi_scene_codes(request.prompt, request.num_scenes)
    
    created_scenes = []
    now = datetime.utcnow()
    
    for i, (scene_prompt, scene_code) in enumerate(scene_data):
        scene_id = str(uuid.uuid4())
        order_index = len(project.get("scenes", [])) + i
        
        new_scene = {
            "id": scene_id,
            "project_id": request.project_id,
            "prompt": scene_prompt,
            "code": scene_code,
            "video_url": None,
            "thumbnail_url": None,
            "duration_seconds": 0,
            "order_index": order_index,
            "status": SceneStatus.pending,
            "error_message": None,
            "created_at": now,
            "updated_at": now
        }
        
        scenes_db[scene_id] = new_scene
        project["scenes"].append(scene_id)
        created_scenes.append(Scene(**new_scene))
    
    project["scene_count"] = len(project["scenes"])
    
    return MultiSceneResponse(
        success=True,
        data=created_scenes,
        message=f"Created {len(created_scenes)} scenes. Render each one and then export to create your video."
    )
