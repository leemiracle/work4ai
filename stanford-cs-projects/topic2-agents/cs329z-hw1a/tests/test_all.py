"""
CS329Z HW1 Part A - 单元测试
覆盖：LLM / RAG / Tools / ReAct / Hybrid Search
"""
import sys
import os
import pytest
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.llm import LLMClient, Message
from agent.tools import ToolRegistry, safe_calculator, mock_search, file_reader
from agent.rag import SimpleRAG, Document, SimpleEmbedder, SimpleVectorStore
from agent.hybrid_search import SimpleBM25, normalize_scores, HybridSearcher
from agent.react import ReActAgent


# ============ LLM Client Tests ============

class TestLLMClient:
    def test_mock_mode_default(self):
        """无 API key 应该用 mock 模式"""
        client = LLMClient(model="mock")
        assert client._is_mock is True

    def test_mock_chat_returns_string(self):
        client = LLMClient(model="mock")
        resp = client.chat([Message(role="user", content="hello")])
        assert isinstance(resp, str)
        assert len(resp) > 0

    def test_mock_math(self):
        """Mock 应该识别数学表达式"""
        client = LLMClient(model="mock")
        resp = client.chat([Message(role="user", content="计算 5 * 7")])
        assert "5" in resp and "7" in resp and "35" in resp

    def test_mock_react_format(self):
        """Mock 在 ReAct 系统 prompt 下应该返回 ReAct 格式"""
        client = LLMClient(model="mock")
        system = ("Thought:...\nAction:...\nAction Input:...\n"
                  "Final Answer:...")
        resp = client.chat([
            Message(role="system", content=system),
            Message(role="user", content="计算 10 + 20")
        ])
        assert "Thought:" in resp
        assert "Action:" in resp or "Final Answer:" in resp


# ============ Tools Tests ============

class TestCalculator:
    def test_addition(self):
        assert "30" in safe_calculator("10 + 20")

    def test_subtraction(self):
        assert "0" in safe_calculator("10 - 10")

    def test_multiplication(self):
        assert "50" in safe_calculator("5 * 10")

    def test_division(self):
        assert "2.5" in safe_calculator("5 / 2")

    def test_power(self):
        assert "8" in safe_calculator("2 ** 3")

    def test_compound(self):
        assert "20" in safe_calculator("(2 + 2) * 5")

    def test_safety_import(self):
        """import os 应该被拒绝"""
        result = safe_calculator("import os")
        assert "失败" in result or "错误" in result

    def test_safety_dunder(self):
        """__import__ 应该被拒绝"""
        result = safe_calculator("__import__('os')")
        assert "失败" in result or "错误" in result


class TestToolRegistry:
    def test_default_tools_loaded(self):
        reg = ToolRegistry()
        names = reg.list_names()
        assert "calculator" in names
        assert "search" in names
        assert "read_file" in names

    def test_unknown_tool(self):
        reg = ToolRegistry()
        result = reg.run("nonexistent", "input")
        assert "未知工具" in result or "错误" in result

    def test_register_custom(self):
        reg = ToolRegistry()
        from agent.tools import Tool
        reg.register(Tool(name="echo", description="echo input", func=lambda x: f"ECHO: {x}", examples=[]))
        assert "echo" in reg.list_names()
        assert "ECHO: hi" == reg.run("echo", "hi")


# ============ RAG Tests ============

class TestEmbedder:
    def test_dimension(self):
        emb = SimpleEmbedder(dim=64)
        v = emb.embed("hello world")
        assert len(v) == 64

    def test_normalized(self):
        """Hash embedding 应该 L2 normalized"""
        emb = SimpleEmbedder(dim=32)
        v = emb.embed("test")
        norm = sum(x*x for x in v) ** 0.5
        assert abs(norm - 1.0) < 0.01

    def test_same_input_same_output(self):
        emb = SimpleEmbedder(dim=32)
        v1 = emb.embed("hello world")
        v2 = emb.embed("hello world")
        assert v1 == v2


class TestRAG:
    def test_add_and_retrieve(self):
        rag = SimpleRAG(chunk_size=10, chunk_overlap=2)
        docs = [
            Document(id="d1", content="cats are great pets"),
            Document(id="d2", content="dogs are loyal companions"),
            Document(id="d3", content="python is a programming language"),
        ]
        n = rag.add_documents(docs)
        assert n > 0

        # 应该 retrieve 相关文档
        results = rag.retrieve("cats pets", top_k=1)
        assert len(results) > 0
        assert results[0].doc_id == "d1"

    def test_empty_query(self):
        rag = SimpleRAG()
        results = rag.retrieve("anything", top_k=5)
        assert results == []

    def test_chunking(self):
        """长文档应该被切成多个 chunks"""
        rag = SimpleRAG(chunk_size=5, chunk_overlap=1)
        long_doc = Document(id="long", content=" ".join([f"word{i}" for i in range(20)]))
        chunks = rag._chunk_document(long_doc)
        assert len(chunks) > 1


# ============ Hybrid Search Tests ============

class TestBM25:
    def test_exact_match(self):
        bm25 = SimpleBM25()
        bm25.fit([("d1", "hello world"), ("d2", "goodbye universe")])
        scores = bm25.score("hello")
        assert scores["d1"] > 0
        assert scores.get("d2", 0) == 0

    def test_term_frequency(self):
        bm25 = SimpleBM25()
        bm25.fit([
            ("d1", "cat cat cat"),
            ("d2", "cat"),
        ])
        scores = bm25.score("cat")
        # 多次出现 cat 的文档分数应该更高
        assert scores["d1"] > scores["d2"]


class TestNormalize:
    def test_basic(self):
        scores = {"a": 1, "b": 3, "c": 5}
        norm = normalize_scores(scores)
        assert norm["a"] == 0
        assert norm["c"] == 1
        assert abs(norm["b"] - 0.5) < 0.01

    def test_empty(self):
        assert normalize_scores({}) == {}

    def test_constant(self):
        scores = {"a": 5, "b": 5}
        norm = normalize_scores(scores)
        assert norm["a"] == 1 and norm["b"] == 1


# ============ ReAct Agent Tests ============

class TestReActAgent:
    def test_math_task(self):
        """数学任务应该调 calculator 并得到正确结果"""
        llm = LLMClient(model="mock")
        tools = ToolRegistry()
        agent = ReActAgent(llm=llm, tools=tools, rag=None, max_iterations=3,
                            verbose=False)
        trace = agent.run("计算 5 + 3")
        assert trace.final_answer
        assert "8" in trace.final_answer or "calculator" in str(trace.steps).lower()

    def test_max_iterations(self):
        """超过 max_iterations 应该终止"""
        llm = LLMClient(model="mock")
        tools = ToolRegistry()
        agent = ReActAgent(llm=llm, tools=tools, max_iterations=1, verbose=False)
        trace = agent.run("complex task")
        assert len(trace.steps) <= 1

    def test_trace_structure(self):
        llm = LLMClient(model="mock")
        tools = ToolRegistry()
        agent = ReActAgent(llm=llm, tools=tools, max_iterations=2, verbose=False)
        trace = agent.run("test")
        assert trace.query == "test"
        assert isinstance(trace.steps, list)
        assert all(hasattr(s, "thought") for s in trace.steps)


# ============ Integration Test ============

class TestIntegration:
    def test_full_pipeline_math(self):
        """端到端：数学任务"""
        llm = LLMClient(model="mock")
        tools = ToolRegistry()
        rag = SimpleRAG(chunk_size=10)
        rag.add_documents([Document(id="d1", content="math is fun")])
        agent = ReActAgent(llm=llm, tools=tools, rag=rag, max_iterations=3, verbose=False)
        trace = agent.run("计算 7 * 6")
        assert trace.final_answer

    def test_full_pipeline_rag(self):
        """端到端：知识检索"""
        llm = LLMClient(model="mock")
        tools = ToolRegistry()
        rag = SimpleRAG(chunk_size=20)
        rag.add_documents([
            Document(id="paper", content="RAG was introduced in 2020 by Lewis et al."),
        ])
        agent = ReActAgent(llm=llm, tools=tools, rag=rag, max_iterations=3, verbose=False)
        trace = agent.run("When was RAG introduced?")
        assert "2020" in trace.final_answer or "paper" in trace.final_answer.lower()
