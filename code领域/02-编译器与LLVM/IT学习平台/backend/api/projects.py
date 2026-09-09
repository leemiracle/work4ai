"""Project management API routes."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from ..core.database import get_db
from ..models.database import Project, Task, Milestone, TimeLog
from ..models.schemas import (
    ProjectCreate, ProjectUpdate, ProjectResponse,
    TaskCreate, TaskUpdate, TaskResponse,
    MilestoneCreate, MilestoneUpdate, MilestoneResponse,
    TimeLogCreate, TimeLogResponse
)

router = APIRouter(prefix="/projects", tags=["projects"])


# ==================== Projects Endpoints ====================

@router.post("/", response_model=ProjectResponse)
async def create_project(
    project: ProjectCreate,
    owner_id: int = 1,  # TODO: Get from auth
    db: Session = Depends(get_db)
):
    """Create a new project."""
    db_project = Project(**project.model_dump(), owner_id=owner_id)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


@router.get("/", response_model=List[ProjectResponse])
async def get_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: str = None,
    priority: str = None,
    db: Session = Depends(get_db)
):
    """Get list of projects with optional filtering."""
    query = db.query(Project)
    if status:
        query = query.filter(Project.status == status)
    if priority:
        query = query.filter(Project.priority == priority)
    projects = query.offset(skip).limit(limit).all()
    return projects


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: int, db: Session = Depends(get_db)):
    """Get a specific project by ID."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project_update: ProjectUpdate,
    db: Session = Depends(get_db)
):
    """Update a project."""
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")

    update_data = project_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            setattr(db_project, field, value)

    db_project.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_project)

    return db_project


@router.delete("/{project_id}")
async def delete_project(project_id: int, db: Session = Depends(get_db)):
    """Delete a project."""
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")

    db.delete(db_project)
    db.commit()
    return {"message": "Project deleted successfully"}


@router.get("/{project_id}/tasks", response_model=List[TaskResponse])
async def get_project_tasks(
    project_id: int,
    status: str = None,
    assignee_id: int = None,
    db: Session = Depends(get_db)
):
    """Get all tasks for a project."""
    query = db.query(Task).filter(Task.project_id == project_id)
    if status:
        query = query.filter(Task.status == status)
    if assignee_id:
        query = query.filter(Task.assignee_id == assignee_id)
    tasks = query.all()
    return tasks


# ==================== Tasks Endpoints ====================

@router.post("/tasks/", response_model=TaskResponse)
async def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    """Create a new task."""
    # Verify project exists
    project = db.query(Project).filter(Project.id == task.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    db_task = Task(**task.model_dump())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


@router.get("/tasks/", response_model=List[TaskResponse])
async def get_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: str = None,
    priority: str = None,
    db: Session = Depends(get_db)
):
    """Get list of tasks with optional filtering."""
    query = db.query(Task)
    if status:
        query = query.filter(Task.status == status)
    if priority:
        query = query.filter(Task.priority == priority)
    tasks = query.offset(skip).limit(limit).all()
    return tasks


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int, db: Session = Depends(get_db)):
    """Get a specific task by ID."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    db: Session = Depends(get_db)
):
    """Update a task."""
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    update_data = task_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            setattr(db_task, field, value)

    db_task.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_task)

    return db_task


@router.delete("/tasks/{task_id}")
async def delete_task(task_id: int, db: Session = Depends(get_db)):
    """Delete a task."""
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(db_task)
    db.commit()
    return {"message": "Task deleted successfully"}


# ==================== Milestones Endpoints ====================

@router.post("/milestones/", response_model=MilestoneResponse)
async def create_milestone(milestone: MilestoneCreate, db: Session = Depends(get_db)):
    """Create a new milestone."""
    # Verify project exists
    project = db.query(Project).filter(Project.id == milestone.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    db_milestone = Milestone(**milestone.model_dump())
    db.add(db_milestone)
    db.commit()
    db.refresh(db_milestone)
    return db_milestone


@router.get("/milestones/", response_model=List[MilestoneResponse])
async def get_milestones(
    project_id: int = None,
    status: str = None,
    db: Session = Depends(get_db)
):
    """Get list of milestones with optional filtering."""
    query = db.query(Milestone)
    if project_id:
        query = query.filter(Milestone.project_id == project_id)
    if status:
        query = query.filter(Milestone.status == status)
    milestones = query.all()
    return milestones


@router.get("/milestones/{milestone_id}", response_model=MilestoneResponse)
async def get_milestone(milestone_id: int, db: Session = Depends(get_db)):
    """Get a specific milestone by ID."""
    milestone = db.query(Milestone).filter(Milestone.id == milestone_id).first()
    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")
    return milestone


@router.put("/milestones/{milestone_id}", response_model=MilestoneResponse)
async def update_milestone(
    milestone_id: int,
    milestone_update: MilestoneUpdate,
    db: Session = Depends(get_db)
):
    """Update a milestone."""
    db_milestone = db.query(Milestone).filter(Milestone.id == milestone_id).first()
    if not db_milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")

    update_data = milestone_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            setattr(db_milestone, field, value)

    db_milestone.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_milestone)

    return db_milestone


@router.delete("/milestones/{milestone_id}")
async def delete_milestone(milestone_id: int, db: Session = Depends(get_db)):
    """Delete a milestone."""
    db_milestone = db.query(Milestone).filter(Milestone.id == milestone_id).first()
    if not db_milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")

    db.delete(db_milestone)
    db.commit()
    return {"message": "Milestone deleted successfully"}


# ==================== Time Logs Endpoints ====================

@router.post("/tasks/{task_id}/timelogs", response_model=TimeLogResponse)
async def create_time_log(
    task_id: int,
    time_log: TimeLogCreate,
    user_id: int = 1,  # TODO: Get from auth
    db: Session = Depends(get_db)
):
    """Create a time log for a task."""
    # Verify task exists
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    db_time_log = TimeLog(
        user_id=user_id,
        task_id=task_id,
        duration_hours=time_log.duration_hours,
        notes=time_log.notes,
        date=time_log.date or datetime.utcnow()
    )
    db.add(db_time_log)
    db.commit()
    db.refresh(db_time_log)
    return db_time_log


@router.get("/tasks/{task_id}/timelogs", response_model=List[TimeLogResponse])
async def get_task_time_logs(task_id: int, db: Session = Depends(get_db)):
    """Get all time logs for a task."""
    time_logs = db.query(TimeLog).filter(TimeLog.task_id == task_id).all()
    return time_logs


@router.get("/timelogs/", response_model=List[TimeLogResponse])
async def get_user_time_logs(
    user_id: int = 1,  # TODO: Get from auth
    db: Session = Depends(get_db)
):
    """Get all time logs for a user."""
    time_logs = db.query(TimeLog).filter(TimeLog.user_id == user_id).all()
    return time_logs
