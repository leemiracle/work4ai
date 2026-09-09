"""Agent Memory System - Short-term, Long-term, and Episodic Memory."""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from sqlalchemy import create_engine, Column, Integer, String, Text, Float, DateTime, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from collections import OrderedDict
import json
from .config import AISettings

Base = declarative_base()


class MemoryEntry(Base):
    """Memory entry in database."""

    __tablename__ = "agent_memories"

    id = Column(Integer, primary_key=True, index=True)
    agent_name = Column(String(100), index=True)
    memory_type = Column(String(50))  # 'short_term', 'long_term', 'episodic'
    key = Column(String(255), index=True)
    value = Column(Text)
    importance = Column(Float, default=0.5)
    access_count = Column(Integer, default=0)
    last_accessed = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    metadata = Column(Text)  # JSON string


class Memory(ABC):
    """Base Memory class."""

    @abstractmethod
    async def store(self, key: str, value: Any, importance: float = 0.5, metadata: Dict = None):
        """Store a memory."""
        pass

    @abstractmethod
    async def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve a memory by key."""
        pass

    @abstractmethod
    async def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search memories."""
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete a memory."""
        pass


class ShortTermMemory(Memory):
    """Short-term memory - limited capacity, fast access."""

    def __init__(self, max_items: int = 100):
        self.max_items = max_items
        self.memory: OrderedDict = OrderedDict()
        self.created_at = datetime.utcnow()

    async def store(self, key: str, value: Any, importance: float = 0.5, metadata: Dict = None):
        """Store in short-term memory."""
        # Update access count and last accessed time
        if key in self.memory:
            self.memory.move_to_end(key)
            self.memory[key]['access_count'] += 1
            self.memory[key]['last_accessed'] = datetime.utcnow()
        else:
            # Add new entry
            if len(self.memory) >= self.max_items:
                # Remove oldest (FIFO)
                self.memory.popitem(last=False)

            self.memory[key] = {
                'value': value,
                'importance': importance,
                'access_count': 1,
                'created_at': datetime.utcnow(),
                'last_accessed': datetime.utcnow(),
                'metadata': metadata or {}
            }

    async def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve from short-term memory."""
        if key in self.memory:
            self.memory.move_to_end(key)
            self.memory[key]['access_count'] += 1
            self.memory[key]['last_accessed'] = datetime.utcnow()
            return self.memory[key]['value']
        return None

    async def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search short-term memory (simple keyword match)."""
        results = []
        query_lower = query.lower()

        for key, data in reversed(self.memory.items()):
            if query_lower in key.lower() or query_lower in str(data['value']).lower():
                results.append({
                    'key': key,
                    'value': data['value'],
                    'importance': data['importance'],
                    'memory_type': 'short_term'
                })

            if len(results) >= limit:
                break

        return results

    async def delete(self, key: str) -> bool:
        """Delete from short-term memory."""
        if key in self.memory:
            del self.memory[key]
            return True
        return False

    async def get_all(self) -> List[Dict[str, Any]]:
        """Get all short-term memories."""
        return [
            {
                'key': key,
                'value': data['value'],
                'importance': data['importance'],
                'memory_type': 'short_term'
            }
            for key, data in self.memory.items()
        ]

    async def clear(self):
        """Clear all short-term memory."""
        self.memory.clear()


class LongTermMemory(Memory):
    """Long-term memory - persistent, semantic search."""

    def __init__(self, database_url: str):
        self.engine = create_engine(database_url)
        SessionLocal = sessionmaker(bind=self.engine)
        self.Session = SessionLocal

        # Create tables
        Base.metadata.create_all(self.engine)

    async def store(self, key: str, value: Any, importance: float = 0.5, metadata: Dict = None):
        """Store in long-term memory."""
        db = self.Session()
        try:
            # Check if key already exists
            existing = db.query(MemoryEntry).filter(
                MemoryEntry.key == key,
                MemoryEntry.memory_type == 'long_term'
            ).first()

            if existing:
                # Update existing
                existing.value = json.dumps(value) if not isinstance(value, str) else value
                existing.importance = importance
                existing.last_accessed = datetime.utcnow()
                if metadata:
                    existing.metadata = json.dumps(metadata)
            else:
                # Create new
                entry = MemoryEntry(
                    agent_name="default",
                    memory_type='long_term',
                    key=key,
                    value=json.dumps(value) if not isinstance(value, str) else value,
                    importance=importance,
                    metadata=json.dumps(metadata) if metadata else None
                )
                db.add(entry)

            db.commit()
        finally:
            db.close()

    async def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve from long-term memory."""
        db = self.Session()
        try:
            entry = db.query(MemoryEntry).filter(
                MemoryEntry.key == key,
                MemoryEntry.memory_type == 'long_term'
            ).first()

            if entry:
                # Update access count and last accessed
                entry.access_count += 1
                entry.last_accessed = datetime.utcnow()
                db.commit()

                # Parse value
                try:
                    return json.loads(entry.value)
                except json.JSONDecodeError:
                    return entry.value
            return None
        finally:
            db.close()

    async def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search long-term memory (keyword search)."""
        db = self.Session()
        try:
            entries = db.query(MemoryEntry).filter(
                MemoryEntry.memory_type == 'long_term',
                MemoryEntry.key.contains(query) |
                MemoryEntry.value.contains(query)
            ).order_by(
                MemoryEntry.importance.desc(),
                MemoryEntry.last_accessed.desc()
            ).limit(limit).all()

            results = []
            for entry in entries:
                try:
                    value = json.loads(entry.value)
                except json.JSONDecodeError:
                    value = entry.value

                results.append({
                    'key': entry.key,
                    'value': value,
                    'importance': entry.importance,
                    'access_count': entry.access_count,
                    'last_accessed': entry.last_accessed.isoformat(),
                    'memory_type': 'long_term',
                    'metadata': json.loads(entry.metadata) if entry.metadata else {}
                })

            return results
        finally:
            db.close()

    async def delete(self, key: str) -> bool:
        """Delete from long-term memory."""
        db = self.Session()
        try:
            entry = db.query(MemoryEntry).filter(
                MemoryEntry.key == key,
                MemoryEntry.memory_type == 'long_term'
            ).first()

            if entry:
                db.delete(entry)
                db.commit()
                return True
            return False
        finally:
            db.close()


class EpisodicMemory(Memory):
    """Episodic memory - stores complete episodes of agent interactions."""

    def __init__(self, database_url: str):
        self.engine = create_engine(database_url)
        SessionLocal = sessionmaker(bind=self.engine)
        self.Session = SessionLocal

        # Create tables
        Base.metadata.create_all(self.engine)

    async def store_episode(
        self,
        episode_id: str,
        task: Dict[str, Any],
        actions: List[Dict[str, Any]],
        observations: List[Dict[str, Any]],
        outcome: Dict[str, Any],
        importance: float = 0.5
    ):
        """Store a complete episode."""
        db = self.Session()
        try:
            episode_key = f"episode_{episode_id}"
            episode_data = {
                'task': task,
                'actions': actions,
                'observations': observations,
                'outcome': outcome
            }

            entry = MemoryEntry(
                agent_name="default",
                memory_type='episodic',
                key=episode_key,
                value=json.dumps(episode_data),
                importance=importance,
                metadata=json.dumps({
                    'episode_id': episode_id,
                    'task_type': task.get('type'),
                    'outcome_type': outcome.get('type')
                })
            )

            db.add(entry)
            db.commit()
        finally:
            db.close()

    async def retrieve(self, episode_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve an episode by ID."""
        return await self.retrieve(f"episode_{episode_id}")

    async def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve from episodic memory."""
        db = self.Session()
        try:
            entry = db.query(MemoryEntry).filter(
                MemoryEntry.key == key,
                MemoryEntry.memory_type == 'episodic'
            ).first()

            if entry:
                entry.access_count += 1
                entry.last_accessed = datetime.utcnow()
                db.commit()

                try:
                    return json.loads(entry.value)
                except json.JSONDecodeError:
                    return entry.value
            return None
        finally:
            db.close()

    async def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search episodic memory."""
        db = self.Session()
        try:
            entries = db.query(MemoryEntry).filter(
                MemoryEntry.memory_type == 'episodic',
                MemoryEntry.value.contains(query)
            ).order_by(
                MemoryEntry.importance.desc(),
                MemoryEntry.last_accessed.desc()
            ).limit(limit).all()

            results = []
            for entry in entries:
                try:
                    value = json.loads(entry.value)
                except json.JSONDecodeError:
                    value = entry.value

                results.append({
                    'key': entry.key,
                    'episode_data': value,
                    'importance': entry.importance,
                    'memory_type': 'episodic'
                })

            return results
        finally:
            db.close()

    async def delete(self, key: str) -> bool:
        """Delete from episodic memory."""
        db = self.Session()
        try:
            entry = db.query(MemoryEntry).filter(
                MemoryEntry.key == key,
                MemoryEntry.memory_type == 'episodic'
            ).first()

            if entry:
                db.delete(entry)
                db.commit()
                return True
            return False
        finally:
            db.close()


class MemorySystem:
    """Unified memory system managing all memory types."""

    def __init__(self, settings: AISettings):
        self.settings = settings
        self.short_term = ShortTermMemory(max_items=100)
        self.long_term = LongTermMemory(settings.DATABASE_URL)
        self.episodic = EpisodicMemory(settings.DATABASE_URL)

    async def store(
        self,
        key: str,
        value: Any,
        memory_type: str = "long_term",
        importance: float = 0.5,
        metadata: Dict = None
    ):
        """Store in specified memory type."""
        if memory_type == "short_term":
            await self.short_term.store(key, value, importance, metadata)
        elif memory_type == "long_term":
            await self.long_term.store(key, value, importance, metadata)
        elif memory_type == "episodic":
            await self.episodic.store(key, value, importance, metadata)
        else:
            raise ValueError(f"Unknown memory type: {memory_type}")

    async def retrieve(self, key: str, memory_type: str = None) -> Optional[Any]:
        """Retrieve from specified or all memory types."""
        if memory_type:
            if memory_type == "short_term":
                return await self.short_term.retrieve(key)
            elif memory_type == "long_term":
                return await self.long_term.retrieve(key)
            elif memory_type == "episodic":
                return await self.episodic.retrieve(key)
        else:
            # Search all memory types
            result = await self.short_term.retrieve(key)
            if result is None:
                result = await self.long_term.retrieve(key)
            if result is None:
                result = await self.episodic.retrieve(key)
            return result

    async def search(
        self,
        query: str,
        memory_type: str = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search across memory types."""
        results = []

        if memory_type is None or memory_type == "short_term":
            stm_results = await self.short_term.search(query, limit)
            results.extend(stm_results)

        if memory_type is None or memory_type == "long_term":
            ltm_results = await self.long_term.search(query, limit)
            results.extend(ltm_results)

        if memory_type is None or memory_type == "episodic":
            em_results = await self.episodic.search(query, limit)
            results.extend(em_results)

        # Sort by importance
        results.sort(key=lambda x: x.get('importance', 0), reverse=True)

        return results[:limit]

    async def delete(self, key: str, memory_type: str = None) -> bool:
        """Delete from memory."""
        if memory_type:
            if memory_type == "short_term":
                return await self.short_term.delete(key)
            elif memory_type == "long_term":
                return await self.long_term.delete(key)
            elif memory_type == "episodic":
                return await self.episodic.delete(key)
        else:
            # Try all memory types
            deleted = False
            if await self.short_term.delete(key):
                deleted = True
            if await self.long_term.delete(key):
                deleted = True
            if await self.episodic.delete(key):
                deleted = True
            return deleted

    async def cleanup(self, max_age_days: int = 30):
        """Clean up old short-term memories and unused long-term memories."""
        # Short-term memory automatically cleans up via LRU
        # Long-term: remove entries not accessed in max_age_days
        db = self.long_term.Session
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=max_age_days)
            db.query(MemoryEntry).filter(
                MemoryEntry.memory_type == 'long_term',
                MemoryEntry.last_accessed < cutoff_date,
                MemoryEntry.importance < 0.3  # Don't delete important memories
            ).delete(synchronize_session=False)
            db.commit()
        finally:
            db.close()
