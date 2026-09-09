"""Pydantic schemas for request/response validation."""

from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field, EmailStr


# ==================== User Schemas ====================

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8)


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ProfileBase(BaseModel):
    name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    skills: Optional[List[str]] = None


class ProfileCreate(ProfileBase):
    pass


class ProfileUpdate(ProfileBase):
    pass


class ProfileResponse(ProfileBase):
    id: int
    user_id: int
    preferences: Optional[dict] = None

    class Config:
        from_attributes = True


# ==================== Note Schemas ====================

class NoteBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    category: Optional[str] = None
    is_public: bool = False


class NoteCreate(NoteBase):
    parent_id: Optional[int] = None
    tags: Optional[List[str]] = []


class NoteUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    category: Optional[str] = None
    is_public: Optional[bool] = None
    tags: Optional[List[str]] = None


class NoteResponse(NoteBase):
    id: int
    author_id: int
    parent_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    tags: List["TagResponse"] = []

    class Config:
        from_attributes = True


class TagBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    color: Optional[str] = None


class TagCreate(TagBase):
    pass


class TagResponse(TagBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class NoteLinkCreate(BaseModel):
    target_id: int
    link_type: str
    description: Optional[str] = None


class NoteLinkResponse(BaseModel):
    id: int
    source_id: int
    target_id: int
    link_type: str
    description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== Learning Schemas ====================

class CourseBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    difficulty: str = "beginner"


class CourseCreate(CourseBase):
    modules: Optional[List[Any]] = []
    total_hours: Optional[float] = None


class CourseUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    modules: Optional[List[Any]] = None
    total_hours: Optional[float] = None
    difficulty: Optional[str] = None


class CourseResponse(CourseBase):
    id: int
    modules: List[Any]
    total_hours: Optional[float]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SkillBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    level: str = "beginner"
    category: Optional[str] = None


class SkillCreate(SkillBase):
    estimated_hours: Optional[float] = None
    dependencies: Optional[List[int]] = []


class SkillUpdate(BaseModel):
    description: Optional[str] = None
    level: Optional[str] = None
    estimated_hours: Optional[float] = None


class SkillResponse(SkillBase):
    id: int
    estimated_hours: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True


class LearningPlanBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)


class LearningPlanCreate(LearningPlanBase):
    goals: List[str]
    timeline: dict
    start_date: datetime
    end_date: datetime


class LearningPlanUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    goals: Optional[List[str]] = None
    timeline: Optional[dict] = None
    status: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class LearningPlanResponse(LearningPlanBase):
    id: int
    goals: List[str]
    timeline: dict
    status: str
    start_date: datetime
    end_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LearningProgressCreate(BaseModel):
    item_type: str
    item_id: int
    progress: float = Field(..., ge=0.0, le=1.0)
    notes: Optional[str] = None


class LearningProgressUpdate(BaseModel):
    progress: Optional[float] = Field(None, ge=0.0, le=1.0)
    notes: Optional[str] = None


class LearningProgressResponse(BaseModel):
    id: int
    user_id: int
    item_type: str
    item_id: int
    progress: float
    notes: Optional[str]
    last_accessed: datetime

    class Config:
        from_attributes = True


# ==================== Project Schemas ====================

class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    priority: str = "medium"


class ProjectCreate(ProjectBase):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class ProjectResponse(ProjectBase):
    id: int
    status: str
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    priority: str = "medium"


class TaskCreate(TaskBase):
    project_id: int
    assignee_id: Optional[int] = None
    due_date: Optional[datetime] = None
    estimated_hours: Optional[float] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    assignee_id: Optional[int] = None
    due_date: Optional[datetime] = None
    estimated_hours: Optional[float] = None


class TaskResponse(TaskBase):
    id: int
    project_id: int
    status: str
    assignee_id: Optional[int]
    due_date: Optional[datetime]
    estimated_hours: Optional[float]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MilestoneBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None


class MilestoneCreate(MilestoneBase):
    project_id: int
    target_date: datetime


class MilestoneUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[str] = None
    target_date: Optional[datetime] = None


class MilestoneResponse(MilestoneBase):
    id: int
    project_id: int
    target_date: datetime
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TimeLogCreate(BaseModel):
    task_id: int
    duration_hours: float = Field(..., gt=0)
    notes: Optional[str] = None
    date: Optional[datetime] = None


class TimeLogResponse(BaseModel):
    id: int
    user_id: int
    task_id: int
    duration_hours: float
    notes: Optional[str]
    date: datetime
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== Auth Schemas ====================

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
