# Self-render engine

A tiny, from-scratch motion-graphics renderer — no AI video-gen model, no
headless browser, no Node/npm. Draws raw pixels directly, pipes them to
FFmpeg as `rawvideo`, and gets back an MP4.

## Two implementations, same logic

| | Language | Dependencies | When to use |
|---|---|---|---|
| **Primary** | Rust (`motion.rs`) | Only `std` + the `ffmpeg` binary. No Cargo.toml, no crates, no network needed to build. | Default choice — compiles with plain `rustc`. |
| **Fallback** | Python (`python_fallback/`) | Only the standard library + the `ffmpeg` binary. | Use when a Rust toolchain genuinely isn't available and can't be installed. |

Both implementations were developed together — the Python version was built
and visually verified first, then the Rust version was written to mirror
its logic line-for-line. `examples/kinetic_typography.rs` and
`python_fallback/demo_kinetic_typography.py` produce the same animation;
likewise for the `abstract_particles` pair.

**Important honesty note:** the Rust code in this skill has been carefully
written and cross-checked against the tested Python logic, but it has not
been compiled in the environment that produced this skill (no Rust
toolchain was available there). The first thing to do with it in any new
environment is a plain compile — if `rustc` reports an error, that's a
real bug to fix, not a sign something deeper is wrong with the approach.

## Capability check — which tier to use (do this first)

**Tier A — Rust (preferred).**
Check for `rustc` on PATH. If present, compile and run directly:
```
cd renderer/examples
rustc kinetic_typography.rs --edition 2021 -O -o kinetic_typography
./kinetic_typography
```
No `cargo`, no `Cargo.toml`, no network access needed — `motion.rs` has zero
external dependencies.

**Tier B — install Rust, then Tier A.**
If `rustc` is missing but there's a package manager and working network
access, install a Rust toolchain (e.g. `rustup-init` or the OS package
manager's `rustc`/`cargo` package) and proceed as Tier A. Mention to the
user that a toolchain was installed, since it's a real change to their
environment.

**Tier C — Python fallback.**
If Rust isn't available and can't be installed (no network, sandboxed, etc.)
but Python 3 and `ffmpeg` are available, use `python_fallback/` instead —
same drawing logic, same API shape (`Canvas`, `render_video`, easing
helpers), just in Python:
```
cd renderer/python_fallback
python3 demo_kinetic_typography.py
```

**Tier D — hand off to the user.**
If there's no code execution at all in the current environment, this skill
can't render anything itself. Show the relevant script (Rust or Python,
whichever is more likely to match what the user has locally) and give the
exact commands above, adapted to their filenames/choices. Don't silently
skip to the AI-prompt genre bucket unless the user says they'd rather have
a prompt for a third-party tool than run something locally themselves.

Re-check this every time the skill runs in a new session — don't assume
the tier from an earlier conversation still applies.

## Writing a new scene

Copy `examples/kinetic_typography.rs` (or the Python equivalent) as a
starting point. The pattern for both languages is the same:

1. Pick canvas size (`W`, `H`), `FPS`, and `DURATION`.
2. Write a `draw_frame(canvas, t, frame_index)` function that draws
   whatever should be visible at time `t` (in seconds). Use the easing
   helpers (`lerp`, `clamp01`, `ease_in_out`, `ease_out_back`) to animate
   properties smoothly over specific time windows rather than snapping.
3. Call `render_video(...)` once with that function.

`motion.rs` / `canvas.py` + `render.py` expose the same primitives:
`fill_rect`, `fill_circle`, `draw_line`, `draw_text` / `draw_text_centered`
(5x7 bitmap font, built in — no font files needed), and alpha blending on
every draw call for fades.

## What this engine is (and isn't) good for

Good fit — genres that are naturally describable as shapes/text/motion:
kinetic typography, abstract/particle visuals, simple diagrams and data
visualization, logo/icon motion graphics, deterministic music-visualizer
pulses (see `references/self-render/`).

Not a good fit — anything that needs photorealistic or richly-detailed
imagery (human faces, realistic landscapes, detailed character designs,
believable animal motion). That's what the AI-prompt genre bucket in
`references/ai-prompt/` is for — see the main `SKILL.md` for the full
decision process.
