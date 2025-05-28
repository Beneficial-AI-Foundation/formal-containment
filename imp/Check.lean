import Artifacts

open Lean Elab Command

unsafe def checkSorryInTerm (termName : Name) : CommandElabM String := do
  let env ← getEnv
  match env.find? termName with
  | none => return "Bug: Term {termName} not found"
  | some info => do
    let exp := info.value?
    match exp with
    | none => return "Bug: Term has no expression"
    | some e =>
      if e.hasSorry then
        return "<HOARE_TRIPLE_TERM_HAS_SORRY>"
      else
        return "<HOARE_TRIPLE_TERM_PROVEN_OK>"

-- This runs the check and stores the result
#eval checkSorryInTerm `my_hoare_triple

def ctx : Context := { fileName := "Check.lean", fileMap := default, snap? := none, cancelTk? := none}

def main : IO UInt32 := do
  return 0
