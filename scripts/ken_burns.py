#!/usr/bin/env python3
"""
ken_burns.py — turn a static image into a short video clip with a slow
pan/zoom ("Ken Burns") effect, using FFmpeg's zoompan filter.

Requires: a working `ffmpeg` binary on PATH. No Python packages beyond the
standard library.

Usage examples:

    # Slow zoom in, centered, 5 seconds, 1920x1080, 30fps
    python ken_burns.py photo.jpg -o clip.mp4 --duration 5

    # Zoom out instead of in
    python ken_burns.py photo.jpg -o clip.mp4 --direction zoom-out

    # Pan left-to-right with a slight zoom, 9:16 vertical output for Reels/Shorts
    python ken_burns.py photo.jpg -o clip.mp4 --pan left-to-right --width 1080 --height 1920
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def check_ffmpeg() -> None:
    if shutil.which("ffmpeg") is None:
        sys.exit(
            "ERROR: `ffmpeg` was not found on PATH. Install it first "
            "(e.g. `apt install ffmpeg`, `brew install ffmpeg`, or download "
            "from https://ffmpeg.org/download.html), then re-run this script."
        )


def build_zoompan_expr(direction: str, pan: str, zoom_amount: float, frames: int) -> tuple:
    """Return (z_expr, x_expr, y_expr) for ffmpeg's zoompan filter."""
    if direction == "zoom-in":
        z_expr = f"min(zoom+{zoom_amount / frames},{1 + zoom_amount})"
    else:  # zoom-out
        z_expr = f"if(eq(on,1),{1 + zoom_amount},max(zoom-{zoom_amount / frames},1))"

    pan_map = {
        "center": ("iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"),
        "left-to-right": ("(iw-iw/zoom)*(on/{f})".format(f=frames), "ih/2-(ih/zoom/2)"),
        "right-to-left": ("(iw-iw/zoom)*(1-on/{f})".format(f=frames), "ih/2-(ih/zoom/2)"),
        "top-to-bottom": ("iw/2-(iw/zoom/2)", "(ih-ih/zoom)*(on/{f})".format(f=frames)),
        "bottom-to-top": ("iw/2-(iw/zoom/2)", "(ih-ih/zoom)*(1-on/{f})".format(f=frames)),
    }
    x_expr, y_expr = pan_map.get(pan, pan_map["center"])
    return z_expr, x_expr, y_expr


def main() -> None:
    check_ffmpeg()
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("image", help="Path to the input image")
    parser.add_argument("-o", "--output", required=True)
    parser.add_argument("--duration", type=float, default=5.0, help="Clip duration in seconds")
    parser.add_argument("--fps", type=int, default=30)
    parser.add_argument("--width", type=int, default=1920)
    parser.add_argument("--height", type=int, default=1080)
    parser.add_argument("--direction", choices=["zoom-in", "zoom-out"], default="zoom-in")
    parser.add_argument(
        "--pan",
        choices=["center", "left-to-right", "right-to-left", "top-to-bottom", "bottom-to-top"],
        default="center",
    )
    parser.add_argument("--zoom-amount", type=float, default=0.25, help="How much to zoom by, e.g. 0.25 = 25%")
    args = parser.parse_args()

    image_path = str(Path(args.image).resolve())
    if not Path(image_path).exists():
        sys.exit(f"ERROR: image not found: {image_path}")
    output = str(Path(args.output).resolve())

    frames = int(args.duration * args.fps)
    z_expr, x_expr, y_expr = build_zoompan_expr(args.direction, args.pan, args.zoom_amount, frames)

    # Upscale first so zoompan has headroom to pan/zoom without pixelating,
    # then zoompan, then crop/scale to the exact target size.
    vf = (
        f"scale=8000:-1,"
        f"zoompan=z='{z_expr}':x='{x_expr}':y='{y_expr}':d={frames}:s={args.width}x{args.height}:fps={args.fps},"
        f"format=yuv420p"
    )

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1",
        "-i", image_path,
        "-vf", vf,
        "-t", str(args.duration),
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        output,
    ]
    print("Running:", " ".join(cmd))
    result = subprocess.run(cmd)
    if result.returncode != 0:
        sys.exit(f"ERROR: command failed with exit code {result.returncode}")
    print(f"Done: {output}")


if __name__ == "__main__":
    main()
