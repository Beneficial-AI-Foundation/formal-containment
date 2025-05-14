#import "@preview/charged-ieee:0.1.3": ieee

#show: ieee.with(
  title: [Formal Containment *draft*],
  abstract: [
    We would like to put the AI in a box. We show how to create an _interface_ between the *box* and the *world* using specifications in Lean. It is the AI's responsibility to provide a proof that it's (restricted) output abides by the spec.
  ],
  authors: (
    (
      name: "Quinn Dougherty",
      department: [Research Engineer],
      organization: [Beneficial AI Foundation],
      location: [Cambridge, MA],
      email: "quinn@beneficialaifoundation.org",
    ),
  ),
  index-terms: ("AI", "ML", "AI Safety", "Formal Verification"),
  bibliography: bibliography("refs.bib"),
  figure-supplement: [Fig.],
)

= Introduction
_Prereqs: hoare triples, errors as values, mcp_

Previously, classical AI safety warned against trying to put the AI in a box @LessWrong2020AIBoxing.
#figure(
  image("images/frontierbox.png"),
  caption: [Made funnier by the reply being from the author of FrontierMath],
)

Yudkowsky famously convinced people of this via a roleplay game back in the extropians mailing list days @Yudkowsky2002AIBox.

Recent work from AI Control and Safeguarded AI have reignited interest in this long neglected area.

- Like AI Control @greenblatt2024aicontrolimprovingsafety @bhatt2025ctrlzcontrollingaiagents, the current work is reasoning about getting useful work out of an untrusted (possibly misaligned) ai.
- Like Safeguarded AI @Dalrymple2024SafeguardedAI, we try to isolate the trust surface to a specification and a proof checker.

= The formal containment protocol

A box is constructed in the MCP standard @ModelContextProtocol2025.

Let an MCP server's codomain be the data structure formed from an oracle's completion formatted to be sent over the MCP wire. The *interface* between the box and the world is an MCP client equipped with a *whitelist*, which is a subtype of the codomain of the MCP server that wraps the llm/oracle. The client has children, aspects of the world (like a git repo or deployment environment). The client decides whether a completion can be sent to the world based on some criterion programmed in by the user.

In this whitepaper, the criterion will be a precondition and postcondition of a hoare triple @Hoare_PLF, since the oracle throughout this prototype is an imp programmer. Imp is a minimal imperative programming language known for its pedagogical properties.

== Example

MCP server $S$ has a Lean tool use with the following codomain

```
Enumerated codS {
  Pass: (prec, post) -> codS,
  Fail: (prec, post) -> stderr -> codS
}
```

MCP client $B$ is equipped with the `Pass` constructor of `codS` (it's _whitelist_).

Let criterion $C$ be the pair $("prec", "post") := (X > 0, X > 1)$.

Then, programs $c$ provided by imp oracle $cal(O)_i$ at relevant prompt $p := p("prec", "post")$ will form the command at the center of the hoare triple. In other words, $forall c ~ cal(O)_i (p), {"prec"} c {"post"}$ is either provable or not. (In this easy case, $cal(O)_i$ submits $X := X + 1$ under any reasonable prompt).

When $cal(O)_i$ submits a program $c$ to the interface client $B$, $B$ sends the triple ${"prec"} c {"post"}$ to the proof oracle $cal(O)_p$ in one thread and the triple's negation in another thread. If the negative thread terminates in success, then a negative certificate is sent to $B$ and $B$ informs $cal(O)_i$ that it shall not run that code in the world, and that $cal(O)_i$ must try again. If the positive thread terminates in success, then the positive certificate is sent to $B$ and $B$ passes along program $c$ to its children to be run in the world.
