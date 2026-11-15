# Music Visualizer (self-render)

Rhythmic, pulsing visuals — a natural extension of the abstract/particle
pattern, driven by a tempo instead of arbitrary motion.

## How to approach it
This engine can't analyze an actual audio file's beats (no audio-decoding
library, by design — zero dependencies). Instead, drive the animation with
a **BPM parameter the user supplies**:
1. Ask the user for the track's BPM (or an estimate — "fast", "medium",
   "slow" maps roughly to ~140+, ~100-120, ~70-90).
2. Convert BPM to a beat period: `beat_seconds = 60.0 / bpm`.
3. Drive a pulse with something like
   `pulse = abs(sin(t / beat_seconds * PI))` so it peaks once per beat.
4. Apply that pulse to element size, brightness, or position offset —
   reuse the abstract/particle pattern (`references/self-render/abstract-experimental.md`)
   as the base visual, with the pulse wired into the particle size/alpha
   instead of a free-running sine wave.

## Getting the render in sync with the actual audio file
This engine only produces the silent video track. To combine it with the
real audio:
1. Render the visual clip at the exact duration of the song (or the
   section needed).
2. Use `scripts/render_ffmpeg.py add-audio --mode replace` to attach the
   real audio file to the rendered clip.
3. Because the pulse was driven by the BPM the user supplied rather than
   real beat-detection, double-check the sync by eye/ear after muxing —
   it'll be close but not frame-perfect to the actual beat unless the BPM
   given was exact and the track has a steady, consistent tempo throughout.

## When to still reach for an AI-prompt instead
If true audio-reactive analysis (actual waveform/frequency response, not a
BPM estimate) is required, that's outside this engine's scope — consider
whether a dedicated audio-visualizer tool (outside this skill) is a better
fit than either self-render or a generic AI video-gen prompt.
