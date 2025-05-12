import Imp.Expr.Eval
import Imp.Expr.Syntax
import Imp.Stmt.BigStep
import Imp.Stmt.Basic
import Imp.Hoare.Basic

open Imp Stmt

theorem hoare_skip : forall P, {{P}}(imp { skip; }){{P}} := by
  intro P
  simp [ValidHoareTriple]
  intros _ _ _ h2
  cases h2; assumption

theorem hoare_seq : forall P Q R c1 c2, {{P}}c1{{Q}} -> {{Q}}c2{{R}} -> {{P}}(imp { ~c1 ~c2 }){{R}} := by
  intro P Q R c1 c2
  simp [ValidHoareTriple]
  intros h1 h2 _ _ hP h3
  cases h3 with
  | seq h3 h4 =>
    apply h2
    apply h1
    apply hP
    apply h3
    apply h4

theorem hoare_assign : forall P x a, {{P[x ↦ a]}}(imp { ~x := ~a; }){{P}} := by
  intros P x a
  simp [ValidHoareTriple]
  intros σ σ' h1 h2
  simp [assertionSubstitution, Env.setOption] at h1
  cases h2 with
  | assign h2_eq =>
    rw [h2_eq] at h1
    simp at h1
    assumption

theorem hoare_consequence_pre : forall (P P' Q : Assertion) c,
  {{P'}}c{{Q}} →
  P ->> P' →
  {{P}}c{{Q}} := by
  simp [ValidHoareTriple, assertImplies]
  intros P P' Q c h1 h2 σ σ' h3 h4
  apply (h1 σ σ')
  apply (h2 σ h3)
  assumption

theorem hoare_consequence_post : forall (P Q Q' : Assertion) c,
  {{P}}c{{Q'}} →
  Q' ->> Q →
  {{P}}c{{Q}} := by
  simp [ValidHoareTriple, assertImplies]
  intros P Q Q' c h1 h2 σ σ' h3 h4
  apply (h2 σ')
  apply (h1 σ σ') <;> assumption

theorem hoare_consequence : forall (P P' Q Q' : Assertion) c,
  {{P'}}c{{Q'}} →
  (P ->> P') →
  (Q' ->> Q) →
  {{P}}c{{Q}} := by
  simp [ValidHoareTriple, assertImplies]
  intros P P' Q Q' c h1 h2 h3 σ σ' h4 h5
  apply (hoare_consequence_pre P P' _ c)
  apply (hoare_consequence_post P' Q Q' c)
  apply h1 <;> simp [assertImplies]
  intros σ0 h6
  apply (h3 σ0)
  assumption
  assumption
  assumption
  assumption

theorem hoare_if : forall P Q (b : Expr) c1 c2,
  {{(P ∧ b)}}c1{{Q}} →
  {{(P ∧ !b)}}c2{{Q}} →
  {{P}}(imp { if (~b) { ~c1 } else { ~c2 } }){{Q}} := by
  simp [ValidHoareTriple]
  intros P Q b c1 c2 h1 h2 σ σ' h3 h4
  cases h4 with
  | ifTrue h5 =>
    apply (h1 σ σ')
    simp [Assertion.and]
    constructor <;> assumption
    assumption
  | ifFalse h5 =>
    apply (h2 σ σ')
    simp [Assertion.and]
    constructor
    . assumption
    . simp [Assertion.not]
      apply Falsy.not_truthy
      assumption
    . assumption

theorem hoare_while : forall P (b : Expr) c,
  {{(P ∧ b)}}c{{P}} →
  {{P}}(imp { while (~b) { ~c } }){{(P ∧ !b)}} := by
  simp [ValidHoareTriple]
  intros P b c h1 σ σ'' h3 h4
  have h4_orig := h4
  cases h4 with
  | whileTrue h5 h6 h7 =>
    constructor
    . apply h1
      constructor <;> assumption
      sorry
    . simp [Assertion.not]
      intros contra
      sorry
  | whileFalse h5 =>
    constructor
    . assumption
    . simp [Assertion.not]
      apply Falsy.not_truthy
      assumption
