import Mathlib.Data.Real.Basic
import Mathlib.Data.List.Basic
import Mathlib.Data.Nat.Basic
import Mathlib.Data.Finset.Basic

namespace Leantime

inductive ProjectStatus where | open | inProgress | onHold | closed deriving Repr
inductive TaskStatus where | new | inProgress | waiting | done | archived deriving Repr

structure Project where
  id : Nat
  name : String
  status : ProjectStatus
  budget : Real
  spent : Real
  progress : Real
  deriving Repr

def isValidProject (p : Project) : Bool :=
  p.name ≠ "" ∧ p.budget ≥ 0 ∧ p.spent ≥ 0 ∧ p.spent ≤ p.budget ∧ p.progress ≥ 0 ∧ p.progress ≤ 100

theorem valid_project_budget (p : Project) (h : isValidProject p) : p.spent ≤ p.budget := by
  simp [isValidProject] at h; exact h.2.2.1

theorem valid_project_progress (p : Project) (h : isValidProject p) : p.progress ≥ 0 ∧ p.progress ≤ 100 := by
  simp [isValidProject] at h; exact ⟨h.2.2.2.1, h.2.2.2.2⟩

structure Task where
  id : Nat
  projectId : Nat
  headline : String
  status : TaskStatus
  storyPoints : Nat
  deriving Repr

def isValidTask (t : Task) : Bool := t.headline ≠ "" ∧ t.storyPoints ≤ 21

theorem valid_task_story_points (t : Task) (h : isValidTask t) : t.storyPoints ≤ 21 := by
  simp [isValidTask] at h; exact h.2

structure Risk where
  id : Nat
  probability : Real
  impact : Real
  deriving Repr

def riskScore (r : Risk) : Real := r.probability * r.impact

def isValidRisk (r : Risk) : Bool := r.probability ≥ 0 ∧ r.probability ≤ 1 ∧ r.impact ≥ 0 ∧ r.impact ≤ 1

theorem risk_score_bounded (r : Risk) (h : isValidRisk r) : riskScore r ≥ 0 ∧ riskScore r ≤ 1 := by
  simp [riskScore, isValidRisk] at *
  constructor
  · exact mul_nonneg h.1 h.2.2.1
  · exact mul_le_one h.2.1 h.2.2.2

end Leantime
