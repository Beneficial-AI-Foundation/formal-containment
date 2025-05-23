//#import "@preview/charged-ieee:0.1.3": ieee
#import "@preview/cetz:0.3.4"

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
  Beneficial AI Foundation \
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
//     department: [Research Engineer],
//     organization: [Beneficial AI Foundation],
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
Yudkowsky famously convinced people of this via a roleplay game back in the extropians mailing list days @Yudkowsky2002AIBox. Recent work from AI Control and Safeguarded AI have reignited interest in this long neglected area.

- Like AI Control @greenblatt2024aicontrolimprovingsafety @bhatt2025ctrlzcontrollingaiagents (_Ctrl_), the current work is reasoning about getting useful work out of an untrusted (possibly misaligned) ai.
- Like Safeguarded AI @Dalrymple2024SafeguardedAI (_SgAI_), we try to isolate the trust surface to a specification and a proof checker.

While no one is saying we can be safe with respect to an arbitrary superintelligence with boxes, there is increasing interest in using non-robust techniques to get us through some percentage of the transition and empowering our successors to bootstrap from there to something more robust.

Separately, a forgotten literature on proof carrying code @necula1997proof (_PCC_) provides a background for the AI's obligation to tag code it wants to execute in the world with a "proof" (here, a sequence of Lean tactics) that the code is "correct" (up to some specification). Reviving ideas from _PCC_ for AI safety is discussed in @tegmark2023provablysafesystemspath and @dalrymple2024guaranteedsafeaiframework.

== Contributions

We present the natural midpoint between _PCC_ and _Ctrl_, while for simplicity ignoring many characteristics of _SgAI_ (@sec:related). We deliver a prototype #footnote[https://github.com/Beneficial-AI-Foundation/formal-containment] AI box in Python in which we can lock up an agent graph that writes programs in a toy language (called #imp) along with hoare @Hoare_PLF proofs in Lean.

= A Formal Containment Protocol (_FCP_)

#let box_picture(
  prec: "Prec",
  post: "Post",
  code: "Output",
  proof: "Proof",
) = cetz.canvas({
  import cetz.draw: *

  // Set up coordinate system
  set-style(stroke: black + 1.5pt) // Reduced stroke weight

  let screen_color = rgb("#e8f4f8")
  // Human figure
  group(name: "human", {
    // Head
    circle((0.2, 2.0), radius: 0.2, fill: rgb("#f5d0c5"), stroke: black + 0.8pt)

    // Body
    line((0.2, 1.8), (0.2, 1.0), stroke: black + 0.8pt)

    // Arms
    line(
      (0.2, 1.6),
      (0.5, 2.1),
      stroke: black + 0.8pt,
    ) // Right arm pointing up at 45°
    line((0.2, 1.6), (0.0, 1.4), stroke: black + 0.8pt) // Left arm

    // Legs
    line((0.2, 1.0), (0.1, 0.7), stroke: black + 0.8pt)
    line((0.2, 1.0), (0.3, 0.7), stroke: black + 0.8pt)
  })

  // Main box with firm boundary
  let box_color = rgb("#888eb7")
  rect(
    (1, 0),
    (6, 4.7),
    stroke: box_color + 2pt,
    fill: box_color,
  ) // Scaled down dimensions

  let box_border_width = 1pt
  // Precondition input port - hole in box
  set-style(stroke: black + box_border_width)
  // Draw only top, right, and bottom sides
  line((0.4, 3.2), (1, 3.2), stroke: black + box_border_width) // Top
  line((0.4, 3.8), (1, 3.8), stroke: black + box_border_width) // Bottom
  content((0.3, 3.5), anchor: "center", text(
    [#prec],
    size: 8pt,
  )) // Smaller text

  // Postcondition input port - hole in box
  set-style(stroke: black + box_border_width)
  // Draw only top, right, and bottom sides
  line((0.4, 2.2), (1, 2.2), stroke: black + box_border_width) // Top
  line((0.4, 2.8), (1, 2.8), stroke: black + box_border_width) // Bottom
  content((0.3, 2.5), anchor: "center", text(
    [#post],
    size: 8pt,
  )) // Smaller text

  let screen_bottom = 1.75
  let screen_top = 4.1
  // Right output port (code output)
  set-style(stroke: black + box_border_width, fill: white)
  line(
    (6, screen_top),
    (7.5, screen_top),
    stroke: black + box_border_width,
  ) // Top
  line((6, 3.1), (7.5, 3.1), stroke: black + box_border_width) // Bottom
  content((6.75, 3.525), anchor: "center", text(
    [#code],
    size: 8pt,
  )) // Smaller text

  // Proof output port
  set-style(stroke: black + box_border_width, fill: white)
  line((6, 2.35), (7.5, 2.35), stroke: black + box_border_width) // Top
  line(
    (6, screen_bottom),
    (7.5, screen_bottom),
    stroke: black + box_border_width,
  ) // Bottom
  content((7.3, 2.05), anchor: "center", text(
    [#proof],
    size: 8pt,
  )) // Smaller text

  line((2, 0.5), (4, 0.5), stroke: screen_color + 1pt, mark: (end: ">"))

  // Robot
  group(name: "robot", {
    // Robot head
    circle(
      (3.5, 2.5),
      radius: 0.4375,
      fill: rgb("#d0d0d0"),
      stroke: black + 0.8pt,
    ) // Scaled head

    // Robot eyes
    circle(
      (3.2, 2.6),
      radius: 0.09,
      fill: rgb("#3498db"),
      stroke: black + 0.4pt,
    ) // Scaled eyes
    circle(
      (3.8, 2.6),
      radius: 0.09,
      fill: rgb("#3498db"),
      stroke: black + 0.4pt,
    ) // Scaled eyes

    // Robot mouth
    line((3.2, 2.35), (3.5, 2.3), stroke: black + 0.6pt) // Scaled mouth
    line((3.5, 2.3), (3.8, 2.35), stroke: black + 0.6pt) // Scaled mouth

    // Robot body
    rect(
      (3.075, 1.6),
      (3.925, 2.05),
      fill: rgb("#d0d0d0"),
      stroke: black + 0.8pt,
    ) // Scaled body

    // Robot arms
    line((3.075, 1.75), (2.85, 2.35), stroke: black + 0.8pt) // Scaled arms
    line((3.925, 1.75), (4.15, 2.35), stroke: black + 0.8pt) // Scaled arms

    // Robot legs
    line((3.225, 1.6), (3.225, 1.4), stroke: black + 0.8pt) // Scaled legs
    line((3.775, 1.6), (3.775, 1.4), stroke: black + 0.8pt) // Scaled legs

    // Robot antenna
    line((3.5, 2.9375), (3.5, 3.125), stroke: black + 0.6pt) // Scaled antenna
    circle(
      (3.5, 3.175),
      radius: 0.06,
      fill: red,
      stroke: black + 0.4pt,
    ) // Scaled antenna top
  })

  group(name: "checker", {
    // Screen/filter for output code
    rect(
      (5.35, screen_bottom),
      (6, screen_top),
      fill: screen_color,
      stroke: black + 0.8pt,
    ) // Scaled screen

    // Screen pattern
    for i in range(4) {
      line(
        (5.35, 2.05 + i * 0.585),
        (6, 2.05 + i * 0.585),
        stroke: black + 0.3pt,
      ) // Scaled pattern
    }
    for i in range(3) {
      line(
        (5.5 + i * 0.15, 1.75),
        (5.5 + i * 0.15, 4.1),
        stroke: black + 0.3pt,
      ) // Scaled pattern
    }
    // Lean4 label
    content((5.625, 1.6), text(size: 7pt)[Lean4], anchor: "center")
  })

  group(name: "globe", {
    // Simple world representation
    let x_coord = 7.9
    circle((x_coord, 2.925), radius: 0.7, fill: green, stroke: black + 0.8pt)
    content((x_coord, 2.925), text(size: 8pt)[World], anchor: "center")
  })
})

#let precondition_example = $lambda sigma. sigma x > 0$
#let postcondition_example = $lambda sigma. sigma x > 1$
#let code_example = ```<imp>
x := x + 1
 </imp>```
#let proof_example = ```<prf> ... </prf>```

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
  box_picture(
    prec: [#precondition_example],
    post: [#postcondition_example],
    code: [#code_example],
    proof: [#proof_example],
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

Let's walk through an FCP trace as you'd see it if you cloned our repo.

First, the user passes in a precondition and a postcondition. We will continue using the example in @fig:box-picture, passing in $x > 0$ and $x > 1$ for precondition and postcondition, respectively. Let's say for the sake of argument that the AI's first guess is `x := x - 1;`. Then, the proof agent will flail about until `MAX_ITERATIONS` is reached, since the program is incorrect, at which point it will report to the boundary its failed proof state. Then, the boundary replies "_try again, I'm not executing that code in the world_" and hands the program back to the AI, asking for another one. Suppose that this time, the AI finds `x := x + 1;`. This time, the proof agent converges and Lean reports an exit code of `0`. The AI sends the #imp program to the boundary and attests to it's correctness with the Lean program, which it also attaches.

The Lean program would look like this (Note it must be run with `lake build` in the appropriate lake project, as it has imports)
#figure(
  [```lean
    import Aesop
    import Imp
    open Imp

    example : {{fun st => st "x" > 0}}(imp { x := x + 1; }){{fun st => st "x" > 1}} := by

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
  caption: [Proof of the example hoare triple from @fig:box-picture],
) <fig:example-proof>

This file paired with an exit code of zero pinned to a particular Lean toolchain (version) can be signed in a GPG context for attestation of correctness.

= Experiments

#let experiments_spec = toml("experiments.toml")
#let format-samples-table = {
  let samples = experiments_spec.sample

  table(
    columns: 4,
    stroke: 0.5pt,
    align: (left, left, left, left),
    inset: 8pt,

    // Header row
    table.header(
      [*Sample*],
      [*Precondition*],
      [*Postcondition*],
      [*$forall$-bound metavariables*],
    ),

    // Data rows
    ..samples
      .enumerate()
      .map(((i, sample)) => (
        str(i + 1),
        raw(sample.precondition, lang: none),
        if "postcondition" in sample {
          if sample.postcondition.contains("\n") {
            // Multi-line postcondition - use block code
            raw(sample.postcondition, block: true, lang: none)
          } else {
            // Single-line postcondition - use inline code
            raw(sample.postcondition, lang: none)
          }
        } else { [—] },
        if "metavariables" in sample {
          raw(sample.metavariables, lang: none)
        } else { [—] },
      ))
      .flatten()
  )
}

#let filter-model-pins(human-name-whitelist) = {
  let models = experiments_spec.model

  let filtered-pins = models
    .filter(model => model.human_name in human-name-whitelist)
    .map(model => model.model_pin)

  // Format as a readable list
  if filtered-pins.len() == 1 {
    filtered-pins.first()
  } else if filtered-pins.len() == 2 {
    filtered-pins.join(" and ")
  } else {
    let last = filtered-pins.last()
    let rest = filtered-pins.slice(0, -1)
    rest.join(", ") + ", and " + last
  }
}

We test the following specifications

#format-samples-table

on #filter-model-pins(("snt4", "gpt41", "ops4")). For each run the #imp programmer and the prover are the same model (though in principle this doesn't matter).

*TODO*: See https://github.com/Beneficial-AI-Foundation/formal-containment/issues/7 for what I'd like to do.

= Related Work <sec:related>

Our work is well situated within _PCC_ @necula1997proof and the closely related certifying algorithms @mcconnell2011certifying. TODO: say more

The main difference between the current work and _Ctrl_ @greenblatt2024aicontrolimprovingsafety is we don't _emphasize_ intentional subversion (as in try to elicit it for stress testing).

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

Canary string: NDcwODA1MTY4MzQ0NjE4Njk4MA==

#bibliography("refs.bib")
