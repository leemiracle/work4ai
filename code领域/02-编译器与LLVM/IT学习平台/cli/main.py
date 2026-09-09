"""IT Learning & Project Management Platform - CLI Tool."""

import click
import sys
import os

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from sqlalchemy.orm import Session
from backend.core.database import SessionLocal, init_db
from backend.models.database import Note, Course, Skill, Project, Task


@click.group()
def cli():
    """IT Learning & Project Management Platform CLI."""
    pass


@cli.command()
def init():
    """Initialize the database."""
    click.echo("Initializing database...")
    init_db()
    click.echo("Database initialized successfully!")


@cli.group()
def notes():
    """Note management commands."""
    pass


@notes.command('list')
def list_notes():
    """List all notes."""
    db = SessionLocal()
    try:
        notes_list = db.query(Note).all()
        if not notes_list:
            click.echo("No notes found.")
        else:
            click.echo("\nNotes:")
            for note in notes_list:
                click.echo(f"  [{note.id}] {note.title}")
                click.echo(f"      Category: {note.category or 'N/A'}")
                click.echo(f"      Created: {note.created_at}")
    finally:
        db.close()


@notes.command('create')
@click.option('--title', required=True, help='Note title')
@click.option('--content', required=True, help='Note content')
@click.option('--category', help='Note category')
def create_note(title, content, category):
    """Create a new note."""
    db = SessionLocal()
    try:
        note = Note(title=title, content=content, category=category, author_id=1)
        db.add(note)
        db.commit()
        db.refresh(note)
        click.echo(f"Note created successfully with ID: {note.id}")
    finally:
        db.close()


@notes.command('show')
@click.argument('note_id', type=int)
def show_note(note_id):
    """Show a specific note."""
    db = SessionLocal()
    try:
        note = db.query(Note).filter(Note.id == note_id).first()
        if not note:
            click.echo(f"Note with ID {note_id} not found.")
            return
        click.echo(f"\nTitle: {note.title}")
        click.echo(f"Category: {note.category or 'N/A'}")
        click.echo(f"Created: {note.created_at}")
        click.echo(f"\nContent:\n{note.content}")
    finally:
        db.close()


@cli.group()
def learning():
    """Learning management commands."""
    pass


@learning.command('courses')
def list_courses():
    """List all courses."""
    db = SessionLocal()
    try:
        courses = db.query(Course).all()
        if not courses:
            click.echo("No courses found.")
        else:
            click.echo("\nCourses:")
            for course in courses:
                click.echo(f"  [{course.id}] {course.title}")
                click.echo(f"      Difficulty: {course.difficulty}")
                click.echo(f"      Hours: {course.total_hours or 'N/A'}")
    finally:
        db.close()


@learning.command('skills')
def list_skills():
    """List all skills."""
    db = SessionLocal()
    try:
        skills = db.query(Skill).all()
        if not skills:
            click.echo("No skills found.")
        else:
            click.echo("\nSkills:")
            for skill in skills:
                click.echo(f"  [{skill.id}] {skill.name}")
                click.echo(f"      Level: {skill.level}")
                click.echo(f"      Category: {skill.category or 'N/A'}")
    finally:
        db.close()


@cli.group()
def projects():
    """Project management commands."""
    pass


@projects.command('list')
def list_projects():
    """List all projects."""
    db = SessionLocal()
    try:
        projects_list = db.query(Project).all()
        if not projects_list:
            click.echo("No projects found.")
        else:
            click.echo("\nProjects:")
            for project in projects_list:
                click.echo(f"  [{project.id}] {project.name}")
                click.echo(f"      Status: {project.status}")
                click.echo(f"      Priority: {project.priority}")
                task_count = db.query(Task).filter(Task.project_id == project.id).count()
                click.echo(f"      Tasks: {task_count}")
    finally:
        db.close()


@projects.command('create')
@click.option('--name', required=True, help='Project name')
@click.option('--description', help='Project description')
@click.option('--priority', default='medium', help='Project priority (low/medium/high)')
def create_project(name, description, priority):
    """Create a new project."""
    db = SessionLocal()
    try:
        project = Project(name=name, description=description, priority=priority, owner_id=1)
        db.add(project)
        db.commit()
        db.refresh(project)
        click.echo(f"Project created successfully with ID: {project.id}")
    finally:
        db.close()


@projects.command('tasks')
@click.argument('project_id', type=int)
def list_project_tasks(project_id):
    """List tasks for a project."""
    db = SessionLocal()
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            click.echo(f"Project with ID {project_id} not found.")
            return

        tasks = db.query(Task).filter(Task.project_id == project_id).all()
        if not tasks:
            click.echo(f"No tasks found for project '{project.name}'.")
        else:
            click.echo(f"\nTasks for '{project.name}':")
            for task in tasks:
                click.echo(f"  [{task.id}] {task.title}")
                click.echo(f"      Status: {task.status}")
                click.echo(f"      Priority: {task.priority}")
                click.echo(f"      Assignee ID: {task.assignee_id or 'N/A'}")
    finally:
        db.close()


@cli.command()
def status():
    """Show platform status."""
    db = SessionLocal()
    try:
        note_count = db.query(Note).count()
        course_count = db.query(Course).count()
        skill_count = db.query(Skill).count()
        project_count = db.query(Project).count()
        task_count = db.query(Task).count()

        click.echo("\nPlatform Status:")
        click.echo(f"  Notes: {note_count}")
        click.echo(f"  Courses: {course_count}")
        click.echo(f"  Skills: {skill_count}")
        click.echo(f"  Projects: {project_count}")
        click.echo(f"  Tasks: {task_count}")
    finally:
        db.close()


if __name__ == '__main__':
    cli()
