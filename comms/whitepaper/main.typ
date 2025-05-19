#import "@preview/charged-ieee:0.1.3": ieee

#show: ieee.with(
  title: [Formal Containment *draft*: AI Control via Proof Carrying Code],
  abstract: [
    We would like to put the AI in a box. We show how to create an _interface_ between the *box* and the *world* using specifications in Lean. It is the AI's responsibility to provide a proof that its (restricted) output abides by the spec. The runnable prototype is at https://github.com/Beneficial-AI-Foundation/formal-containment.
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

Previously, classical AI safety warned against trying to put the AI in a box @LessWrong2020AIBoxing.
#figure(
  image("images/frontierbox.png"),
  caption: [Made funnier by the reply being from the author of FrontierMath],
)

Yudkowsky famously convinced people of this via a roleplay game back in the extropians mailing list days @Yudkowsky2002AIBox.

Recent work from AI Control and Safeguarded AI have reignited interest in this long neglected area.

- Like AI Control @greenblatt2024aicontrolimprovingsafety @bhatt2025ctrlzcontrollingaiagents (_Ctrl_), the current work is reasoning about getting useful work out of an untrusted (possibly misaligned) ai.
- Like Safeguarded AI @Dalrymple2024SafeguardedAI (_SgAI_), we try to isolate the trust surface to a specification and a proof checker.

While no one is saying we can be safe with respect to an arbitrary superintelligence with boxes, there is increasing interest in using non-robust techniques to get us through some percentage of the transition and empowering our successors to bootstrap from there to something more robust.

Separately, a forgotten literature on proof carrying code @necula1997proof (_PCC_) provides a background for the AI's obligation to tag code it wants to execute in the world with a "proof" (here, a sequence of Lean tactics) that the code is "correct" (up to some specification).

== Contributions

We present the natural midpoint between _PCC_ and _Ctrl_, while for simplicity ignoring many characteristics of _SgAI_. We deliver a prototype #footnote[https://github.com/Beneficial-AI-Foundation/formal-containment] AI box in Python in which we can lock up a Sonnet-3.7 agent that writes programs in a toy language (called `imp`) along with hoare @Hoare_PLF proofs in Lean.

= A Formal Containment Protocol (_FCP_)

A box is constructed in the Model Context Protocol (MCP) standard @ModelContextProtocol2025. In the simplest architecture: an MCP _server_ provides tools (executables, in our case the Lean typechecker), resources (such as data), and prompt templates; while an MCP _client_ may house language model (_oracle_) calls that can rely on the server's tools, resources, or prompts. Our architecture uses a MCP server-client relationship to generate proof carrying code, then forms the box out of another client (one which does not feature an oracle call).

When an MCP server returns terms of a type from a tool or resource, we say that that type is the server's _codomain_. Let an MCP server's codomain be the data structure formed from a tool's execution, formatted to be sent over the MCP wire. The *interface* between the box and the world is an MCP client equipped with a *whitelist*, which is a subtype of the codomain of the MCP server. The box client has children, aspects of the world (like a git repo or deployment environment). The box client decides whether a completion can be sent to the world based on some criterion programmed in by the user.

In the current work, the criterion will be a precondition and postcondition of a hoare triple @Hoare_PLF, since the oracle throughout the prototype is an `imp` programmer. `Imp` is a minimal imperative programming language known for its pedagogical properties, expressing important constructs like `if`, `while`, and so on.

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

= Related Work

Our work is well situated within _PCC_ @necula1997proof and the closely related certifying algorithms @mcconnell2011certifying. TODO: say more

The main difference between the current work and _Ctrl_ @greenblatt2024aicontrolimprovingsafety is we don't _emphasize_ intentional subversion (as in try to elicit it for stress testing).

The main difference between the current work and _SgAI_ @Dalrymple2024SafeguardedAI we pay no mind to probabilistic semantics, expected value bounds, or dynamical systems.

= Future Work

== Non-toy languages

There are several formal verification stacks that work on real world languages like C or Rust (TODO: cite). It would be fairly straightforward to extend our codebase to work with them rather than `imp`.

== `mcp-hardened`

If MCP is an appropriate foundational framework for a box, it'd be nice to build in stronger security guarantees and fewer footguns. A hardened MCP would enable box authors to rely on the framework to increase friction to writing insecure boxes. If we'd like to deploy narrowly superhuman AIs in boxes, this becomes more important.

== Demonstrate subversive code getting caught by the protocol and sent back to the model

In @greenblatt2024aicontrolimprovingsafety, Greenblatt et al elicit subversive code from the AI to see if their protocol can catch it. It'd be nice to transfer this aspect to the _PCC_ setting. We'd have to declare nontrivial specifications that soundly, but not necessarily completely, identify "backdoor-free programs", which might be too hard to do to get started, at least in a hoare-like setting.
