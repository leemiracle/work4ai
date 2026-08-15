"""
Cambridge CST - Shared Infrastructure v0.1
ReAct 循环：Thought → Action → Observation → ... → Final Answer

参考论文：Yao et al. "ReAct: Synergizing Reasoning and Acting in Language Models" ICLR 2023

ReAct Prompt 模板（标准格式）:
```
Thought: 我需要思考下一步
Action: 工具名
Action Input: 工具输入
Observation: 工具返回结果
... (循环)
Thought: 我现在知道答案了
Final Answer: 最终回答
```
"""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import Optional
from .llm import LLMClient, Message
from .tools import ToolRegistry
from .rag import SimpleRAG


SYSTEM_PROMPT_REACT = """You are a helpful AI assistant that solves problems using the ReAct framework.

You have access to these tools:
{tools_description}

You also have access to a knowledge base via RAG (retrieval will be auto-applied when relevant).

Follow this EXACT format for each step:

Thought: <your reasoning about what to do next>
Action: <tool name>
Action Input: <input for the tool>

OR if you have the final answer:

Thought: <your reasoning>
Final Answer: <your final response to the user>

Rules:
- Always think before acting
- Use tools when you need information or computation
- Cite sources (doc ids) when you use retrieved context
- Maximum {max_iterations} iterations
"""


@dataclass
class AgentStep:
    iteration: int
    thought: str
    action: Optional[str] = None
    action_input: Optional[str] = None
    observation: Optional[str] = None
    final_answer: Optional[str] = None


@dataclass
class AgentTrace:
    query: str
    steps: list[AgentStep] = field(default_factory=list)
    final_answer: str = ""

    def __str__(self):
        lines = [f"🔍 Query: {self.query}"]
        for s in self.steps:
            lines.append(f"\n--- 迭代 {s.iteration} ---")
            lines.append(f"Thought: {s.thought}")
            if s.action:
                lines.append(f"Action: {s.action}({s.action_input})")
                lines.append(f"Observation: {s.observation[:200] if s.observation else ''}")
            if s.final_answer:
                lines.append(f"✅ Final Answer: {s.final_answer}")
        return "\n".join(lines)


class ReActAgent:
    """ReAct Agent 主循环"""

    def __init__(
        self,
        llm: LLMClient,
        tools: ToolRegistry,
        rag: Optional[SimpleRAG] = None,
        max_iterations: int = 5,
        verbose: bool = True,
    ):
        self.llm = llm
        self.tools = tools
        self.rag = rag
        self.max_iterations = max_iterations
        self.verbose = verbose

    def _parse_response(self, response: str) -> dict:
        """解析 LLM 的 ReAct 格式响应"""
        result = {"thought": "", "action": None, "action_input": None, "final_answer": None}

        # 提取 Thought
        thought_match = re.search(r"Thought:\s*(.+?)(?=\n(?:Action|Final)|$)", response, re.S)
        if thought_match:
            result["thought"] = thought_match.group(1).strip()

        # 提取 Final Answer
        final_match = re.search(r"Final Answer:\s*(.+)$", response, re.S)
        if final_match:
            result["final_answer"] = final_match.group(1).strip()
            return result

        # 提取 Action + Action Input
        action_match = re.search(r"Action:\s*(\w+)", response)
        input_match = re.search(r"Action Input:\s*(.+?)(?=\n(?:Thought|Final|Observation)|$)",
                                  response, re.S)
        if action_match:
            result["action"] = action_match.group(1).strip()
        if input_match:
            result["action_input"] = input_match.group(1).strip()

        return result

    def run(self, query: str) -> AgentTrace:
        """执行 ReAct 循环"""
        trace = AgentTrace(query=query)

        # 构建初始消息
        system = SYSTEM_PROMPT_REACT.format(
            tools_description=self.tools.describe(),
            max_iterations=self.max_iterations,
        )

        # 如果有 RAG，先检索（增强 query）
        if self.rag and self.rag.store.chunks:
            context, chunks = self.rag.query_with_context(query, top_k=3)
            system += f"\n\nRetrieved context:\n{context}"
            if self.verbose:
                print(f"📚 RAG 检索到 {len(chunks)} 个 chunks")

        messages = [
            Message(role="system", content=system),
            Message(role="user", content=query),
        ]

        for it in range(1, self.max_iterations + 1):
            if self.verbose:
                print(f"\n--- 迭代 {it}/{self.max_iterations} ---")

            # LLM 推理
            response = self.llm.chat(messages, temperature=0.3, max_tokens=300)
            if self.verbose:
                print(f"LLM 响应:\n{response[:300]}")

            # 解析
            parsed = self._parse_response(response)
            step = AgentStep(
                iteration=it,
                thought=parsed["thought"],
                action=parsed["action"],
                action_input=parsed["action_input"],
                final_answer=parsed["final_answer"],
            )

            # 终止条件 1: Final Answer
            if parsed["final_answer"]:
                trace.steps.append(step)
                trace.final_answer = parsed["final_answer"]
                if self.verbose:
                    print(f"\n✅ 完成！")
                return trace

            # 终止条件 2: 无有效 action
            if not parsed["action"]:
                step.final_answer = parsed["thought"] or "（无法解析响应）"
                trace.steps.append(step)
                trace.final_answer = step.final_answer
                return trace

            # 执行工具
            obs = self.tools.run(parsed["action"], parsed["action_input"] or "")
            step.observation = obs
            trace.steps.append(step)

            if self.verbose:
                print(f"Action: {parsed['action']}({parsed['action_input']})")
                print(f"Observation: {obs[:200]}")

            # 把 observation 加到对话
            messages.append(Message(role="assistant", content=response))
            messages.append(Message(
                role="user",
                content=f"Observation: {obs}\n\nContinue. If you have the answer, "
                        f"use 'Final Answer:'"
            ))

        # 超过最大迭代
        trace.final_answer = f"（达到最大迭代 {self.max_iterations}，未得到 final answer）"
        return trace


# 测试
if __name__ == "__main__":
    print("=" * 60)
    print("ReAct Agent 测试")
    print("=" * 60)

    # 初始化组件
    llm = LLMClient(model="mock")
    tools = ToolRegistry()
    rag = SimpleRAG(chunk_size=30)

    # 添加测试文档
    from .rag import Document
    rag.add_documents([
        Document(id="paper1", content=(
            "The Transformer architecture uses self-attention to process tokens in parallel. "
            "BERT is based on the encoder, GPT on the decoder."
        )),
    ])

    agent = ReActAgent(llm=llm, tools=tools, rag=rag, max_iterations=3)

    # 测试用例
    queries = [
        "计算 23 * 17 等于多少？",
        "Transformer 架构是什么？",
    ]
    for q in queries:
        print(f"\n{'='*60}")
        print(f"📝 Query: {q}")
        print(f"{'='*60}")
        trace = agent.run(q)
        print(f"\n{trace}")
