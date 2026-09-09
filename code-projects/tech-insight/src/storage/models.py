"""数据模型 - 定义所有数据结构"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Article:
    """文章/内容统一模型"""
    id: str = ""
    source: str = ""
    source_name: str = ""
    title: str = ""
    url: str = ""
    author: str = ""
    author_id: str = ""
    summary: str = ""
    content: str = ""
    content_html: str = ""
    category: str = ""
    tags: list[str] = field(default_factory=list)
    published_at: Optional[str] = None
    collected_at: str = ""
    view_count: int = 0
    like_count: int = 0
    comment_count: int = 0
    bookmark_count: int = 0
    cover_image: str = ""
    uuid: str = ""
    language: str = "zh-CN"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "source": self.source,
            "source_name": self.source_name,
            "title": self.title,
            "url": self.url,
            "author": self.author,
            "author_id": self.author_id,
            "summary": self.summary,
            "content": self.content,
            "category": self.category,
            "tags": "||".join(self.tags),
            "published_at": self.published_at or "",
            "collected_at": self.collected_at or datetime.now().isoformat(),
            "view_count": self.view_count,
            "like_count": self.like_count,
            "comment_count": self.comment_count,
            "bookmark_count": self.bookmark_count,
            "cover_image": self.cover_image,
            "uuid": self.uuid,
            "language": self.language,
        }


@dataclass
class Entity:
    """知识图谱实体"""
    name: str
    entity_type: str
    description: str = ""
    mentions: int = 1
    source_articles: list[str] = field(default_factory=list)
    properties: dict = field(default_factory=dict)


@dataclass
class Relation:
    """知识图谱关系"""
    source_entity: str
    target_entity: str
    relation_type: str
    confidence: float = 1.0
    evidence: str = ""
    source_articles: list[str] = field(default_factory=list)


@dataclass
class TechTrend:
    """技术趋势"""
    keyword: str
    category: str
    current_count: int
    previous_count: int
    growth_rate: float
    first_seen: Optional[str] = None
    last_seen: Optional[str] = None
    related_entities: list[str] = field(default_factory=list)


@dataclass
class ArchitecturePattern:
    """架构模式"""
    name: str
    pattern_type: str
    description: str
    technologies: list[str] = field(default_factory=list)
    pros: list[str] = field(default_factory=list)
    cons: list[str] = field(default_factory=list)
    use_cases: list[str] = field(default_factory=list)
    source_articles: list[str] = field(default_factory=list)


@dataclass
class Opportunity:
    """AI时代个人机会"""
    title: str
    dimension: str
    description: str
    evidence: list[str] = field(default_factory=list)
    skills_needed: list[str] = field(default_factory=list)
    market_signal: str = ""
    action_items: list[str] = field(default_factory=list)
    confidence: float = 0.5
    time_horizon: str = "6-12个月"
