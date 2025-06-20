-- Testing the affirmative polarity of hoare triple proofs
import Aesop
import Imp
open Imp

example : {{astn x < y}}swap{{astn x >= y}} := by
  auto_hoare_pos

example : {{astn x > 0}}(imp { x := x + 1; }){{astn x > 1}} := by
  auto_hoare_pos

example : forall (n m : Int), {{ astn x = ~n <^> y = ~m }}swap{{ astn x = ~m <^> y = ~n }} := by
  auto_hoare_pos
