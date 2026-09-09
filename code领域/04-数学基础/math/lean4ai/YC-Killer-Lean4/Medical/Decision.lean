import Mathlib.Data.Real.Basic
import Mathlib.Data.Finset.Basic
import Mathlib.Data.Nat.Basic

namespace YCKiller.Medical

inductive Symptom where | fever | cough | headache | fatigue | shortnessOfBreath | nausea deriving Repr, DecidableEq
inductive Severity where | mild | moderate | severe | critical deriving Repr, DecidableEq
inductive Disease where | commonCold | influenza | covid19 | migraine | pneumonia | gastritis deriving Repr, DecidableEq
inductive Medication where | paracetamol | ibuprofen | aspirin | amoxicillin deriving Repr, DecidableEq

structure Patient where
  age : Nat
  weight : Real
  symptoms : Finset Symptom
  deriving Repr

def diagnose (symptoms : Finset Symptom) (age : Nat) : Disease :=
  if Symptom.fever ∈ symptoms ∧ Symptom.cough ∈ symptoms then Disease.commonCold
  else if Symptom.headache ∈ symptoms then Disease.migraine
  else Disease.commonCold

theorem diagnosis_deterministic (s1 s2 : Finset Symptom) (a1 a2 : Nat) (hs : s1 = s2) (ha : a1 = a2) :
    diagnose s1 a1 = diagnose s2 a2 := by simp [hs, ha]

theorem diagnosis_complete (symptoms : Finset Symptom) (age : Nat) : ∃ d : Disease, diagnose symptoms age = d := by
  use diagnose symptoms age

def calculateDose (med : Medication) (weight : Real) (age : Nat) : Real :=
  match med with
  | Medication.paracetamol => min (weight * 15) 1000
  | Medication.ibuprofen => if age ≥ 12 then min (weight * 10) 800 else min (weight * 5) 400
  | Medication.aspirin => if age < 16 then 0 else min (weight * 10) 1000
  | Medication.amoxicillin => weight * 25

theorem paracetamol_safe (w : Real) (a : Nat) : calculateDose Medication.paracetamol w a ≤ 1000 := by
  simp [calculateDose]; exact min_le_right _ _

theorem aspirin_contraindicated (w : Real) (a : Nat) (h : a < 16) : calculateDose Medication.aspirin w a = 0 := by
  simp [calculateDose, h]

def assessUrgency (p : Patient) : Severity :=
  if Symptom.shortnessOfBreath ∈ p.symptoms then Severity.critical else Severity.mild

theorem breathlessness_critical (p : Patient) (h : Symptom.shortnessOfBreath ∈ p.symptoms) : 
    assessUrgency p = Severity.critical := by simp [assessUrgency, h]

end YCKiller.Medical
