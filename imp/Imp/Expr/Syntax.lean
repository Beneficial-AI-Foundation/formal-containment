import Lean.PrettyPrinter.Parenthesizer
import Imp.Expr.Basic
import Imp.Expr.Eval

namespace Imp.Expr

open Lean PrettyPrinter Parenthesizer


/- Add a new nonterminal to Lean's grammar, called `varname` -/
/-- Variable names in Imp -/
declare_syntax_cat varname

/- There are two productions: identifiers and antiquoted terms -/
syntax ident : varname
syntax:max "~" term:max : varname

/- `varname`s are included in terms using `var { ... }`, which is a hook on which to hang the macros
that translate the `varname` syntax into ordinary Lean expressions. -/
syntax "var " "{" varname "}" : term

/- These macros translate each production of the `varname` nonterminal into Lean expressions -/
macro_rules
  | `(var { $x:ident }) => `(term|$(quote x.getId.toString))
  | `(var { ~$stx }) => pure stx

/-- Expressions in Imp -/
declare_syntax_cat exp

/-- Variable names -/
syntax varname : exp

/-- Numeric constant -/
syntax num : exp

/-- Arithmetic complement -/
syntax:75 "-" exp:75 : exp

/-- Multiplication -/
syntax:70 exp:70 " * " exp:71 : exp
/-- Division -/
syntax:70 exp:70 " / " exp:71 : exp

/-- Addition -/
syntax:65 exp:65 " + " exp:66 : exp
/-- Subtraction -/
syntax:65 exp:65 " - " exp:66 : exp

/-- Boolean negation -/
syntax:75 "!" exp:75 : exp
/-- Less than -/
syntax:50 exp:50 " < " exp:51 : exp
/-- Less than or equal to -/
syntax:50 exp:50 " ≤ " exp:51 : exp
/-- Greater than or equal to -/
syntax:50 exp:50 " ≥ " exp:51 : exp
/-- Greater than -/
syntax:50 exp:50 " > " exp:51 : exp
/-- Equal -/
syntax:45 exp:45 " == " exp:46 : exp

/-- Boolean conjunction -/
syntax:35 exp:35 " && " exp:36 : exp
/-- Boolean disjunction -/
syntax:35 exp:35 " || " exp:36 : exp

/-- Parentheses for grouping -/
syntax "(" exp ")" : exp

/-- Escape to Lean -/
syntax:max "~" term:max : exp

/-- Embed an Imp expression into a Lean expression -/
syntax:min "expr " "{ " exp " }" : term

macro_rules
  | `(expr{$x:ident}) => `(Expr.var $(quote x.getId.toString))
  | `(expr{$n:num}) => `(Expr.const $(quote n.getNat))

  | `(expr{-$e}) => `(Expr.un .neg (expr{$e}))
  | `(expr{!$e}) => `(Expr.un .not (expr{$e}))

  | `(expr{$e1 + $e2}) => `(Expr.bin .plus (expr{$e1}) (expr{$e2}))
  | `(expr{$e1 * $e2}) => `(Expr.bin .times (expr{$e1}) (expr{$e2}))
  | `(expr{$e1 - $e2}) => `(Expr.bin .minus (expr{$e1}) (expr{$e2}))
  | `(expr{$e1 / $e2}) => `(Expr.bin .div (expr{$e1}) (expr{$e2}))

  | `(expr{$e1 && $e2}) => `(Expr.bin .and (expr{$e1}) (expr{$e2}))
  | `(expr{$e1 || $e2}) => `(Expr.bin .or (expr{$e1}) (expr{$e2}))

  | `(expr{$e1 < $e2}) => `(Expr.bin .lt (expr{$e1}) (expr{$e2}))
  | `(expr{$e1 ≤ $e2}) => `(Expr.bin .le (expr{$e1}) (expr{$e2}))
  | `(expr{$e1 == $e2}) => `(Expr.bin .eq (expr{$e1}) (expr{$e2}))
  | `(expr{$e1 ≥ $e2}) => `(Expr.bin .le (expr{$e2}) (expr{$e1}))
  | `(expr{$e1 > $e2}) => `(Expr.bin .lt (expr{$e2}) (expr{$e1}))
  | `(expr{($e)}) => `(expr{$e})
  | `(expr{~$stx}) => pure stx

-- Copied from Lean's term parenthesizer - applies the precedence rules in the grammar to add
-- parentheses as needed. This isn't needed when adding new input syntax to Lean, but because the
-- file `Delab.lean` makes Lean use this syntax in its output, the parentheses are needed.
@[category_parenthesizer exp]
def exp.parenthesizer : CategoryParenthesizer | prec => do
  maybeParenthesize `exp true wrapParens prec $
    parenthesizeCategoryCore `exp prec
where
  wrapParens (stx : Syntax) : Syntax := Unhygienic.run do
    let pstx ← `(($(⟨stx⟩)))
    return pstx.raw.setInfo (SourceInfo.fromRef stx)

/- Add new nonterminals to Lean's grammar, called `val` and `env` -/
/-- Values in Imp -/
declare_syntax_cat val
syntax:10 num : val
macro_rules
  | `(val| $n:num) => `(Value.int $(quote n.getNat))
/-- Environments in Imp -/
declare_syntax_cat _association
declare_syntax_cat env

syntax val ";" ident "|->" val : _association
syntax "⟨" _association "⟩" : env
syntax env : term
syntax env "||" env : env
syntax "[" env "]" : term  -- coercion from env to term
macro_rules
  | `(_association| $i:num ; $x:ident |-> $n:num) => `(Expr.Env.set $(quote x.getId.toString) $(quote n.getNat) $ Expr.Env.init $(quote i.getNat))
  | `(env| ⟨$a:_association⟩) => `(_association| $a)
  -- | `(env| $σ:env || $σ':env) => `(Expr.Env.union [$σ] [$σ'])
  -- | `([$σ:env]) => `($σ)

variable (e : Expr)
-- #eval ⟨1; x |-> 2⟩

-- -- Basic environment binding: varname := exp
-- syntax varname ":=" exp : env
-- -- Multiple bindings separated by commas
-- syntax sepBy(env, ",") : env
-- -- Environment lookup syntax: σ[varname] (high precedence, function application level)
-- syntax:1000 term "[" varname "]" : term
-- -- Environment update syntax: σ[bindings] (high precedence, function application level)
-- syntax:1000 term "[" env "]" : term
-- -- Environment literals using angle brackets: ⟨base | bindings⟩ (atom level)
-- syntax:200 "⟨" term:arg "|" env "⟩" : term
-- -- Environment syntax within exp category - allows environments as values (atom level)
-- syntax:200 term:max "[" varname "]" : exp
-- -- Environment initialization: ∅[default_val]
-- syntax:200 "∅[" exp "]" : term
--
-- macro_rules
--   -- Environment lookup macro rules
--   | `($σ[var { $x:ident }]) => `(Expr.Env.get $(quote x.getId.toString) $σ)
--   | `($σ[var { ~$stx }]) => `(Expr.Env.get $stx $σ)
--   -- Environment update macro rules
--   | `($σ[var { $x:ident } := expr{ $e }]) => `(Expr.Env.set $(quote x.getId.toString) (expr{$e}) $σ)
--   | `($σ[var { ~$stx } := expr{ $e }]) => `(Expr.Env.set $stx (expr{$e}) $σ)
--   -- | `($σ[$binding, $rest,*]) => `($σ[$binding][$rest,*])
--   -- Environment literal macro rules
--   | `(⟨$base | var { $x:ident } := expr{ $e }⟩) => `((Expr.Env.init $base).set $(quote x.getId.toString) (expr{$e}))
--   | `(⟨$base | var { ~$stx } := expr{ $e }⟩) => `((Expr.Env.init $base).set $stx (expr{$e}))
--   -- | `(⟨$base | $binding, $rest,*⟩) => `(⟨$base | $binding⟩[$rest,*])
--   -- Environment operations within exp syntax
--   | `(expr{$σ[var { $x:ident }]}) => `(Expr.Env.get $(quote x.getId.toString) $σ)
--   | `(expr{$σ[var { ~$stx }]}) => `(Expr.Env.get $stx $σ)
