import Aesop
import Imp.Expr
import Imp.Stmt
import Imp.Hoare.Basic
import Imp.Hoare.Syntax

open Imp Stmt

-- set_option diagnostics true

@[simp]
theorem hoare_skip : forall P, {{P}}(imp { skip; }){{P}} := by aesop

@[simp]
theorem hoare_seq : forall P Q R c1 c2,
  {{P}}c1{{Q}} →
  {{Q}}c2{{R}} →
  {{P}}(imp { ~c1 ~c2 }){{R}} := by
  simp; intros _ _ _ _ _ h1 h2 _ _ h3 h4
  cases h4 with
  | seq h5 h6 =>
    apply h2 <;> aesop

@[simp]
theorem hoare_assign : forall P x a, {{P[x ↦ a]}}(imp { ~x := ~a; }){{P}} := by
  simp [Env.setOption]
  aesop

@[simp]
theorem hoare_consequence_pre : forall (P P' Q : Assertion) c,
  {{P'}}c{{Q}} →
  P ->> P' →
  {{P}}c{{Q}} := by aesop

@[simp]
theorem hoare_consequence_post : forall (P Q Q' : Assertion) c,
  {{P}}c{{Q'}} →
  Q' ->> Q →
  {{P}}c{{Q}} := by aesop

@[simp]
theorem hoare_consequence : forall (P P' Q Q' : Assertion) c,
  {{P'}}c{{Q'}} →
  (P ->> P') →
  (Q' ->> Q) →
  {{P}}c{{Q}} := by aesop

@[simp]
theorem hoare_if : forall P Q (b : Expr) c1 c2,
  {{ P <^> b }}c1{{Q}} →
  {{ P <^> <!>b }}c2{{Q}} →
  {{P}}(imp { if (~b) { ~c1 } else { ~c2 } }){{Q}} := by
  simp; intros _ _ _ _ _ h1 h2 _ _ h3 h4
  cases h4 with
  | ifTrue h5 =>
    aesop
  | ifFalse h5 =>
    apply (h2 _ _ h3) <;> try assumption
    apply Falsy.not_truthy
    assumption

theorem hoare_while_aux1 : forall b c σ σ',
  Truthy (b.eval σ) →
  (imp { ~c while (~b) { ~c } }) / σ ↓ σ' →
  (imp { while (~b) { ~c } }) / σ ↓ σ' := by
  intros b c σ σ' h1 h2
  cases h2 with
  | seq h3 h4 => apply (BigStep.whileTrue h1 h3 h4)

theorem hoare_while_aux : forall b c σ σ',
  Truthy (b.eval σ) →
  (imp { while (~b) { ~c } }) / σ ↓ σ' →
  c / σ ↓ σ' := by
  intros b c σ σ'' h1 h2
  cases h2 with
  | whileTrue _ h4 h5 =>
    have h6 := BigStep.whileTrue h1 h4 h5

    sorry
    -- apply (BigStep.whileTrue h1 h4 h5)
  | whileFalse h3 => aesop

@[simp]
theorem hoare_while : forall P (b : Expr) c,
  {{ P <^> b }}c{{P}} →
  {{P}}(imp { while (~b) { ~c } }){{ P <^> <!>b }} := by
  simp [ValidHoareTriple]
  intros P b c h1 σ σ'' h3 h4
  have h4_orig := h4
  -- have c_orig := imp { while (~b) { ~c } }
  cases h4 with
  | whileTrue h5 h6 h7 =>
    constructor
    . apply h1
      assumption
      assumption
      apply (hoare_while_aux b c σ σ'' h5)
      assumption
    . intros contra
      sorry
  | whileFalse h5 =>
    simp [Falsy] at h5
    constructor
    . assumption
    . simp [Truthy]; intros contra
      aesop

example : {{astn x < y}}swap{{astn x >= y}} := by
  simp [swap]
  intros _ _ h1 h2
  cases h2 with
  | seq h2_1 h2_2 =>
    cases h2_2 with
    | seq h2_2_1 h2_2_2 =>
      cases h2_1 with
      | assign h2_1_eq =>
        cases h2_2_1 with
        | assign h2_2_1_eq =>
          cases h2_2_2 with
          | assign h2_2_2_eq =>
            simp [Env.set]
            simp [Expr.eval] at h2_1_eq
            simp [Expr.eval] at h2_2_1_eq
            simp [Expr.eval] at h2_2_2_eq
            rw [h2_2_2_eq] at h2_1_eq
            simp [Env.get] at h2_1_eq
            simp [Env.get] at h2_2_1_eq
            subst h2_2_2_eq
            rw [h2_1_eq, h2_2_1_eq] at h1
            apply Value.lt_implies_le
            assumption

example : {{astn x > 0}}(imp { x := x + 1; }){{astn x > 1}} := by
  simp; intros σ σ' h1 h2
  cases h2 with
  | assign h2_eq =>
    simp [Expr.eval] at h2_eq
    simp [Env.set]
    simp [Env.get] at h2_eq
    cases h2_eq
    rw [Value.int_lt]
    simp [*]
    simp [Value.int_lt] at h1
    omega

example : forall (n m : Int), {{fun σ => σ "x" = n ∧ σ "y" = m}}swap{{fun σ => σ "x" = m ∧ σ "y" = n}} := by
  simp [swap]
  intros n m σ σ' h1 h2 h3
  cases h3 with
  | seq h3_1 h3_2 =>
    cases h3_2 with
    | seq h3_2_1 h3_2_2 =>
      cases h3_1 with
      | assign h3_1_eq =>
        cases h3_2_1 with
        | assign h3_2_1_eq =>
          cases h3_2_2 with
          | assign h3_2_2_eq =>
            simp [Env.set]
            simp [Expr.eval] at h3_1_eq
            simp [Expr.eval] at h3_2_1_eq
            simp [Expr.eval] at h3_2_2_eq
            rw [h3_2_2_eq] at h3_1_eq
            aesop
