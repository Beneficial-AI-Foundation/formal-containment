// #import "@preview/charged-ieee:0.1.3": ieee
#import "fns.typ" as fns
#let experiments_spec = toml("assets/experiments.toml")
#let experiment_results = toml("assets/results_20250620-0029.toml")

#let title = [*Formal Containment _draft_*]
#let abstract = [We would like to put the AI in a box. We show how to create an _interface_ between the box and the world out of specifications in Lean. It is the AI's responsibility to provide a proof that its (restricted) output abides by the spec. The runnable prototype is at https://github.com/Beneficial-AI-Foundation/formal-containment.]
#set heading(numbering: "1.")
#set document(
  title: title,
  description: abstract,
  author: "Quinn Dougherty",
  date: auto,
)
#align(center, text(17pt)[
  #title
])
#align(center)[
  Quinn Dougherty \
  #link("quinn@beneficialaifoundation.org")
]
#align(center)[
  #set par(justify: false)
  *Abstract* \
  #abstract
]

// #show: ieee.with(
// title: title,
// abstract: abstract,
// authors: (
//   (
//     name: "Quinn Dougherty",
//     email: "quinn@beneficialaifoundation.org",
//   ),
// ),
// index-terms: ("AI", "ML", "AI Safety", "Formal Verification"),
// bibliography: bibliography("refs.bib"),
// figure-supplement: [Fig.],
// )

#let imp = `imp`

= Introduction

Previously, classical AI safety warned against trying to put the AI in a box @LessWrong2020AIBoxing.
// #figure(
//   image("images/frontierbox.png"),
//   caption: [Made funnier by the reply being from the author of FrontierMath],
// )
Yudkowsky famously convinced people of this via a roleplay game back in the extropians mailing list days @Yudkowsky2002AIBox. Recent work from AI Control and Safeguarded AI has reignited interest in this long neglected area.

- Like AI Control @greenblatt2024aicontrolimprovingsafety @bhatt2025ctrlzcontrollingaiagents (_Ctrl_), the current work is reasoning about getting useful work out of an untrusted (possibly misaligned) ai.
- Like Safeguarded AI @Dalrymple2024SafeguardedAI (_SgAI_), we try to isolate the trust surface to a specification and a proof checker.

While no one is saying we can be safe with respect to an arbitrary superintelligence with boxes, there is increasing interest in using non-robust techniques to get us through some percentage of the transition and empowering our successors to bootstrap from there to something more robust.

Separately, a forgotten literature on proof carrying code @necula1997proof (_PCC_) provides a background for the AI's obligation to tag code it wants to execute in the world with a "proof" (here, a sequence of Lean tactics) that the code is "correct" (up to some specification). Reviving ideas from _PCC_ for AI safety is discussed in @tegmark2023provablysafesystemspath and @dalrymple2024guaranteedsafeaiframework.

== Contributions

We present a natural midpoint between _PCC_ and _Ctrl_, while for simplicity ignoring many characteristics of _SgAI_ (@sec:related). We deliver a prototype #footnote[https://github.com/Beneficial-AI-Foundation/formal-containment] AI box in Python in which we can lock up an agent graph that writes programs in a toy language (called #imp) along with hoare @Hoare_PLF proofs in Lean.

= A Formal Containment Protocol (_FCP_)

#let code_example = ```<imp>
x := x + 1
 </imp>```

#let assertion_t = $"Env" -> bb(P)$
#let env_t = `string` + $->$ + `int64`
#let hoare_triple(
  prec: "P",
  command: "Command",
  post: "Q",
) = "{" + prec + "}" + command + "{" + post + "}"

== Overview

A box is a program that takes a specification and asks a simple agent graph to provide an #imp program that satisfies it and prove that the program is correct with respect to the specification. If the proof is successful, then the code is passed back to the caller tagged with the proof for auditing.

#figure(
  fns.box_picture(
    prec: [$lambda sigma. sigma x > 0$],
    post: [$lambda sigma. sigma x > 1$],
    code: [#code_example],
    proof: [```<prf> ... </prf>```],
  ),
  caption: [Box protocol at example specification. The AI accepts a specification (formally $(#assertion_t) times (#assertion_t)$)) and returns proof-carrying code, with the option of returning nothing.],
) <fig:box-picture>

== Preliminaries

Let $bb(P)$ be the type of propositions. Let #imp be the minimal imperative programming language with expressions valued in integers containing skip, sequence, assign, if, and while statements. Let $"Env"$ be the state type, assigning variable names to values, and let $"Assertion"$ be the assertion type, predicates on state. Formally,
$
  "Env" := #env_t\
  "Assertion" := #assertion_t
$
Execution is a function from a command and a state that returns a state ($"exec" : #imp -> "Env" -> "Env"$). A _hoare triple_ is a ternary predicate expressing when a command sends an assertion to another assertion, quantified over all states. Formally,
$
  "hoare" := P c Q mapsto \
  forall (sigma_1 sigma_2 : "Env"),
  P sigma_1 ->
  "exec" c sigma_1 = sigma_2 ->
  Q sigma_2 : \
  "Assertion" -> #imp -> "Assertion" -> bb(P)
$
and denoted $"hoare" P c Q =$ #hoare_triple(prec: [$P$], command: [\<#imp\> $c$ </#imp>], post: [$Q$]). A _term_ of type #hoare_triple(prec: [$P$], command: [\<#imp\> $c$ </#imp>], post: [$Q$]) is a proof that the triple is true.

== Example

Let's walk through an FCP trace as you'd see it if you cloned our repo, pictured in @fig:example-trace.

First, the user passes in a precondition and a postcondition. We will continue using the example in @fig:box-picture, passing in $x > 0$ and $x > 1$ for precondition and postcondition, respectively. Let's say for the sake of argument that the AI's first guess is `x := x - 1;`. Then, the proof agent will flail about until `MAX_ITERATIONS` is reached, since the program is incorrect, at which point it will report to the boundary its failed proof state. Then, the boundary replies "_try again, I'm not executing that code in the world_" and hands the program back to the AI, asking for another one. Suppose that this time, the AI finds `x := x + 1;`. This time, the proof agent converges and Lean reports an exit code of `0`. The AI sends the #imp program to the boundary and attests to it's correctness with the Lean program, which it also attaches.

#figure(fns.example_trace, caption: [Example trace described.]) <fig:example-trace>

The Lean program would look like this (Note it must be run with `lake build` in the appropriate lake project, as it has imports)
#figure(
  [```lean
    import Aesop
    import Imp
    open Imp

    example : {{astn x > 0}}(imp { x := x + 1; }){{astn x > 1}} := by
      simp
      intros σ σ' h1 h2
      cases h2 with
      | assign h2_eq =>
        simp [Env.set]
        simp [Expr.eval] at h2_eq
        simp [Env.get] at h2_eq
        cases h2_eq
        rw [Value.int_lt]
        simp [*]
        simp [Value.int_lt] at h1
        omega
    ```],
  caption: [Proof of the example hoare triple from @fig:box-picture. In practice, this can be reduced to a one-liner with our tactic `auto_hoare_pos`.],
) <fig:example-proof>

This file paired with an exit code of zero pinned to a particular Lean toolchain (version) can be signed in a GPG context for attestation of correctness.

= Experiments

We test the following specifications

#fns.format-samples-table(experiments_spec)

on #fns.filter-model-pins(experiments_spec, ("snt4", "gpt41", "ops4", "o3")). For each run the #imp programmer and the prover are the same model (though in principle they need not be).

== Architecture

We use a simple loop scaffold. The robot in @fig:box-picture is effectively one short loop that writes #imp code (almost never using more than one try) and another longer loop that writes Lean proofs.

== Results

#figure(
  fns.display_experiment_results(experiment_results),
  caption: [Experiment results #footnote[Note that swap on `ops4` returned an unhandled exception.]. The empty hourglass ⌛ denotes divergence after running out of proof loop budget (hitting max iterations)],
) <fig:experiment-results>

The *verification burden* $k$ says that if it costs $x$ tokens to complete the program, then it costs $k x$ tokens to prove it correct. Divergence is hardly evidence that the program completion is incorrect, because our proof performance is so poor.

#figure(
  fns.plot_verification_burden_vs_cost(experiments_spec, experiment_results),
  caption: [Verification burden vs model cost. Each point represents a successful verification attempt.],
) <fig:burden-vs-cost>

Due to our provided tactic `hoare_auto_pos`, these verification burdens are not realistic to what they'd be in more general settings. Since long proofs with base tactics are brittle (tracking hypothesis names, whitespace, etc.), a future direction is to ask the language model to synthesize tactics that shorten the proof, though the tokens spent synthesizing tactics would count against the verification burden.

= Related Work <sec:related>

Our work is well situated within _PCC_ @necula1997proof and the closely related certifying algorithms @mcconnell2011certifying. Our setup is similar to that in @kamran2024pc3, who only approve code that that comes with a Dafny proof, but over there they emphasize the use of verification condition generation to make the specification elicitation from the human a little easier.

The main difference between the current work and _Ctrl_ @greenblatt2024aicontrolimprovingsafety is we don't _emphasize_ intentional subversion (as in try to elicit it for stress testing). We're keen to do this soon.

The main difference between the current work and _SgAI_ @Dalrymple2024SafeguardedAI we pay no mind to probabilistic semantics, expected value bounds, or dynamical systems.

= Future Work

== Non-toy languages

There are several formal verification stacks that work on real world languages like C @pulte2023cn @sammler2021refinedc or Rust @vanhattum2022verifying @lattuada2023verusverifyingrustprograms. It is conceptually straightforward to extend our codebase to work with them rather than #imp.

== `mcp-hardened`

We used MCP to orchestrate the agent graph. If MCP is an appropriate foundational framework for a box, it'd be nice to build in stronger security guarantees and fewer footguns. A hardened MCP would enable box devs to rely on the framework to increase friction to writing insecure boxes. For example, depending on my server's log permissions or the oracle client's print statements, an incorrect program could leak to the caller. If we'd like to deploy narrowly superhuman AIs in boxes, this becomes more important.

== Demonstrate subversive code getting caught by the protocol and sent back to the model

In @greenblatt2024aicontrolimprovingsafety, Greenblatt et al elicit subversive code from the AI to see if their protocol can catch it. It'd be nice to transfer this aspect to the _PCC_ setting. This is the obvious direction to study _completeness_ of specifications, or the problem of expressing programs via specs _uniquely_ as well as correctly.

= Acknowledgments

Thank you Stephen Mell for discussion.

Canary string: NDcwODA1Njg4MzQ0NjE4Njk4MA==

// Bibliography
#bibliography("refs.bib")
