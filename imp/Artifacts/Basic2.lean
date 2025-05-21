import Aesop
import Imp
open Imp


example : forall (n m : Int),
{{astn x = n <^> y = m}}(
imp {
  z := x;
  x := y;
  y := z;
}
){{astn x = m <^> y = n}} := by
intros n m
simp
intros σ σ' h_x h_y h_prog
cases h_prog with
| seq h_z h_rest =>
  cases h_z with
  | assign h_z_eq =>
    cases h_rest with
    | seq h_x h_y =>
      cases h_x with
      | assign h_x_eq =>
        cases h_y with
        | assign h_y_eq =>
          simp [Env.set] at *
          simp [Expr.eval] at *
          simp [Env.get] at *
          constructor
          · rw [h_x_eq]
            exact h_y
          · rw [h_y_eq]
            rw [h_z_eq]
            exact h_x
