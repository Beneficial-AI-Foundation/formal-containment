-- Testing the affirmative polarity of hoare triple proofs
import Aesop
import Imp
open Imp

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

example : forall (n m : Int), {{ astn x = ~n <^> y = ~m }}swap{{ astn x = ~m <^> y = ~n }} := by
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
            aesop
