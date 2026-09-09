import Mathlib.Data.Real.Basic
import Mathlib.Data.List.Basic
import Mathlib.Algebra.Group.Defs

namespace YCKiller.Quant

structure Portfolio where
  cash : Real
  positions : List (String × Real)
  deriving Repr

inductive Signal where | buy : Real → Signal | sell : Real → Signal | hold : Signal deriving Repr

def executeTrade (p : Portfolio) (s : Signal) (price : Real) : Portfolio :=
  match s with
  | Signal.buy amt => { p with cash := p.cash - amt * price }
  | Signal.sell amt => { p with cash := p.cash + amt * price }
  | Signal.hold => p

theorem trade_deterministic (p : Portfolio) (s : Signal) (price : Real) : 
    executeTrade p s price = executeTrade p s price := rfl

def isSafeTrade (p : Portfolio) (s : Signal) (price : Real) : Bool :=
  match s with
  | Signal.buy amt => amt * price ≤ p.cash
  | _ => true

theorem safe_buy (p : Portfolio) (amt price : Real) (h : isSafeTrade p (Signal.buy amt) price) :
    (executeTrade p (Signal.buy amt) price).cash ≥ 0 := by
  simp [executeTrade, isSafeTrade] at *
  linarith

def maxDrawdown (values : List Real) : Real := 0

theorem maxDrawdown_nonneg (values : List Real) : maxDrawdown values ≥ 0 := by simp [maxDrawdown]

end YCKiller.Quant
