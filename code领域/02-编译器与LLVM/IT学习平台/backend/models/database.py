"""Database models for the application."""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean,
    ForeignKey, Table, Float, JSON
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


# Association tables for many-to-many relationships
note_tags = Table(
    'note_tags',
    Base.metadata,
    Column('note_id', Integer, ForeignKey('notes.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True)
)

skill_dependencies = Table(
    'skill_dependencies',
    Base.metadata,
    Column('skill_id', Integer, ForeignKey('skills.id'), primary_key=True),
    Column('dependency_id', Integer, ForeignKey('skills.id'), primary_key=True)
)

course_skills = Table(
    'course_skills',
    Base.metadata,
    Column('course_id', Integer, ForeignKey('courses.id'), primary_key=True),
    Column('skill_id', Integer, ForeignKey('skills.id'), primary_key=True)
)

plan_courses = Table(
    'plan_courses',
    Base.metadata,
    Column('plan_id', Integer, ForeignKey('learning_plans.id'), primary_key=True),
    Column('course_id', Integer, ForeignKey('courses.id'), primary_key=True)
)


# ==================== User Models ====================

class User(Base):
    """User model."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    profile = relationship("Profile", back_populates="user", uselist=False)
    notes = relationship("Note", back_populates="author")
    tasks_assigned = relationship("Task", foreign_keys="Task.assignee_id", back_populates="assignee")
    time_logs = relationship("TimeLog", back_populates="user")
    learning_progress = relationship("LearningProgress", back_populates="user")


class Profile(Base):
    """User profile model."""

    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    name = Column(String(100))
    bio = Column(Text)
    avatar_url = Column(String(255))
    skills = Column(JSON)  # List of skill names
    preferences = Column(JSON)  # User preferences

    # Relationships
    user = relationship("User", back_populates="profile")


# ==================== Knowledge Base Models ====================

class Note(Base):
    """Note model for knowledge base."""

    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    content = Column(Text, nullable=False)
    category = Column(String(50), index=True)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    parent_id = Column(Integer, ForeignKey("notes.id"), nullable=True)
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    author = relationship("User", back_populates="notes")
    parent = relationship("Note", remote_side=[id], backref="children")
    tags = relationship("Tag", secondary=note_tags, back_populates="notes")
    links_from = relationship("NoteLink", foreign_keys="NoteLink.source_id", back_populates="source")
    links_to = relationship("NoteLink", foreign_keys="NoteLink.target_id", back_populates="target")


class Tag(Base):
    """Tag model for categorization."""

    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    color = Column(String(7))  # Hex color code
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    notes = relationship("Note", secondary=note_tags, back_populates="tags")


class NoteLink(Base):
    """Link between notes for knowledge graph."""

    __tablename__ = "note_links"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("notes.id"), nullable=False)
    target_id = Column(Integer, ForeignKey("notes.id"), nullable=False)
    link_type = Column(String(20))  # reference, related, depends_on, etc.
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    source = relationship("Note", foreign_keys=[source_id], back_populates="links_from")
    target = relationship("Note", foreign_keys=[target_id], back_populates="links_to")


# ==================== Learning Management Models ====================

class Course(Base):
    """Course model."""

    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    modules = Column(JSON)  # List of modules
    total_hours = Column(Float)
    difficulty = Column(String(20))  # beginner, intermediate, advanced
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    skills = relationship("Skill", secondary=course_skills, back_populates="courses")


class Skill(Base):
    """Skill model for skill tree."""

    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text)
    level = Column(String(20))  # beginner, intermediate, advanced, expert
    category = Column(String(50))
    estimated_hours = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    courses = relationship("Course", secondary=course_skills, back_populates="skills")
    dependencies = relationship(
        "Skill",
        secondary=skill_dependencies,
        primaryjoin=id == skill_dependencies.c.skill_id,
        secondaryjoin=id == skill_dependencies.c.dependency_id,
        backref="dependents"
    )


class LearningPlan(Base):
    """Learning plan model."""

    __tablename__ = "learning_plans"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    goals = Column(JSON)  # List of learning goals
    timeline = Column(JSON)  # Timeline data
    status = Column(String(20), default="active")  # active, completed, paused
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class LearningProgress(Base):
    """Learning progress tracking."""

    __tablename__ = "learning_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    item_type = Column(String(20))  # course, skill, plan
    item_id = Column(Integer, nullable=False)
    progress = Column(Float, default=0.0)  # 0.0 to 1.0
    notes = Column(Text)
    last_accessed = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="learning_progress")


# ==================== Project Management Models ====================

class Project(Base):
    """Project model."""

    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    status = Column(String(20), default="active")  # active, completed, on_hold
    priority = Column(String(20), default="medium")  # low, medium, high
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tasks = relationship("Task", back_populates="project")
    milestones = relationship("Milestone", back_populates="project")


class Task(Base):
    """Task model."""

    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    status = Column(String(20), default="todo")  # todo, in_progress, done, blocked
    priority = Column(String(20), default="medium")  # low, medium, high, critical
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    assignee_id = Column(Integer, ForeignKey("users.id"))
    due_date = Column(DateTime)
    estimated_hours = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="tasks")
    assignee = relationship("User", foreign_keys=[assignee_id], back_populates="tasks_assigned")
    time_logs = relationship("TimeLog", back_populates="task")


class Milestone(Base):
    """Milestone model."""

    __tablename__ = "milestones"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    target_date = Column(DateTime)
    status = Column(String(20), default="pending")  # pending, completed, overdue
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="milestones")


class TimeLog(Base):
    """Time log for tracking work."""

    __tablename__ = "time_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    duration_hours = Column(Float, nullable=False)
    notes = Column(Text)
    date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="time_logs")
    task = relationship("Task", back_populates="time_logs")
