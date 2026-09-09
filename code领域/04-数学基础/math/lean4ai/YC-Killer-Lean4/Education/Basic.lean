import Mathlib.Tactic

namespace Education

theorem add_zero (n : Nat) : n + 0 = n := by simp
theorem add_comm (n m : Nat) : n + m = m + n := by omega
theorem add_assoc (n m k : Nat) : (n + m) + k = n + (m + k) := by omega
theorem mul_zero (n : Nat) : n * 0 = 0 := by simp
theorem mul_comm (n m : Nat) : n * m = m * n := by omega
theorem mul_assoc (n m k : Nat) : (n * m) * k = n * (m * k) := by omega
theorem mul_add (n m k : Nat) : n * (m + k) = n * m + n * k := by omega
theorem add_mul (n m k : Nat) : (n + m) * k = n * k + m * k := by omega
theorem zero_add (n : Nat) : 0 + n = n := by simp
theorem one_mul (n : Nat) : 1 * n = n := by simp
theorem mul_one (n : Nat) : n * 1 = n := by simp
theorem nat_eq_refl (n : Nat) : n = n := rfl
theorem nat_le_refl (n : Nat) : n ≤ n := by omega

end Education
