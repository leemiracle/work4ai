"""
CMU SCS Shared Evaluation Framework
共享评估模块：所有课程项目都用这个评估

4-tuple (CMU SCS W7):
  - request: 任务请求
  - environment: 执行环境（含工具/数据）
  - stopping_criteria: 终止条件
  - scorer: 评分函数
"""
from __future__ import annotations
import re
import math
from dataclasses import dataclass, field
from typing import Any, Callable, Optional


@dataclass
class EvalRequest:
    query: str
    metadata: dict = field(default_factory=dict)


@dataclass
class EvalEnvironment:
    tools: dict = field(default_factory=dict)
    knowledge: list = field(default_factory=list)
    constraints: dict = field(default_factory=dict)


@dataclass
class EvalResult:
    request: EvalRequest
    response: str
    score: float
    passed: bool
    rationale: str = ""
    metadata: dict = field(default_factory=dict)


# ============ Scorers ============

def exact_match(expected: str) -> Callable[[str], tuple[float, str]]:
    """精确匹配 scorer"""
    def scorer(response: str) -> tuple[float, str]:
        passed = expected.lower().strip() in response.lower()
        return (1.0 if passed else 0.0,
                f"Expected '{expected}' {'✓' if passed else '✗'}")
    return scorer


def number_extractor(text: str) -> list[float]:
    """从文本提取所有数字"""
    return [float(x) for x in re.findall(r'-?\d+(?:\.\d+)?', text)]


def numeric_match(expected: float, tolerance: float = 0.01) -> Callable:
    """数值匹配（容差）"""
    def scorer(response: str) -> tuple[float, str]:
        nums = number_extractor(response)
        if not nums:
            return 0.0, "未找到数字"
        for n in nums:
            if abs(n - expected) <= tolerance:
                return 1.0, f"匹配 {expected} ✓"
        return 0.0, f"期望 {expected}, 实际数字: {nums}"
    return scorer


def keyword_scorer(keywords: list[str], min_hits: int = 1) -> Callable:
    """关键词命中 scorer"""
    def scorer(response: str) -> tuple[float, str]:
        resp_lower = response.lower()
        hits = sum(1 for k in keywords if k.lower() in resp_lower)
        score = min(hits / max(min_hits, 1), 1.0)
        return score, f"命中 {hits}/{len(keywords)} 关键词"
    return scorer


def llm_judge_prompt(question: str, response: str,
                     rubric: str) -> float:
    """简化版 LLM-as-Judge（mock）。
    真实场景需要调 LLM 评分。这里用关键词 + 长度启发式。
    """
    score = 0.0
    # 长度合理（10-500 字符）
    if 10 <= len(response) <= 500:
        score += 0.2
    # 提及 rubric 关键词
    rubric_terms = re.findall(r'\w+', rubric.lower())
    resp_lower = response.lower()
    hits = sum(1 for t in rubric_terms if t in resp_lower)
    score += min(hits / max(len(rubric_terms), 1), 0.5)
    # 包含数字 / 引用
    if re.search(r'\d|引用|来源|source', response, re.I):
        score += 0.15
    # 没有幻觉标记（如"我不知道"+"猜测"组合）
    if not ("猜测" in response and "不确定" in response):
        score += 0.15
    return min(score, 1.0)


# ============ 4-Tuple Suite ============

@dataclass
class EvalCase:
    """4-tuple 评估用例"""
    name: str
    request: EvalRequest
    environment: EvalEnvironment
    stopping_criteria: Callable[[str], bool]  # 返回 True = 终止
    scorer: Callable[[str], tuple[float, str]]


class EvalSuite:
    """评估套件：跑多个 case"""

    def __init__(self, name: str = "default"):
        self.name = name
        self.cases: list[EvalCase] = []

    def add(self, case: EvalCase):
        self.cases.append(case)

    def run(self, agent_fn: Callable[[EvalRequest, EvalEnvironment], str],
            verbose: bool = True) -> list[EvalResult]:
        """跑全部 cases，调用 agent_fn 返回 response"""
        results = []
        for case in self.cases:
            if verbose:
                print(f"\n📋 Case: {case.name}")
                print(f"   Query: {case.request.query[:60]}")

            try:
                response = agent_fn(case.request, case.environment)
            except Exception as e:
                response = f"[AGENT ERROR] {e}"

            # Stopping criteria check
            terminated = case.stopping_criteria(response)
            # Score
            score, rationale = case.scorer(response)
            passed = score >= 0.7 and terminated

            result = EvalResult(
                request=case.request, response=response,
                score=score, passed=passed, rationale=rationale,
            )
            results.append(result)
            if verbose:
                print(f"   Score: {score:.2f} {'✅' if passed else '❌'}")
                print(f"   Rationale: {rationale}")
                print(f"   Response: {response[:100]}")

        # Summary
        passed_n = sum(1 for r in results if r.passed)
        if verbose:
            print(f"\n📊 Summary: {passed_n}/{len(results)} passed "
                  f"({passed_n/max(len(results),1)*100:.0f}%)")
        return results


# ============ Pass@k vs Pass^k ============

def pass_at_k(results_per_query: list[list[bool]], k: int) -> float:
    """pass@k: 至少 1 次通过（best case）"""
    if not results_per_query:
        return 0.0
    passes = []
    for trials in results_per_query:
        trials_k = trials[:k]
        passes.append(any(trials_k))
    return sum(passes) / len(passes)


def pass_pow_k(results_per_query: list[list[bool]], k: int) -> float:
    """pass^k: 全部通过（reliability）"""
    if not results_per_query:
        return 0.0
    passes = []
    for trials in results_per_query:
        trials_k = trials[:k]
        passes.append(all(trials_k) and len(trials_k) == k)
    return sum(passes) / len(passes)


# ============ Demo ============

if __name__ == "__main__":
    print("=" * 60)
    print("Eval Framework Demo")
    print("=" * 60)

    suite = EvalSuite(name="mini-agent-eval")

    # Case 1: 数学
    suite.add(EvalCase(
        name="math_simple",
        request=EvalRequest(query="计算 5 + 3"),
        environment=EvalEnvironment(),
        stopping_criteria=lambda r: True,
        scorer=numeric_match(8.0),
    ))

    # Case 2: 关键词
    suite.add(EvalCase(
        name="knowledge",
        request=EvalRequest(query="什么是 transformer"),
        environment=EvalEnvironment(),
        stopping_criteria=lambda r: True,
        scorer=keyword_scorer(["attention", "self-attention", "encoder", "decoder"], min_hits=2),
    ))

    # Mock agent
    def mock_agent(req, env):
        if "5 + 3" in req.query:
            return "结果是 8"
        return "Transformer 使用 self-attention 机制，encoder-decoder 架构"

    results = suite.run(mock_agent)

    # pass@k demo
    print(f"\npass@k demo:")
    trials = [
        [True, False, True],   # query 1: 2/3 通过
        [True, True, True],    # query 2: 3/3 通过
        [False, False, True],  # query 3: 1/3 通过
    ]
    print(f"  pass@1: {pass_at_k(trials, 1):.2f}")  # 至少 1 次
    print(f"  pass@3: {pass_at_k(trials, 3):.2f}")
    print(f"  pass^3: {pass_pow_k(trials, 3):.2f}")  # 全部通过
