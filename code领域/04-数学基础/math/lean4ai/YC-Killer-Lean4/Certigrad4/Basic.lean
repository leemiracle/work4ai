import Mathlib.Data.Real.Basic
import Mathlib.Data.Array.Basic
import Mathlib.Tactic

namespace Certigrad4

inductive Tensor : Type where | scalar : Float → Tensor | vector : Array Float → Tensor deriving Repr

inductive Node : Type where
  | const : Tensor → Node
  | add : Node → Node → Node
  | mul : Node → Node → Node
  deriving Repr

def forward : Node → Tensor
  | Node.const t => t
  | Node.add _ _ => Tensor.scalar 0
  | Node.mul _ _ => Tensor.scalar 0

theorem forward_deterministic (n : Node) : forward n = forward n := rfl

def backward (_ : Node) : Tensor := Tensor.scalar 0

theorem backward_deterministic (n : Node) : backward n = backward n := rfl

end Certigrad4
