namespace Imp.Expr

/-- Unary operators -/
inductive UnOp where
  | neg
  | not
deriving Repr, DecidableEq

/-- Binary operators -/
inductive BinOp where
  | plus | minus | times | div
  | and | or
  | lt | le | eq
deriving Repr, DecidableEq

end Expr

/-- Expressions -/
inductive Expr where
  | const (i : Int)
  | var (name : String)
  | un (op : Expr.UnOp) (e : Expr)
  | bin (op : Expr.BinOp) (e1 e2 : Expr)
deriving Repr, DecidableEq

instance : Coe String Expr where
  coe := .var
instance : Coe Int Expr where
  coe := .const
