/-
  NeoOsFormalSeed.RaftElection   (Phase 1 · ElectionSafety 完整版)
  ===================================================================
  Raft 选举安全定理（对齐 dsyme/raft-lean-squad RE5 + Ongaro §5.2）。
  完整版：从 vote 函数推导单值性（disjoint_votesFor），无 hdisjoint 假设。

  关键技术（攻克 Lean4 core decide if 难点）：
    - cases hd : decide ... with | true | false（Bool 结构分情形，cases 自动替换 goal）
    - decide_eq_true_iff.mp / .mpr（decide = true ↔ p）
    - dsimp only [] 计算 cond true/false（definitional）
    - disjoint_votesFor 对 voters 归纳，非平凡——超过 omega
-/
namespace NeoOs.RaftElection

def votesFor (voters : List Nat) (vote : Nat → Option Nat) (c : Nat) : Nat :=
  voters.countP (fun v => decide (vote v = some c))

private theorem disjoint_votesFor (voters : List Nat) (vote : Nat → Option Nat)
    (c1 c2 : Nat) (hne : c1 ≠ c2) :
    votesFor voters vote c1 + votesFor voters vote c2 ≤ voters.length := by
  induction voters with
  | nil => simp [votesFor]
  | cons v vs IH =>
    simp only [votesFor, List.countP_cons] at IH ⊢
    -- Bool 结构分情形：cases 自动把 goal 的 decide 替换为 true/false
    cases hd1 : decide (vote v = some c1) with
    | true =>
      have h1 : vote v = some c1 := decide_eq_true_iff.mp hd1
      have h2 : ¬ (vote v = some c2) := by
        intro he; exact hne (Option.some_inj.mp (h1.symm.trans he))
      cases hd2 : decide (vote v = some c2) with
      | true => exact absurd (decide_eq_true_iff.mp hd2) h2
      | false => simp; omega
    | false =>
      cases hd2 : decide (vote v = some c2) with
      | true => simp; omega
      | false => simp; omega

theorem electionSafety (voters : List Nat) (vote : Nat → Option Nat)
    (c1 c2 : Nat)
    (h1 : 2 * votesFor voters vote c1 > voters.length)
    (h2 : 2 * votesFor voters vote c2 > voters.length) :
    c1 = c2 := by
  by_cases hne : c1 = c2
  · exact hne
  · exfalso
    have hdis : votesFor voters vote c1 + votesFor voters vote c2 ≤ voters.length :=
      disjoint_votesFor voters vote c1 c2 hne
    omega

#print axioms disjoint_votesFor
#print axioms electionSafety

end NeoOs.RaftElection
