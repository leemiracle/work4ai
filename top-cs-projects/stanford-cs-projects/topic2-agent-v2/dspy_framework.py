"""
CS329Z HW1B - DSPy-style Framework
覆盖课程模块：W3 (DSPy) + W5 (GEPA prompt optimization)

实现内容：
1. Signature（声明式 LLM 调用）
2. Module（可组合）
3. Optimizer（Bootstrap FewShot + 模拟 GEPA）
4. 与 HW1A 的对比反思

参考：Khattab et al. "DSPy" ICLR 2024
"""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import Any, Callable, Optional
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "core"))
from llm import LLMClient, Message


# ============ Signature ============

@dataclass
class Signature:
    """DSPy-style signature: 输入输出契约"""
    instruction: str  # 自然语言描述
    input_fields: list[str]
    output_fields: list[str]

    def format_prompt(self, **inputs) -> list[Message]:
        """生成 prompt"""
        sys_prompt = self.instruction + "\n\nInputs:\n"
        for f in self.input_fields:
            sys_prompt += f"  {f}: {inputs.get(f, '')}\n"
        sys_prompt += "\nPlease produce the following outputs:\n"
        for f in self.output_fields:
            sys_prompt += f"  {f}: <your response>\n"
        return [
            Message(role="system", content=sys_prompt),
            Message(role="user", content="Proceed."),
        ]

    def parse_output(self, response: str) -> dict:
        """从响应中解析字段"""
        result = {}
        for f in self.output_fields:
            # 匹配 `field: value` 或 `field=value`
            m = re.search(rf"{f}\s*[:=]\s*(.+?)(?=\n\w+\s*[:=]|$)", response, re.S | re.I)
            if m:
                result[f] = m.group(1).strip()
        # fallback：把整个 response 当第一个字段
        if not result and self.output_fields:
            result[self.output_fields[0]] = response.strip()
        return result


# ============ Module ============

class Module:
    """DSPy-style module：组合 signatures"""

    def __init__(self, signature: Signature, llm: Optional[LLMClient] = None):
        self.signature = signature
        self.llm = llm or LLMClient(model="mock")
        self.demos: list[dict] = []  # few-shot examples

    def forward(self, **inputs) -> dict:
        """执行一次"""
        msgs = self.signature.format_prompt(**inputs)
        if self.demos:
            demo_str = "\n\nExamples:\n"
            for d in self.demos[:3]:
                demo_str += f"Input: {d.get('input', '')}\nOutput: {d.get('output', '')}\n"
            msgs[0].content += demo_str
        resp = self.llm.chat(msgs)
        return self.signature.parse_output(resp)

    def add_demos(self, demos: list[dict]):
        self.demos.extend(demos)


# ============ Optimizer: Bootstrap FewShot ============

class BootstrapFewShot:
    """从训练样本生成 few-shot demos"""

    def __init__(self, max_demos: int = 3):
        self.max_demos = max_demos

    def compile(self, module: Module, trainset: list[tuple[dict, dict]],
                validate: Callable[[dict, dict], bool]) -> Module:
        """
        用 LLM 生成预测，正确的当 demos
        """
        good_demos = []
        for inp, expected in trainset:
            if len(good_demos) >= self.max_demos:
                break
            pred = module.forward(**inp)
            if validate(pred, expected):
                # 转成 demo 格式
                demo = {"input": str(inp), "output": str(pred)}
                good_demos.append(demo)
        module.demos = good_demos
        return module


# ============ GEPA-style Prompt Evolution ============

class GEPAOptimizer:
    """
    GEPA (Agrawal 2026): Reflective Prompt Evolution
    简化版：让 LLM 反思失败，改 instruction
    """

    def __init__(self, llm: Optional[LLMClient] = None):
        self.llm = llm or LLMClient(model="mock")
        self.history: list[dict] = []

    def evolve(self, signature: Signature, trainset: list[tuple[dict, dict]],
               scorer: Callable[[dict, dict], float],
               rounds: int = 3) -> Signature:
        """迭代改进 instruction"""
        current = signature
        for r in range(rounds):
            # 跑训练集，记录失败
            failures = []
            scores = []
            for inp, expected in trainset:
                mod = Module(current, self.llm)
                pred = mod.forward(**inp)
                s = scorer(pred, expected)
                scores.append(s)
                if s < 0.7:
                    failures.append({"input": inp, "expected": expected, "got": pred})

            avg = sum(scores) / max(len(scores), 1)
            self.history.append({"round": r, "score": avg, "instruction": current.instruction})
            print(f"   Round {r}: avg_score = {avg:.3f}, failures = {len(failures)}")

            if not failures or avg >= 0.95:
                break

            # 让 LLM 反思并改进 instruction（mock 简化）
            current = Signature(
                instruction=f"[Optimized round {r+1}] {current.instruction}\n"
                            f"Past failures: {len(failures)}. Be more specific.",
                input_fields=current.input_fields,
                output_fields=current.output_fields,
            )
        return current


# ============ Demo ============

def demo():
    print("=" * 60)
    print("CS329Z HW1B: DSPy-style Framework")
    print("=" * 60)

    # 定义签名
    sig = Signature(
        instruction="Answer the math question precisely.",
        input_fields=["question"],
        output_fields=["answer"],
    )

    llm = LLMClient(model="mock")
    mod = Module(sig, llm)

    # 单次执行
    print("\n📋 1. 单次 forward")
    result = mod.forward(question="What is 5 + 3?")
    print(f"   Input: question='What is 5 + 3?'")
    print(f"   Output: {result}")

    # Bootstrap few-shot
    print("\n📋 2. Bootstrap FewShot")
    trainset = [
        ({"question": "1 + 1"}, {"answer": "2"}),
        ({"question": "2 * 3"}, {"answer": "6"}),
        ({"question": "10 - 4"}, {"answer": "6"}),
        ({"question": "20 / 5"}, {"answer": "4"}),
    ]

    def validate(pred, expected):
        return expected["answer"] in pred.get("answer", "")

    optimizer = BootstrapFewShot(max_demos=2)
    mod = optimizer.compile(mod, trainset, validate)
    print(f"   编译出 {len(mod.demos)} 个 demos")

    # GEPA 风格优化
    print("\n📋 3. GEPA-style Prompt Evolution")
    gepa = GEPAOptimizer(llm)

    def scorer(pred, expected):
        return 1.0 if expected["answer"] in pred.get("answer", "") else 0.0

    opt_sig = gepa.evolve(sig, trainset, scorer, rounds=3)
    print(f"   最终 instruction: {opt_sig.instruction[:80]}...")

    # 反思：与 HW1A 对比
    print("\n📋 4. HW1A vs HW1B 对比反思")
    print("""
    HW1A（手写）:
    + 直接控制 prompt 每一行
    + 可以做 ReAct 等复杂逻辑
    - 换模型需重写 prompt
    - 没有自动优化
    
    HW1B（DSPy）:
    + 写 signature，optimizer 自动加 demos
    + GEPA 可以迭代改进 instruction
    + 模型无关
    - 抽象成本（学习曲线）
    - 复杂控制流（ReAct loop）不如手写灵活
    
    结论：简单 QA / 分类 → DSPy。复杂 agent → 手写。
    """)


if __name__ == "__main__":
    demo()
