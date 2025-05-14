import Aesop
import Imp
open Imp

example : {{fun st => st "x" > st "y"}}(
imp {
  x := y;
}
){{fun st => st "x" <= st "y"}} := by

simp
intros σ σ' h1 h2
cases h2 with
| assign h2_eq =>
  simp [Env.set]
  simp [Expr.eval, Env.get] at h2_eq
  subst h2_eq
  apply Int.le_refl
