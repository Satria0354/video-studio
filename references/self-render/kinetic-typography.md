# Kinetic Typography (self-render)

Text-driven motion graphics — this is one of the best-suited genres for the
self-render engine (`renderer/`), since the content IS shapes and text, not
photorealistic imagery.

## How to approach it
1. Break the message into short lines/phrases — one idea per on-screen beat,
   similar to how you'd pace a lyric video.
2. Pick an entrance animation per line: pop-in with overshoot
   (`ease_out_back`), slide-up fade-in (`ease_in_out` + alpha), or a simple
   cut. Don't use the same entrance for every line — vary it a little.
3. Time each line's active window explicitly (e.g. line 1 visible from
   t=0.2s to t=3.0s, line 2 from t=1.0s onward) rather than showing
   everything from frame 0.
4. Layer in simple background motion (slowly drifting translucent circles,
   a subtle color gradient shift) so it doesn't feel static — see
   `renderer/examples/kinetic_typography.rs` for a working example of
   exactly this.
5. A pulsing accent (underline bar, dot, small shape) timed to a beat or to
   the end of the last line is a cheap way to add punctuation/finality.

## Reference implementation
`renderer/examples/kinetic_typography.rs` (Rust) and
`renderer/python_fallback/demo_kinetic_typography.py` (Python) implement
exactly this pattern — a title pops in, a second line slides up while
fading in, and a pulsing bar appears last. Copy and adapt rather than
starting from a blank file.

## Limits of the built-in font
The bitmap font in `motion.rs`/`canvas.py` is a simple 5x7 pixel font
covering A–Z, 0–9, space, and basic punctuation (`. , ! ? ' - :`). It's
legible but blocky/retro-looking by nature — fine for a stylized look, but
if the user wants an elegant/branded typeface, that's beyond what this
built-in font can do. In that case, either accept the blocky aesthetic as
the style, or fall back to a tool with real font rendering (the
`scripts/render_ffmpeg.py overlay-text` command uses FFmpeg's `drawtext`
filter, which *can* load an arbitrary `.ttf`/`.otf` — see `assets/fonts/`).
