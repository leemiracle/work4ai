"""Notes API routes."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ..core.database import get_db
from ..models.database import Note, Tag, NoteLink
from ..models.schemas import (
    NoteCreate, NoteUpdate, NoteResponse,
    TagCreate, TagResponse,
    NoteLinkCreate, NoteLinkResponse
)

router = APIRouter(prefix="/notes", tags=["notes"])


# ==================== Notes Endpoints ====================

@router.post("/", response_model=NoteResponse)
async def create_note(
    note: NoteCreate,
    author_id: int = 1,  # TODO: Get from auth
    db: Session = Depends(get_db)
):
    """Create a new note."""
    db_note = Note(**note.model_dump(), author_id=author_id)
    db.add(db_note)
    db.commit()
    db.refresh(db_note)

    # Add tags if provided
    if note.tags:
        for tag_name in note.tags:
            tag = db.query(Tag).filter(Tag.name == tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.add(tag)
                db.commit()
                db.refresh(tag)
            db_note.tags.append(tag)
        db.commit()
        db.refresh(db_note)

    return db_note


@router.get("/", response_model=List[NoteResponse])
async def get_notes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    category: Optional[str] = None,
    tag: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get list of notes with optional filtering."""
    query = db.query(Note)

    if category:
        query = query.filter(Note.category == category)
    if tag:
        query = query.join(Note.tags).filter(Tag.name == tag)

    notes = query.offset(skip).limit(limit).all()
    return notes


@router.get("/{note_id}", response_model=NoteResponse)
async def get_note(note_id: int, db: Session = Depends(get_db)):
    """Get a specific note by ID."""
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@router.put("/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: int,
    note_update: NoteUpdate,
    db: Session = Depends(get_db)
):
    """Update a note."""
    db_note = db.query(Note).filter(Note.id == note_id).first()
    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")

    update_data = note_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field != "tags" and value is not None:
            setattr(db_note, field, value)

    # Update tags if provided
    if note_update.tags is not None:
        db_note.tags.clear()
        for tag_name in note_update.tags:
            tag = db.query(Tag).filter(Tag.name == tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.add(tag)
                db.commit()
                db.refresh(tag)
            db_note.tags.append(tag)

    db_note.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_note)

    return db_note


@router.delete("/{note_id}")
async def delete_note(note_id: int, db: Session = Depends(get_db)):
    """Delete a note."""
    db_note = db.query(Note).filter(Note.id == note_id).first()
    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")

    db.delete(db_note)
    db.commit()
    return {"message": "Note deleted successfully"}


# ==================== Tags Endpoints ====================

@router.post("/tags/", response_model=TagResponse)
async def create_tag(tag: TagCreate, db: Session = Depends(get_db)):
    """Create a new tag."""
    existing_tag = db.query(Tag).filter(Tag.name == tag.name).first()
    if existing_tag:
        raise HTTPException(status_code=400, detail="Tag already exists")

    db_tag = Tag(**tag.model_dump())
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag


@router.get("/tags/", response_model=List[TagResponse])
async def get_tags(db: Session = Depends(get_db)):
    """Get all tags."""
    tags = db.query(Tag).all()
    return tags


# ==================== Note Links Endpoints ====================

@router.post("/{note_id}/links", response_model=NoteLinkResponse)
async def create_note_link(
    note_id: int,
    link: NoteLinkCreate,
    db: Session = Depends(get_db)
):
    """Create a link between notes."""
    source_note = db.query(Note).filter(Note.id == note_id).first()
    if not source_note:
        raise HTTPException(status_code=404, detail="Source note not found")

    target_note = db.query(Note).filter(Note.id == link.target_id).first()
    if not target_note:
        raise HTTPException(status_code=404, detail="Target note not found")

    db_link = NoteLink(
        source_id=note_id,
        target_id=link.target_id,
        link_type=link.link_type,
        description=link.description
    )
    db.add(db_link)
    db.commit()
    db.refresh(db_link)

    return db_link


@router.get("/{note_id}/links", response_model=List[NoteLinkResponse])
async def get_note_links(note_id: int, db: Session = Depends(get_db)):
    """Get all links for a note."""
    links = db.query(NoteLink).filter(
        (NoteLink.source_id == note_id) | (NoteLink.target_id == note_id)
    ).all()
    return links


@router.post("/search")
async def search_notes(
    query: str = Query(..., min_length=1),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Search notes by title or content."""
    notes = db.query(Note).filter(
        (Note.title.contains(query)) | (Note.content.contains(query))
    ).offset(skip).limit(limit).all()
    return notes
