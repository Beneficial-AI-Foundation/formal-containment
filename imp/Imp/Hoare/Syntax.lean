import Lean
import Imp.Hoare.Basic

open Lean Elab Meta Term

declare_syntax_cat assertionTerm
syntax ident : assertionTerm
syntax num : assertionTerm
syntax "~" term:max : assertionTerm

declare_syntax_cat assertion
syntax ident "=" num : assertion
syntax num "=" ident : assertion
syntax ident "=" ident : assertion
-- syntax term "=" ident : assertion
syntax ident "!=" num : assertion
syntax num "!=" ident : assertion
syntax ident "!=" ident : assertion
syntax ident "<" num : assertion
syntax num "<" ident : assertion
syntax ident "<" ident : assertion
syntax ident ">" num : assertion
syntax num ">" ident : assertion
syntax ident ">" ident : assertion
syntax ident "<=" num : assertion
syntax num "<=" ident : assertion
syntax ident "<=" ident : assertion
syntax ident ">=" num : assertion
syntax num ">=" ident : assertion
syntax ident ">=" ident : assertion
syntax assertion " <^> " assertion : assertion
syntax assertion " <> " assertion : assertion
syntax "<!>" assertion : assertion
syntax assertion " ->> " assertion : assertion
syntax assertion " <<->> " assertion : assertion

@[simp] def valValEq (n m : Int) : Assertion := fun _ => n = m
@[simp] def valValNe (n m : Int) : Assertion := fun _ => n ≠ m
@[simp] def valValLt (n m : Int) : Assertion := fun _ => n < m
@[simp] def valValGt (n m : Int) : Assertion := fun _ => n > m
@[simp] def valValLe (n m : Int) : Assertion := fun _ => n ≤ m
@[simp] def valValGe (n m : Int) : Assertion := fun _ => n ≥ m
@[simp] def strValEq (x : String) (n : Int) : Assertion := fun σ => σ x = n
@[simp] def strValNe (x : String) (n : Int) : Assertion := fun σ => σ x ≠ n
@[simp] def strValLt (x : String) (n : Int) : Assertion := fun σ => σ x < n
@[simp] def strValGt (x : String) (n : Int) : Assertion := fun σ => σ x > n
@[simp] def strValLe (x : String) (n : Int) : Assertion := fun σ => σ x ≤ n
@[simp] def strValGe (x : String) (n : Int) : Assertion := fun σ => σ x ≥ n
@[simp] def valStrEq (n : Int) (x : String) : Assertion := fun σ => n = σ x
@[simp] def valStrNe (n : Int) (x : String) : Assertion := fun σ => n ≠ σ x
@[simp] def valStrLt (n : Int) (x : String) : Assertion := fun σ => n < σ x
@[simp] def valStrGt (n : Int) (x : String) : Assertion := fun σ => n > σ x
@[simp] def valStrLe (n : Int) (x : String) : Assertion := fun σ => n ≤ σ x
@[simp] def valStrGe (n : Int) (x : String) : Assertion := fun σ => n ≥ σ x
@[simp] def strStrEq (x y : String) : Assertion := fun σ => σ x = σ y
@[simp] def strStrNe (x y : String) : Assertion := fun σ => σ x ≠ σ y
@[simp] def strStrLt (x y : String) : Assertion := fun σ => σ x < σ y
@[simp] def strStrGt (x y : String) : Assertion := fun σ => σ x > σ y
@[simp] def strStrLe (x y : String) : Assertion := fun σ => σ x ≤ σ y
@[simp] def strStrGe (x y : String) : Assertion := fun σ => σ x ≥ σ y
partial def elabAssertionLit : Syntax → MetaM Expr
  -- Eq
  | `(assertion| $x:ident = $n:num) => do
    let x <- pure $ mkStrLit x.getId.toString
    let n <- pure $ mkIntLit n.getNat
    mkAppM ``strValEq  #[x, n]
  | `(assertion| $n:num = $x:ident) => do
    let x <- pure $ mkStrLit x.getId.toString
    let n <- pure $ mkIntLit n.getNat
    mkAppM ``strValEq  #[x, n]
  | `(assertion| $x:ident = $y:ident) => do
    let x <- pure $ mkStrLit x.getId.toString
    let y <- pure $ mkStrLit y.getId.toString
    mkAppM ``strStrEq  #[x, y]
  -- Neq
  | `(assertion| $x:ident != $n:num) => do
    let x <- pure $ mkStrLit x.getId.toString
    let n <- pure $ mkIntLit n.getNat
    mkAppM ``strValNe  #[x, n]
  | `(assertion| $n:num != $x:ident) => do
    let n <- pure $ mkIntLit n.getNat
    let localDecls ← getLCtx
    match localDecls.findFromUserName? x.getId with
    | some decl =>
      let x <- pure $ decl.toExpr
      mkAppM ``valValNe #[x, n]
    | none =>
      let x <- pure $ mkStrLit x.getId.toString
      mkAppM ``strValNe  #[x, n]
  | `(assertion| $x:ident != $y:ident) => do
    let x <- pure $ mkStrLit x.getId.toString
    let y <- pure $ mkStrLit y.getId.toString
    mkAppM ``strStrNe  #[x, y]
  -- LT
  | `(assertion| $x:ident < $n:num) => do
    let x <- pure $ mkStrLit x.getId.toString
    let n <- pure $ mkIntLit n.getNat
    mkAppM ``strValLt  #[x, n]
  | `(assertion| $n:num < $x:ident) => do
    let x <- pure $ mkStrLit x.getId.toString
    let n <- pure $ mkIntLit n.getNat
    mkAppM ``strValLt  #[x, n]
  | `(assertion| $x:ident < $y:ident) => do
    let x <- pure $ mkStrLit x.getId.toString
    let y <- pure $ mkStrLit y.getId.toString
    mkAppM ``strStrLt  #[x, y]
  -- GT
  | `(assertion| $x:ident > $n:num) => do
    let x <- pure $ mkStrLit x.getId.toString
    let n <- pure $ mkIntLit n.getNat
    mkAppM ``strValGt  #[x, n]
  | `(assertion| $n:num > $x:ident) => do
    let x <- pure $ mkStrLit x.getId.toString
    let n <- pure $ mkIntLit n.getNat
    mkAppM ``strValGt  #[x, n]
  |`(assertion| $x:ident > $y:ident) => do
    let x <- pure $ mkStrLit x.getId.toString
    let y <- pure $ mkStrLit y.getId.toString
    mkAppM ``strStrGt  #[x, y]
  -- LE
  | `(assertion| $x:ident <= $n:num) => do
    let x <- pure $ mkStrLit x.getId.toString
    let n <- pure $ mkIntLit n.getNat
    mkAppM ``strValLe  #[x, n]
  | `(assertion| $n:num <= $x:ident) => do
    let x <- pure $ mkStrLit x.getId.toString
    let n <- pure $ mkIntLit n.getNat
    mkAppM ``strValLe  #[x, n]
  | `(assertion| $x:ident <= $y:ident) => do
    let x <- pure $ mkStrLit x.getId.toString
    let y <- pure $ mkStrLit y.getId.toString
    mkAppM ``strStrLe  #[x, y]
  -- GE
  | `(assertion| $x:ident >= $n:num) => do
    let x <- pure $ mkStrLit x.getId.toString
    let n <- pure $ mkIntLit n.getNat
    mkAppM ``strValGe  #[x, n]
  | `(assertion| $n:num >= $x:ident) => do
    let x <- pure $ mkStrLit x.getId.toString
    let n <- pure $ mkIntLit n.getNat
    mkAppM ``strValGe  #[x, n]
  | `(assertion| $x:ident >= $y:ident) => do
    let x <- pure $ mkStrLit x.getId.toString
    let y <- pure $ mkStrLit y.getId.toString
    mkAppM ``strStrGe  #[x, y]
  -- Conjunction
  | `(assertion| $a:assertion <^> $b:assertion) => do
        let a <- elabAssertionLit a
        let b <- elabAssertionLit b
        mkAppM ``Assertion.and #[a, b]
  -- Disjunction
  | `(assertion| $a:assertion <> $b:assertion) => do
        let a <- elabAssertionLit a
        let b <- elabAssertionLit b
        mkAppM ``Assertion.or #[a, b]
  -- Negation
  | `(assertion| <!> $a:assertion) => do
        let a <- elabAssertionLit a
        mkAppM ``Assertion.not #[a]
  -- Implication
  | `(assertion| $a:assertion ->> $b:assertion) => do
        let a <- elabAssertionLit a
        let b <- elabAssertionLit b
        mkAppM ``Assertion.implies #[a, b]
  -- Biimplication
  | `(assertion| $a:assertion <<->> $b:assertion) => do
        let a <- elabAssertionLit a
        let b <- elabAssertionLit b
        mkAppM ``Assertion.iff #[a, b]
  | _ => throwUnsupportedSyntax

elab "astn " a:assertion : term => elabAssertionLit a

/--
info: (strStrLe "y" "z").and (strValGt "x" 5) : Assertion
-/
#guard_msgs in
#check astn y <= z <^> x > 5

#check forall (n : Int), astn 4 != n ->> x < 10

variable (c : Imp.Stmt)
#check forall (n : Int), {{ astn 0 != x }}c{{ astn x < y }}
