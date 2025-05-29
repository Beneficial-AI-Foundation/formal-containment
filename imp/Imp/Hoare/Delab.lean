import Imp.Hoare.Basic
import Imp.Hoare.Syntax
import Lean.PrettyPrinter.Delaborator.Basic

namespace Imp.Hoare.Delab

open Imp.Hoare
open Imp.Expr.Delab
open Lean PrettyPrinter Delaborator SubExpr

-- Helper function to extract string literals
def getStringLit (e : Lean.Expr) : Option String :=
  match e with
  | .lit (.strVal s) => some s
  | _ => none

-- Helper function to extract integer literals
def getIntLit (e : Lean.Expr) : Option Int :=
  match e with
  | .lit (.natVal n) => some (Int.ofNat n)
  | _ => none

-- Helper function to create identifier syntax from string
def mkIdentFromString (s : String) : TSyntax `ident :=
  mkIdent (Name.mkSimple s)

-- Helper function to create number syntax from integer
def mkNumFromInt (n : Int) : TSyntax `num :=
  Syntax.mkNumLit (toString n.natAbs)

-- Delaborators for comparison operations

@[delab app.strValEq]
def delabStrValEq : Delab := do
  let e ← getExpr
  guard <| e.getAppNumArgs == 2
  let args := e.getAppArgs
  let some x := getStringLit args[0]! | failure
  let some n := getIntLit args[1]! | failure
  `(astn $(mkIdentFromString x):ident = $(mkNumFromInt n):num)

@[delab app.valStrEq]
def delabValStrEq : Delab := do
  let e ← getExpr
  guard <| e.getAppNumArgs == 2
  let args := e.getAppArgs
  let some n := getIntLit args[0]! | failure
  let some x := getStringLit args[1]! | failure
  `(astn $(mkNumFromInt n):num = $(mkIdentFromString x):ident)

@[delab app.strStrEq]
def delabStrStrEq : Delab := do
  let e ← getExpr
  guard <| e.getAppNumArgs == 2
  let args := e.getAppArgs
  let some x := getStringLit args[0]! | failure
  let some y := getStringLit args[1]! | failure
  `(astn $(mkIdentFromString x):ident = $(mkIdentFromString y):ident)

@[delab app.valValEq]
def delabValValEq : Delab := do
  let e ← getExpr
  guard <| e.getAppNumArgs == 2
  let x ← withAppFn $ withAppArg delab
  let y ← withAppArg delab
  `(astn ~$x:term = ~$y:term)

-- Delaborators for inequality

@[delab app.strValNe]
def delabStrValNe : Delab := do
  let e ← getExpr
  guard <| e.getAppNumArgs == 2
  let args := e.getAppArgs
  let some x := getStringLit args[0]! | failure
  let some n := getIntLit args[1]! | failure
  `(astn $(mkIdentFromString x):ident != $(mkNumFromInt n):num)

@[delab app.valStrNe]
def delabValStrNe : Delab := do
  let e ← getExpr
  guard <| e.getAppNumArgs == 2
  let args := e.getAppArgs
  let some n := getIntLit args[0]! | failure
  let some x := getStringLit args[1]! | failure
  `(astn $(mkNumFromInt n):num != $(mkIdentFromString x):ident)

@[delab app.strStrNe]
def delabStrStrNe : Delab := do
  let e ← getExpr
  guard <| e.getAppNumArgs == 2
  let args := e.getAppArgs
  let some x := getStringLit args[0]! | failure
  let some y := getStringLit args[1]! | failure
  `(astn $(mkIdentFromString x):ident != $(mkIdentFromString y):ident)

@[delab app.valValNe]
def delabValValNe : Delab := do
  let e ← getExpr
  guard <| e.getAppNumArgs == 2
  let x ← withAppFn $ withAppArg delab
  let y ← withAppArg delab
  `(astn ~$x:term != ~$y:term)

-- Delaborators for less than

@[delab app.strValLt]
def delabStrValLt : Delab := do
  let e ← getExpr
  guard <| e.getAppNumArgs == 2
  let args := e.getAppArgs
  let some x := getStringLit args[0]! | failure
  let some n := getIntLit args[1]! | failure
  `(astn $(mkIdentFromString x):ident < $(mkNumFromInt n):num)

@[delab app.valStrLt]
def delabValStrLt : Delab := do
  let e ← getExpr
  guard <| e.getAppNumArgs == 2
  let args := e.getAppArgs
  let some n := getIntLit args[0]! | failure
  let some x := getStringLit args[1]! | failure
  `(astn $(mkNumFromInt n):num < $(mkIdentFromString x):ident)

@[delab app.strStrLt]
def delabStrStrLt : Delab := do
  let e ← getExpr
  guard <| e.getAppNumArgs == 2
  let args := e.getAppArgs
  let some x := getStringLit args[0]! | failure
  let some y := getStringLit args[1]! | failure
  `(astn $(mkIdentFromString x):ident < $(mkIdentFromString y):ident)

@[delab app.valValLt]
def delabValValLt : Delab := do
  let e ← getExpr
  guard <| e.getAppNumArgs == 2
  let x ← withAppFn $ withAppArg delab
  let y ← withAppArg delab
  `(astn ~$x:term < ~$y:term)

-- Delaborators for greater than

@[delab app.strValGt]
def delabStrValGt : Delab := do
  let e ← getExpr
  guard <| e.getAppNumArgs == 2
  let args := e.getAppArgs
  let some x := getStringLit args[0]! | failure
  let some n := getIntLit args[1]! | failure
  `(astn $(mkIdentFromString x):ident > $(mkNumFromInt n):num)

@[delab app.valStrGt]
def delabValStrGt : Delab := do
  let e ← getExpr
  guard <| e.getAppNumArgs == 2
  let args := e.getAppArgs
  let some n := getIntLit args[0]! | failure
  let some x := getStringLit args[1]! | failure
  `(astn $(mkNumFromInt n):num > $(mkIdentFromString x):ident)

@[delab app.strStrGt]
def delabStrStrGt : Delab := do
  let e ← getExpr
  guard <| e.getAppNumArgs == 2
  let args := e.getAppArgs
  let some x := getStringLit args[0]! | failure
  let some y := getStringLit args[1]! | failure
  `(astn $(mkIdentFromString x):ident > $(mkIdentFromString y):ident)

@[delab app.valValGt]
def delabValValGt : Delab := do
  let e ← getExpr
  guard <| e.getAppNumArgs == 2
  let x ← withAppFn $ withAppArg delab
  let y ← withAppArg delab
  `(astn ~$x:term > ~$y:term)

-- Delaborators for less than or equal

@[delab app.strValLe]
def delabStrValLe : Delab := do
  let e ← getExpr
  guard <| e.getAppNumArgs == 2
  let args := e.getAppArgs
  let some x := getStringLit args[0]! | failure
  let some n := getIntLit args[1]! | failure
  `(astn $(mkIdentFromString x):ident <= $(mkNumFromInt n):num)

@[delab app.valStrLe]
def delabValStrLe : Delab := do
  let e ← getExpr
  guard <| e.getAppNumArgs == 2
  let args := e.getAppArgs
  let some n := getIntLit args[0]! | failure
  let some x := getStringLit args[1]! | failure
  `(astn $(mkNumFromInt n):num <= $(mkIdentFromString x):ident)

@[delab app.strStrLe]
def delabStrStrLe : Delab := do
  let e ← getExpr
  guard <| e.getAppNumArgs == 2
  let args := e.getAppArgs
  let some x := getStringLit args[0]! | failure
  let some y := getStringLit args[1]! | failure
  `(astn $(mkIdentFromString x):ident <= $(mkIdentFromString y):ident)

@[delab app.valValLe]
def delabValValLe : Delab := do
  let e ← getExpr
  guard <| e.getAppNumArgs == 2
  let x ← withAppFn $ withAppArg delab
  let y ← withAppArg delab
  `(astn ~$x:term <= ~$y:term)

-- Delaborators for greater than or equal

@[delab app.strValGe]
def delabStrValGe : Delab := do
  let e ← getExpr
  guard <| e.getAppNumArgs == 2
  let args := e.getAppArgs
  let some x := getStringLit args[0]! | failure
  let some n := getIntLit args[1]! | failure
  `(astn $(mkIdentFromString x):ident >= $(mkNumFromInt n):num)

@[delab app.valStrGe]
def delabValStrGe : Delab := do
  let e ← getExpr
  guard <| e.getAppNumArgs == 2
  let args := e.getAppArgs
  let some n := getIntLit args[0]! | failure
  let some x := getStringLit args[1]! | failure
  `(astn $(mkNumFromInt n):num >= $(mkIdentFromString x):ident)

@[delab app.strStrGe]
def delabStrStrGe : Delab := do
  let e ← getExpr
  guard <| e.getAppNumArgs == 2
  let args := e.getAppArgs
  let some x := getStringLit args[0]! | failure
  let some y := getStringLit args[1]! | failure
  `(astn $(mkIdentFromString x):ident >= $(mkIdentFromString y):ident)

@[delab app.valValGe]
def delabValValGe : Delab := do
  let e ← getExpr
  guard <| e.getAppNumArgs == 2
  let x ← withAppFn $ withAppArg delab
  let y ← withAppArg delab
  `(astn ~$x:term >= ~$y:term)


-- Delaborators for logical operations

@[delab app.Assertion.and]
def delabAssertionAnd : Delab := do
  let e ← getExpr
  guard <| e.getAppNumArgs == 2
  let a ← withAppFn $ withAppArg delab
  let b ← withAppArg delab
  -- Handle syntax conversion properly
  match a, b with
    | `(astn $aInner:assertion), `(astn $bInner:assertion) =>
      `(astn $aInner:assertion <^> $bInner:assertion)
    | _, _ => failure

@[delab app.Assertion.or]
def delabAssertionOr : Delab := do
  let e ← getExpr
  guard <| e.getAppNumArgs == 2
  let a ← withAppFn $ withAppArg delab
  let b ← withAppArg delab
  -- Handle syntax conversion properly
  match a, b with
    | `(astn $aInner:assertion), `(astn $bInner:assertion) =>
      `(astn $aInner:assertion <> $bInner:assertion)
    | _, _ => failure

@[delab app.Assertion.not]
def delabAssertionNot : Delab := do
  let e ← getExpr
  guard <| e.getAppNumArgs == 1
  withAppArg do
    let a ← delab
    -- Remove the outer "astn" wrapper if present
    match a with
      | `(astn $inner) => `(astn <!> $inner:assertion)
      | _ => failure


@[delab app.Assertion.implies]
def delabAssertionImplies : Delab := do
  let e ← getExpr
  guard <| e.getAppNumArgs == 2
  let a ← withAppFn $ withAppArg delab
  let b ← withAppArg delab
  -- Handle syntax conversion properly
  match a, b with
    | `(astn $aInner:assertion), `(astn $bInner:assertion) =>
      `(astn $aInner:assertion ->> $bInner:assertion)
    | _, _ => failure

@[delab app.Assertion.iff]
def delabAssertionIff : Delab := do
  let e ← getExpr
  guard <| e.getAppNumArgs == 2
  let a ← withAppFn $ withAppArg delab
  let b ← withAppArg delab
  -- Handle syntax conversion properly
  match a, b with
    | `(astn $aInner:assertion), `(astn $bInner:assertion) =>
      `(astn $aInner:assertion <<->> $bInner:assertion)
    | _, _ => failure

-- #check astn y <= z <^> x > 5
-- #check forall (n : Int), astn x = ~n ->> x < 10
