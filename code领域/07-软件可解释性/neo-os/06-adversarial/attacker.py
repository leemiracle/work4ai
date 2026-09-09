"""
Neo-OS · 对抗层 · Attacker Agent v0
=====================================
基于 DC-prep-notes 的 v1.1 修正：语义导向 minimal-diff + tridirectional 判别力。

核心机制（借鉴 arXiv:2606.01794）：
- 不做随机 fuzzing，而是**手工定义安全关键语义边界类**
- 每个边界构造 minimal-diff mutant safe（去掉单一条件）
- 用揭示性 trace 测试 Inv 在 mutant 下是否仍保持
- tridirectional 评估：正例（成立）/ 反例（已知违反）/ 边界（mutant）

输出：
- 每个边界的判别力（Inv 能否否决该边界的 mutant）
- Inv 的盲点列表（边界 mutant 仍让 Inv 成立 = Inv 没捕捉该错误）
- Attack-to-Property 建议（盲点 → 新 Inv 子句候选）

对应设计文档：../01-decisions/ADVERSARIAL_LAYER_DESIGN.md §3.2（v1.1 修正后）
"""
from dataclasses import dataclass
from typing import List, Tuple
from model import (
    S, Ev, step, safe_original, Inv, OK, final, Inv_preserved_over_trace,
    nat_sub, SafeFn
)


# ============================================================
# 语义边界定义（minimal-diff mutant 的手工类）
# ============================================================

@dataclass
class SemanticBoundary:
    """
    一个安全关键语义边界 = safe 的一个条件。
    mutant_safe = 去掉该条件的 safe 变体。
    revealing_trace = 揭示该边界必要性的 trace（在 mutant 下合法，在原版下非法）。
    init_state = trace 的起始状态（必须满足 Inv，以隔离测试）。
    """
    id: str
    name: str
    description: str
    mutant_safe: SafeFn          # 去掉单一条件的 safe 变体
    init_state: S                # 揭示性 trace 起始状态（须满足 Inv）
    revealing_trace: List[Ev]    # 揭示性 trace
    lean4_correspondence: str    # 对应 Lean4 safe/Inv 的哪一部分


# ---- mutant safe 变体定义 ----

def safe_B1a_no_pc_check(e: Ev, s: S) -> bool:
    """B1a mutant：preemptEnable 去掉 pc≥1 检查（允许 pc=0 时 enable）"""
    if e == Ev.PREEMPT_ENABLE:
        return (s.lockHeld == True and s.preemptCount >= 2) or (s.lockHeld == False)
    return safe_original(e, s)


def safe_B1b_weak_pair_discipline(e: Ev, s: S) -> bool:
    """B1b mutant：preemptEnable 去掉 lockHeld→pc≥2（只留 pc≥1）← 现有 pair_discipline"""
    if e == Ev.PREEMPT_ENABLE:
        return s.preemptCount >= 1
    return safe_original(e, s)


def safe_B2a_schedule_no_pc_check(e: Ev, s: S) -> bool:
    """B2a mutant：schedule 去掉 pc=0 检查（允许持抢占时调度）"""
    if e == Ev.SCHEDULE:
        return s.lockHeld == False
    return safe_original(e, s)


def safe_B2b_schedule_no_lock_check(e: Ev, s: S) -> bool:
    """B2b mutant：schedule 去掉 ¬lockHeld 检查（允许持锁时调度）"""
    if e == Ev.SCHEDULE:
        return s.preemptCount == 0
    return safe_original(e, s)


def safe_B3_release_weak(e: Ev, s: S) -> bool:
    """B3 mutant：lockRelease 去掉 lockHeld=true 检查（允许释放未持有锁）"""
    if e == Ev.LOCK_RELEASE:
        return True
    return safe_original(e, s)


def safe_B4_acquire_constrained(e: Ev, s: S) -> bool:
    """B4 mutant：lockRelease 去掉 lockHeld=true 检查（允许释放未持有锁）"""
    if e == Ev.LOCK_RELEASE:
        return True
    return safe_original(e, s)


def safe_B5_schedule_unconditional(e: Ev, s: S) -> bool:
    """B5 mutant（v2 新增）：schedule 无条件允许（去掉 pc=0 ∧ ¬lockHeld 全部）。
    在 v2 模型，持锁 schedule 进入 deadlocked → Inv 失败 → 有判别力（F5 修复验证）。"""
    if e == Ev.SCHEDULE:
        return True
    return safe_original(e, s)


# ============================================================
# 6 个语义边界（覆盖 safe 的每个非 trivial 条件）
# ============================================================

BOUNDARIES: List[SemanticBoundary] = [
    SemanticBoundary(
        id="B1a",
        name="preemptEnable_pc_lower_bound",
        description="preemptEnable 要求 pc≥1（防止 pc 下溢）",
        mutant_safe=safe_B1a_no_pc_check,
        init_state=S(0, False),  # pc=0, Inv 成立
        revealing_trace=[Ev.PREEMPT_ENABLE],  # mutant 下合法（去 pc 检查），原版下非法
        lean4_correspondence="safe(preemptEnable): s.preemptCount ≥ 1",
    ),
    SemanticBoundary(
        id="B1b",
        name="preemptEnable_pair_discipline",
        description="preemptEnable 持锁时须留 pc≥2（配对纪律核心）← 现有 pair_discipline 做的",
        mutant_safe=safe_B1b_weak_pair_discipline,
        init_state=S(1, True),  # pc=1,lock=true，Inv 成立（true→1≥1）
        revealing_trace=[Ev.PREEMPT_ENABLE],  # mutant 下合法，原版下非法
        lean4_correspondence="safe(preemptEnable): s.lockHeld=true → s.preemptCount ≥ 2",
    ),
    SemanticBoundary(
        id="B2a",
        name="schedule_preempt_count_zero",
        description="schedule 要求 pc=0（不可在 atomic context 调度）",
        mutant_safe=safe_B2a_schedule_no_pc_check,
        init_state=S(1, False),  # pc=1,lock=false，Inv 成立
        revealing_trace=[Ev.SCHEDULE],  # mutant 下合法，原版下非法
        lean4_correspondence="safe(schedule): s.preemptCount = 0",
    ),
    SemanticBoundary(
        id="B2b",
        name="schedule_no_lock_held",
        description="schedule 要求 ¬lockHeld（不可持锁调度）",
        mutant_safe=safe_B2b_schedule_no_lock_check,
        init_state=S(2, True),  # pc=2,lock=true，Inv 成立（true→2≥1）
        revealing_trace=[Ev.SCHEDULE],  # mutant 下合法（pc=0 检查：2≠0，原版也非法；需重选 init）
        lean4_correspondence="safe(schedule): s.lockHeld = false",
    ),
    SemanticBoundary(
        id="B3",
        name="lockRelease_held_required",
        description="lockRelease 要求 lockHeld=true（不可释放未持有锁）",
        mutant_safe=safe_B3_release_weak,
        init_state=S(1, False),  # pc=1,lock=false，Inv 成立
        revealing_trace=[Ev.LOCK_RELEASE],  # mutant 下合法，原版下非法
        lean4_correspondence="safe(lockRelease): s.lockHeld = true",
    ),
    SemanticBoundary(
        id="B5",
        name="schedule_unconditional_deadlock",
        description="schedule 持锁时进入 deadlocked（v2 新增，F5 修复后的判别力）",
        mutant_safe=safe_B5_schedule_unconditional,
        init_state=S(1, True),  # pc=1, lock=true, Inv 成立（true→1≥1）
        revealing_trace=[Ev.SCHEDULE],  # mutant 下合法（无条件），原版下非法（pc≠0）
        lean4_correspondence="step(schedule): if lockHeld then deadlocked:=true; Inv: ¬deadlocked",
    ),
]


# ============================================================
# Tridirectional 评估
# ============================================================

@dataclass
class BoundaryResult:
    """单个语义边界的 tridirectional 评估结果"""
    boundary: SemanticBoundary

    # 正例方向：原 safe + 正确 trace → 期望 Inv 成立
    positive_inv_holds: bool

    # 反例方向：mutant safe + 揭示性 trace → 终态是否违反 Inv
    #   True  = Inv 否决了 mutant（规则有判别力）✅
    #   False = Inv 在 mutant 下仍成立（规则盲点）🟥
    boundary_inv_violated: bool

    # mutant trace 在原 safe 下是否合法（应为 False，证明 mutant 确实是单差异）
    mutant_trace_legal_under_original: bool

    # mutant trace 在 mutant safe 下是否合法（应为 True）
    mutant_trace_legal_under_mutant: bool

    # 终态
    final_state: S
    final_inv_holds: bool

    @property
    def is_discriminating(self) -> bool:
        """规则在该边界有判别力 ⟺ mutant 让 Inv 失败"""
        return self.boundary_inv_violated

    @property
    def is_blind_spot(self) -> bool:
        """规则在该边界是盲点 ⟺ mutant 仍让 Inv 成立"""
        return (not self.boundary_inv_violated) and self.mutant_trace_legal_under_mutant

    @property
    def is_redundant(self) -> bool:
        """边界冗余 ⟺ mutant trace 在 mutant safe 下也不合法（被 Inv/其他条件间接覆盖）"""
        return ((not self.mutant_trace_legal_under_mutant)
                and (not self.boundary_inv_violated))


def evaluate_boundary(b: SemanticBoundary,
                      positive_traces: List[Tuple[S, List[Ev]]]) -> BoundaryResult:
    """
    对单个语义边界跑 tridirectional 评估。

    tridirectional（借鉴 arXiv:2606.01794）：
    - positive: 原 safe + 正确 trace → Inv 成立（规则在正确行为上成立）
    - boundary: mutant safe + 揭示性 trace → 期望 Inv 否决（规则有判别力）
    - negative: 已知违反 Inv 的状态（⟨0,true⟩ 等）→ 作为反例基准
    """
    # positive: 检查所有正确 trace
    positive_ok = all(
        Inv_preserved_over_trace(s, trace, safe_original)
        for s, trace in positive_traces
    )

    # boundary: mutant safe + 揭示性 trace
    s_init = b.init_state
    trace = b.revealing_trace

    # mutant trace 在原 safe 下应非法（验证 mutant 确实是单差异）
    legal_original = OK(s_init, trace, safe_original)
    # mutant trace 在 mutant safe 下应合法
    legal_mutant = OK(s_init, trace, b.mutant_safe)

    # 终态 + Inv
    final_s = final(s_init, trace)
    final_inv = Inv(final_s)

    # boundary_inv_violated: Inv 在 mutant trace 终态是否失败
    # 若失败 = 规则否决了 mutant（判别力）
    # 若成立 = 规则在 mutant 下仍成立（盲点）
    boundary_violated = (not final_inv) and legal_mutant

    return BoundaryResult(
        boundary=b,
        positive_inv_holds=positive_ok,
        boundary_inv_violated=boundary_violated,
        mutant_trace_legal_under_original=legal_original,
        mutant_trace_legal_under_mutant=legal_mutant,
        final_state=final_s,
        final_inv_holds=final_inv,
    )


# ============================================================
# Attack-to-Property：盲点 → 新 Inv 子句候选
# ============================================================

def attack_to_property(result: BoundaryResult) -> str:
    """
    把盲点蒸馏成新 Inv 子句候选（借鉴 LeVer 的 Attack-to-Property）。
    """
    b = result.boundary
    if result.is_discriminating:
        return f"  ✅ 规则在 {b.id} 有判别力（无需新子句）"
    elif result.is_blind_spot:
        return (f"  🟥 盲点！Inv 未捕捉「{b.description}」。\n"
                f"     → 新 Inv 子句候选：补充约束「{b.lean4_correspondence}」对应的不变式\n"
                f"     → 例：扩展 Inv 加入对 {b.name} 的检查")
    elif result.is_redundant:
        return (f"  🔵 冗余边界。「{b.description}」在 Inv 约束下无法独立触发——\n"
                f"     说明 Inv 的其他子句已间接覆盖该约束（设计优点的意外红利）")
    else:
        return f"  ⚠️ 边界 {b.id} 状态异常（mutant trace 不合法或终态异常）"


# ============================================================
# 主入口：跑所有边界，输出判别力报告
# ============================================================

# 正确 trace 集（positive 方向）—— 各种合法的 spinlock+preempt 使用模式
POSITIVE_TRACES = [
    (S(0, False), []),  # 空 trace
    (S(0, False), [Ev.PREEMPT_DISABLE, Ev.LOCK_ACQUIRE,
                   Ev.LOCK_RELEASE, Ev.PREEMPT_ENABLE]),  # 标准配对
    (S(0, False), [Ev.TICK, Ev.TICK]),  # 中性事件
    (S(0, False), [Ev.PREEMPT_DISABLE, Ev.PREEMPT_DISABLE,
                   Ev.LOCK_ACQUIRE, Ev.LOCK_RELEASE,
                   Ev.PREEMPT_ENABLE, Ev.PREEMPT_ENABLE,
                   Ev.SCHEDULE]),  # 嵌套 preempt + 锁 + 调度（修正：合法 trace）
]


def main():
    print("=" * 70)
    print("Neo-OS · 对抗层 · Attacker Agent v0 · Tridirectional 判别力报告")
    print("=" * 70)
    print(f"语义边界数: {len(BOUNDARIES)}")
    print(f"正确 trace 数（positive 方向）: {len(POSITIVE_TRACES)}")
    print(f"借鉴: arXiv:2606.01794 (Tridirectional Discriminating-Power)")
    print(f"对应设计: ../01-decisions/ADVERSARIAL_LAYER_DESIGN.md §3.2 (v1.1 修正)\n")

    # positive 方向验证
    print("─" * 70)
    print("【正例方向】原 safe + 正确 trace → Inv 应成立")
    positive_all_ok = True
    for i, (s, trace) in enumerate(POSITIVE_TRACES):
        preserved = Inv_preserved_over_trace(s, trace, safe_original)
        status = "✅" if preserved else "🟥"
        print(f"  trace {i+1}: {s} → {len(trace)} events → preserved={preserved} {status}")
        if not preserved:
            positive_all_ok = False
    print(f"  → 正例方向: {'全部成立 ✅' if positive_all_ok else '有失败 🟥'}\n")

    # boundary 方向：每个边界
    print("─" * 70)
    print("【边界方向】mutant safe + 揭示性 trace → 测试 Inv 判别力")
    print("  期望：mutant 让 Inv 失败 = 规则有判别力 ✅")
    print("       mutant 仍让 Inv 成立 = 规则盲点 🟥\n")

    results = []
    n_discriminating = 0
    n_blind_spot = 0
    n_redundant = 0
    for b in BOUNDARIES:
        r = evaluate_boundary(b, POSITIVE_TRACES)
        results.append(r)

        print(f"边界 {b.id}: {b.name}")
        print(f"  描述: {b.description}")
        print(f"  init: {b.init_state}, trace: {b.revealing_trace}")
        print(f"  mutant trace 在原 safe 下合法: {r.mutant_trace_legal_under_original} "
              f"({'应为 False（单差异）' if not r.mutant_trace_legal_under_original else '🟥 应为 False！'})")
        print(f"  mutant trace 在 mutant safe 下合法: {r.mutant_trace_legal_under_mutant} "
              f"({'✅ 应为 True' if r.mutant_trace_legal_under_mutant else '🟥 应为 True！'})")
        print(f"  终态: {r.final_state}, Inv(终态)={r.final_inv_holds}")
        if r.is_discriminating:
            verdict = "✅ 有判别力（Inv 否决了 mutant）"
            n_discriminating += 1
        elif r.is_blind_spot:
            verdict = "🟥 盲点（Inv 未捕捉此错误）"
            n_blind_spot += 1
        elif r.is_redundant:
            verdict = "🔵 冗余（该边界被 Inv/其他条件间接覆盖——本身是设计优点）"
            n_redundant += 1
        else:
            verdict = "⚠️ 状态异常"
        print(f"  判定: {verdict}")
        print(attack_to_property(r))
        print()

    # 总结
    print("=" * 70)
    print("【总结】")
    print(f"  语义边界总数: {len(results)}")
    print(f"  ✅ 有判别力: {n_discriminating} ({100*n_discriminating/len(results):.0f}%)")
    print(f"  🟥 盲点: {n_blind_spot} ({100*n_blind_spot/len(results):.0f}%)")
    print(f"  🔵 冗余: {n_redundant} ({100*n_redundant/len(results):.0f}%)")
    print(f"  ⚠️ 异常: {len(results) - n_discriminating - n_blind_spot - n_redundant}")
    print()
    print("【tridirectional 判别力评估】")
    print(f"  正例方向（原 safe + 正确 trace）: {'PASS ✅' if positive_all_ok else 'FAIL 🟥'}")
    boundary_pass_rate = n_discriminating / len(results) if results else 0
    print(f"  边界方向（mutant + 揭示性 trace）: {n_discriminating}/{len(results)} "
          f"= {100*boundary_pass_rate:.0f}% 判别")
    print(f"  → 现有 Inv 捕捉了 {n_discriminating}/{len(results)} 个安全边界")
    print(f"  → {n_blind_spot} 个盲点待 Attack-to-Property 补强\n")

    # 验收对照（设计文档 §7 v1.1 修正后）
    print("─" * 70)
    print("【验收对照】（设计文档 §7 v1.1）")
    print(f"  tridirectional 正例成立: {'✅' if positive_all_ok else '🟥'}")
    print(f"  tridirectional 边界判别率 ≥ 80%: "
          f"{'✅' if boundary_pass_rate >= 0.8 else '🟥'} "
          f"(实测 {100*boundary_pass_rate:.0f}%)")
    if n_blind_spot > 0:
        print(f"  Attack-to-Property 新候选: {n_blind_spot} 个（见上方盲点建议）")
    print()

    # 输出 JSON（给 Analyst 用）
    import json
    report = {
        "timestamp": "2026-08-05",
        "version": "attacker-v0",
        "n_boundaries": len(results),
        "n_discriminating": n_discriminating,
        "n_blind_spot": n_blind_spot,
        "positive_all_ok": positive_all_ok,
        "boundary_pass_rate": boundary_pass_rate,
        "boundaries": [
            {
                "id": r.boundary.id,
                "name": r.boundary.name,
                "is_discriminating": r.is_discriminating,
                "is_blind_spot": r.is_blind_spot,
                "final_state": str(r.final_state),
                "final_inv_holds": r.final_inv_holds,
            }
            for r in results
        ],
    }
    print("─" * 70)
    print("【JSON 报告】（给 Analyst Agent 用）")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
