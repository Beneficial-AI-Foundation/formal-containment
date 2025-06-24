// #import "@preview/charged-ieee:0.1.3": ieee
#import "fns.typ" as fns
#let experiments_spec = toml("assets/experiments.toml")
#let experiment_results = toml("assets/results_20250620-0029.toml")

#let title = [*Formal Containment _draft_*]
#let abstract = [We would like to put the AI in a box. We show how to create an _interface_ between the box and the world out of specifications in Lean. It is the AI's responsibility to provide a proof that its (restricted) output abides by the spec. The runnable prototype is at https://github.com/quinn-dougherty/formal-containment.]
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

Previously, classical AI safety warned against trying to put the AI in a box @LessWrong2020AIBoxing. Yudkowsky famously convinced people of this via a roleplay game in the extropians mailing list days @Yudkowsky2002AIBox. Recent work from AI Control and Safeguarded AI has reignited interest in this long neglected area.

- AI Control @greenblatt2024aicontrolimprovingsafety @bhatt2025ctrlzcontrollingaiagents (_Ctrl_) is reasoning about getting useful work out of an untrusted (possibly misaligned) AI. @greenblatt2024aicontrolimprovingsafety introduces control evaluations, stress‑testing safety protocols in an APPS @Hendrycks2021MeasuringCC backdooring testbed: GPT‑4 attempts to embed hidden backdoors, GPT‑3.5 flags the riskiest submissions, and scarce audits verify only the worst cases.
- Safeguarded AI @Dalrymple2024SafeguardedAI (_SgAI_) tries to isolate the trust surface to a specification and a proof checker. In _SgAI_'s "gatekeeper" architecture, every proposed action must come with a machine-checkable proof. The AI generates proof certificates; a minimal, verified checker enforces them.

What these lines of work have in common is policing the interface between the AI and the outside world. Though boxes don't solve the whole problem with respect to arbitrary superintelligences, they are still worthwhile because we can use non-robust techniques to get us through some percentage of the transition, empowering our successors to bootstrap from there to something more robust @yampolskiy2012leakproofing.

Separately, a forgotten literature on proof-carrying code @necula1997proof (_PCC_) provides a background for the AI's obligation to tag code it wants to execute in the world with a "proof" that the code is "correct" (up to some specification). Reviving ideas from _PCC_ for AI safety is discussed in @tegmark2023provablysafesystemspath and @dalrymple2024guaranteedsafeaiframework.

Here, we're seeking a minimal, concrete, end-to-end prototype synthesizing a subset of these ideas.

== Contributions

We present a natural midpoint between _PCC_ and _Ctrl_, while for simplicity ignoring many characteristics of _SgAI_ (@sec:related). We deliver a prototype #footnote[https://github.com/quinn-dougherty/formal-containment] AI box in Python in which we can lock up an agent graph that writes programs in a toy language along with correctness proofs in Lean @deMoura2015Lean.

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

== Preliminaries <sec:preliminaries>

Let $bb(P)$ be the type of propositions. Let #imp be the minimal imperative programming language with expressions valued in integers containing skip, sequence, assign, if, and while statements. Let $"Env"$ be the state type, assigning variable names to values, and let $"Assertion"$ be the assertion type, predicates on state. Formally,
$
  "Env" := #env_t\
  "Assertion" := #assertion_t
$
Execution is a function from a command and a state that returns a state ($"exec" : #imp -> "Env" -> "Env"$). A _hoare triple_ is a ternary predicate expressing when a command sends an assertion (the precondition) to another assertion (the postcondition), quantified over all states. Formally,
$
  "hoare" := P c Q mapsto \
  forall (sigma_1 sigma_2 : "Env"),
  P sigma_1 ->
  "exec" c sigma_1 = sigma_2 ->
  Q sigma_2 : \
  "Assertion" -> #imp -> "Assertion" -> bb(P)
$
and denoted $"hoare" P c Q =$ #hoare_triple(prec: [$P$], command: [\<#imp\> $c$ </#imp>], post: [$Q$]) @Hoare_PLF. A _term_ of type #hoare_triple(prec: [$P$], command: [\<#imp\> $c$ </#imp>], post: [$Q$]) is a proof that the triple is true.

== Example trace

Let's walk through an FCP trace as you'd see it if you cloned our repo, pictured in @fig:example-trace.

First, the user passes in a precondition and a postcondition. We will continue using the example in @fig:box-picture, passing in $x > 0$ and $x > 1$ for precondition and postcondition, respectively. Let's say for the sake of argument that the AI's first guess is `x := x - 1;`. Then, the proof agent will flail about until `MAX_ITERATIONS` is reached, since the program is incorrect, at which point it will report to the boundary its failed proof state. Then, the boundary replies "_try again, I'm not executing that code in the world_" and hands the program back to the AI, asking for another one. Suppose that this time, the AI finds `x := x + 1;`. This time, the proof agent converges and Lean reports an exit code of `0`. The AI sends the #imp program to the boundary and attests to its correctness with the Lean program, which it also attaches.

#figure(fns.example_trace, caption: [Example trace described.]) <fig:example-trace>

The Lean program would look like this (Note it must be run with `lake build` in the appropriate lake project, as it has imports)
#figure(
  [```lean
    import Imp
    open Imp

    example : {{astn x > 0}}(imp { x := x + 1; }){{astn x > 1}} := by
      auto_hoare_pos
    ```],
  caption: [Proof of the example hoare triple from @fig:box-picture.],
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

== Proof-carrying code and LLMs
Our work is well situated within _PCC_ @necula1997proof and the closely related certifying algorithms @mcconnell2011certifying. Our setup is similar to that in @kamran2024pc3, who only approve code that that comes with a Dafny proof, but over there they emphasize the use of verification condition generation to make the specification elicitation from the human a little easier.

== Confinement
In the seminal @Lampson1973Confinement, Lampson 1973 states _confinement rules_ to reason about when a program is or isn't confined.
1. Total isolation or transitivity: either it does not call any other program or if it calls another program that program is also confined.
2. Masking and enforcement: all inputs (including side-channels) must be fully specified and enforced by the caller, and input to covert channels conforms to caller's specifications.

Building on Lampson, Yampolskiy 2012 @yampolskiy2012leakproofing considers confinement of AI, especially superintelligence.
#quote(attribution: [Yampolskiy 2012 @yampolskiy2012leakproofing], block: true)[
  In the hopes of starting a new subfield of computer security, AI Safety Engineering, we define the Artificial Intelligence Confinement Problem (AICP) as the challenge of restricting an artificially intelligent entity to a confined environment from which it can’t exchange information with the outside environment via legitimate or covert channels if such information exchange was not authorized by the confinement authority
]

The current formal containment work explores a restriction of Yampolskiy's AICP to the #imp programming language, where the confinement authority is the user providing precondition and postcondition backed by Lean. In fact, the setting is so restricted that we meet the Lampson rules almost for free. This makes a ripe opportunity for future work.

See @Babcock2016Containment for a review of common software bugs and cybersecurity pitfalls, many of which are greatly alleviated if not outright blocked by formal verification. For something more modern, see @costa2025securingaiagentsinformationflow for the connection between LLM agents and information-flow security.

== AI control
_Ctrl_ @greenblatt2024aicontrolimprovingsafety frames oversight as a contest between an untrusted model (U), a trusted model (T), and limited high-quality audits (H). Their trusted/untrusted monitoring, defer‑to‑trusted routing, and trusted editing strategies map out a safety-usefulness Pareto frontier, with trusted editing nearly eliminating backdoors at modest utility cost

The main difference between the current work and _Ctrl_ @greenblatt2024aicontrolimprovingsafety is we don't _emphasize_ intentional subversion (as in try to elicit it for stress testing). We're keen to do this soon.

== Safeguarded AI
_SgAI_ @Dalrymple2024SafeguardedAI wants to accomplish confinement via proof-carrying code, but crucially attempts to reason with probabilistic semantics and expected value bounds so it can tackle dynamical and stochastic systems. This enables safety guarantees over stochastic and continuous domains at the cost of a more complex proof stack.

Our protocol instead fixes the domain to discrete #imp programs and embeds Lean proofs for every action, shrinking the trusted base to Lean’s off-the-shelf kernel and an interpretable specification.

= Future Work

== Non-toy languages

There are several formal verification stacks that work on real world languages like C @pulte2023cn @sammler2021refinedc or Rust @vanhattum2022verifying @lattuada2023verusverifyingrustprograms. It is conceptually straightforward to extend our codebase to work with them rather than #imp.

== `mcp-hardened`

We used MCP to orchestrate the agent graph. If MCP is an appropriate foundational framework for a box, it'd be nice to build in stronger security guarantees and fewer footguns. A hardened MCP would enable box devs to rely on the framework to increase friction to writing insecure boxes. For example, depending on my server's log permissions or the oracle client's print statements, an incorrect program could leak to the caller. If we'd like to deploy narrowly superhuman AIs in boxes, this becomes more important.

== Demonstrate subversive code getting caught by the protocol and sent back to the model

In @greenblatt2024aicontrolimprovingsafety, Greenblatt et al elicit subversive code from the AI to see if their protocol can catch it. It'd be nice to transfer this aspect to the _PCC_ setting. This is the obvious direction to study _completeness_ of specifications, or the problem of expressing programs via specs _uniquely_ as well as correctly.

= Acknowledgments

Thank you Stephen Mell for discussion.

// Bibliography
#bibliography("refs.bib", style: "ieee")
