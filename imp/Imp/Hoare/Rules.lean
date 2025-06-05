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
  intros _ _ _ _ _ h1 h2
  cases h2 with
  | assign h2_eq =>
    rw [h2_eq] at h1
    simp at h1
    assumption

@[simp]
theorem hoare_consequence_pre : forall (P P' Q : Assertion) c,
  {{P'}}c{{Q}} →
  P ->> P' →
  {{P}}c{{Q}} := by
  simp
  intros _ _ _ _ h1 h2 _ _ h3 h4
  apply (h1 _ _ (h2 _ h3))
  assumption

@[simp]
theorem hoare_consequence_post : forall (P Q Q' : Assertion) c,
  {{P}}c{{Q'}} →
  Q' ->> Q →
  {{P}}c{{Q}} := by
  simp
  intros _ _ _ _ h1 h2 _ _ h3 h4
  apply h2
  apply (h1 _ _ h3)
  assumption

@[simp]
theorem hoare_consequence : forall (P P' Q Q' : Assertion) c,
  {{P'}}c{{Q'}} →
  (P ->> P') →
  (Q' ->> Q) →
  {{P}}c{{Q}} := by
  simp
  intros _ _ _ _ _ h1 h2 h3 _ _ h4 h5
  apply h3
  specialize (h2 _ h4)
  apply (h1 _ _ h2)
  assumption

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

theorem hoare_while_aux_left : forall b c σ σ',
  Truthy (b.eval σ) →
  (imp { while (~b) { ~c } }) / σ ↓ σ' →
  c / σ ↓ σ' := by
  intros b c σ σ'' h1 h2
  cases h2 with
  | whileTrue _ h3 h4 =>
    sorry
  | whileFalse h3 => aesop

theorem hoare_while_aux_right : forall b c σ σ',
  Truthy (b.eval σ) →
  Truthy (b.eval σ') →
  (imp { while (~b) { ~c } }) / σ ↓ σ' →
  False := by
  intros b c σ σ' h1 h2 h3
  cases h3 with
  | whileTrue _ h4 h5 =>
    sorry
  | whileFalse h4 => aesop

@[simp]
theorem hoare_while : forall P (b : Expr) c,
  {{ P <^> b }}c{{P}} →
  {{P}}(imp { while (~b) { ~c } }){{ P <^> <!>b }} := by
  simp
  intros P b c h1 σ σ'' h3 h4
  have h4_orig := h4
  cases h4 with
  | whileTrue h5 h6 h7 =>
    constructor
    . apply h1
      assumption
      assumption
      apply (hoare_while_aux_left b c σ σ'' h5)
      assumption
    . intros contra
      apply (hoare_while_aux_right b c σ σ'' h5 contra)
      assumption
  | whileFalse h5 =>
    simp [Falsy] at h5
    constructor
    . assumption
    . simp [Truthy]; intros contra
      aesop
