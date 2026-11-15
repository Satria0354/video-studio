# Fonts (optional)

Drop a `.ttf` or `.otf` font file here if you want text overlays
(`render_ffmpeg.py overlay-text`) to use a specific custom font instead of
FFmpeg's built-in default.

Usage:
```
python ../scripts/render_ffmpeg.py overlay-text input.mp4 -o output.mp4 \
    --text "Your text" --fontfile ./my-font.ttf
```

This folder is empty by default — it's just a convenient place to keep font
files alongside the rest of the skill so paths stay relative and portable.
