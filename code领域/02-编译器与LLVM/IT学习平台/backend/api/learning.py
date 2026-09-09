"""Learning management API routes."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from ..core.database import get_db
from ..models.database import Course, Skill, LearningPlan, LearningProgress
from ..models.schemas import (
    CourseCreate, CourseUpdate, CourseResponse,
    SkillCreate, SkillUpdate, SkillResponse,
    LearningPlanCreate, LearningPlanUpdate, LearningPlanResponse,
    LearningProgressCreate, LearningProgressUpdate, LearningProgressResponse
)

router = APIRouter(prefix="/learning", tags=["learning"])


# ==================== Courses Endpoints ====================

@router.post("/courses/", response_model=CourseResponse)
async def create_course(course: CourseCreate, db: Session = Depends(get_db)):
    """Create a new course."""
    db_course = Course(**course.model_dump())
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course


@router.get("/courses/", response_model=List[CourseResponse])
async def get_courses(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    difficulty: str = None,
    db: Session = Depends(get_db)
):
    """Get list of courses with optional filtering."""
    query = db.query(Course)
    if difficulty:
        query = query.filter(Course.difficulty == difficulty)
    courses = query.offset(skip).limit(limit).all()
    return courses


@router.get("/courses/{course_id}", response_model=CourseResponse)
async def get_course(course_id: int, db: Session = Depends(get_db)):
    """Get a specific course by ID."""
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


@router.put("/courses/{course_id}", response_model=CourseResponse)
async def update_course(
    course_id: int,
    course_update: CourseUpdate,
    db: Session = Depends(get_db)
):
    """Update a course."""
    db_course = db.query(Course).filter(Course.id == course_id).first()
    if not db_course:
        raise HTTPException(status_code=404, detail="Course not found")

    update_data = course_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_course, field, value)

    db_course.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_course)

    return db_course


@router.delete("/courses/{course_id}")
async def delete_course(course_id: int, db: Session = Depends(get_db)):
    """Delete a course."""
    db_course = db.query(Course).filter(Course.id == course_id).first()
    if not db_course:
        raise HTTPException(status_code=404, detail="Course not found")

    db.delete(db_course)
    db.commit()
    return {"message": "Course deleted successfully"}


# ==================== Skills Endpoints ====================

@router.post("/skills/", response_model=SkillResponse)
async def create_skill(skill: SkillCreate, db: Session = Depends(get_db)):
    """Create a new skill."""
    db_skill = Skill(**skill.model_dump(exclude={"dependencies"}))
    db.add(db_skill)
    db.commit()
    db.refresh(db_skill)

    # Add dependencies if provided
    if skill.dependencies:
        for dep_id in skill.dependencies:
            dep_skill = db.query(Skill).filter(Skill.id == dep_id).first()
            if dep_skill:
                db_skill.dependencies.append(dep_skill)
        db.commit()

    return db_skill


@router.get("/skills/", response_model=List[SkillResponse])
async def get_skills(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    level: str = None,
    category: str = None,
    db: Session = Depends(get_db)
):
    """Get list of skills with optional filtering."""
    query = db.query(Skill)
    if level:
        query = query.filter(Skill.level == level)
    if category:
        query = query.filter(Skill.category == category)
    skills = query.offset(skip).limit(limit).all()
    return skills


@router.get("/skills/{skill_id}", response_model=SkillResponse)
async def get_skill(skill_id: int, db: Session = Depends(get_db)):
    """Get a specific skill by ID."""
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    return skill


@router.put("/skills/{skill_id}", response_model=SkillResponse)
async def update_skill(
    skill_id: int,
    skill_update: SkillUpdate,
    db: Session = Depends(get_db)
):
    """Update a skill."""
    db_skill = db.query(Skill).filter(Skill.id == skill_id).first()
    if not db_skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    update_data = skill_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            setattr(db_skill, field, value)

    db.commit()
    db.refresh(db_skill)

    return db_skill


@router.get("/skills/{skill_id}/tree", response_model=dict)
async def get_skill_tree(skill_id: int, db: Session = Depends(get_db)):
    """Get skill tree including dependencies."""
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    def build_tree(s):
        return {
            "id": s.id,
            "name": s.name,
            "level": s.level,
            "category": s.category,
            "dependencies": [build_tree(d) for d in s.dependencies]
        }

    return build_tree(skill)


# ==================== Learning Plans Endpoints ====================

@router.post("/plans/", response_model=LearningPlanResponse)
async def create_learning_plan(plan: LearningPlanCreate, db: Session = Depends(get_db)):
    """Create a new learning plan."""
    db_plan = LearningPlan(**plan.model_dump())
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    return db_plan


@router.get("/plans/", response_model=List[LearningPlanResponse])
async def get_learning_plans(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: str = None,
    db: Session = Depends(get_db)
):
    """Get list of learning plans with optional filtering."""
    query = db.query(LearningPlan)
    if status:
        query = query.filter(LearningPlan.status == status)
    plans = query.offset(skip).limit(limit).all()
    return plans


@router.get("/plans/{plan_id}", response_model=LearningPlanResponse)
async def get_learning_plan(plan_id: int, db: Session = Depends(get_db)):
    """Get a specific learning plan by ID."""
    plan = db.query(LearningPlan).filter(LearningPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Learning plan not found")
    return plan


@router.put("/plans/{plan_id}", response_model=LearningPlanResponse)
async def update_learning_plan(
    plan_id: int,
    plan_update: LearningPlanUpdate,
    db: Session = Depends(get_db)
):
    """Update a learning plan."""
    db_plan = db.query(LearningPlan).filter(LearningPlan.id == plan_id).first()
    if not db_plan:
        raise HTTPException(status_code=404, detail="Learning plan not found")

    update_data = plan_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            setattr(db_plan, field, value)

    db_plan.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_plan)

    return db_plan


# ==================== Learning Progress Endpoints ====================

@router.post("/progress/", response_model=LearningProgressResponse)
async def create_learning_progress(
    progress: LearningProgressCreate,
    user_id: int = 1,  # TODO: Get from auth
    db: Session = Depends(get_db)
):
    """Create or update learning progress."""
    db_progress = db.query(LearningProgress).filter(
        LearningProgress.user_id == user_id,
        LearningProgress.item_type == progress.item_type,
        LearningProgress.item_id == progress.item_id
    ).first()

    if db_progress:
        db_progress.progress = progress.progress
        db_progress.notes = progress.notes
        db_progress.last_accessed = datetime.utcnow()
    else:
        db_progress = LearningProgress(
            user_id=user_id,
            **progress.model_dump()
        )
        db.add(db_progress)

    db.commit()
    db.refresh(db_progress)
    return db_progress


@router.get("/progress/", response_model=List[LearningProgressResponse])
async def get_learning_progress(
    user_id: int = 1,  # TODO: Get from auth
    item_type: str = None,
    db: Session = Depends(get_db)
):
    """Get learning progress for a user."""
    query = db.query(LearningProgress).filter(LearningProgress.user_id == user_id)
    if item_type:
        query = query.filter(LearningProgress.item_type == item_type)
    progress_items = query.all()
    return progress_items


@router.get("/progress/{item_type}/{item_id}", response_model=LearningProgressResponse)
async def get_item_progress(
    item_type: str,
    item_id: int,
    user_id: int = 1,  # TODO: Get from auth
    db: Session = Depends(get_db)
):
    """Get progress for a specific item."""
    progress = db.query(LearningProgress).filter(
        LearningProgress.user_id == user_id,
        LearningProgress.item_type == item_type,
        LearningProgress.item_id == item_id
    ).first()

    if not progress:
        raise HTTPException(status_code=404, detail="Progress not found")
    return progress
