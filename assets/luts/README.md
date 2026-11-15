# LUTs (optional)

Drop a `.cube` 3D LUT file here if you want to color-grade a clip.

This isn't wired into `render_ffmpeg.py` by default. To apply one manually
with FFmpeg's `lut3d` filter:
```
ffmpeg -i input.mp4 -vf lut3d=my-lut.cube output.mp4
```

This folder is empty by default — it's just a convenient place to keep LUT
files alongside the rest of the skill so paths stay relative and portable.
