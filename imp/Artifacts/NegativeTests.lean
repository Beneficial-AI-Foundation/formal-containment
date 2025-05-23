-- Testing the refutative polarity of hoare triple proofs
import Aesop
import Imp
open Imp

example : ¬ {{astn x > 0}}(imp { x := x - 1; }){{astn x > 1}} := by
  simp
  exists (Env.init (Value.int (-1))).set "x" (Value.int 1)
  simp [Env.set]
  constructor
  . rw [Value.int_lt]
    simp
  . sorry
