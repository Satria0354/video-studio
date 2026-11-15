---
name: video-studio
description: Make a video end-to-end — self-rendered from scratch with code whenever the genre allows it (kinetic typography, abstract/particle visuals, diagrams, deterministic music visualizers), falling back to a ready-to-paste prompt for a third-party AI video-gen tool (Runway, Kling, Sora, Veo, Pika, etc.) only when the genre genuinely needs photorealistic or richly-detailed imagery (cinematic live-action, 3D/2D character animation, cyberpunk cityscapes, fantasy creatures, stop-motion, nature documentary, talking avatars, architectural walkthroughs) — then assembles the result with FFmpeg (concatenation, transitions, text overlay, audio, Ken Burns from a still image). Use this skill whenever a user wants to make a video with AI or with code, needs a video-gen prompt, wants to turn an idea/script/image into a video, wants clips joined/captioned/scored, or wants a still image turned into a moving clip. Self-render path requires Rust (preferred, zero external crates) or Python (fallback) plus FFmpeg; degrades gracefully to handing the user runnable code if no execution environment is available, and to the AI-prompt path if the user would rather not run anything locally.
---

# Video Studio

One skill covering the whole path from idea to finished video file, built
around a simple priority: **render it yourself from scratch with code
whenever the genre allows it; only ask the user to go to a third-party AI
video-gen tool when the genre genuinely can't be faked with shapes/text/
motion math** (photorealistic people, detailed creatures, believable
real-world environments). Either path ends the same way: a finished file,
optionally assembled/captioned/scored with FFmpeg.

## Step 1 — Identify the genre and pick a path

| The user wants... | Path | Where to look |
|---|---|---|
| Kinetic typography / animated text, lyric-video style | **Self-render** | `references/self-render/kinetic-typography.md` |
| Abstract/particle visuals, geometric motion | **Self-render** | `references/self-render/abstract-experimental.md` |
| Music visualizer (rhythmic pulsing, given a BPM) | **Self-render** | `references/self-render/music-visualizer.md` |
| Animated chart/diagram/flowchart/explainer | **Self-render** | `references/self-render/diagram-dataviz.md` |
| Slideshow / pan-zoom from a still photo | **Self-render** (FFmpeg only) | `scripts/ken_burns.py` — no renderer code needed |
| Cinematic live-action, realistic human subjects | AI-prompt | `references/ai-prompt/cinematic-live-action.md` |
| Drone/aerial realistic footage | AI-prompt | `references/ai-prompt/drone-aerial.md` |
| 3D animated character (Pixar/game-cinematic look) | AI-prompt | `references/ai-prompt/3d-animation.md` |
| 2D anime style | AI-prompt | `references/ai-prompt/2d-anime.md` |
| Product commercial (photoreal hero shots) | AI-prompt | `references/ai-prompt/product-commercial.md` |
| Cyberpunk / sci-fi cityscape | AI-prompt | `references/ai-prompt/cyberpunk-scifi.md` |
| Fantasy / epic creatures and scale | AI-prompt | `references/ai-prompt/fantasy-epic.md` |
| Stop-motion / claymation look | AI-prompt | `references/ai-prompt/stop-motion.md` |
| Vintage / retro film (VHS, Super 8) | AI-prompt | `references/ai-prompt/vintage-retro-film.md` |
| Talking avatar / presenter | AI-prompt | `references/ai-prompt/talking-avatar.md` |
| Horror / thriller atmosphere (photoreal) | AI-prompt | `references/ai-prompt/horror-thriller.md` |
| Nature documentary (real wildlife/landscapes) | AI-prompt | `references/ai-prompt/nature-documentary.md` |
| Architectural walkthrough (photoreal interiors) | AI-prompt | `references/ai-prompt/architectural-walkthrough.md` |

If it's ambiguous or blends both (e.g. "kinetic typography over a
cyberpunk city background"), split it: self-render the typography layer,
get an AI-prompt for the background plate, then composite/assemble with
FFmpeg (`scripts/`).

If a request doesn't fit any self-render genre above but also doesn't
clearly need photorealism, lean toward trying self-render first — a simple
geometric interpretation of most ideas is possible, and it avoids the
dependency on a third-party tool entirely.

## Step 2 — If self-render: gather specs, check capability tier, then build

1. **Ask for (or infer from what's already given) the duration and
   aspect ratio/resolution.** Don't silently keep the bundled examples'
   hardcoded `DURATION`, `W`, and `H` constants — those are starting
   points for learning the API, not the user's actual request. Typical
   resolutions: 1920x1080 (16:9, landscape), 1080x1920 (9:16, Reels/
   Shorts/TikTok), 1080x1080 (1:1, square).
2. **Check capability tier — do this every time**, don't assume a
   previous session's result still applies:
   - **Tier A (preferred): Rust.** If `rustc` is on PATH, use
     `renderer/motion.rs` + `renderer/examples/` as a starting point.
     Zero external crates — compiles with plain `rustc`, no `cargo`, no
     network.
   - **Tier B: install Rust, then Tier A.** If `rustc` is missing but
     there's a package manager and working network access, install a
     toolchain and proceed as Tier A. Tell the user briefly that you did
     this.
   - **Tier C: Python fallback.** If Rust isn't available or installable
     but Python 3 + FFmpeg are, use `renderer/python_fallback/` instead —
     same API shape, same visual result, just slower to render.
   - **Tier D: hand off.** No code execution at all → show the relevant
     source file and the exact commands to run it locally (see
     `renderer/README.md`), rather than silently falling back to an
     AI-prompt for a genre that doesn't need one. Only switch to the
     AI-prompt path instead if the user says they'd rather have a prompt
     than run code locally.
3. Read the matching `references/self-render/*.md` file for genre-specific
   composition/animation guidance before writing the scene.
4. **Write the scene for the requested duration, not the example's.**
   Copying `kinetic_typography.rs`'s structure is fine, but its specific
   animation beats (e.g. "line 1 enters at t=0.2s, line 2 at t=1.0s, bar
   at t=2.0s") were timed for a 4-second clip. If the requested duration
   is different, retime every beat to fit it — stretch/compress the
   existing beats proportionally and/or add more beats/elements — so the
   full requested duration stays visually active. Never just raise
   `DURATION` and leave the screen frozen/static after the last
   hardcoded animation finishes.

Full detail on tiers, the drawing API, and the honesty note about this
Rust code not having been compiled in the environment that authored it:
`renderer/README.md`.

## Step 3 — If AI-prompt: gather specs, then write the prompt

1. Ask which tool the user plans to use (Runway, Kling, Sora, Veo, Pika,
   or "whatever's available" / "I don't know"). If named, check
   `references/ai-prompt/tool-notes.md` for anything tool-specific;
   otherwise write a portable natural-language prompt.
2. Ask for duration, aspect ratio, mood, and whether there's a reference
   image (image-to-video should describe motion/camera only, not
   re-describe the subject's appearance).
3. Read the matching genre file in `references/ai-prompt/` for vocabulary
   and a prompt template, then build the prompt using the universal
   structure: `[Shot/framing] of [subject] [one specific action], in
   [setting], [camera movement], [lighting], [style keywords], [mood]`.
4. Offer 2-3 meaningfully different variations for an open-ended request;
   one solid prompt for a well-specified one.
5. Flag real limitations honestly: character consistency across separate
   generations is unreliable, clip length is usually short (4-10s) so a
   longer video means multiple chained clips, and commercial-use rights
   depend on the specific tool's terms.

## Step 4 — Assemble with FFmpeg (either path)

Once there are one or more finished clips (self-rendered, AI-generated, or
both) and/or a still image, use `scripts/` to finish the job:

- `scripts/render_ffmpeg.py concat` — join clips, hard cut or crossfade
- `scripts/render_ffmpeg.py overlay-text` — burn in captions/titles
  (supports a custom font from `assets/fonts/` via `--fontfile`)
- `scripts/render_ffmpeg.py add-audio` — replace or mix in music/narration
- `scripts/ken_burns.py` — turn a still image into a panning/zooming clip

**Same capability check applies here, independently:** Tier 1 — `ffmpeg`
already on PATH, run the scripts directly. Tier 2 — missing but
installable (package manager + network), install then run. Tier 3 — can't
run or install, show the script and the exact command to run locally.

## Copyright and safety (applies to both paths)

- Never write a prompt, or self-render a scene, that names or reproduces a
  copyrighted character, franchise, or real celebrity's likeness. If the
  user's reference is clearly a copyrighted character/franchise, build an
  **original** visual equivalent instead and say plainly that's what's
  happening.
- Decline anything aimed at a real, identifiable private person's likeness
  without consent, non-consensual intimate content, or anything else
  outside normal content-safety bounds — this applies regardless of
  genre, path, or tool.

## Repository layout

```
video-studio/
├── SKILL.md                       (this file)
├── README.md                      Human-facing overview and quick start
├── LICENSE                        MIT
├── .gitignore
├── renderer/
│   ├── motion.rs                  Rust engine — std only, zero crates
│   ├── README.md                  Tiers, compile instructions, honesty note
│   ├── examples/
│   │   ├── kinetic_typography.rs
│   │   └── abstract_particles.rs
│   └── python_fallback/           Same logic, pure Python + ffmpeg
│       ├── canvas.py
│       ├── render.py
│       ├── demo_kinetic_typography.py
│       └── demo_abstract_particles.py
├── references/
│   ├── self-render/                 Genre guidance for the code-render path
│   └── ai-prompt/                   Genre guidance for the AI video-gen path
├── scripts/
│   ├── render_ffmpeg.py            concat / overlay-text / add-audio
│   └── ken_burns.py                still image -> pan/zoom clip
└── assets/
    ├── fonts/                      optional custom fonts for text overlay
    └── luts/                       optional .cube LUTs for color grading
```
