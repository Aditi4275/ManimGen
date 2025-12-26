from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid

router = APIRouter()

# In-memory storage (replace with database in production)
projects_db: dict = {}


class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class Project(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    scene_count: int = 0
    audio_url: Optional[str] = None


class ProjectResponse(BaseModel):
    success: bool
    data: Optional[Project] = None
    message: Optional[str] = None


@router.post("/", response_model=ProjectResponse)
async def create_project(project: ProjectCreate):
    """Create a new project."""
    project_id = str(uuid.uuid4())
    now = datetime.utcnow()
    
    new_project = {
        "id": project_id,
        "name": project.name,
        "description": project.description,
        "created_at": now,
        "updated_at": now,
        "scene_count": 0,
        "scenes": [],
        "audio_url": None
    }
    
    projects_db[project_id] = new_project
    
    return ProjectResponse(
        success=True,
        data=Project(**{k: v for k, v in new_project.items() if k != "scenes"}),
        message="Project created successfully"
    )


@router.get("/", response_model=dict)
async def list_projects():
    """List all projects."""
    projects = [
        Project(**{k: v for k, v in p.items() if k != "scenes"})
        for p in projects_db.values()
    ]
    return {"success": True, "data": projects}


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: str):
    """Get a specific project."""
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = projects_db[project_id]
    return ProjectResponse(
        success=True,
        data=Project(**{k: v for k, v in project.items() if k != "scenes"})
    )


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(project_id: str, update: ProjectUpdate):
    """Update a project."""
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = projects_db[project_id]
    
    if update.name is not None:
        project["name"] = update.name
    if update.description is not None:
        project["description"] = update.description
    
    project["updated_at"] = datetime.utcnow()
    
    return ProjectResponse(
        success=True,
        data=Project(**{k: v for k, v in project.items() if k != "scenes"}),
        message="Project updated successfully"
    )


@router.delete("/{project_id}")
async def delete_project(project_id: str):
    """Delete a project."""
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    
    del projects_db[project_id]
    return {"success": True, "message": "Project deleted successfully"}
