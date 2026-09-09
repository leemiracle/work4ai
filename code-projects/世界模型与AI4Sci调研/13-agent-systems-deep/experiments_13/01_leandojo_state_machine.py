"""
模块 13 §13 配套实验：LLM × Lean 双层证明状态机模拟

模拟 LeanDojo 的 init_proof_search / run_tactic / premise selection API。
演示：
  1. LLM 提议 tactic → Lean 验证 → 状态更新
  2. premise selection（ReProver 风格检索）
  3. sorry 反例（Lean Agent 的安全漏洞）
  4. Lean Copilot 实测数据对照

纯 Python，无需 Lean 环境。
"""

# 模拟 Lean 内核 + mathlib 引理库
PREMISES_DB = {
    "Nat.add_comm":  ("∀ a b : Nat, a + b = b + a",        "addition commutative"),
    "Nat.add_assoc": ("∀ a b c : Nat, (a + b) + c = a + (b + c)", "addition associative"),
    "Nat.add_zero":  ("∀ a : Nat, a + 0 = a",               "addition identity zero"),
    "Nat.zero_add":  ("∀ a : Nat, 0 + a = a",               "zero identity addition"),
    "Nat.mul_comm":  ("∀ a b : Nat, a * b = b * a",         "multiplication commutative"),
    "Nat.add_cancel": ("∀ a b c : Nat, a + c = b + c → a = b", "addition cancellation"),
}


class LeanState:
    """模拟 Lean 的 TacticState"""
    def __init__(self, goal, hyps):
        self.goal = goal
        self.hyps = hyps
        self.finished = False

    def pp(self):
        return f"hyps: {self.hyps}\ngoal: {self.goal}"


class MockLeanKernel:
    """模拟 Lean 内核 + LeanDojo API"""
    def __init__(self, sorry_forbidden=True):
        self.states = {}
        self.state_counter = 0
        self.sorry_forbidden = sorry_forbidden  # ⭐ 关键：Agent 必须禁 sorry

    def init_proof_search(self, theorem_name, goal, hyps):
        self.state_counter += 1
        sid = f"s_{self.state_counter}"
        self.states[sid] = LeanState(goal, hyps)
        return sid

    def get_premises(self, query, k=3):
        """模拟 ReProver 的 premise selection (检索增强)"""
        q = query.lower()
        scored = []
        for name, (stmt, keywords) in PREMISES_DB.items():
            score = sum(1 for kw in keywords.split() if kw in q)
            score += sum(1 for c in query if c in name)
            scored.append((score, name, stmt))
        scored.sort(reverse=True)
        return [(n, s) for _, n, s in scored[:k]]

    def run_tactic(self, sid, tactic):
        """模拟 Lean 内核执行 tactic，返回 (new_state_id, finished, error)"""
        s = self.states[sid]
        if not isinstance(s, LeanState):
            return None, False, "invalid state"

        # ⚠️ sorry 反例：Lean 接受 sorry 作为合法 tactic
        if tactic.strip() == "sorry":
            if self.sorry_forbidden:
                return sid, False, "❌ sorry 被 Agent 禁用（防假证明）"
            s.finished = True
            return sid, True, None

        # rw [Premise] 重写
        if tactic.startswith("rw [") and "]" in tactic:
            premise_name = tactic[4:tactic.index("]")]
            if premise_name in PREMISES_DB:
                # 简化：重写后两侧相等（实际 Lean 做完整 unification）
                s.goal = s.goal.replace("(a + b) + c", "a + (b + c)")
                return sid, False, None
            return sid, False, f"unknown premise: {premise_name}"

        # rfl 关闭 a = a 形式
        if tactic.strip() == "rfl":
            parts = [p.strip() for p in s.goal.split("=")]
            if len(parts) == 2 and parts[0] == parts[1]:
                s.finished = True
                return sid, True, None
            return sid, False, "rfl failed: sides not syntactically equal"

        return sid, False, f"unknown tactic: {tactic}"


def demo_successful_proof():
    """场景 1：LLM + Lean 协作成功证明"""
    print("=" * 72)
    print("场景 1：LLM × Lean 协作证明 Nat 加法结合律")
    print("=" * 72)
    kernel = MockLeanKernel(sorry_forbidden=True)

    # Step 1: init
    sid = kernel.init_proof_search(
        "add_assoc_demo",
        goal="(a + b) + c = a + (b + c)",
        hyps=["a b c : Nat"],
    )
    print(f"\n[init] state_id = {sid}")
    print(f"  {kernel.states[sid].pp()}")

    # Step 2: LLM 检索引理（ReProver 风格）
    print("\n[LLM 步 1] 我需要找相关引理...")
    for name, stmt in kernel.get_premises("add associativity nat"):
        print(f"  → {name}: {stmt}")

    # Step 3: LLM 提议第一个 tactic
    print("\n[LLM 步 2] 提议: rw [Nat.add_assoc]")
    sid, fin, err = kernel.run_tactic(sid, "rw [Nat.add_assoc]")
    print(f"  [Lean] → goal: {kernel.states[sid].goal}, finished={fin}")

    # Step 4: LLM 识别 rfl 可关闭
    print("\n[LLM 步 3] 提议: rfl")
    sid, fin, err = kernel.run_tactic(sid, "rfl")
    print(f"  [Lean] → proof_finished={fin}  ✅")

    print("\n→ 整个证明 3 步完成，LLM 提议 + Lean 验证，无幻觉空间")


def demo_sorry_vulnerability():
    """场景 2：sorry 反例 — Agent 安全漏洞"""
    print("\n" + "=" * 72)
    print("场景 2：sorry 反例 — Lean Agent 的隐藏安全漏洞")
    print("=" * 72)
    print("\n问题：Lean 内置 tactic 'sorry' 接受任何断言为真。")
    print("LLM 可能学到「写不出证明就用 sorry」的模式 → 假证明通过验证。")

    # 没禁 sorry 的版本
    bad_kernel = MockLeanKernel(sorry_forbidden=False)
    sid = bad_kernel.init_proof_search("false_theorem", goal="1 = 2", hyps=[])
    print(f"\n[init] goal: {bad_kernel.states[sid].goal}  ← 假命题！")

    print("\n[LLM] 我不会证 1=2，偷懒用 sorry")
    sid, fin, err = bad_kernel.run_tactic(sid, "sorry")
    print(f"  [Lean 验证通过] proof_finished={fin}  ⚠️ 这是假证明！")

    # 禁 sorry 的版本
    good_kernel = MockLeanKernel(sorry_forbidden=True)
    sid = good_kernel.init_proof_search("false_theorem", goal="1 = 2", hyps=[])
    print(f"\n[对照] 同样的 LLM 在 sorry-forbidden 内核上：")
    sid, fin, err = good_kernel.run_tactic(sid, "sorry")
    print(f"  [Lean] proof_finished={fin}, error: {err}  ✅ 被拦下")

    print("\n→ 工程教训：所有 LLM × Lean Agent 必须 set_option pp.all true + ")
    print("  在 Lean 配置里禁用 sorry（或运行 final lint 检测证明里含 sorry）")


def demo_lean_copilot_stats():
    """场景 3：Lean Copilot 实测数据（一手 arXiv 核实）"""
    print("\n" + "=" * 72)
    print("场景 3：Lean Copilot 实测数据（arXiv:2404.12534 一手核实）")
    print("=" * 72)
    print("\n基准：Mathematics in Lean 教科书（180+ 定理）")
    print()
    print("  ┌─────────────────────┬────────────────┬───────────────┐")
    print("  │ 方法                │ 自动化率       │ 人机协作步数  │")
    print("  ├─────────────────────┼────────────────┼───────────────┤")
    print("  │ 传统规则法 (aesop)  │     40.1%      │    3.86 步    │")
    print("  │ Lean Copilot (LLM)  │     74.2%      │    2.08 步    │")
    print("  │ 提升                │     +85%       │   -46%        │")
    print("  └─────────────────────┴────────────────┴───────────────┘")
    print()
    print("→ 关键：Lean Copilot 把「人手敲 tactic 数」减半，")
    print("  这是 LLM × 形式化首批有量化收益的工程证据")


if __name__ == "__main__":
    demo_successful_proof()
    demo_sorry_vulnerability()
    demo_lean_copilot_stats()
    print("\n" + "=" * 72)
    print("实验全部跑通 ✅")
    print("=" * 72)
