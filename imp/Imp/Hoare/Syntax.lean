import Lean
import Imp.Hoare.Basic

open Lean Elab Meta

declare_syntax_cat assertion
syntax ident "=" num : assertion
syntax num "=" ident : assertion
syntax ident "=" ident : assertion
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
syntax "!" assertion : assertion
syntax assertion " ->> " assertion : assertion
syntax assertion " <<->> " assertion : assertion

@[simp] def strValEq (x : String) (n : Int) : Assertion := fun σ => σ x = n
@[simp] def strValNe (x : String) (n : Int) : Assertion := fun σ => σ x ≠ n
@[simp] def strValLt (x : String) (n : Int) : Assertion := fun σ => σ x < n
@[simp] def strValGt (x : String) (n : Int) : Assertion := fun σ => σ x > n
@[simp] def strValLe (x : String) (n : Int) : Assertion := fun σ => σ x ≤ n
@[simp] def strValGe (x : String) (n : Int) : Assertion := fun σ => σ x ≥ n
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
    let x <- pure $ mkStrLit x.getId.toString
    let n <- pure $ mkIntLit n.getNat
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
  -- Negation
  | `(assertion| ! $a:assertion) => do
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
