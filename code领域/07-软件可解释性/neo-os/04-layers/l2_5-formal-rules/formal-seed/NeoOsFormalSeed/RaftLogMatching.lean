/-
  NeoOsFormalSeed.RaftLogMatching   (Phase 1 · LogMatching 种子)
  ===================================================================
  Raft 日志匹配定理（对齐 dsyme/raft-lean-squad LogMatching + Ongaro §5.4.1）。
  Phase 1 第三个形式化规则。

  当前（种子）：logMatchingSingle（Raft §5.4.1 核心：同 index+term → 同 entry）。
    零公理（Option 单值 + Prod 注入）。

  Phase 1 后续（完整 LogMatching）：
    - append_preserves_get? / leaderAppendPreserves（leader append 保持 matching）
    - 技术难点：Lean4 core（无 Std/Mathlib）缺 `(l1 ++ l2).get? i` 的 simp 引理，
      get? 的 cons_succ 方程 rw 在 append 上 type mismatch（defeq 不自动）。
      需 Std（`List.get?_append_left`）或手证 get? 的 list 归纳。
    - 解锁后完整 Raft §5.4.1（leader append 不破坏 log matching）。
-/
namespace NeoOs.RaftLogMatching

/-- logMatchAt: log 在 index i 是 (term t, entry e) -/
def logMatchAt (log : List (Nat × Nat)) (i : Nat) (t : Nat) (e : Nat) : Prop :=
  log.get? i = some (t, e)

-- ============================================================
-- 单点 LogMatching（Raft §5.4.1 核心：同 index+term → 同 entry）
-- ============================================================

theorem logMatchingSingle (log : List (Nat × Nat)) (i : Nat) (t : Nat) (e1 e2 : Nat)
    (h1 : logMatchAt log i t e1) (h2 : logMatchAt log i t e2) :
    e1 = e2 := by
  simp only [logMatchAt] at h1 h2
  rw [h1] at h2
  -- h2 : some (t, e1) = some (t, e2)；Option 注入 + Prod 注入
  injection h2 with hprod
  injection hprod with _ heq
  exact heq

-- ============================================================
-- Leader append 保持前置一致（Raft §5.4.1 完整版）
-- Phase 1 后续——需 Lean4 Std 的 List.get?_append_left 或手证
-- ============================================================

/-
 theorem append_preserves_get? (log : List (Nat × Nat)) (e : Nat × Nat) (i : Nat)
     (hi : i < log.length) :
     (log ++ [e]).get? i = log.get? i :=
   List.get?_append_left [e] hi  -- 需 Std

 theorem leaderAppendPreserves (leader follower : List (Nat × Nat)) (e : Nat × Nat)
     (i : Nat) (hi : i < leader.length)
     (hmatch : follower.get? i = leader.get? i) :
     follower.get? i = (leader ++ [e]).get? i := by
   rw [append_preserves_get? leader e i hi]
   exact hmatch
-/

#print axioms logMatchingSingle

end NeoOs.RaftLogMatching
