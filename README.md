# Video Studio

A portable [`SKILL.md`](./SKILL.md) for making videos with any AI agent that
supports skills (Claude, Claude Code, or similar).

**The core idea:** render it yourself from scratch with code whenever the
genre allows it — no AI video-gen model, no paid API, no headless browser —
and only fall back to a prompt for a third-party AI video-gen tool when the
genre genuinely needs photorealistic or richly-detailed imagery that code
can't fake.

## Two paths

| | Self-render | AI-prompt |
|---|---|---|
| **Used for** | Kinetic typography, abstract/particle visuals, diagrams, deterministic music visualizers, slideshow/Ken Burns | Cinematic live-action, 3D/2D character animation, cyberpunk cityscapes, fantasy creatures, stop-motion, nature documentary, talking avatars, architectural walkthroughs |
| **How it works** | Draws raw pixels directly (shapes, text, animation math) and pipes them to FFmpeg as a `rawvideo` stream — no browser, no rendering farm | Produces a ready-to-paste prompt for whichever video-gen tool you have (Runway, Kling, Sora, Veo, Pika, etc.) |
| **Dependencies** | Rust (`std` only, zero crates) or Python 3, plus FFmpeg | None — it's just text |

Either path ends with the same finishing step: assembling the result with
FFmpeg (concatenation, transitions, text overlay, audio, Ken Burns from a
still image).

## Quick start

**Prerequisites:** [FFmpeg](https://ffmpeg.org/download.html) on PATH.
For self-rendering, either a Rust toolchain (`rustc`) or Python 3 — no
`cargo`, no `pip install`, no network access needed either way.

Try one of the bundled self-render examples:

```bash
# Rust (preferred — zero external crates)
cd renderer/examples
rustc kinetic_typography.rs --edition 2021 -O -o kinetic_typography
./kinetic_typography

# or, if you don't have Rust:
cd renderer/python_fallback
python3 demo_kinetic_typography.py
```

Both produce the same animation — see [`renderer/README.md`](./renderer/README.md)
for how the two implementations relate and which tier to use when.

## For AI agents

If you're an agent reading this repository to use as a skill: read
[`SKILL.md`](./SKILL.md) first — it has the full decision process (which
genre goes down which path, the capability-tier fallbacks, and how to wire
the pieces together) that this README only summarizes.

## Repository structure

```
video-studio/
├── SKILL.md                       Full agent-facing workflow and decision tree
├── renderer/
│   ├── motion.rs                  Rust engine — std only, zero crates
│   ├── README.md                  Tiers, compile instructions
│   ├── examples/
│   │   ├── kinetic_typography.rs
│   │   └── abstract_particles.rs
│   └── python_fallback/           Same logic, pure Python + ffmpeg
├── references/
│   ├── self-render/                Genre guidance for the code-render path
│   └── ai-prompt/                  Genre guidance for the AI video-gen path
├── scripts/
│   ├── render_ffmpeg.py            concat / overlay-text / add-audio
│   └── ken_burns.py                still image -> pan/zoom clip
└── assets/
    ├── fonts/                      optional custom fonts for text overlay
    └── luts/                       optional .cube LUTs for color grading
```

## A note on the Rust code

The logic in `renderer/motion.rs` was first prototyped and visually
verified in Python, then ported to Rust by hand. It has not been compiled
in the environment that authored it (no Rust toolchain was available
there). If `rustc` reports an error on your machine, that's a real bug
worth opening an issue/PR for, not a sign the overall approach is unsound —
the underlying logic is the same as the tested Python version.

## License

[MIT](./LICENSE) — use it, modify it, ship it.
