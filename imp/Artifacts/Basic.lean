import Aesop
import Imp

example : {{fun st => st "x" > 0}}(
imp {
  x := x + 1;
}
){{fun st => st "x" > 1}} := by

sorry
