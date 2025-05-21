import Imp.Expr.Eval
import Imp.Stmt.BigStep
import Imp.Stmt.Basic

open Imp

def Assertion : Type := Env → Prop
syntax "{{ " term:50 " }}" : term
macro_rules
  | `({{ $P }}) => `(($P : Assertion))

@[simp]
def ValidHoareTriple (P : Assertion) (c : Stmt) (Q : Assertion) : Prop :=
  forall (σ σ' : Env), P σ -> c / σ ↓ σ' -> Q σ'

syntax "{{" term:60 "}} " term:61 " {{" term:62 "}}" : term
macro_rules
  | `({{ $P }} $c{{ $Q }}) => `(ValidHoareTriple $P $c $Q)

namespace Assertion

@[simp]
def implies (P Q : Assertion) : Prop :=
  forall σ, P σ → Q σ
syntax term:90 "->>" term:91 : term
macro_rules
  | `($P ->> $Q) => `(implies $P $Q)

@[simp]
def iff (P Q : Assertion) : Prop :=
  forall σ, P σ ↔ Q σ
syntax term:90 "<<->>" term:91 : term
macro_rules
  | `($P <<->> $Q) => `(iff $P $Q)

@[simp]
def substitution (P : Assertion) (x : String) (a : Expr) : Assertion :=
  fun σ => P (σ.setOption x (a.eval σ))
syntax term " [ " ident " ↦ " term "]" : term
macro_rules
  | `($P [$x ↦ $a]) => `(substitution $P $x $a)

@[simp]
def and (P Q : Assertion) : Assertion :=
  fun σ => P σ ∧ Q σ
syntax term:90 " <^> " term:91 : term
macro_rules
  | `($P <^> $Q) => `(and $P $Q)

@[simp]
def not (P : Assertion) : Assertion :=
  fun σ => ¬ P σ
macro_rules
  | `(! $P) => `(not $P)

end Assertion

instance : Coe Expr Assertion where
  coe b := fun σ => Truthy $ b.eval σ
@[simp]
theorem Truthy.assert_true : ∀ (b : Expr), (fun σ => Truthy (b.eval σ)) <<->> b := by
  intro b σ
  constructor <;> intro h <;> assumption

instance ExprToBool (σ : Env) : Coe Expr Bool where
  coe b := Truthy $ b.eval σ
instance ExprToValue (σ : Env) : Coe Expr Prop where
  coe b := Truthy $ b.eval σ

instance : Coe Prop Assertion where
  coe P := fun _ => P
instance : Coe Bool Assertion where
  coe b := fun _ => if b then True else False

-- def Assertion.expInt : Type := Env → Int
-- def Assertion.expV : Type := Env -> Value
-- instance : Coe Int Assertion.expInt where
--   coe i := fun _ => i
-- instance : Coe Value Assertion.expInt where
--   coe v := fun _ => v
-- instance : Coe Value Assertion.expV where
--   coe v := fun _ => v
-- instance : Coe Expr Assertion.expInt where
--   coe e := fun σ => match e.eval σ with
--     | some i => i
--     | none => 0
-- instance : Coe Expr Assertion.expV where
--   coe e := fun σ => match e.eval σ with
--     | some v => v
--     | none => Value.int 0
--
-- instance : Coe String Assertion.expInt where
--   coe s := fun σ => σ s
-- instance : Coe String Assertion.expV where
--   coe s := fun σ => σ s
-- instance expIntToExpr (σ : Env) : Coe Assertion.expInt Expr where
--   coe i := Expr.const $ i σ
-- instance ExpVToExpr (σ : Env) : Coe Assertion.expV Expr where
--   coe v := Expr.const $ v σ
