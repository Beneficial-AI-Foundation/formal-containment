import Aesop
import Imp
open Imp

example : {{fun st => st "x" > st "y"}}(
imp {
  while (x > y) {
    x := x - 1;
  }
}
){{fun st => st "x" <= st "y"}} := by
apply hoare_consequence
. apply hoare_while
  aesop
. aesop
. simp; intros σ h
  have h0 := Truthy.assert_true (expr { y < x })
  simp [Assertion.iff] at h0
  simp [Truthy] at h
