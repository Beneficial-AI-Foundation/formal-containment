import Lean
import Lean.Meta
import Lean.Elab
import Lean.Elab.Tactic
import Imp.Expr
import Imp.Stmt
import Imp.Hoare.Basic

open Lean
open Lean.Meta
open Lean.Elab
open Lean.Elab.Tactic
-- open Imp Stmt

/-- Find a local hypothesis that matches a given predicate -/
def findLocalHyp? (predType : Expr) : MetaM (Option FVarId) := do
  let ctx ← getLCtx
  for ldecl in ctx do
    if ldecl.isImplementationDetail then continue
    try
      let ldeclType ← instantiateMVars ldecl.type
      if (← isDefEq predType ldeclType) || (← isExprDefEqAux predType ldeclType) then
        return some ldecl.fvarId
    catch _ =>
      pure ()
  return none

/-- Extract the statement from an Executes expression -/
def extractStmtFromExecExpr (e : Expr) : MetaM (Option Expr) := do
  match e with
  | Expr.app (Expr.app (Expr.app _ stmt) _) _ =>
      return some stmt
  | _ =>
      return none

/-- A tactic for symbolic execution of programs in Hoare proofs -/
def symExecStep : TacticM Unit := do
  let goal ← getMainGoal
  try
    goal.withContext do
      -- Look for an execution hypothesis
      let stmtExecConst ← mkConstM `Executes
      let execHyp ← findLocalHyp? (← mkApp2 stmtExecConst (mkConst `_) (mkConst `_))

      if let some hypFVarId := execHyp then
        let hypExpr ← getFVarLocalDecl hypFVarId
        let hypType ← inferType hypExpr.toExpr

        -- Extract statement using our helper function
        if let some stmt ← extractStmtFromExecExpr hypType then
          let stmtType ← inferType stmt
        -- Match on statement type
          if (← isDefEq stmtType (← mkConstM `Stmt.skip)) then
            -- Handle skip
            evalTactic (← `(tactic| cases $(mkIdent hypFVarId.name)))

          else if (← isDefEq stmtType (← mkConstM `Stmt.assign)) then
            -- Handle assignment
            evalTactic (← `(tactic|
              cases $(mkIdent hypFVarId.name) with
              | assign h_eq => rw [h_eq]; simp [Env.set, Env.get]; try assumption
            ))

          else if (← isDefEq stmtType (← mkConstM `Stmt.seq)) then
            -- Handle sequence - using a more direct approach
            evalTactic (← `(tactic|
              cases $(mkIdent hypFVarId.name) with
              | seq h1 h2 =>
                  try {
                    cases h1;
                    cases h2;
                    simp [Env.set, Env.get];
                    try assumption
                  }
            ))

          else if (← isDefEq stmtType (← mkConstM `Stmt.ite)) then
            -- Handle if statement
            evalTactic (← `(tactic|
              cases $(mkIdent hypFVarId.name) with
              | ifTrue h => apply h1; constructor; assumption; assumption
              | ifFalse h => apply h2; constructor; assumption; simp [Assertion.not]; apply Falsy.not_truthy; assumption
            ))

          else
            throwError "Unsupported statement type in execution hypothesis"
        else
          throwError "Could not match execution hypothesis type"
      else
        throwError "No execution hypothesis found"
  catch err =>
    trace `Tactic.symExec.debug (fun () => err.toMessageData)
    throwError "Failed to perform symbolic execution step: {err.toMessageData}"

/-- Create a custom focusing tactic similar to solve1 -/
def focusAndSolve (tac : TacticM Unit) : TacticM Unit := do
  let gs ← getGoals
  if gs.isEmpty then
    throwError "no goals to be solved"
  let g := gs.head!
  setGoals [g]
  tac
  let gs' ← getGoals
  if gs'.isEmpty.not then
    throwError "failed to solve the goal"
  setGoals gs.tail

/-- Helper tactic for recursive symbolic execution -/
syntax "sym_exec_seq" : tactic

/-- Main symbolic execution tactic -/
syntax "sym_exec" : tactic

macro_rules
  | `(tactic| sym_exec_seq) => `(tactic|
      repeat
        (cases h1 <;> cases h2 <;> simp [Env.set, Env.get] <;> try assumption))

macro_rules
  | `(tactic| sym_exec) => `(tactic| repeat symExecStep)
