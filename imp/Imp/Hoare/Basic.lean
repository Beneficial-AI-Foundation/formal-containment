import Imp.Expr.Eval
import Imp.Stmt.BigStep
import Imp.Stmt.Basic

open Imp Stmt

def Assertion : Type := Env → Prop

@[simp]
def ValidHoareTriple (P : Assertion) (c : Stmt) (Q : Assertion) : Prop :=
  forall (σ σ' : Env), P σ -> c / σ ↓ σ' -> Q σ'

syntax "{{" term:90 "}} " term:91 " {{" term:92 "}}" : term
macro_rules
  | `({{ $P }} $c{{ $Q }}) => `(ValidHoareTriple $P $c $Q)

@[simp]
def Assertion.implies (P Q : Assertion) : Prop :=
  forall σ, P σ → Q σ
syntax term:90 "->>" term:91 : term
macro_rules
  | `($P ->> $Q) => `(Assertion.implies $P $Q)

@[simp]
def Assertion.iff (P Q : Assertion) : Prop :=
  forall σ, P σ ↔ Q σ
syntax term:90 "<<->>" term:91 : term
macro_rules
  | `($P <<->> $Q) => `(Assertion.iff $P $Q)

@[simp]
def Assertion.substitution (P : Assertion) (x : String) (a : Expr) : Assertion :=
  fun σ => P (σ.setOption x (a.eval σ))
syntax term " [ " ident " ↦ " term "]" : term
macro_rules
  | `($P [$x ↦ $a]) => `(Assertion.substitution $P $x $a)

instance : Coe Expr Assertion where
  coe b := fun σ => Truthy $ b.eval σ

@[simp]
def Assertion.and (P Q : Assertion) : Assertion :=
  fun σ => P σ ∧ Q σ
macro_rules
  | `($P ∧ $Q) => `(Assertion.and $P $Q)

@[simp]
def Assertion.not (P : Assertion) : Assertion :=
  fun σ => ¬ P σ
macro_rules
  | `(! $P) => `(Assertion.not $P)

@[simp]
theorem Truthy.assert_true : ∀ (b : Expr), (fun σ => Truthy (b.eval σ)) <<->> b := by
  intro b σ
  constructor <;> intro h <;> assumption
