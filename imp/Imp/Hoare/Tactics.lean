import Lean
import Aesop
import Imp.Stmt
import Imp.Expr

open Imp Stmt Expr

attribute [simp]                 -- evaluate the object language
  eval set get Value.int_lt Value.int_le

attribute [aesop safe]           -- monotone helper
  Value.lt_implies_le

open Lean Meta Elab Tactic

/--
`destructBigSteps` repeatedly performs `cases` on **every** hypothesis
whose type is the inductive judgement `BigStep …`.
-/
partial def destructBigStepsGo : TacticM Unit := do
  let goal ← getMainGoal
  goal.withContext do
    let ctx ← getLCtx
    let mut found := false
    for h in ctx do
      unless h.isAuxDecl || h.isImplementationDetail do
        let ty ← instantiateMVars h.type
        let constName := ty.getAppFn.constName?
        match constName with
        | some ``BigStep =>
            found := true
            evalTactic (← `(tactic| cases $(mkIdent h.userName):ident))
            destructBigStepsGo
            return
        | _ => pure ()
    if !found then
      pure ()

elab "destructBigSteps" : tactic => destructBigStepsGo

/--
`hoare` removes 100% of the hand‑written routine:

1. `intro`s until the goal is no longer a `∀`/`→`;
2. cracks open any `BigStep` derivation with `destructBigSteps`;
3. evaluates the concrete program with `simp`;
4. lets `aesop` polish off propositional crumbs;
5. and (optionally) finishes linear arithmetic with `omega`.
-/
elab "hoare_pos" : tactic => do
  evalTactic (← `(tactic| repeat intro))
  evalTactic (← `(tactic| destructBigSteps))
  evalTactic (← `(tactic| try simp at *))
  evalTactic (← `(tactic| try (simp [Env.get, Env.set] at *)))
  evalTactic (← `(tactic| try (simp [Expr.eval, Expr.BinOp.apply] at *)))
  evalTactic (← `(tactic| try (apply Value.lt_implies_le; assumption)))
  evalTactic (← `(tactic| try aesop))
  evalTactic (← `(tactic| try omega))
