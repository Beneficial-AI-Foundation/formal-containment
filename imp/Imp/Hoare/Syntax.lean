import Imp.Hoare.Basic

open Lean Elab Meta Term

declare_syntax_cat _assertion_term
syntax ident : _assertion_term
syntax num : _assertion_term
syntax "~" term:max : _assertion_term

declare_syntax_cat assertion
syntax _assertion_term "=" _assertion_term : assertion
syntax _assertion_term "!=" _assertion_term : assertion
syntax _assertion_term "<" _assertion_term : assertion
syntax _assertion_term ">" _assertion_term : assertion
syntax _assertion_term "<=" _assertion_term : assertion
syntax _assertion_term ">=" _assertion_term : assertion
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

partial def elabAssertionLit : Syntax → TermElabM Expr
  -- Eq
  | `(assertion| $x:ident = $n:num) => do
    mkAppM ``strValEq  #[mkStrLit x.getId.toString, mkIntLit n.getNat]
  | `(assertion| $n:num = $x:ident) => do
    mkAppM ``valStrEq  #[mkIntLit n.getNat, mkStrLit x.getId.toString]
  | `(assertion| $x:ident = $y:ident) => do
    mkAppM ``strStrEq  #[mkStrLit x.getId.toString, mkStrLit y.getId.toString]
  | `(assertion| ~$t:term = $y:ident) => do
    let x <- elabTermEnsuringType t (some <| .const ``Int [])
    mkAppM ``valStrEq #[x, mkStrLit y.getId.toString]
  | `(assertion| $x:ident = ~$t:term) => do
    let y <- elabTermEnsuringType t (some <| .const ``Int [])
    mkAppM ``strValEq #[mkStrLit x.getId.toString, y]
  | `(assertion| ~$t1:term = ~$t2:term) => do
    let x <- elabTermEnsuringType t1 (some <| .const ``Int [])
    let y <- elabTermEnsuringType t2 (some <| .const ``Int [])
    mkAppM ``valValEq #[x, y]
  -- Neq
  | `(assertion| $x:ident != $n:num) => do
    mkAppM ``strValNe  #[mkStrLit x.getId.toString, mkIntLit n.getNat]
  | `(assertion| $n:num != $x:ident) => do
    mkAppM ``valStrNe  #[mkIntLit n.getNat, mkStrLit x.getId.toString]
  | `(assertion| $x:ident != $y:ident) => do
    mkAppM ``strStrNe  #[mkStrLit x.getId.toString, mkStrLit y.getId.toString]
  | `(assertion| ~$t:term != $y:ident) => do
    let x <- elabTermEnsuringType t (some <| .const ``Int [])
    mkAppM ``valStrNe #[x, mkStrLit y.getId.toString]
  | `(assertion| $x:ident != ~$t:term) => do
    let y <- elabTermEnsuringType t (some <| .const ``Int [])
    mkAppM ``strValNe #[mkStrLit x.getId.toString, y]
  | `(assertion| ~$t1:term != ~$t2:term) => do
    let x <- elabTermEnsuringType t1 (some <| .const ``Int [])
    let y <- elabTermEnsuringType t2 (some <| .const ``Int [])
    mkAppM ``valValNe #[x, y]
  -- LT
  | `(assertion| $x:ident < $n:num) => do
    mkAppM ``strValLt  #[mkStrLit x.getId.toString, mkIntLit n.getNat]
  | `(assertion| $n:num < $x:ident) => do
    mkAppM ``valStrLt  #[mkStrLit x.getId.toString, mkIntLit n.getNat]
  | `(assertion| $x:ident < $y:ident) => do
    mkAppM ``strStrLt  #[mkStrLit x.getId.toString, mkStrLit y.getId.toString]
  | `(assertion| ~$t:term < $y:ident) => do
    let x <- elabTermEnsuringType t (some <| .const ``Int [])
    mkAppM ``valStrLt #[x, mkStrLit y.getId.toString]
  | `(assertion| $x:ident < ~$t:term) => do
    let y <- elabTermEnsuringType t (some <| .const ``Int [])
    mkAppM ``strValLt #[mkStrLit x.getId.toString, y]
  | `(assertion| ~$t1:term < ~$t2:term) => do
    let x <- elabTermEnsuringType t1 (some <| .const ``Int [])
    let y <- elabTermEnsuringType t2 (some <| .const ``Int [])
    mkAppM ``valValLt #[x, y]
  -- GT
  | `(assertion| $x:ident > $n:num) => do
    mkAppM ``strValGt  #[mkStrLit x.getId.toString, mkIntLit n.getNat]
  | `(assertion| $n:num > $x:ident) => do
    mkAppM ``valStrGt  #[mkStrLit x.getId.toString, mkIntLit n.getNat]
  |`(assertion| $x:ident > $y:ident) => do
    mkAppM ``strStrGt  #[mkStrLit x.getId.toString, mkStrLit y.getId.toString]
  | `(assertion| ~$t:term > $y:ident) => do
    let x <- elabTermEnsuringType t (some <| .const ``Int [])
    mkAppM ``valStrGt #[x, mkStrLit y.getId.toString]
  | `(assertion| $x:ident > ~$t:term) => do
    let y <- elabTermEnsuringType t (some <| .const ``Int [])
    mkAppM ``strValGt #[mkStrLit x.getId.toString, y]
  | `(assertion| ~$t1:term > ~$t2:term) => do
    let x <- elabTermEnsuringType t1 (some <| .const ``Int [])
    let y <- elabTermEnsuringType t2 (some <| .const ``Int [])
    mkAppM ``valValGt #[x, y]
  -- LE
  | `(assertion| $x:ident <= $n:num) => do
    mkAppM ``strValLe  #[mkStrLit x.getId.toString, mkIntLit n.getNat]
  | `(assertion| $n:num <= $x:ident) => do
    mkAppM ``valStrLe  #[mkStrLit x.getId.toString, mkIntLit n.getNat]
  | `(assertion| $x:ident <= $y:ident) => do
    mkAppM ``strStrLe  #[mkStrLit x.getId.toString, mkStrLit y.getId.toString]
  | `(assertion| ~$t:term <= $y:ident) => do
    let x <- elabTermEnsuringType t (some <| .const ``Int [])
    mkAppM ``valStrLe #[x, mkStrLit y.getId.toString]
  | `(assertion| $x:ident <= ~$t:term) => do
    let y <- elabTermEnsuringType t (some <| .const ``Int [])
    mkAppM ``strValLe #[mkStrLit x.getId.toString, y]
  | `(assertion| ~$t1:term <= ~$t2:term) => do
    let x <- elabTermEnsuringType t1 (some <| .const ``Int [])
    let y <- elabTermEnsuringType t2 (some <| .const ``Int [])
    mkAppM ``valValLe #[x, y]
  -- GE
  | `(assertion| $x:ident >= $n:num) => do
    mkAppM ``strValGe  #[mkStrLit x.getId.toString, mkIntLit n.getNat]
  | `(assertion| $n:num >= $x:ident) => do
    mkAppM ``valStrGe  #[mkStrLit x.getId.toString, mkIntLit n.getNat]
  | `(assertion| $x:ident >= $y:ident) => do
    mkAppM ``strStrGe  #[mkStrLit x.getId.toString, mkStrLit y.getId.toString]
  | `(assertion| ~$t:term >= $y:ident) => do
    let x <- elabTermEnsuringType t (some <| .const ``Int [])
    mkAppM ``valStrGe #[x, mkStrLit y.getId.toString]
  | `(assertion| $x:ident >= ~$t:term) => do
    let y <- elabTermEnsuringType t (some <| .const ``Int [])
    mkAppM ``strValGe #[mkStrLit x.getId.toString, y]
  | `(assertion| ~$t1:term >= ~$t2:term) => do
    let x <- elabTermEnsuringType t1 (some <| .const ``Int [])
    let y <- elabTermEnsuringType t2 (some <| .const ``Int [])
    mkAppM ``valValGe #[x, y]
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

/--
info: ∀ (n : Int), (strValEq "x" n).implies (strValLt "x" 10) : Prop
-/
#guard_msgs in
#check forall (n : Int), astn x = ~n ->> x < 10
