"""
Neo-OS · 对抗层 · SpinlockPreempt Python 语义模型
=================================================
忠实映射 `../04-layers/l2_5-formal-rules/formal-seed/NeoOsFormalSeed/SpinlockPreempt.lean` 的语义，
用于对抗层 v0 的快速 mutant 评估（不依赖 lake/Lean4 环境）。

设计原则：
- 1:1 对应 Lean4 定义（S/Ev/step/safe/Inv/OK/final）
- Nat 减法用饱和语义（Lean4 Nat 减法是饱和的：0-1=0）
- 每个函数有 docstring 标注对应的 Lean4 定义
- 用 dataclass + frozen=True 保证状态不可变（对应 Lean4 的 immutable structure）
"""
from dataclasses import dataclass, replace
from typing import Callable, List
from enum import Enum


# ============================================================
# 状态 S（对应 Lean4 `structure S`）
# ============================================================

@dataclass(frozen=True)
class S:
    """系统状态：preemptCount（抢占禁用深度）+ lockHeld（持锁标志）+ deadlocked（v2 新增）"""
    preemptCount: int   # ≥ 0（Lean4 Nat）
    lockHeld: bool
    deadlocked: bool = False  # v2 新增：持锁时 schedule 进入死锁态（F5 修复）

    def __repr__(self):
        return f"⟨pc={self.preemptCount}, lock={self.lockHeld}⟩"


# ============================================================
# 事件 Ev（对应 Lean4 `inductive Ev`）
# ============================================================

class Ev(Enum):
    """六原子事件（覆盖 OS 调度/锁的关键决策点）"""
    LOCK_ACQUIRE = "lockAcquire"        # 获取自旋锁 (pc+1, lockHeld:=true)
    LOCK_RELEASE = "lockRelease"        # 释放自旋锁 (pc-1, lockHeld:=false)
    PREEMPT_DISABLE = "preemptDisable"  # 关闭抢占 (pc+1)
    PREEMPT_ENABLE = "preemptEnable"    # 开启抢占 (pc-1，须守配对纪律)
    TICK = "tick"                       # 时钟中性事件
    SCHEDULE = "schedule"               # 调度（须 pc=0 ∧ 无锁）


# ============================================================
# 饱和减法（对应 Lean4 Nat 减法）
# ============================================================

def nat_sub(a: int, b: int) -> int:
    """Lean4 Nat 减法是饱和的：max(0, a-b)"""
    assert a >= 0 and b >= 0, f"Nat 减法要求非负: {a} - {b}"
    return max(0, a - b)


# ============================================================
# step 函数（对应 Lean4 `def step`）
# ============================================================

def step(e: Ev, s: S) -> S:
    """事件语义（确定性状态转移）。对应 Lean4 `step`。"""
    if e == Ev.LOCK_ACQUIRE:
        return replace(s, preemptCount=s.preemptCount + 1, lockHeld=True)
    elif e == Ev.LOCK_RELEASE:
        return replace(s, preemptCount=nat_sub(s.preemptCount, 1), lockHeld=False)
    elif e == Ev.PREEMPT_DISABLE:
        return replace(s, preemptCount=s.preemptCount + 1)
    elif e == Ev.PREEMPT_ENABLE:
        return replace(s, preemptCount=nat_sub(s.preemptCount, 1))
    elif e == Ev.TICK:
        return s
    elif e == Ev.SCHEDULE:
        # v2：持锁时 schedule 进入死锁态（F5 修复，对应 SpinlockPreempt.lean v2）
        if s.lockHeld:
            return replace(s, deadlocked=True)
        return s
    else:
        raise ValueError(f"未知事件: {e}")


# ============================================================
# safe 函数（对应 Lean4 `def safe`）—— 配对纪律编码于此
# ============================================================
# safe 类型：事件前置条件谓词
SafeFn = Callable[[Ev, S], bool]


def safe_original(e: Ev, s: S) -> bool:
    """
    原版 safe（kernel 真实配对纪律）。对应 Lean4 `safe`。
    - preemptEnable: pc≥1 ∧ (lockHeld→pc≥2)  ← 配对纪律核心
    - schedule: pc=0 ∧ ¬lockHeld              ← 不可睡眠持锁
    - lockRelease: lockHeld=true              ← 不可释放未持有锁
    """
    if e == Ev.LOCK_ACQUIRE:
        return True
    elif e == Ev.LOCK_RELEASE:
        return s.lockHeld == True
    elif e == Ev.PREEMPT_DISABLE:
        return True
    elif e == Ev.PREEMPT_ENABLE:
        return s.preemptCount >= 1 and (s.lockHeld == True and s.preemptCount >= 2 or s.lockHeld == False)
    elif e == Ev.TICK:
        return True
    elif e == Ev.SCHEDULE:
        return s.preemptCount == 0 and s.lockHeld == False
    return False


# ============================================================
# Inv 不变式（对应 Lean4 `def Inv`）
# ============================================================

def Inv(s: S) -> bool:
    """
    核心因果规则。对应 Lean4 `Inv` v2。
    Inv s := pc≥0 ∧ (lockHeld=true → pc≥1) ∧ ¬deadlocked
    即：持有 spinlock 时 preempt_count 必须 ≥ 1（不可睡眠持锁）；未死锁。
    """
    return s.preemptCount >= 0 and (s.lockHeld != True or s.preemptCount >= 1) and not s.deadlocked


# ============================================================
# trace 合法性 OK（对应 Lean4 `inductive OK`）
# ============================================================

def OK(s: S, es: List[Ev], safe_fn: SafeFn = safe_original) -> bool:
    """
    trace 合法性判断。对应 Lean4 `OK` 归纳谓词。
    OK s es ⟺ 每一步都满足 safe_fn，且递归成立。
    """
    cur = s
    for e in es:
        if not safe_fn(e, cur):
            return False
        cur = step(e, cur)
    return True


# ============================================================
# final 终态（对应 Lean4 `def final`）
# ============================================================

def final(s: S, es: List[Ev]) -> S:
    """trace 执行后的终态。对应 Lean4 `final`（fold step over trace）。"""
    cur = s
    for e in es:
        cur = step(e, cur)
    return cur


# ============================================================
# 主定理 Python 版（对应 Lean4 `Inv_preserved_over_trace`）
# ============================================================

def Inv_preserved_over_trace(s: S, es: List[Ev], safe_fn: SafeFn = safe_original) -> bool:
    """
    主定理 Python 版。对应 Lean4 `Inv_preserved_over_trace`。
    定理：OK s es → Inv s → Inv (final s es)
    
    Python 版直接计算：若 trace 合法且初态满足 Inv，则终态满足 Inv。
    （这是 step_preserves_Inv 的迭代版——Python 无法做归纳证明，但可数值验证）
    """
    if not OK(s, es, safe_fn):
        return False  # trace 不合法，定理前提不成立
    if not Inv(s):
        return False  # 初态不满足 Inv
    return Inv(final(s, es))


# ============================================================
# 自测（对照 Lean4 已验证结果）
# ============================================================

if __name__ == "__main__":
    print("=== SpinlockPreempt Python 语义模型自测 ===\n")

    # 测试 1：正确 trace 保持 Inv
    s0 = S(0, False)
    trace_correct = [Ev.PREEMPT_DISABLE, Ev.LOCK_ACQUIRE, Ev.LOCK_RELEASE,
                     Ev.PREEMPT_ENABLE]  # 正确配对
    print(f"初态 {s0}, trace {trace_correct}")
    print(f"  OK = {OK(s0, trace_correct)}")
    print(f"  final = {final(s0, trace_correct)}")
    print(f"  Inv_preserved = {Inv_preserved_over_trace(s0, trace_correct)}")
    assert OK(s0, trace_correct), "正确 trace 应合法"
    assert Inv_preserved_over_trace(s0, trace_correct), "正确 trace 应保持 Inv"

    # 测试 2：pair_discipline 反例（对应 Lean4 `pair_discipline_is_necessary`）
    # ⟨1, true⟩ → preemptEnable → ⟨0, true⟩
    # 在原 safe 下：preemptEnable ⟨1,true⟩ 要 pc≥2，但 pc=1，所以 safe=False（非法）
    s1 = S(1, True)
    print(f"\n反例状态 {s1}, preemptEnable:")
    print(f"  safe_original(preemptEnable, ⟨1,true⟩) = {safe_original(Ev.PREEMPT_ENABLE, s1)}")
    assert not safe_original(Ev.PREEMPT_ENABLE, s1), "⟨1,true⟩ preemptEnable 应违反配对纪律"

    # 但 step 后 ⟨0, true⟩ 违反 Inv
    s1_after = step(Ev.PREEMPT_ENABLE, s1)
    print(f"  step 后 = {s1_after}, Inv = {Inv(s1_after)}")
    assert not Inv(s1_after), "⟨0,true⟩ 应违反 Inv"

    print("\n✅ 模型自测通过（对照 Lean4 已验证结果）")
