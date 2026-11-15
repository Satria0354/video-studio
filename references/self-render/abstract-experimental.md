# Abstract / Experimental (self-render)

Non-representational motion — particles, orbiting shapes, geometric
patterns, pulsing glows. This is arguably the single best-suited genre for
the self-render engine: there's no face, no anatomy, no "does this look
real" bar to clear — just parametric motion math.

## How to approach it
1. Decide on a motion pattern: orbiting particles, a grid of pulsing
   shapes, expanding/contracting rings, flowing lines. Simple trigonometric
   motion (sine/cosine offsets per element, phase-shifted so elements don't
   move in lockstep) goes a long way.
2. Vary color smoothly over time per element using phase-shifted sine waves
   per RGB channel — this gives a hue-cycling effect without needing an
   HSL-to-RGB conversion.
3. Add a soft "glow" by drawing the same shape twice: once at full
   opacity/small radius, once larger and much more transparent.
4. A gentle pulsing center/background element ties the composition together
   and is cheap to add.

## Reference implementation
`renderer/examples/abstract_particles.rs` (Rust) and
`renderer/python_fallback/demo_abstract_particles.py` (Python) implement a
ring of color-cycling orbiting particles with glow — copy and adapt the
particle count, motion pattern, and palette rather than starting from
scratch.

## When to still reach for an AI-prompt instead
If the user wants something more painterly/organic (flowing smoke, fluid
simulation, fractal-like detail) rather than clean geometric motion, that's
harder to fake convincingly with simple primitives — consider
`references/ai-prompt/` for that specific look instead.
