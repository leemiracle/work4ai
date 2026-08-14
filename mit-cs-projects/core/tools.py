"""
6.5940 Agent Lab - mini-Agent v0.1
工具集：calculator / search / file_reader

参考：MCP (Model Context Protocol) Specification, Linux Foundation 2025
设计原则：
- 每个工具有明确的 input schema
- 工具自己处理错误，返回结构化结果
- 易于扩展（新增工具只需 1 个函数）
"""
from __future__ import annotations
import ast
import operator
import re
from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class Tool:
    name: str
    description: str
    func: Callable[[str], str]
    examples: list[str]


def safe_calculator(expression: str) -> str:
    """安全计算器：用 AST 解析，避免 eval 风险"""
    try:
        # 支持 + - * / ** %
        allowed_ops = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Pow: operator.pow,
            ast.Mod: operator.mod,
            ast.USub: operator.neg,
        }

        def _eval(node):
            if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
                return node.value
            if isinstance(node, ast.BinOp) and type(node.op) in allowed_ops:
                return allowed_ops[type(node.op)](_eval(node.left), _eval(node.right))
            if isinstance(node, ast.UnaryOp) and type(node.op) in allowed_ops:
                return allowed_ops[type(node.op)](_eval(node.operand))
            raise ValueError(f"不支持的表达式: {ast.dump(node)}")

        tree = ast.parse(expression.strip(), mode="eval")
        result = _eval(tree.body)
        return f"结果: {result}"
    except Exception as e:
        return f"计算失败: {e}"


def mock_search(query: str) -> str:
    """模拟搜索（无真实 API）"""
    results = [
        f"  [1] Wikipedia: 关于 '{query}' 的基础介绍...",
        f"  [2] ArXiv 论文: '{query}' 相关最新研究...",
        f"  [3] Stack Overflow: '{query}' 常见问题解答...",
    ]
    return "搜索结果（mock）:\n" + "\n".join(results)


def file_reader(path: str) -> str:
    """读取本地文件"""
    try:
        # 安全限制：只读当前目录及子目录
        if ".." in path or path.startswith("/"):
            return f"错误: 不允许的路径 '{path}'"
        with open(path, "r", encoding="utf-8") as f:
            content = f.read(2000)  # 最多 2000 字符
        return f"文件 '{path}' 内容（前 {len(content)} 字符）:\n{content}"
    except FileNotFoundError:
        return f"错误: 文件 '{path}' 不存在"
    except Exception as e:
        return f"读取失败: {e}"


# 标准工具集
DEFAULT_TOOLS: list[Tool] = [
    Tool(
        name="calculator",
        description="数学计算。输入数学表达式如 '23 * 17' 或 '(2+3)**2'",
        func=safe_calculator,
        examples=["23 * 17", "(2+3)**2", "100 / 7"],
    ),
    Tool(
        name="search",
        description="网络搜索（mock）。输入查询词",
        func=mock_search,
        examples=["transformer architecture", "RLHF tutorial"],
    ),
    Tool(
        name="read_file",
        description="读取本地文件（限制当前目录）",
        func=file_reader,
        examples=["README.md", "data/test.txt"],
    ),
]


class ToolRegistry:
    """工具注册表"""

    def __init__(self, tools: list[Tool] = None):
        self.tools: dict[str, Tool] = {}
        for t in (tools or DEFAULT_TOOLS):
            self.register(t)

    def register(self, tool: Tool):
        self.tools[tool.name] = tool

    def get(self, name: str) -> Tool | None:
        return self.tools.get(name)

    def list_names(self) -> list[str]:
        return list(self.tools.keys())

    def run(self, name: str, input_str: str) -> str:
        tool = self.get(name)
        if not tool:
            return f"错误: 未知工具 '{name}'。可用: {list(self.tools.keys())}"
        try:
            return tool.func(input_str)
        except Exception as e:
            return f"工具 {name} 执行失败: {e}"

    def describe(self) -> str:
        """生成给 LLM 的工具说明"""
        lines = ["可用工具:"]
        for name, t in self.tools.items():
            lines.append(f"- {name}: {t.description}")
            if t.examples:
                lines.append(f"    示例: {', '.join(t.examples[:2])}")
        return "\n".join(lines)


# 测试
if __name__ == "__main__":
    print("=" * 60)
    print("工具集测试")
    print("=" * 60)

    reg = ToolRegistry()

    print("\n📋 工具说明:")
    print(reg.describe())

    print("\n🧮 calculator 测试:")
    for expr in ["23 * 17", "(2+3)**2", "100 / 7", "1 + + 2", "import os"]:
        result = reg.run("calculator", expr)
        print(f"  '{expr}' → {result}")

    print("\n🔍 search 测试:")
    print(reg.run("search", "transformer"))

    print("\n📁 read_file 测试:")
    print(reg.run("read_file", "README.md")[:100] + "...")

    print("\n❌ 未知工具:")
    print(reg.run("nonexistent", "test"))
