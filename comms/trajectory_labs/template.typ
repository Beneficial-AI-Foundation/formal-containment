#import "@preview/touying:0.6.1": *
#import "@preview/touying-unistra-pristine:1.4.0": *
#import "fns.typ" as fns
#let experiments_spec = toml("assets/experiments.toml")
#let experiment_results = toml("assets/results_20250620-0029.toml")

#show: unistra-theme.with(aspect-ratio: "16-9", config-info(
  title: [Formal Containment],
  subtitle: [_Proof-carrying code and AI safety_],
  author: [Quinn Dougherty],
  date: [June 26, 2025 | Trajectory Labs],
  logo: image("assets/img/baif.svg"),
))

#title-slide(logo: image("assets/img/baif.svg"))

#let imp = `imp`
#let assertion_t = $"Env" -> bb(P)$
#let env_t = `string` + $->$ + `int64`
#let hoare_triple(
  prec: "P",
  command: "Command",
  post: "Q",
) = "{" + prec + "}" + command + "{" + post + "}"

#let box_picture = fns.box_picture(
  prec: [$lambda sigma. sigma x > 0$],
  post: [$lambda sigma. sigma x > 1$],
  code: [```<imp>
      x := x + 1;
    </imp>```],
  proof: [```<prf> ... </prf>```],
)
#let box_figure = figure(
  align(center)[#scale(200%)[#box_picture]],
  caption: text(
    size: 20pt,
  )[Box protocol at example specification. The AI accepts a specification (formally $(#assertion_t) times (#assertion_t)$)) and returns proof-carrying code, with the option of returning nothing.],
  gap: 3.5em,
)

==
#box_figure <fig:box-picture>

= Background

#focus-slide(theme: "neon", image("assets/img/somehow-boxing-returned.jpg"))

== Two old literatures

- In Yudkowsky 2002 @Yudkowsky2002AIBox, _AI boxing_ is the attempt to *contain* AI by policing its interface to the world.
- In Necula 1997 @necula1997proof, _proof-carrying code_ is the attempt to *tag* code with a proof of it's correctness.

== AI Containment (Boxing)

#quote(attribution: [Yudkowsky 2002 @Yudkowsky2002AIBox])[_When we build AI, why not just keep it in sealed hardware that can’t affect the outside world in any way except through one communications channel with the original programmers?  That way it couldn’t get out until we were convinced it was safe_.]

Spoiler alert: Yudkowsky recommends against trying this.

#align(center)[#image("assets/img/somehow-boxing-returned.jpg")]

== Somehow AI Boxing Returned

Recent work from AI Control (@greenblatt2024aicontrolimprovingsafety @bhatt2025ctrlzcontrollingaiagents) and Safeguarded AI (@Dalrymple2024SafeguardedAI) is thinking through containment to bootstrap into early stages of the transition.

== Proof-Carrying Code

#quote(attribution: [Necula 1997 @necula1997proof])[The untrusted code producer must supply with the code a safety proof that attests to the code's adherence to a previously defined safety policy.]

Conceptually like *$exists c : "program", P c$* where $P$ is some predicate on programs.

Or the dependent pair *$(c, pi) : "program" times P c$* (i.e., $pi$ is a proof of $P c$)

#align(center)[#image("assets/img/somehow-pcc.jpg")]

== Somehow Proof-Carrying Code returned

Recently Kamran et al 2024 @kamran2024pc3 revived proof-carrying code in the form of _proof-carrying code completions_, language model calls that provide verified dafny code.

= Formal Containment Protocol

#focus-slide(theme: "neon")[Formal Containment Protocol]

== Box

#box_figure

== Preliminaries: notations

- $bb(P)$ := the type of propositions
- #imp := the minimal imperative programming language with expressions valued in integers containing skip, sequence, assign, if, and while statements
- $"Env"$ := state type, assigning variable names to values (formally #env_t)
- $"Assertion"$ := assertion type, predicates on state (formally #assertion_t)
- $"exec"$ := execution, a function from a command and a state that returns a state (formally, $#imp -> "Env" -> "Env"$)

== Preliminaries: hoare logic
A _hoare triple_ is a ternary predicate expressing when a command sends an assertion to another assertion, quantified over all states. Formally,
$
  "hoare" := P c Q mapsto \
  forall (sigma_1 sigma_2 : "Env"),
  P sigma_1 ->
  "exec" c sigma_1 = sigma_2 ->
  Q sigma_2 : \
  "Assertion" -> #imp -> "Assertion" -> bb(P)
$
and denoted $"hoare" P c Q =$ #hoare_triple(prec: [$P$], command: [\<#imp\> $c$ </#imp>], post: [$Q$]). A _term_ of type #hoare_triple(prec: [$P$], command: [\<#imp\> $c$ </#imp>], post: [$Q$]) is a proof that the triple is true.

== Containment Protocol: example trace

#figure(
  align(center)[#fns.example_trace],
  caption: text(
    size: 19pt,
  )[Example trace of the Formal Containment Protocol showing the decision fork at proof attempt, with failure leading to retry and success leading to safe execution.],
  gap: 1em,
) <fig:example-trace>

== Example PCC pair

#figure(
  [```lean
    example : {{astn x > 0}}(imp {
      x := x + 1;
    }){{astn x > 1}} := by auto_hoare_pos
    ```],
  caption: [Proof of the example hoare triple from @fig:box-picture.],
) <fig:example-proof>

= Experiments
#focus-slide(theme: "neon")[Experiments]

== Specification samples

#text(size: 16pt)[#fns.format-samples-table(experiments_spec)]

== Experiment results

#align(center)[#text(size: 10pt)[#fns.display_experiment_results(
      experiment_results,
    )]]

== Verification burden

The *verification burden* $k$ says that if it costs $x$ tokens to complete the program, then it costs $k x$ tokens to prove it correct.
- Divergence is hardly evidence that the program completion is incorrect, because our proof performance is so poor.

== Verification burden vs cost

#figure(
  text(size: 10pt)[#scale(165%)[#fns.plot_verification_burden_vs_cost(
        experiments_spec,
        experiment_results,
      )]],
  caption: [Verification burden vs model cost. Each point represents a successful verification attempt.],
  gap: 3em,
) <fig:verification-burden-vs-cost>

== Caveat
- *Verification burden is deflated by my custom tactic*. Fewer custom tactics probably means more token cost (or more intelligent model), for the same amount of performance.

= Future Work
#focus-slide(theme: "neon")[Future Work]

== Non-toy languages and proof stacks
- Make realistic verification burden estimates that would apply to actually useful programming

== Elicit subversive code as in @greenblatt2024aicontrolimprovingsafety
- In Greenblatt et al 2024 they elicit subversive/backdoored code to stress test their protocol.

#focus-slide(theme: "neon")[Strategic outlook]

= Strategically...
TODO

= End
== Thanks

#bibliography("refs.bib")

#focus-slide(theme: "neon")[`quinn@beneficialaifoundation.org`]
