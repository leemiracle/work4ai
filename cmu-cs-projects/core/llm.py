"""
CMU SCS Shared Infrastructure
LLM 抽象层：litellm 统一接口 + Mock 模式 fallback

设计原则：
1. 真实优先：有 API key 用真实 LLM
2. Mock 兜底：无 key 也能跑通逻辑（教学用）
3. 接口一致：上层不感知是真实还是 mock
"""
from __future__ import annotations
import os
import re
import json
import random
from typing import Optional
from dataclasses import dataclass


@dataclass
class Message:
    role: str  # "system" | "user" | "assistant" | "tool"
    content: str
    name: Optional[str] = None  # tool name


class LLMClient:
    """统一 LLM 客户端：litellm 优先，Mock 兜底"""

    def __init__(self, model: str = "mock", verbose: bool = False):
        self.model = model
        self.verbose = verbose
        self._is_mock = self._detect_mock()

    def _detect_mock(self) -> bool:
        """检测是否需要 mock 模式"""
        if self.model.startswith("mock"):
            return True
        # 检查是否有任何 API key
        keys = ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY",
                "DEEPSEEK_API_KEY", "GROQ_API_KEY"]
        return not any(os.getenv(k) for k in keys)

    def chat(self, messages: list[Message], temperature: float = 0.7,
             max_tokens: int = 500) -> str:
        """对话接口，返回 assistant 文本"""
        if self._is_mock:
            return self._mock_chat(messages, temperature)
        return self._real_chat(messages, temperature, max_tokens)

    def _real_chat(self, messages: list[Message], temperature: float,
                   max_tokens: int) -> str:
        """真实 LLM 调用（litellm）"""
        try:
            import litellm
            litellm.verbose = self.verbose
            msgs = [{"role": m.role, "content": m.content} for m in messages]
            resp = litellm.completion(
                model=self.model,
                messages=msgs,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return resp.choices[0].message.content
        except ImportError:
            print("⚠️  litellm 未安装，回退到 mock 模式")
            self._is_mock = True
            return self._mock_chat(messages, temperature)
        except Exception as e:
            print(f"⚠️  LLM 调用失败: {e}，回退到 mock")
            return self._mock_chat(messages, temperature)

    def _mock_chat(self, messages: list[Message], temperature: float) -> str:
        """Mock 实现：基于规则的简单响应，用于教学演示"""
        last_user = ""
        system_prompt = ""
        observation = ""
        for m in reversed(messages):
            if m.role == "user" and not last_user:
                last_user = m.content
            if m.role == "system" and not system_prompt:
                system_prompt = m.content
        # 如果上一条 user 是 Observation，记下来
        if messages and messages[-1].role == "user" and "Observation:" in messages[-1].content:
            observation = messages[-1].content

        # 1. ReAct 优先（system 含 "Thought:" 模板）
        if "Thought:" in system_prompt and ("Final Answer" in system_prompt or "Action:" in system_prompt):
            return self._mock_react_response(last_user, system_prompt, observation)

        # 2. RAG
        if "context:" in system_prompt.lower() or "retrieved context" in system_prompt.lower():
            return self._mock_rag_response(last_user)

        # 3. 简单数学
        math_match = re.search(r'(\d+)\s*([+\-*/])\s*(\d+)', last_user)
        if math_match:
            a, op, b = int(math_match.group(1)), math_match.group(2), int(math_match.group(3))
            ops = {'+': a + b, '-': a - b, '*': a * b, '/': a / b if b else 0}
            return f"[Mock LLM] 计算结果: {a} {op} {b} = {ops[op]}"

        # 4. 默认
        return (f"[Mock LLM] 收到问题: '{last_user[:50]}...'\n"
                f"  模式: 模拟响应（无 API key）\n"
                f"  提示: 设置 OPENAI_API_KEY 等环境变量启用真实 LLM")


    def _mock_react_response(self, query: str, system_prompt: str = "",
                             observation: str = "") -> str:
        """Mock ReAct 响应——遵循 ReAct 格式"""
        # 如果刚刚有 Observation，说明已经执行了一步，现在该 Final Answer 了
        if observation:
            # 从 observation 提取关键信息做最终回答
            obs_content = observation.replace("Observation:", "").strip()[:200]
            return (f"Thought: 基于观察结果，我现在可以回答了\n"
                    f"Final Answer: [Mock Agent] 根据工具调用结果：{obs_content}")

        # 第一次响应：决策用哪个工具
        # 复杂表达式（带括号或多个运算符）→ calculator
        if re.search(r'\d.*[+\-*/].*\d', query) or '(' in query:
            # 提取数学表达式
            expr_match = re.search(r'[\d\s+\-*/().]+', query)
            expr = expr_match.group(0).strip() if expr_match else query
            return (f"Thought: 这是一个数学问题，需要使用计算器\n"
                    f"Action: calculator\n"
                    f"Action Input: {expr}")
        # 检索类问题（系统 prompt 提供了 retrieved context）
        if "retrieved context" in system_prompt.lower():
            # 提取相关文档片段
            ctx_match = re.search(r"Retrieved context:(.+)", system_prompt, re.S)
            ctx = ctx_match.group(1)[:300] if ctx_match else "未找到相关文档"
            return (f"Thought: 基于检索到的文档，我可以回答\n"
                    f"Final Answer: [Mock RAG Agent] 根据知识库:\n{ctx[:200]}...")
        # 默认：声明无法处理
        return (f"Thought: 我没有合适的工具回答这个问题\n"
                f"Final Answer: [Mock] 我无法回答 '{query[:50]}...'（mock 模式能力有限）")


    def _mock_rag_response(self, query: str) -> str:
        """Mock RAG 响应"""
        return (f'[Mock RAG] 基于检索到的"文档"回答: {query[:40]}...\n'
                f'  引用: [Mock Doc 1], [Mock Doc 2]')


# 测试
if __name__ == "__main__":
    print("=" * 60)
    print("LLM Client 测试")
    print("=" * 60)

    client = LLMClient(model="mock")

    # 测试 1: 简单对话
    print("\n📝 测试 1: 简单对话")
    resp = client.chat([Message(role="user", content="你好，介绍自己")])
    print(f"Response: {resp}")

    # 测试 2: 数学
    print("\n📝 测试 2: 数学（mock 应识别）")
    resp = client.chat([Message(role="user", content="计算 23 * 17")])
    print(f"Response: {resp}")

    # 测试 3: ReAct
    print("\n📝 测试 3: ReAct 决策")
    resp = client.chat([Message(role="user", content="Thought: 用户问 2+2\nAction:")])
    print(f"Response: {resp}")
