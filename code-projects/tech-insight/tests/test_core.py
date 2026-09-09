"""核心模块单元测试"""
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from src.config import Config
from src.storage.models import Article
from src.storage.database import init_db, save_article, get_stats, article_exists
from src.collectors.base import BaseCollector
from src.collectors.factory import create_collector, get_all_source_keys
from src.analysis.trend_analysis import TrendAnalyzer
from src.analysis.knowledge_graph import KnowledgeGraphBuilder
from src.storage.vectorstore import VectorStore


class TestConfig:
    def test_settings_load(self):
        s = Config.settings()
        assert "llm" in s
        assert "storage" in s

    def test_sources_load(self):
        sources = Config.sources()
        assert "sources" in sources
        assert "infoq" in sources["sources"]
        assert "devto" in sources["sources"]

    def test_env_var_resolution(self):
        os.environ["TEST_VAR_123"] = "resolved_value"
        s = Config.settings()
        # settings.yaml uses {env:...} in llm section
        assert s is not None

    def test_ensure_dirs(self):
        Config.ensure_dirs()
        assert (Config.base_dir() / "data" / "raw").exists()
        assert (Config.base_dir() / "data" / "processed").exists()


class TestModels:
    def test_article_creation(self):
        a = Article(title="Test", url="https://example.com/test", source="test")
        assert a.title == "Test"
        assert a.source == "test"
        d = a.to_dict()
        assert d["title"] == "Test"
        assert "||".join([]) == d["tags"]


class TestDatabase:
    def setup_method(self):
        init_db()

    def test_save_and_query(self):
        a = Article(
            title="Unit Test Article",
            url="https://example.com/unit-test",
            source="unittest",
            content="This is test content for unit testing.",
        )
        save_article(a)
        assert article_exists("unittest", "https://example.com/unit-test")

    def test_stats(self):
        stats = get_stats()
        assert "total_articles" in stats
        assert "by_source" in stats
        assert isinstance(stats["total_articles"], int)


class TestCollectors:
    def test_get_all_source_keys(self):
        keys = get_all_source_keys()
        assert "infoq" in keys
        assert "devto" in keys
        assert len(keys) >= 10

    def test_create_collector(self):
        c = create_collector("devto")
        assert c is not None
        assert c.source_key == "devto"

    def test_robots_check(self):
        c = create_collector("devto")
        # robots.txt check should not crash
        result = c.can_fetch("https://dev.to/")
        assert isinstance(result, bool)

    def test_create_article(self):
        c = create_collector("devto")
        a = c._create_article(title="Test", url="https://dev.to/test")
        assert a.source == "devto"
        assert a.title == "Test"
        assert a.id != ""


class TestVectorStore:
    def test_add_and_search(self):
        vs = VectorStore()
        initial = vs.size
        vs.add(
            ids=["v1", "v2"],
            texts=["人工智能", "云计算"],
            vectors=[[0.1, 0.9, 0.0], [0.9, 0.1, 0.0]],
        )
        assert vs.size == initial + 2
        results = vs.search([0.1, 0.9, 0.0], top_k=2)
        assert len(results) >= 1
        assert results[0]["text"] == "人工智能"
        assert results[0]["score"] > 0.99

    def test_empty_search(self):
        vs = VectorStore()
        results = vs.search([0.0, 0.0, 0.0], top_k=5)
        # May have leftover from other test, but should not crash
        assert isinstance(results, list)


class TestTrendAnalyzer:
    def test_analyze(self):
        ta = TrendAnalyzer()
        articles = [
            {"title": "GPT and LLM are hot", "content": "GPT LLM Agent RAG", "tags": "",
             "published_at": "2026-01-01T00:00:00", "collected_at": "2026-01-01T00:00:00",
             "view_count": 100, "like_count": 10, "comment_count": 5, "bookmark_count": 3,
             "source_name": "test", "url": "http://test.com/1", "id": "1"},
            {"title": "Rust vs Go", "content": "Rust Go performance", "tags": "",
             "published_at": "2026-01-02T00:00:00", "collected_at": "2026-01-02T00:00:00",
             "view_count": 200, "like_count": 20, "comment_count": 10, "bookmark_count": 5,
             "source_name": "test", "url": "http://test.com/2", "id": "2"},
        ]
        result = ta.analyze(articles)
        assert "trends" in result
        assert "hot_topics" in result
        assert "emerging" in result
        assert len(result["hot_topics"]) > 0


class TestKnowledgeGraph:
    def test_keyword_fallback(self):
        kg = KnowledgeGraphBuilder()
        result = kg._keyword_fallback("GPT and LLM", "GPT LLM Agent RAG Docker Kubernetes")
        assert "entities" in result
        assert len(result["entities"]) > 0
        names = [e["name"] for e in result["entities"]]
        assert "GPT" in names or "LLM" in names


class TestReportGenerator:
    def test_generate_all(self):
        from src.reports.generator import ReportGenerator
        gen = ReportGenerator()
        results = gen.generate_all({
            "content_digest": {"by_source": {"devto": 10}, "hot_topics": []},
            "knowledge_graph": {"nodes": [], "edges": [], "communities": [],
                                "stats": {"total_nodes": 0, "total_edges": 0, "by_type": {}}},
            "trend_report": {"trends": [], "emerging": [], "declining": [],
                             "hot_topics": [], "narrative": "test", "time_windows": [7]},
            "architecture_map": {"patterns": [], "tech_stacks": {},
                                 "landscape": {"top_technologies": [], "pattern_groups": {}},
                                 "stats": {"total_patterns": 0, "by_type": {}, "total_technologies": 0}},
            "industry_insight": {},
            "ai_opportunity": {"opportunities": [], "by_dimension": {}, "summary": "test"},
        })
        assert "master" in results
        assert len(results) >= 5


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
