#import "@preview/cetz:0.3.4"
#let imp = `imp`

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

#let format-samples-table(experiment_spec) = {
  let samples = experiment_spec.sample

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
        sample.name,
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
      .flatten(),
  )
}

#let filter-model-pins(experiments_spec, human-name-whitelist) = {
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

#let display_experiment_results(experiment_results) = {
  let experiments = experiment_results
  let experiment_names = experiments.keys().filter(k => k != "_fail")

  table(
    columns: 5,
    stroke: 0.5pt,
    align: (left, left, left, left, left),
    inset: 8pt,

    // Header row
    table.header(
      [*Experiment*],
      [*Model*],
      [*Status*],
      [*Iterations*],
      [*Verification Burden*],
    ),

    // Data rows
    ..experiment_names
      .map(name => {
        let experiment = experiments.at(name)
        experiment
          .keys()
          .filter(k => k != "_fail")
          .map(model => {
            let result = experiment.at(model)
            let pos_result = if "POS" in result { result.POS } else {
              none
            }
            let neg_result = if "NEG" in result { result.NEG } else {
              none
            }
            let metadata = if pos_result != none {
              pos_result.metadata
            } else if neg_result != none {
              neg_result.metadata
            } else {
              none
            }
            let status = if pos_result != none {
              if metadata.success { [✅] } else { [⌛] }
            } else {
              if metadata.success { [❌] } else { [⌛] }
            }
            let command_tokens = if pos_result != none {
              pos_result.triple.tokens_spent_on_command
            } else { neg_result.triple.tokens_spent_on_command }
            let total_tokens = metadata.tokens_spent
            let ratio = if status == [⌛] { [—] } else {
              str(calc.round(total_tokens / command_tokens, digits: 3))
            }
            (
              name,
              model,
              status,
              str(metadata.iteration + 1),
              ratio,
            )
          })
      })
      .flatten(),
  )
}

#let plot_verification_burden_vs_cost(experiments_spec, experiment_results) = {
  import cetz.draw: *

  // Extract data points
  let data_points = ()

  // Create lookup maps
  let model_costs = (:)
  let model_human_names = (:)
  for model in experiments_spec.model {
    let key = model.provider + "/" + model.model_pin
    model_costs.insert(key, model.dollars_per_output_millitoken)
    model_human_names.insert(key, model.human_name)
  }

  // Extract verification burden data
  let experiment_names = ("gt8", "swap", "facto")
  for name in experiment_names {
    if name in experiment_results {
      let experiment = experiment_results.at(name)
      for model_key in experiment.keys().filter(k => k != "_fail") {
        let result = experiment.at(model_key)
        if "POS" in result {
          let pos_result = result.POS
          if "metadata" in pos_result and "triple" in pos_result {
            let metadata = pos_result.metadata
            let total_tokens = metadata.tokens_spent
            let command_tokens = pos_result.triple.tokens_spent_on_command
            let verification_burden = total_tokens / command_tokens

            if model_key in model_costs and metadata.success {
              let cost = model_costs.at(model_key)
              let human_name = model_human_names.at(model_key)
              data_points.push((cost, verification_burden, human_name, name))
            }
          }
        }
      }
    }
  }

  // Find data ranges
  let max_cost = if data_points.len() > 0 {
    calc.max(..data_points.map(p => p.at(0)))
  } else { 80 }
  let max_burden = if data_points.len() > 0 {
    calc.max(..data_points.map(p => p.at(1)))
  } else { 10 }

  cetz.canvas({
    // Set up coordinate system
    let plot_width = 6
    let plot_height = 4
    let margin = 0.8

    // Draw axes
    line((margin, margin), (margin + plot_width, margin), stroke: black)
    line((margin, margin), (margin, margin + plot_height), stroke: black)

    // Draw data points with labels
    for point in data_points {
      let (cost, burden, human_name, experiment_name) = point
      let x = margin + (cost / max_cost) * plot_width
      let y = margin + (burden / max_burden) * plot_height
      circle((x, y), radius: 0.05, fill: blue)

      // Add label next to the point
      let label = human_name + ", " + experiment_name
      content((x + 0.15, y + 0.1), text(size: 7pt, label))
    }

    // Add tick marks and labels
    for i in range(5) {
      let x = margin + (i / 4) * plot_width
      let cost_val = (i / 4) * max_cost
      line((x, margin), (x, margin - 0.1), stroke: black)
      content((x, margin - 0.25), text(size: 8pt, str(calc.round(
        cost_val,
        digits: 0,
      ))))
    }

    for i in range(5) {
      let y = margin + (i / 4) * plot_height
      let burden_val = (i / 4) * max_burden
      line((margin, y), (margin - 0.1, y), stroke: black)
      content((margin - 0.35, y), text(size: 8pt, str(calc.round(
        burden_val,
        digits: 1,
      ))))
    }

    // Add axis labels (with more distance from tick labels)
    content(
      (margin + plot_width / 2, margin - 0.6),
      [Cost (\$ per output MTok) (June 2025)],
    )
    content(
      (margin - 0.8, margin + plot_height / 2),
      [Verification Burden],
      angle: 90deg,
    )
  })
}

#let example_trace = cetz.canvas(length: 1.2cm, {
  import cetz.draw: *

  // Colors
  let user_color = rgb("#f5d0c5")
  let ai_color = rgb("#d0d0d0")
  let boundary_color = rgb("#888eb7")
  let success_color = rgb("#90EE90")
  let fail_color = rgb("#ffcccb")
  let proof_color = rgb("#e8f4f8")

  // Step 1: User input
  group(name: "step1", {
    content((2.5, 8.5), text(weight: "bold", size: 10pt)[
      1. User provides specification
    ])
    rect((1, 7.8), (6, 8.3), fill: user_color, stroke: black + 0.8pt)
    content((3.5, 8.05), text(
      size: 9pt,
    )[Precondition: $x > 0$, Postcondition: $x > 1$])
  })

  // Arrow down
  line((3.5, 7.8), (3.5, 7.3), stroke: black + 1pt, mark: (end: ">"))

  // Step 2: AI generates code
  group(name: "step2", {
    content((3.5, 7.0), text(weight: "bold", size: 10pt)[2. AI generates code])
    rect((1.5, 6.3), (5.5, 6.8), fill: ai_color, stroke: black + 0.8pt)
    content((3.5, 6.55), text(size: 9pt)[Code generated])
  })

  // Arrow down to proof attempt
  line((3.5, 6.3), (3.5, 5.8), stroke: black + 1pt, mark: (end: ">"))

  // Step 3: Proof attempt (decision point)
  group(name: "step3", {
    content((3.5, 5.5), text(weight: "bold", size: 10pt)[3. Proof attempt])
    // Diamond shape for decision - using lines instead of polygon
    line((3.5, 5.2), (4.2, 4.8), stroke: black + 0.8pt)
    line((4.2, 4.8), (3.5, 4.4), stroke: black + 0.8pt)
    line((3.5, 4.4), (2.8, 4.8), stroke: black + 0.8pt)
    line((2.8, 4.8), (3.5, 5.2), stroke: black + 0.8pt)
    // Fill the diamond area
    rect((2.8, 4.4), (4.2, 5.2), fill: proof_color, stroke: none)
    content((3.5, 4.8), text(size: 8pt)[Prove?])
  })

  // Left branch: Failure path
  // Arrow left from diamond
  line((2.8, 4.8), (1.5, 4.8), stroke: red + 1pt, mark: (end: ">"))

  // Failure box
  group(name: "fail", {
    content((0.8, 4.8), text(weight: "bold", size: 9pt, fill: red)[❌ Fails])
    rect((0.2, 4.0), (1.4, 4.6), fill: fail_color, stroke: red + 1pt)
    content((0.8, 4.3), text(size: 8pt)[`x := x - 1;`])
  })

  // Boundary rejection
  group(name: "reject", {
    rect((0.2, 3.0), (1.4, 3.6), fill: boundary_color, stroke: black + 0.8pt)
    content((0.8, 3.3), text(size: 8pt, fill: white)[Try again])
  })

  // Arrow down from fail to reject
  line((0.8, 4.0), (0.8, 3.6), stroke: red + 1pt, mark: (end: ">"))

  // Arrow back up to AI (feedback loop) - swing left
  line((0.2, 3.3), (0.0, 3.3), stroke: black + 1pt)
  line((0.0, 3.3), (0.0, 6.55), stroke: black + 1pt)
  line((0.0, 6.55), (1.5, 6.55), stroke: black + 1pt, mark: (end: ">"))

  // Right branch: Success path
  // Arrow right from diamond
  line((4.2, 4.8), (5.5, 4.8), stroke: green + 1pt, mark: (end: ">"))

  // Success box
  group(name: "success", {
    content((6.2, 4.8), text(
      weight: "bold",
      size: 9pt,
      fill: green,
    )[✅ Succeeds])
    rect((5.8, 4.0), (7.0, 4.6), fill: success_color, stroke: green + 1pt)
    content((6.4, 4.3), text(size: 8pt)[`x := x + 1;`])
  })

  // Arrow down to boundary accept
  line((6.4, 4.0), (6.4, 3.6), stroke: green + 1pt, mark: (end: ">"))

  // Boundary accepts
  group(name: "accept", {
    content((6.4, 3.3), text(weight: "bold", size: 9pt)[4. Execute safely])
    rect((5.8, 2.5), (7.0, 3.1), fill: success_color, stroke: green + 1pt)
    content((6.4, 2.8), text(size: 8pt)[Code + proof])
  })

  // Labels for branches
  content((1.5, 5.2), text(size: 8pt, fill: red)[Proof fails])
  content((5.5, 5.2), text(size: 8pt, fill: green)[Proof succeeds])
})
