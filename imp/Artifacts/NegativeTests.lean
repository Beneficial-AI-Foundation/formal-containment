-- Testing the refutative polarity of hoare triple proofs
import Aesop
import Imp
open Imp

example : {{astn x > 0}}(imp { x := x - 1; }){{astn x > 1}} → False := by
  intros contra
  simp at contra
  specialize (contra (Env.init (Value.int (-1)) |>.set "x" (Value.int 1)) (Env.init (Value.int (-1)) |>.set "x" (Value.int 1) |>.set "x" (Value.int 0)))
  rw [Value.int_lt] at contra
  simp at contra
  simp [Env.set] at contra
  rw [Value.int_lt] at contra
  simp at contra
  apply contra
  apply (@Stmt.BigStep.assign (x := "x") (v := Value.int 0))
  simp [Expr.eval]
  aesop
