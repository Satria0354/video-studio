# Diagrams / Data Visualization (self-render)

Animated charts, flowcharts, and simple explainer diagrams — another
strong fit for code-based rendering, since the content is inherently
geometric (bars, lines, boxes, arrows, labels).

## How to approach it
- **Animated bar/line chart:** animate each bar's height (or each line
  point's position) from a start value to its data value using
  `ease_in_out` over a shared time window, staggered slightly per bar/point
  (e.g. bar `n` starts animating at `t = n * 0.1`) so they don't all move in
  perfect lockstep.
- **Flowchart/process diagram:** draw boxes (`fill_rect`) and connecting
  lines (`draw_line`) with labels (`draw_text`), animating each node's
  entrance in sequence (fade in / pop in) to walk the viewer through the
  process step by step rather than showing the whole diagram at once.
- **Counters/big numbers:** animate a number counting up using `lerp`
  between a start and end value, formatting the interpolated value as text
  each frame.

## Reference implementation
There's no bundled example for this one yet — build it the same way as
`renderer/examples/kinetic_typography.rs`: a `draw_frame(canvas, t, i)`
function using `fill_rect` for bars/boxes, `draw_line` for connectors/axes,
and `draw_text`/`draw_text_centered` for labels, with `ease_in_out` driving
each element's entrance.

## Limits
The built-in font (5x7 bitmap, A–Z/0–9/basic punctuation only) is fine for
short labels and numbers but not for dense paragraphs of text or precise
typographic control — keep diagram labels short.
