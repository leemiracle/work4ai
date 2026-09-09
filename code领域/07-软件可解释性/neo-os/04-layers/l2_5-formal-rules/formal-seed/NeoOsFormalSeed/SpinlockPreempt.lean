/-
  NeoOsFormalSeed.SpinlockPreempt   (命门 C2 · 非平凡规则 · v2 含 deadlocked 状态)
  ===================================================================
  建模真实 OS 机制：spinlock × preempt_disable 配对纪律 + sleep 持锁死锁。

  v2 改动（2026-08-05，回应 Oracle Review F5）：
    - 新增 deadlocked : Bool 字段——schedule 持锁时进入死锁态
    - 这修复了 v1 的「schedule 是 no-op」模型缺陷：v1 测不到 sleep 持锁死锁
    - Inv 扩展加入 ¬deadlocked 约束
    - 现在模型能表达「持锁时 schedule → 死锁」这个 spinlock 最核心 bug 类
    - 对抗层不再把「模型盲点」误报为「规则盲点」

  为什么这条规则【超过 omega】（council C2 验收点，v1 已成立，v2 保持）：
    - omega 只做 Presburger 线性算术
    - 主定理 `Inv_preserved_over_trace` 必须 `induction on OK`
    - 在 6 个事件分支上分别推导不变式保持——omega 永远做不到

  物理背景（Linux kernel 真实规则）：
    - 自旋锁持有时忙等，不可睡眠；故持有 spinlock 时必须 preempt_disable
    - schedule 持锁时会睡眠 → 死锁（v2 用 deadlocked 字段建模）
    - 配对纪律：preemptEnable 不得把 count 降到 0（当持锁时）

  反例定理：
    - `pair_discipline_is_necessary`：无配对纪律则 Inv 不保持（v1 保留）
    - `schedule_held_causes_deadlock`：持锁 schedule 进入死锁态（v2 新增）
-/
namespace NeoOs.SpinlockPreempt

-- ============================================================
-- 状态（v2：新增 deadlocked 字段）
-- ============================================================

/-- 系统状态：抢占禁用深度 + 自旋锁持有标志 + 死锁标志 -/
structure S where
  preemptCount : Nat   -- preempt_disable 嵌套深度（≥ 0）
  lockHeld     : Bool  -- 是否持有 spinlock
  deadlocked   : Bool  -- v2 新增：持锁时 schedule 进入死锁态（sink state）

-- ============================================================
-- 事件（六原子，覆盖 OS 调度/锁的关键决策点）
-- ============================================================

inductive Ev where
  | lockAcquire    : Ev   -- 获取自旋锁  (pc+1, lockHeld:=true)
  | lockRelease    : Ev   -- 释放自旋锁  (pc-1, lockHeld:=false)
  | preemptDisable : Ev   -- 关闭抢占    (pc+1)
  | preemptEnable  : Ev   -- 开启抢占    (pc-1，须守配对纪律)
  | tick           : Ev   -- 时钟中性事件
  | schedule       : Ev   -- 调度（须 pc=0 ∧ 无锁；v2：持锁时进入 deadlocked）

-- ============================================================
-- 事件语义（v2：schedule 持锁时进入 deadlocked）
-- ============================================================

def step (e : Ev) (s : S) : S :=
  match e with
  | Ev.lockAcquire    => { preemptCount := s.preemptCount + 1, lockHeld := true, deadlocked := s.deadlocked }
  | Ev.lockRelease    => { preemptCount := s.preemptCount - 1, lockHeld := false, deadlocked := s.deadlocked }
  | Ev.preemptDisable => { preemptCount := s.preemptCount + 1, lockHeld := s.lockHeld, deadlocked := s.deadlocked }
  | Ev.preemptEnable  => { preemptCount := s.preemptCount - 1, lockHeld := s.lockHeld, deadlocked := s.deadlocked }
  | Ev.tick           => s
  -- v2 核心：持锁时 schedule 进入死锁态（真实 kernel：sleep 持锁 → 死锁）
  | Ev.schedule       => if s.lockHeld then { preemptCount := s.preemptCount, lockHeld := s.lockHeld, deadlocked := true } else s

-- ============================================================
-- 事件合法性（前置条件 safe）——编码 kernel 配对纪律
-- ============================================================

def safe (e : Ev) (s : S) : Prop :=
  match e with
  | Ev.lockAcquire    => True
  | Ev.lockRelease    => s.lockHeld = true
  | Ev.preemptDisable => True
  | Ev.preemptEnable  => s.preemptCount ≥ 1 ∧ (s.lockHeld = true → s.preemptCount ≥ 2)
  | Ev.tick           => True
  | Ev.schedule       => s.preemptCount = 0 ∧ s.lockHeld = false

-- ============================================================
-- 安全不变式（v2：扩展加入 ¬deadlocked）
-- ============================================================

/-- Inv v2：计数非负 ∧ 持锁时抢占必关 ∧ 未死锁 -/
def Inv (s : S) : Prop :=
  s.preemptCount ≥ 0 ∧ (s.lockHeld = true → s.preemptCount ≥ 1) ∧ s.deadlocked = false

-- ============================================================
-- trace 合法性归纳谓词 OK
-- ============================================================

inductive OK : S → List Ev → Prop where
  | nil  : ∀ s, OK s []
  | cons : ∀ s e es, safe e s → OK (step e s) es → OK s (e :: es)

-- ============================================================
-- 终态（fold step over trace）
-- ============================================================

def final : S → List Ev → S
  | s, []       => s
  | s, e :: es  => final (step e s) es

-- ============================================================
-- 关键引理：单步 safe 事件保持 Inv（v2 含 deadlocked 处理）
-- ============================================================

theorem step_preserves_Inv (e : Ev) (s : S) (hInv : Inv s) (hsafe : safe e s) :
    Inv (step e s) := by
  -- 解构 hInv : Inv s = ⟨pc≥0, lockHeld→pc≥1, deadlocked=false⟩
  obtain ⟨hpc0, hInv2, hdead⟩ := hInv
  cases e with
  | lockAcquire =>
    -- step: pc+1, lockHeld:=true, deadlocked 不变（= s.deadlocked = false）
    refine ⟨?_, ?_, ?_⟩
    · show (s.preemptCount + 1) ≥ 0; omega
    · intro (_ : (true : Bool) = true); show (s.preemptCount + 1) ≥ 1; omega
    · show s.deadlocked = false; exact hdead
  | lockRelease =>
    have hL : s.lockHeld = true := hsafe
    have hpc1 : s.preemptCount ≥ 1 := hInv2 hL
    refine ⟨?_, ?_, ?_⟩
    · show (s.preemptCount - 1) ≥ 0; omega
    · intro (h : (false : Bool) = true); injection h
    · show s.deadlocked = false; exact hdead
  | preemptDisable =>
    refine ⟨?_, ?_, ?_⟩
    · show (s.preemptCount + 1) ≥ 0; omega
    · intro (h : s.lockHeld = true); have := hInv2 h; show (s.preemptCount + 1) ≥ 1; omega
    · show s.deadlocked = false; exact hdead
  | preemptEnable =>
    obtain ⟨h1, h2⟩ := hsafe
    refine ⟨?_, ?_, ?_⟩
    · show (s.preemptCount - 1) ≥ 0; omega
    · intro (h : s.lockHeld = true); have hpc2 : s.preemptCount ≥ 2 := h2 h; show (s.preemptCount - 1) ≥ 1; omega
    · show s.deadlocked = false; exact hdead
  | tick =>
    -- step tick = s，Inv 直接保持
    exact ⟨hpc0, hInv2, hdead⟩
  | schedule =>
    -- safe(schedule) 要求 pc=0 ∧ ¬lockHeld
    -- 故 step schedule = if lockHeld then ... else s，因 ¬lockHeld 走 else = s
    have hNotLock : s.lockHeld = false := by
      obtain ⟨_, h2⟩ := hsafe; exact h2
    -- step schedule s = s（因 lockHeld=false）
    have : step Ev.schedule s = s := by
      simp [step, hNotLock]
    rw [this]
    exact ⟨hpc0, hInv2, hdead⟩

-- ============================================================
-- 主定理：trace 执行保持 Inv（非平凡——需归纳，超过 omega）
-- council C2 验收点（v2 保持）
-- ============================================================

theorem Inv_preserved_over_trace :
    ∀ (s : S) (es : List Ev), OK s es → Inv s → Inv (final s es) := by
  intro s es hOK
  induction hOK with
  | nil s' => intro hInv; exact hInv
  | cons s' e es' hsafe hOK' IH =>
    intro hInv
    have hInv' : Inv (step e s') := step_preserves_Inv e s' hInv hsafe
    -- 显式匹配 final 定义（v1 有此 show，v2 重写时漏掉导致 sorryAx 回归）
    show Inv (final (step e s') es')
    exact IH hInv'

-- ============================================================
-- 反例定理 1：配对纪律是【必要条件】（v1 保留，v2 调整 deadlocked 初始）
-- ============================================================

/-- 弱版 safe'：preemptEnable 只要求 pc≥1（去掉配对纪律） -/
def safe' (e : Ev) (s : S) : Prop :=
  match e with
  | Ev.preemptEnable => s.preemptCount ≥ 1
  | _                => safe e s

theorem pair_discipline_is_necessary :
    ∃ (s : S) (e : Ev),
      Inv s ∧ safe' e s ∧ ¬ Inv (step e s) := by
  -- ⟨1, true, false⟩：持锁，pc=1，未死锁
  refine ⟨⟨1, true, false⟩, Ev.preemptEnable, ?_, ?_, ?_⟩
  · -- Inv ⟨1,true,false⟩ = 1≥0 ∧ (true→1≥1) ∧ false=false
    show (1 : Nat) ≥ 0 ∧ ((true : Bool) = true → (1 : Nat) ≥ 1) ∧ (false : Bool) = false
    refine ⟨Nat.zero_le _, ?_, rfl⟩
    intro _; exact Nat.le.refl
  · -- safe' preemptEnable ⟨1,true,false⟩ = pc≥1
    show (1 : Nat) ≥ 1
    exact Nat.le.refl
  · -- ¬ Inv (step preemptEnable ⟨1,true,false⟩) = ¬ Inv ⟨0,true,false⟩
    -- step preemptEnable: pc-1=0, lockHeld 不变=true, deadlocked 不变=false
    -- Inv ⟨0,true,false⟩ 要求 (true→0≥1) 即 0≥1，矛盾
    show ¬ ((0 : Nat) ≥ 0 ∧ ((true : Bool) = true → (0 : Nat) ≥ 1) ∧ (false : Bool) = false)
    intro ⟨_, h2, _⟩
    have : (0 : Nat) ≥ 1 := h2 rfl
    exact absurd this (by decide)

-- ============================================================
-- 反例定理 2（v2 新增）：持锁 schedule 进入死锁态
-- 回应 Oracle Review F5：模型现在能表达 sleep 持锁死锁
-- ============================================================

/-- 持锁时 schedule 会进入 deadlocked=true（v2 新增，回应 Oracle F5） -/
theorem schedule_held_sets_deadlock (s : S) (hLock : s.lockHeld = true) :
    (step Ev.schedule s).deadlocked = true := by
  -- step schedule s = if s.lockHeld then {..., deadlocked := true} else s
  -- 因 s.lockHeld = true，走 then 分支，deadlocked := true
  unfold step
  rw [if_pos hLock]
  rfl

/-- 持锁时 schedule 进入死锁态，违反 Inv（v2 新增） -/
theorem schedule_held_violates_Inv (s : S) (hLock : s.lockHeld = true) :
    ¬ Inv (step Ev.schedule s) := by
  intro hInv
  obtain ⟨_, _, hdead⟩ := hInv
  -- hdead : (step schedule s).deadlocked = false
  -- 但 schedule_held_sets_deadlock 说 = true，矛盾
  have hTrue : (step Ev.schedule s).deadlocked = true := schedule_held_sets_deadlock s hLock
  rw [hdead] at hTrue
  exact absurd hTrue (by decide)

-- ============================================================
-- sorry 清零验证
-- ============================================================

#print axioms step_preserves_Inv
#print axioms Inv_preserved_over_trace
#print axioms pair_discipline_is_necessary
#print axioms schedule_held_sets_deadlock
#print axioms schedule_held_violates_Inv

end NeoOs.SpinlockPreempt
