import Imp.Expr.Basic

open Lean

namespace Imp

inductive Value where
  | int : Int -> Value
  deriving Repr, DecidableEq, BEq

instance Value.LT : LT Value where
  lt (a b : Value) := match a, b with
    | .int i, .int j => i < j

instance Value.LE : LE Value where
  le (a b : Value) := match a, b with
    | .int i, .int j => i ≤ j

instance Value.OfNat : OfNat Value n := by
  constructor
  exact .int n

instance : Coe Int Value where
  coe i := Value.int i
instance : Coe Value Int where
  coe v := match v with
    | .int i => i

instance : Add Value where
  add (a b : Value) := match a, b with
    | .int i, .int j => Value.int (i + j)

instance : Sub Value where
  sub (a b : Value) := match a, b with
    | .int i, .int j => Value.int (i - j)

instance : Mul Value where
  mul (a b : Value) := match a, b with
    | .int i, .int j => Value.int (i * j)

theorem Value.int_lt (a b : Value) : a < b ↔ (a : Int) < (b : Int) := by
  constructor <;> intros h <;>
    cases a with
    | int i =>
      cases b with
      | int j =>
        have h' : i < j := h
        assumption

theorem Value.int_le (a b : Value) : a ≤ b ↔ (a : Int) ≤ (b : Int) := by
  constructor <;> intros h <;>
    cases a with
    | int i =>
      cases b with
      | int j =>
        have h' : i ≤ j := h
        assumption

theorem Value.lt_implies_le {a b : Value} : a < b → a ≤ b := by
  intros h
  cases a with
  | int i =>
    cases b with
    | int j =>
      have h' : i < j := h
      rw [Int.lt_iff_le_not_le] at h'
      cases h'
      assumption

/-- An environment maps variables names to their values (no pointers) -/
def Env := String → Value

-- instance StringToValue (σ : Env) : Coe String Value where
--   coe := σ
-- instance StringToInt (σ : Env) : Coe String Int where
--   coe s := σ s
--
-- instance varValAdd (σ : Env) : HAdd String Value Value where
--   hAdd x y := σ x + y
-- instance valVarAdd(σ : Env) : HAdd Value String Value where
--   hAdd x y := x + σ y
-- instance varValSub (σ : Env) : HSub String Value Value where
--   hSub x y := σ x - y
-- instance valVarSub (σ : Env) : HSub Value String Value where
--   hSub x y := x - σ y
-- instance varValMul (σ : Env) : HMul String Value Value where
--   hMul x y := σ x * y
-- instance valVarMul (σ : Env) : HMul Value String Value where
--   hMul x y := x * σ y

namespace Env

/-- Set a value in an environment -/
def set (x : String) (v : Value) (σ : Env) : Env :=
  fun y => if x == y then v else σ y

def setOption (x : String) (v : Option Value) (σ : Env) : Env :=
  match v with
  | some v => σ.set x v
  | none => σ

/-- Look up a value in an environment -/
def get (x : String) (σ : Env) : Value :=
  σ x

/-- Initialize an environment, setting all uninitialized memory to `i` -/
def init (i : Value) : Env := fun _ => i

@[simp]
theorem get_init : (Env.init v).get x = v := by rfl

@[simp]
theorem get_set_same {σ : Env} : (σ.set x v).get x = v := by
  simp [get, set]

@[simp]
theorem get_set_different {σ : Env} : x ≠ y → (σ.set x v).get y = σ.get y := by
  intros
  simp [get, set, *]

end Env

namespace Expr

/-- Helper that implements unary operators -/
def UnOp.apply : UnOp → Value → Option Value
  | .neg, .int i => (Value.int ∘ Int.neg) <$> some i
  | .not, .int b => if b == 0 then some (Value.int 1) else some (Value.int 0)

/-- Helper that implements binary operators -/
def BinOp.apply : BinOp → Value → Value → Option Value
  | .plus, .int i, .int j => some $ Value.int (i + j)
  | .minus, .int i, .int j => some $ Value.int (i - j)
  | .times, .int i, .int j => some $ Value.int (i * j)
  | .div, .int i, .int j => if j == 0 then none else some $ Value.int (i / j)
  | .and, .int b, .int c => some $ Value.int (b * c)
  | .or, .int b, .int c => some $ Value.int (b + c)
  | .eq, .int i, .int j => some $ if i == j then Value.int 1 else Value.int 0
  | .le, .int i, .int j => some (if i <= j then Value.int 1 else Value.int 0)
  | .lt, .int i, .int j => some $ if i < j then Value.int 1 else Value.int 0

/--
Evaluates an expression, finding the value if it has one.

Expressions that divide by zero don't have values - the result is undefined.
-/
def eval (σ : Env) : Expr → Option Value
  | .const i => some $ .int i
  | .var x => σ.get x
  | .un op e => do
    let v ← e.eval σ
    op.apply v
  | .bin op e1 e2 => do
    let v1 ← e1.eval σ
    let v2 ← e2.eval σ
    op.apply v1 v2
