from fastapi import APIRouter, HTTPException, Depends, Response, Query
from sqlalchemy.orm import Session
from typing import List
from ..models.database import Project, ComicPanel
from ..services.story_service import StoryService
from ..database import get_db
from pydantic import BaseModel
from datetime import datetime
import os
from pathlib import Path
import requests
import io
import asyncio
import traceback

router = APIRouter()

class StorySubmission(BaseModel):
    title: str
    story_text: str

class ComicPanelResponse(BaseModel):
    panel_number: int
    scene_description: str
    panel_text: str | None = None
    image_url: str

class ProjectResponse(BaseModel):
    id: int
    title: str
    story_text: str
    created_at: datetime
    panels: List[ComicPanelResponse]

@router.post("/generate-comic/", response_model=ProjectResponse)
def generate_comic(story: StorySubmission, db: Session = Depends(get_db)):
    try:
        # Create new project
        project = Project(
            title=story.title,
            story_text=story.story_text
        )
        db.add(project)
        db.commit()
        db.refresh(project)

        # Process story and generate panels (now includes panel_text)
        comic_panels_data = StoryService.process_story(story.story_text)
        
        # Save panels to database
        for panel_data in comic_panels_data:
            panel = ComicPanel(
                project_id=project.id,
                panel_number=panel_data["panel_number"],
                scene_description=panel_data["scene_description"],
                panel_text=panel_data.get("panel_text"), # Get the panel_text
                image_url=panel_data["image_url"]
            )
            db.add(panel)
        
        db.commit()
        db.refresh(project)
        
        return project
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.get("/projects/", response_model=List[ProjectResponse])
async def list_projects(db: Session = Depends(get_db)):
    projects = db.query(Project).all()
    return projects

# The proxy-image endpoint has been removed as we're now handling images differently 