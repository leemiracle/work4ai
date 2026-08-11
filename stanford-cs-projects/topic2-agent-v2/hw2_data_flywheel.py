"""
CS329Z HW2 - Data for Agents
覆盖课程模块：W6 Data Flywheels + W7 Data Selection

完整实现：
1. Agent traces 收集
2. 数据 flywheel（agent → traces → 优化 → 更强 agent）
3. 数据选择策略（信息量 / 多样性 / 难度）
4. 偏好对（preference pairs）提取
5. SFT 数据集构建
6. 数据质量评估

参考：
- Shankar "Data Flywheels for LLM Applications" 2024
- Shankar "Who Validates the Validators?" UIST 2024
- Yang "SWE-smith" NeurIPS 2025

这是 CS329Z 的第二门作业（占 10% 分数）
"""
from __future__ import annotations
import os
import sys
import json
import math
import random
from collections import Counter, defaultdict
from dataclasses import dataclass, field, asdict
from typing import Any, Callable, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "topic2-agents", "cs329z-hw1a"))


# ============ 1. Agent Trace 数据结构 ============

@dataclass
class ToolCall:
    tool: str
    input: str
    output: str
    success: bool = True


@dataclass
class AgentTrace:
    """Agent 执行的完整轨迹（CS329Z HW2 核心数据单元）"""
    query: str
    steps: list[dict] = field(default_factory=list)
    tool_calls: list[ToolCall] = field(default_factory=list)
    final_answer: str = ""
    success: bool = False
    user_feedback: Optional[str] = None  # positive / negative / None
    metadata: dict = field(default_factory=dict)
    timestamp: str = ""

    def to_dict(self) -> dict:
        return {
            "query": self.query,
            "steps": self.steps,
            "tool_calls": [asdict(tc) for tc in self.tool_calls],
            "final_answer": self.final_answer,
            "success": self.success,
            "user_feedback": self.user_feedback,
            "metadata": self.metadata,
            "timestamp": self.timestamp,
        }


# ============ 2. Trace Collector（从 agent 跑 traces）============

class TraceCollector:
    """运行 agent，收集 traces"""

    def __init__(self):
        self.traces: list[AgentTrace] = []

    def collect(self, agent_fn: Callable[[str], AgentTrace], queries: list[str]):
        """对每个 query 跑 agent，存 trace"""
        for q in queries:
            try:
                trace = agent_fn(q)
                self.traces.append(trace)
            except Exception as e:
                failed = AgentTrace(query=q, final_answer=f"[ERROR] {e}",
                                    success=False)
                self.traces.append(failed)
        return self

    def stats(self) -> dict:
        if not self.traces:
            return {}
        return {
            "total": len(self.traces),
            "success": sum(1 for t in self.traces if t.success),
            "fail": sum(1 for t in self.traces if not t.success),
            "with_feedback": sum(1 for t in self.traces if t.user_feedback),
            "avg_steps": sum(len(t.steps) for t in self.traces) / len(self.traces),
            "avg_tools": sum(len(t.tool_calls) for t in self.traces) / len(self.traces),
        }


# ============ 3. Data Selection 策略 ============

class DataSelector:
    """
    从 traces 选最有价值的样本做训练数据
    参考：Yang SWE-smith (NeurIPS 2025)
    """

    @staticmethod
    def by_success(traces: list[AgentTrace]) -> list[AgentTrace]:
        """只保留成功的"""
        return [t for t in traces if t.success]

    @staticmethod
    def by_difficulty(traces: list[AgentTrace], top_pct: float = 0.5) -> list[AgentTrace]:
        """选最难的（步骤数 + 工具调用数最多）"""
        successful = [t for t in traces if t.success]
        if not successful:
            return []
        # 按难度（步数 + 工具数）排序
        scored = [(t, len(t.steps) + len(t.tool_calls) * 2) for t in successful]
        scored.sort(key=lambda x: -x[1])
        n_keep = max(1, int(len(scored) * top_pct))
        return [t for t, _ in scored[:n_keep]]

    @staticmethod
    def by_diversity(traces: list[AgentTrace], target_n: int = 50) -> list[AgentTrace]:
        """多样性选择：覆盖不同 query 模式"""
        if len(traces) <= target_n:
            return traces

        # 用 query 的关键词 fingerprint 聚类
        def fingerprint(query: str) -> frozenset:
            words = set(query.lower().split())
            return frozenset(words)

        # 简单聚类：按 fingerprint 分组，每组取代表
        clusters: dict[frozenset, list[AgentTrace]] = defaultdict(list)
        for t in traces:
            clusters[fingerprint(t.query)].append(t)

        selected = []
        # 轮转从每个 cluster 取 1 个
        cluster_lists = list(clusters.values())
        random.shuffle(cluster_lists)
        i = 0
        while len(selected) < target_n and cluster_lists:
            cluster = cluster_lists[i % len(cluster_lists)]
            if cluster:
                selected.append(cluster.pop(0))
            if not cluster:
                cluster_lists.pop(i % len(cluster_lists))
                if not cluster_lists:
                    break
                i = i % len(cluster_lists)
            else:
                i += 1
        return selected[:target_n]

    @staticmethod
    def by_information(traces: list[AgentTrace], min_info: float = 0.5) -> list[AgentTrace]:
        """按"信息量"过滤：答案长度 + 工具输出丰富度"""
        def info_score(t: AgentTrace) -> float:
            ans_len = min(len(t.final_answer) / 200, 1.0)
            tool_diversity = len(set(tc.tool for tc in t.tool_calls)) / 5
            return 0.6 * ans_len + 0.4 * tool_diversity

        return [t for t in traces if info_score(t) >= min_info]


# ============ 4. Preference Pairs 提取（RLHF 用）============

@dataclass
class PreferencePair:
    """RLHF / DPO 训练对"""
    query: str
    chosen: str  # 偏好的回答
    rejected: str  # 不偏好的
    rationale: str = ""


class PreferencePairExtractor:
    """从 traces 提取 preference pairs"""

    @staticmethod
    def from_user_feedback(traces: list[AgentTrace]) -> list[PreferencePair]:
        """从用户反馈提取"""
        positive = [t for t in traces if t.user_feedback == "positive"]
        negative = [t for t in traces if t.user_feedback == "negative"]

        pairs = []
        # 配对相同/相似 query 的 pos vs neg
        for pos in positive:
            for neg in negative:
                if pos.query == neg.query or _similarity(pos.query, neg.query) > 0.7:
                    pairs.append(PreferencePair(
                        query=pos.query,
                        chosen=pos.final_answer,
                        rejected=neg.final_answer,
                        rationale="user_feedback_direct",
                    ))
                    break
        return pairs

    @staticmethod
    def from_success_vs_failure(traces: list[AgentTrace]) -> list[PreferencePair]:
        """成功 vs 失败对比"""
        successful = [t for t in traces if t.success]
        failed = [t for t in traces if not t.success]

        pairs = []
        for s in successful:
            for f in failed:
                if _similarity(s.query, f.query) > 0.6:
                    pairs.append(PreferencePair(
                        query=s.query,
                        chosen=s.final_answer,
                        rejected=f.final_answer,
                        rationale="success_vs_failure",
                    ))
                    break
        return pairs

    @staticmethod
    def from_self_critique(traces: list[AgentTrace],
                            critique_fn: Callable[[str], str]) -> list[PreferencePair]:
        """自我批判：让 agent 反思自己答案"""
        pairs = []
        for t in traces:
            if not t.success:
                continue
            critique = critique_fn(t.final_answer)
            if critique and critique != t.final_answer:
                pairs.append(PreferencePair(
                    query=t.query,
                    chosen=critique,  # 改进版
                    rejected=t.final_answer,  # 原版
                    rationale="self_critique",
                ))
        return pairs


def _similarity(s1: str, s2: str) -> float:
    """简单 Jaccard 相似度"""
    w1, w2 = set(s1.lower().split()), set(s2.lower().split())
    if not w1 or not w2:
        return 0
    return len(w1 & w2) / len(w1 | w2)


# ============ 5. SFT Dataset 构建 ============

@dataclass
class SFTExample:
    """Supervised Fine-Tuning 样本"""
    instruction: str
    input: str = ""
    output: str = ""
    metadata: dict = field(default_factory=dict)


class SFTDatasetBuilder:
    """从 traces 构建 SFT 数据集"""

    @staticmethod
    def from_successful_traces(traces: list[AgentTrace]) -> list[SFTExample]:
        """只保留成功的（InstructGPT 风格）"""
        examples = []
        for t in traces:
            if not t.success or not t.final_answer:
                continue
            examples.append(SFTExample(
                instruction=t.query,
                output=t.final_answer,
                metadata={"source": "trace", "n_steps": len(t.steps)},
            ))
        return examples

    @staticmethod
    def with_chain_of_thought(traces: list[AgentTrace]) -> list[SFTExample]:
        """带 CoT 的 SFT（含 reasoning trace）"""
        examples = []
        for t in traces:
            if not t.success:
                continue
            # 把 steps 序列化为 reasoning
            cot = "\n".join(
                f"Step {i+1}: {s.get('thought', '')}"
                for i, s in enumerate(t.steps)
            )
            examples.append(SFTExample(
                instruction=t.query,
                output=f"Reasoning:\n{cot}\n\nAnswer: {t.final_answer}",
                metadata={"type": "cot"},
            ))
        return examples

    @staticmethod
    def to_jsonl(examples: list[SFTExample], filepath: str):
        """保存为 JSONL（HuggingFace datasets 格式）"""
        with open(filepath, "w") as f:
            for ex in examples:
                f.write(json.dumps(asdict(ex)) + "\n")


# ============ 6. Data Quality 评估 ============

class DataQualityAssessor:
    """
    CS329Z W7 - Who Validates the Validators?
    评估数据集质量
    """

    @staticmethod
    def basic_stats(examples: list) -> dict:
        if not examples:
            return {}
        if isinstance(examples[0], SFTExample):
            outputs = [e.output for e in examples]
            instructions = [e.instruction for e in examples]
        elif isinstance(examples, AgentTrace):
            outputs = [e.final_answer for e in examples]
            instructions = [e.query for e in examples]
        else:
            return {}

        return {
            "count": len(examples),
            "avg_output_len": sum(len(o) for o in outputs) / len(outputs),
            "avg_input_len": sum(len(i) for i in instructions) / len(instructions),
            "unique_outputs": len(set(outputs)),
            "unique_inputs": len(set(instructions)),
            "duplication_rate": 1 - len(set(outputs)) / len(outputs),
        }

    @staticmethod
    def diversity_check(examples: list) -> dict:
        """多样性：用 instruction 词覆盖度"""
        if not examples:
            return {}
        all_words = set()
        for ex in examples:
            text = ex.instruction if isinstance(ex, SFTExample) else ex.query
            all_words.update(text.lower().split())
        return {
            "unique_words": len(all_words),
            "vocabulary_richness": len(all_words),
        }

    @staticmethod
    def difficulty_distribution(traces: list[AgentTrace]) -> dict:
        """难度分布（步数 + 工具数）"""
        if not traces:
            return {}
        difficulties = []
        for t in traces:
            d = len(t.steps) + len(t.tool_calls) * 2
            difficulties.append(d)
        return {
            "min": min(difficulties),
            "max": max(difficulties),
            "mean": sum(difficulties) / len(difficulties),
            "easy_count": sum(1 for d in difficulties if d <= 3),
            "medium_count": sum(1 for d in difficulties if 3 < d <= 7),
            "hard_count": sum(1 for d in difficulties if d > 7),
        }


# ============ 7. Data Flywheel ============

class DataFlywheel:
    """
    Shankar 2024 "Data Flywheels" 实现
    
    Flywheel:
    Agent → Traces → 数据选择 → SFT/DPO → 更强 Agent → 更好 Traces → ...
    """

    def __init__(self, name: str = "flywheel"):
        self.name = name
        self.iteration = 0
        self.history: list[dict] = []
        self.all_traces: list[AgentTrace] = []

    def step(self, agent_fn: Callable, eval_queries: list[str],
             collect_queries: list[str]) -> dict:
        """一轮 flywheel"""
        self.iteration += 1
        print(f"\n🔄 Flywheel 迭代 {self.iteration}")

        # 1. Eval 当前 agent
        print("   → 评估当前 agent...")
        eval_traces = TraceCollector().collect(agent_fn, eval_queries).traces
        eval_stats = _compute_success_rate(eval_traces)

        # 2. 收集训练数据
        print("   → 收集训练 traces...")
        new_traces = TraceCollector().collect(agent_fn, collect_queries).traces
        self.all_traces.extend(new_traces)

        # 3. 数据选择
        print("   → 选择高质量数据...")
        selector = DataSelector()
        good_traces = selector.by_success(self.all_traces)
        diverse_traces = selector.by_diversity(good_traces, target_n=20)
        hard_traces = selector.by_difficulty(good_traces, top_pct=0.5)

        # 4. 构建 SFT dataset
        print("   → 构建 SFT 数据集...")
        builder = SFTDatasetBuilder()
        sft_examples = builder.from_successful_traces(diverse_traces)
        cot_examples = builder.with_chain_of_thought(hard_traces)

        # 5. 构建 preference pairs
        print("   → 提取 preference pairs...")
        extractor = PreferencePairExtractor()
        pref_pairs = extractor.from_success_vs_failure(self.all_traces)

        # 6. 评估数据质量
        print("   → 评估数据质量...")
        assessor = DataQualityAssessor()
        sft_stats = assessor.basic_stats(sft_examples)
        diversity = assessor.diversity_check(sft_examples)
        difficulty = assessor.difficulty_distribution(self.all_traces)

        # 7. Mock "训练"（真实场景会调 LLM trainer）
        improvement = self._mock_train(sft_examples, pref_pairs)

        record = {
            "iteration": self.iteration,
            "eval_success_rate": eval_stats["success_rate"],
            "traces_collected": len(new_traces),
            "total_traces": len(self.all_traces),
            "sft_examples": len(sft_examples),
            "cot_examples": len(cot_examples),
            "pref_pairs": len(pref_pairs),
            "post_train_success_rate": min(0.95, eval_stats["success_rate"] + improvement),
            "sft_stats": sft_stats,
            "diversity": diversity,
            "difficulty": difficulty,
        }
        self.history.append(record)

        print(f"   📊 迭代 {self.iteration} 结果:")
        print(f"      成功率: {eval_stats['success_rate']:.1%} → {record['post_train_success_rate']:.1%}")
        print(f"      SFT 数据: {len(sft_examples)} examples")
        print(f"      Preference pairs: {len(pref_pairs)}")

        return record

    def _mock_train(self, sft: list, pref: list) -> float:
        """Mock: 假装训练了 agent（真实场景调 SFT/DPO trainer）"""
        # 模拟：数据越多提升越大，但有上限
        n = len(sft) + len(pref)
        if n == 0:
            return 0
        improvement = math.log(n + 1) * 0.03
        return min(improvement, 0.15)


def _compute_success_rate(traces: list[AgentTrace]) -> dict:
    if not traces:
        return {"success_rate": 0}
    return {"success_rate": sum(1 for t in traces if t.success) / len(traces)}


# ============ Demo: 完整跑一遍 ============

def demo():
    print("=" * 70)
    print("CS329Z HW2: Data Flywheels for Agents")
    print("=" * 70)

    random.seed(42)

    # ===== 模拟 agent =====
    def mock_agent(query: str) -> AgentTrace:
        """模拟一个 agent 跑 query"""
        # 决定成功概率（基于 query 难度）
        is_math = any(c.isdigit() for c in query) and any(op in query for op in "+-*/")
        is_knowledge = any(w in query.lower() for w in ["what", "how", "why", "explain"])

        # 模拟成功
        if is_math:
            success = random.random() < 0.7
            n_tools = 1
        elif is_knowledge:
            success = random.random() < 0.8
            n_tools = 0
        else:
            success = random.random() < 0.5
            n_tools = random.randint(0, 2)

        steps = [{"thought": f"分析 query", "action": "process"} for _ in range(random.randint(1, 3))]
        tool_calls = [
            ToolCall(
                tool=random.choice(["calculator", "search", "read_file"]),
                input=query,
                output=f"Result for {query[:30]}",
                success=True,
            ) for _ in range(n_tools)
        ]

        return AgentTrace(
            query=query,
            steps=steps,
            tool_calls=tool_calls,
            final_answer=f"Answer to: {query}" if success else "I don't know",
            success=success,
            user_feedback=random.choice(["positive", "negative", None]),
        )

    # ===== 生成测试 queries =====
    eval_queries = [
        "计算 5+3", "什么是 transformer?", "Why RAG?",
        "How does TCP work?", "Explain gradient descent",
        "Calculate 23*17", "What is GCN?", "How to do PCA?",
        "Why RLHF?", "Explain attention",
    ]
    train_queries = [
        f"Question {i}: " + random.choice([
            "calculate X+Y", "explain concept", "how does X work",
            "what is X", "why X", "compare X and Y"
        ]) for i in range(30)
    ]

    # ===== 跑 Flywheel 3 轮 =====
    flywheel = DataFlywheel("cs329z-hw2")
    for it in range(3):
        flywheel.step(mock_agent, eval_queries, train_queries)

    # ===== 最终统计 =====
    print(f"\n{'='*70}")
    print(f"📊 Final Flywheel Summary")
    print(f"{'='*70}")

    print(f"\n迭代历史:")
    print(f"{'Iter':>4} {'Pre-Success':>12} {'Post-Success':>12} {'Traces':>8} {'SFT':>6} {'Pairs':>6}")
    for h in flywheel.history:
        print(f"{h['iteration']:>4} {h['eval_success_rate']:>12.1%} "
              f"{h['post_train_success_rate']:>12.1%} "
              f"{h['total_traces']:>8} {h['sft_examples']:>6} {h['pref_pairs']:>6}")

    # ===== 保存数据集 =====
    print(f"\n💾 保存数据集...")
    os.makedirs("output", exist_ok=True)
    builder = SFTDatasetBuilder()
    sft_data = builder.from_successful_traces(
        DataSelector.by_success(flywheel.all_traces)
    )
    builder.to_jsonl(sft_data, "output/sft_dataset.jsonl")
    print(f"   SFT: {len(sft_data)} examples → output/sft_dataset.jsonl")

    pref_data = PreferencePairExtractor.from_success_vs_failure(flywheel.all_traces)
    with open("output/preference_pairs.jsonl", "w") as f:
        for p in pref_data:
            f.write(json.dumps(asdict(p)) + "\n")
    print(f"   Pairs: {len(pref_data)} pairs → output/preference_pairs.jsonl")

    # ===== 数据卡 =====
    print(f"\n📋 数据卡 (Data Card):")
    final = flywheel.history[-1]
    assessor = DataQualityAssessor()
    print(f"   - 数据集: cs329z-hw2-flywheel")
    print(f"   - 版本: v{flywheel.iteration}.0")
    print(f"   - 总 traces: {final['total_traces']}")
    print(f"   - SFT examples: {final['sft_examples']}")
    print(f"   - Preference pairs: {final['pref_pairs']}")
    print(f"   - 平均输出长度: {final['sft_stats'].get('avg_output_len', 0):.1f} chars")
    print(f"   - 重复率: {final['sft_stats'].get('duplication_rate', 0):.1%}")
    print(f"   - 词表丰富度: {final['diversity'].get('vocabulary_richness', 0)} unique words")
    print(f"   - 难度分布 (easy/med/hard): "
          f"{final['difficulty']['easy_count']}/"
          f"{final['difficulty']['medium_count']}/"
          f"{final['difficulty']['hard_count']}")

    # ===== 反思 =====
    print(f"\n💡 CS329Z HW2 核心反思:")
    print(f"""
    1. **数据 flywheel 是 agent 时代的核心竞争力**——agent 越用越聪明
    2. **成功 traces ≠ 高质量 traces**——可能存在 shortcut / bias
    3. **多样性 > 数量**——1000 个相似 traces 不如 100 个多样化
    4. **难度选择**重要——只学简单的会停滞
    5. **Preference pairs 比纯 SFT 信息更丰富**——告诉模型"什么不好"
    6. **数据质量评估难**（Shankar 'Who Validates Validators?'）——LLM judge 也有 bias
    
    真实场景改进：
    - 用真实 LLM 替换 mock_agent
    - 加真实 reward model 替代 user_feedback
    - 跑 DPO/PPO 训练而不是 mock_train
    - 加 RLHF / Constitutional AI 反馈循环
    """)

    print(f"\n✅ CS329Z HW2 完成！")


if __name__ == "__main__":
    demo()
