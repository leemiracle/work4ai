"""
CS329Z HW3 + CS329A Self-Improve + CS329M Coding Agent
三个深度项目合并到一个文件（最大化覆盖）

1. CS329Z HW3 - 4-tuple Eval Suite
2. CS329A Self-Improving Agent（bootstrap reasoning）
3. CS329M Coding Agent（mini-SWE-agent）
"""
from __future__ import annotations
import os
import sys
import re
import ast
import json
import math
import time
import random
import subprocess
import tempfile
from collections import Counter, defaultdict
from dataclasses import dataclass, field, asdict
from typing import Any, Callable, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "topic2-agents", "cs329z-hw1a"))
from agent import LLMClient, Message, ToolRegistry, SimpleRAG, Document, ReActAgent


# ============================================
# 🎯 PART 1: CS329Z HW3 - 完整 4-tuple Eval
# ============================================

@dataclass
class EvalTuple:
    """CS329Z 4-tuple: (request, environment, stopping_criteria, scorer)"""
    name: str
    request: str
    environment: dict  # tools, knowledge, constraints
    stopping_criteria: Callable[[str], bool]
    scorer: Callable[[str], tuple[float, str]]


class EvalHarness:
    """完整评估套件：4-tuple + LLM-as-judge + pass@k vs pass^k"""

    def __init__(self, name: str = "cs329z-hw3"):
        self.name = name
        self.cases: list[EvalTuple] = []

    def add(self, case: EvalTuple):
        self.cases.append(case)
        return self

    def run(self, agent_fn: Callable[[str, dict], str],
            n_runs: int = 1, verbose: bool = True) -> dict:
        """跑 n_runs 次，计算 pass@k vs pass^k"""
        all_results = []
        for run_idx in range(n_runs):
            if verbose and n_runs > 1:
                print(f"\n--- Run {run_idx + 1}/{n_runs} ---")
            run_results = []
            for case in self.cases:
                if verbose:
                    print(f"\n📋 {case.name}")
                    print(f"   Request: {case.request[:60]}")

                try:
                    response = agent_fn(case.request, case.environment)
                except Exception as e:
                    response = f"[ERROR] {e}"

                terminated = case.stopping_criteria(response)
                score, rationale = case.scorer(response)
                passed = score >= 0.7 and terminated

                run_results.append({
                    "case": case.name,
                    "passed": passed,
                    "score": score,
                    "rationale": rationale,
                    "response_preview": response[:100],
                })
                if verbose:
                    print(f"   Score: {score:.2f} {'✅' if passed else '❌'} - {rationale}")

            all_results.append(run_results)

        # 计算 pass@k 和 pass^k
        return self._summarize(all_results, verbose)

    def _summarize(self, all_results: list[list[dict]], verbose: bool) -> dict:
        if not all_results:
            return {}
        n_runs = len(all_results)
        n_cases = len(all_results[0])

        # per-case 通过率
        case_pass_at_k = []
        case_pass_pow_k = []
        for case_idx in range(n_cases):
            trials = [run[case_idx]["passed"] for run in all_results]
            case_pass_at_k.append(any(trials))   # ≥1 通过
            case_pass_pow_k.append(all(trials) if trials else False)  # 全部通过

        pass_at_k = sum(case_pass_at_k) / n_cases
        pass_pow_k = sum(case_pass_pow_k) / n_cases

        avg_score = sum(r["score"] for run in all_results for r in run) / (n_runs * n_cases)

        summary = {
            "n_cases": n_cases,
            "n_runs": n_runs,
            "avg_score": avg_score,
            f"pass@{n_runs}": pass_at_k,
            f"pass^{n_runs}": pass_pow_k,
            "reliability_gap": pass_at_k - pass_pow_k,
        }

        if verbose:
            print(f"\n📊 Summary:")
            print(f"   Avg score: {avg_score:.2f}")
            print(f"   pass@{n_runs} (at least 1 pass): {pass_at_k:.1%}")
            print(f"   pass^{n_runs} (all runs pass):   {pass_pow_k:.1%}")
            print(f"   Reliability gap: {pass_at_k - pass_pow_k:.1%}")
            print(f"   → {'✅ Reliable' if pass_pow_k > 0.8 else '⚠️ Unreliable'}")

        return summary


# ============ 标准 scorers ============

def exact_match_scorer(expected: str):
    def scorer(resp):
        ok = expected.lower() in resp.lower()
        return (1.0 if ok else 0.0,
                f"expected '{expected[:30]}' {'✓' if ok else '✗'}")
    return scorer


def numeric_scorer(expected: float, tolerance: float = 0.01):
    def scorer(resp):
        nums = [float(x) for x in re.findall(r'-?\d+(?:\.\d+)?', resp)]
        for n in nums:
            if abs(n - expected) <= tolerance:
                return 1.0, f"matched {expected} ✓"
        return 0.0, f"no match for {expected}"
    return scorer


def keyword_scorer(keywords: list[str], min_hits: int = 1):
    def scorer(resp):
        hits = sum(1 for k in keywords if k.lower() in resp.lower())
        score = min(hits / max(min_hits, 1), 1.0)
        return score, f"hit {hits}/{len(keywords)}"
    return scorer


def llm_judge_scorer(rubric: str, llm: Optional[LLMClient] = None):
    """LLM-as-judge（mock 简化版）"""
    def scorer(resp):
        # 真实场景：调 LLM 用 rubric 打分
        # Mock: 用关键词匹配 + 长度启发式
        score = 0.0
        rubric_terms = re.findall(r'\w+', rubric.lower())
        hits = sum(1 for t in rubric_terms if t in resp.lower())
        score += min(hits / max(len(rubric_terms), 1), 0.5)
        if 10 < len(resp) < 1000:
            score += 0.2
        if any(w in resp.lower() for w in ["because", "therefore", "由于", "因为"]):
            score += 0.15
        if not any(bad in resp.lower() for bad in ["i don't know", "cannot", "无法"]):
            score += 0.15
        return min(score, 1.0), f"LLM judge: {score:.2f}"
    return scorer


# ============ Demo ============

def hw3_demo():
    print("=" * 70)
    print("CS329Z HW3: 4-tuple Evaluation Framework")
    print("=" * 70)

    # 定义测试 cases
    harness = EvalHarness("cs329z-hw3")

    # Case 1: 数学（精确）
    harness.add(EvalTuple(
        name="math_addition",
        request="What is 23 + 17?",
        environment={"tools": ["calculator"]},
        stopping_criteria=lambda r: True,
        scorer=numeric_scorer(40.0),
    ))

    # Case 2: 知识（关键词）
    harness.add(EvalTuple(
        name="knowledge_rag",
        request="What is RAG?",
        environment={"knowledge": "retrieval-augmented generation"},
        stopping_criteria=lambda r: True,
        scorer=keyword_scorer(["retrieval", "generation", "knowledge"], min_hits=2),
    ))

    # Case 3: LLM judge（开放）
    harness.add(EvalTuple(
        name="open_ended_explanation",
        request="Explain how attention works in transformers.",
        environment={},
        stopping_criteria=lambda r: True,
        scorer=llm_judge_scorer("should explain Q/K/V matrices, softmax, weighted sum"),
    ))

    # Case 4: 工具调用
    harness.add(EvalTuple(
        name="tool_use_required",
        request="Calculate the square root of 144.",
        environment={"tools": ["calculator"]},
        stopping_criteria=lambda r: True,
        scorer=numeric_scorer(12.0),
    ))

    # Case 5: 长度限制
    harness.add(EvalTuple(
        name="length_constrained",
        request="Summarize the benefits of exercise in 2 sentences.",
        environment={"constraints": {"max_length": 200}},
        stopping_criteria=lambda r: True,
        scorer=lambda r: (
            min(len(r) / 100, 1.0) if len(r) <= 200 else 0.3,
            f"length={len(r)}"
        ),
    ))

    # Mock agent
    def mock_agent(query: str, env: dict) -> str:
        if "23 + 17" in query:
            return "23 + 17 = 40"
        if "RAG" in query.upper():
            return "RAG (Retrieval-Augmented Generation) combines retrieval with generation for knowledge tasks."
        if "attention" in query.lower():
            return ("Attention in transformers uses Q/K/V matrices. "
                    "Softmax over Q·K^T gives weights, weighted sum of V is output. "
                    "Therefore it can attend to relevant tokens.")
        if "square root" in query.lower() and "144" in query:
            return "sqrt(144) = 12"
        if "exercise" in query.lower():
            return "Exercise improves cardiovascular health and boosts mood. Therefore it's essential."
        return f"[Mock agent] Response to: {query}"

    # 跑 5 次计算 pass@5 vs pass^5
    results = harness.run(mock_agent, n_runs=5, verbose=False)

    print(f"\n📋 Test cases:")
    for case in harness.cases:
        print(f"   • {case.name}: {case.request[:50]}")

    print(f"\n📊 Results (5 runs):")
    for k, v in results.items():
        if isinstance(v, float):
            print(f"   {k}: {v:.2%}")
        else:
            print(f"   {k}: {v}")

    print(f"\n💡 关键洞察:")
    print(f"   - pass@k vs pass^k 差距 = reliability gap")
    print(f"   - 差距大说明 agent 不稳定（生产环境危险）")
    print(f"   - 评估比训练更重要（没评估就不知道改了是不是变好）")


# ============================================
# 🔄 PART 2: CS329A Self-Improving Agent
# STaR (Self-Taught Reasoner) 简化版
# ============================================

@dataclass
class STaRSample:
    question: str
    correct_answer: str
    reasoning: str = ""
    correct: bool = False


class STaRAgent:
    """
    Zelikman et al. 2022 - Self-Taught Reasoner
    核心思想：
    1. Agent 生成 reasoning + answer
    2. 用 ground truth 验证
    3. 把成功的 reasoning 当训练数据
    4. 重新训练（SFT），变得更聪明
    5. 循环

    数学：
    π_{n+1} = SFT(π_n, {successful rationalizations from π_n})
    """

    def __init__(self, llm: Optional[LLMClient] = None):
        self.llm = llm or LLMClient(model="mock")
        self.training_data: list[STaRSample] = []
        self.iteration = 0
        self.performance_history: list[float] = []

    def generate_reasoning(self, question: str) -> str:
        """让 LLM 生成推理（mock）"""
        # 真实场景：调 LLM with question
        # Mock: 简单规则
        if re.search(r'\d+\s*[+\-*/]\s*\d+', question):
            m = re.search(r'(\d+)\s*([+\-*/])\s*(\d+)', question)
            if m:
                a, op, b = int(m.group(1)), m.group(2), int(m.group(3))
                ops = {'+': a+b, '-': a-b, '*': a*b, '/': a/b if b else 0}
                return f"To solve {a} {op} {b}, I apply the operation: {a} {op} {b} = {ops[op]}"
        if "capital" in question.lower():
            countries = {"france": "Paris", "japan": "Tokyo", "brazil": "Brasília"}
            for c, cap in countries.items():
                if c in question.lower():
                    return f"The capital of {c} is {cap}."
        return f"I think the answer involves reasoning about '{question[:30]}'"

    def rationalize(self, question: str, correct_answer: str) -> str:
        """With hint: 给了答案，让 LLM 反推 reasoning（Zelikman 的关键创新）"""
        return f"Since the answer is {correct_answer}, the reasoning must be: ... therefore {correct_answer}"

    def train_iteration(self, samples: list[STaRSample]) -> dict:
        """一轮 STaR 训练"""
        self.iteration += 1
        print(f"\n🌟 STaR 迭代 {self.iteration}")

        # 1. 对每个问题生成 reasoning + answer
        successful = []
        for s in samples:
            reasoning = self.generate_reasoning(s.question)
            # 验证：reasoning 是否得出正确答案
            extracted_answer = self._extract_answer(reasoning)
            correct = self._check_answer(extracted_answer, s.correct_answer)

            if correct:
                successful.append(STaRSample(
                    question=s.question,
                    correct_answer=s.correct_answer,
                    reasoning=reasoning,
                    correct=True,
                ))
            else:
                # 2. 失败的 → 用 rationalize（给答案反推）
                rationalization = self.rationalize(s.question, s.correct_answer)
                # 假设有 P% 概率 rationalize 成功
                if random.random() < 0.7:
                    successful.append(STaRSample(
                        question=s.question,
                        correct_answer=s.correct_answer,
                        reasoning=rationalization,
                        correct=True,
                    ))

        # 3. SFT 在 successful 数据上（mock）
        success_rate = len(successful) / len(samples)
        improvement = math.log(len(successful) + 1) * 0.04

        self.training_data.extend(successful)
        self.performance_history.append(success_rate)

        print(f"   样本: {len(samples)}")
        print(f"   成功: {len(successful)} ({success_rate:.1%})")
        print(f"   累计训练数据: {len(self.training_data)}")

        return {
            "iteration": self.iteration,
            "samples": len(samples),
            "successful": len(successful),
            "success_rate": success_rate,
            "expected_improvement": improvement,
        }

    @staticmethod
    def _extract_answer(reasoning: str) -> str:
        """从推理中提取答案"""
        # 找最后一个数字
        nums = re.findall(r'-?\d+(?:\.\d+)?', reasoning)
        if nums:
            return nums[-1]
        # 找最后一个句子的"X"
        match = re.search(r'(?:is|are|=)\s*([A-Z]\w+|[a-z]+)$', reasoning, re.I)
        if match:
            return match.group(1)
        return ""

    @staticmethod
    def _check_answer(predicted: str, correct: str) -> bool:
        if not predicted:
            return False
        return predicted.lower().strip() in correct.lower().strip() or \
               correct.lower().strip() in predicted.lower().strip()


def cs329a_demo():
    print("\n" + "=" * 70)
    print("CS329A: Self-Improving Agent (STaR)")
    print("=" * 70)

    random.seed(42)
    agent = STaRAgent()

    # 训练样本（含 ground truth）
    samples = [
        STaRSample("What is 5 + 3?", "8"),
        STaRSample("What is 10 * 4?", "40"),
        STaRSample("What is 100 - 37?", "63"),
        STaRSample("What is 24 / 6?", "4"),
        STaRSample("What is the capital of France?", "Paris"),
        STaRSample("What is the capital of Japan?", "Tokyo"),
        STaRSample("What is 7 * 8?", "56"),
        STaRSample("What is the capital of Brazil?", "Brasília"),
        STaRSample("What is 15 + 27?", "42"),
        STaRSample("What is 9 * 9?", "81"),
    ]

    # 跑 3 轮 STaR
    for _ in range(3):
        agent.train_iteration(samples)

    print(f"\n📊 STaR 训练曲线:")
    print(f"{'Iter':>4} {'Success Rate':>12}")
    for i, rate in enumerate(agent.performance_history, 1):
        bar = "█" * int(rate * 30)
        print(f"{i:>4} {rate:>12.1%} {bar}")

    print(f"\n累计训练数据: {len(agent.training_data)} samples")
    print(f"示例 reasoning:")
    for s in agent.training_data[:2]:
        print(f"   Q: {s.question}")
        print(f"   R: {s.reasoning[:80]}")


# ============================================
# 💻 PART 3: CS329M - Mini Coding Agent
# ============================================

@dataclass
class CodingTask:
    description: str
    starter_code: str
    expected_behavior: str
    test_code: str = ""


class MiniCodingAgent:
    """
    CS329M - 简化版 SWE-agent
    
    工作流：
    1. 理解任务（自然语言）
    2. 生成代码（多次尝试）
    3. 执行测试
    4. 如果失败，分析错误，重试
    5. 提交最终代码
    """

    def __init__(self, llm: Optional[LLMClient] = None, max_attempts: int = 3):
        self.llm = llm or LLMClient(model="mock")
        self.max_attempts = max_attempts

    def solve(self, task: CodingTask) -> dict:
        """解决一个 coding task"""
        print(f"\n💻 Solving: {task.description}")

        attempts = []
        for attempt_idx in range(1, self.max_attempts + 1):
            print(f"   Attempt {attempt_idx}/{self.max_attempts}")

            # 1. 生成代码
            if attempt_idx == 1:
                code = self._generate_initial(task)
            else:
                # 基于上次错误重写
                prev = attempts[-1]
                code = self._fix_code(task, prev["code"], prev["error"])

            # 2. 测试
            test_passed, error = self._run_test(code, task)
            attempts.append({
                "attempt": attempt_idx,
                "code": code,
                "test_passed": test_passed,
                "error": error,
            })

            if test_passed:
                print(f"   ✅ 测试通过！")
                return {"success": True, "code": code, "attempts": attempts}

            print(f"   ❌ 测试失败: {error[:80]}")

        return {"success": False, "code": attempts[-1]["code"], "attempts": attempts}

    def _generate_initial(self, task: CodingTask) -> str:
        """生成初版代码（mock）"""
        # Mock: 基于任务描述模式匹配
        if "add" in task.description.lower() or "sum" in task.description.lower():
            return "def solve(a, b):\n    return a + b\n"
        if "factorial" in task.description.lower():
            return ("def solve(n):\n"
                    "    if n <= 1:\n"
                    "        return 1\n"
                    "    return n * solve(n-1)\n")
        if "fibonacci" in task.description.lower():
            return ("def solve(n):\n"
                    "    if n < 2:\n"
                    "        return n\n"
                    "    return solve(n-1) + solve(n-2)\n")
        if "reverse" in task.description.lower():
            return "def solve(s):\n    return s[::-1]\n"
        return task.starter_code + "\n# TODO: implement\n    pass\n"

    def _fix_code(self, task: CodingTask, prev_code: str, error: str) -> str:
        """基于错误修复代码"""
        # Mock: 简单修复策略
        if "NameError" in error:
            return prev_code.replace("pass", "return None")
        if "TypeError" in error:
            return prev_code
        if "AssertionError" in error or "assert" in error:
            # 可能是逻辑错，加 fallback
            return prev_code + "\n# Fixed version\n"
        return prev_code

    @staticmethod
    def _run_test(code: str, task: CodingTask) -> tuple[bool, str]:
        """执行测试（用 subprocess + 沙箱）"""
        # 安全：用 ast 解析先验证语法
        try:
            ast.parse(code)
        except SyntaxError as e:
            return False, f"SyntaxError: {e}"

        # 在临时文件里执行（沙箱）
        full_code = code + "\n\n" + task.test_code
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(full_code)
            temp_path = f.name

        try:
            result = subprocess.run(
                ["python3", temp_path],
                capture_output=True,
                text=True,
                timeout=2.0,  # 安全超时
            )
            if result.returncode == 0:
                return True, "OK"
            else:
                err = result.stderr[-200:] if result.stderr else "Unknown error"
                return False, err
        except subprocess.TimeoutExpired:
            return False, "Timeout"
        except Exception as e:
            return False, str(e)
        finally:
            os.unlink(temp_path)


def cs329m_demo():
    print("\n" + "=" * 70)
    print("CS329M: Mini Coding Agent (SWE-agent style)")
    print("=" * 70)

    agent = MiniCodingAgent(max_attempts=3)

    # 测试 tasks
    tasks = [
        CodingTask(
            description="Write a function that adds two numbers",
            starter_code="def solve(a, b):",
            expected_behavior="solve(2, 3) == 5",
            test_code="assert solve(2, 3) == 5, 'Test failed'\nprint('All tests passed')",
        ),
        CodingTask(
            description="Write factorial function",
            starter_code="def solve(n):",
            expected_behavior="solve(5) == 120",
            test_code="assert solve(5) == 120\nprint('All tests passed')",
        ),
        CodingTask(
            description="Write fibonacci function",
            starter_code="def solve(n):",
            expected_behavior="solve(10) == 55",
            test_code="assert solve(10) == 55\nprint('All tests passed')",
        ),
        CodingTask(
            description="Reverse a string",
            starter_code="def solve(s):",
            expected_behavior="solve('hello') == 'olleh'",
            test_code="assert solve('hello') == 'olleh'\nprint('All tests passed')",
        ),
    ]

    results = []
    for task in tasks:
        result = agent.solve(task)
        results.append(result)

    # 总结
    print(f"\n📊 Mini Coding Agent Results:")
    print(f"   {'Task':40} {'Status':10} {'Attempts':10}")
    for task, result in zip(tasks, results):
        status = "✅ Pass" if result["success"] else "❌ Fail"
        n_attempts = len(result["attempts"])
        print(f"   {task.description[:40]:40} {status:10} {n_attempts}")

    success_rate = sum(1 for r in results if r["success"]) / len(results)
    print(f"\n   Success rate: {success_rate:.1%}")
    print(f"\n💡 CS329M 关键概念:")
    print(f"   - Agent-Computer Interface (SWE-agent 论文)")
    print(f"   - 测试驱动开发（执行反馈作为 reward）")
    print(f"   - 错误恢复（debug → fix → retry）")


# ============================================
# 主入口
# ============================================

def main():
    print("🎓 CS329Z HW3 + CS329A Self-Improve + CS329M Coding Agent")
    print("=" * 70)

    hw3_demo()
    cs329a_demo()
    cs329m_demo()

    print("\n" + "=" * 70)
    print("✅ 三个深度项目完成！")
    print("=" * 70)


if __name__ == "__main__":
    main()
