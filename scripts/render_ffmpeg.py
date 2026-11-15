#!/usr/bin/env python3
"""
render_ffmpeg.py — concat clips (with optional crossfade), overlay text, and
add/sync a background audio track, using FFmpeg under the hood.

Requires: a working `ffmpeg` binary on PATH. No Python packages beyond the
standard library.

Usage examples:

    # Concatenate clips with a hard cut (no transition)
    python render_ffmpeg.py concat clip1.mp4 clip2.mp4 clip3.mp4 -o final.mp4

    # Concatenate with a 0.5s crossfade between each clip
    python render_ffmpeg.py concat clip1.mp4 clip2.mp4 -o final.mp4 --transition fade --transition-duration 0.5

    # Overlay text on a video
    python render_ffmpeg.py overlay-text input.mp4 -o output.mp4 --text "Hello World" --fontsize 64 --position bottom

    # Add/replace the audio track of a video with a music file
    python render_ffmpeg.py add-audio input.mp4 -o output.mp4 --audio music.mp3 --mode replace

    # Mix a music track under the existing audio (e.g. ambient + narration)
    python render_ffmpeg.py add-audio input.mp4 -o output.mp4 --audio music.mp3 --mode mix --volume 0.3
"""

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def check_ffmpeg() -> None:
    if shutil.which("ffmpeg") is None:
        sys.exit(
            "ERROR: `ffmpeg` was not found on PATH. Install it first "
            "(e.g. `apt install ffmpeg`, `brew install ffmpeg`, or download "
            "from https://ffmpeg.org/download.html), then re-run this script."
        )


def run(cmd: list) -> None:
    """Run an ffmpeg command, streaming output, and exit loudly on failure."""
    print("Running:", " ".join(cmd))
    result = subprocess.run(cmd)
    if result.returncode != 0:
        sys.exit(f"ERROR: command failed with exit code {result.returncode}")


def cmd_concat(args: argparse.Namespace) -> None:
    clips = [str(Path(c).resolve()) for c in args.clips]
    for c in clips:
        if not Path(c).exists():
            sys.exit(f"ERROR: clip not found: {c}")

    output = str(Path(args.output).resolve())

    if args.transition == "cut" or len(clips) == 1:
        # Simple, fast path: concat demuxer (requires matching codecs/resolution).
        with tempfile.NamedTemporaryFile(
            "w", suffix=".txt", delete=False
        ) as f:
            for c in clips:
                f.write(f"file '{c}'\n")
            list_path = f.name
        try:
            run(
                [
                    "ffmpeg", "-y",
                    "-f", "concat", "-safe", "0",
                    "-i", list_path,
                    "-c", "copy",
                    output,
                ]
            )
        except SystemExit:
            # Fallback: re-encode instead of stream-copy, in case clips don't
            # share identical codecs/parameters (common when clips come from
            # different AI video-gen tools).
            print("Stream-copy concat failed; retrying with re-encode...")
            run(
                [
                    "ffmpeg", "-y",
                    "-f", "concat", "-safe", "0",
                    "-i", list_path,
                    "-c:v", "libx264", "-c:a", "aac",
                    output,
                ]
            )
        finally:
            Path(list_path).unlink(missing_ok=True)

    else:
        # Crossfade path: chain xfade/acrossfade filters pairwise.
        # Needs each clip's duration to compute offsets.
        durations = [_get_duration(c) for c in clips]
        d = args.transition_duration

        inputs = []
        for c in clips:
            inputs += ["-i", c]

        filter_parts = []
        video_label = "[0:v]"
        audio_label = "[0:a]"
        offset = durations[0] - d
        for i in range(1, len(clips)):
            next_v = f"[v{i}]"
            next_a = f"[a{i}]"
            filter_parts.append(
                f"{video_label}[{i}:v]xfade=transition=fade:duration={d}:offset={offset}{next_v}"
            )
            filter_parts.append(
                f"{audio_label}[{i}:a]acrossfade=d={d}{next_a}"
            )
            video_label = next_v
            audio_label = next_a
            if i < len(clips) - 1:
                offset += durations[i] - d

        filter_complex = ";".join(filter_parts)
        run(
            [
                "ffmpeg", "-y",
                *inputs,
                "-filter_complex", filter_complex,
                "-map", video_label,
                "-map", audio_label,
                "-c:v", "libx264", "-c:a", "aac",
                output,
            ]
        )

    print(f"Done: {output}")


def _get_duration(path: str) -> float:
    result = subprocess.run(
        [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            path,
        ],
        capture_output=True, text=True,
    )
    if result.returncode != 0 or not result.stdout.strip():
        sys.exit(f"ERROR: could not read duration of {path} (is ffprobe installed?)")
    return float(result.stdout.strip())


def cmd_overlay_text(args: argparse.Namespace) -> None:
    input_path = str(Path(args.input).resolve())
    if not Path(input_path).exists():
        sys.exit(f"ERROR: input not found: {input_path}")
    output = str(Path(args.output).resolve())

    position_map = {
        "top": "x=(w-text_w)/2:y=h*0.08",
        "center": "x=(w-text_w)/2:y=(h-text_h)/2",
        "bottom": "x=(w-text_w)/2:y=h*0.85",
    }
    xy = position_map.get(args.position, position_map["bottom"])

    drawtext = (
        f"drawtext=text='{_escape(args.text)}':"
        f"fontsize={args.fontsize}:fontcolor={args.color}:"
        f"{xy}:"
        "box=1:boxcolor=black@0.4:boxborderw=12"
    )
    if args.fontfile:
        drawtext = f"fontfile='{args.fontfile}':" + drawtext

    if args.start is not None or args.duration is not None:
        start = args.start or 0
        end = start + args.duration if args.duration else 1e9
        drawtext += f":enable='between(t,{start},{end})'"

    run(
        [
            "ffmpeg", "-y",
            "-i", input_path,
            "-vf", drawtext,
            "-c:a", "copy",
            output,
        ]
    )
    print(f"Done: {output}")


def _escape(text: str) -> str:
    # Escape characters that are special to ffmpeg's drawtext filter.
    return (
        text.replace("\\", "\\\\\\\\")
        .replace(":", "\\:")
        .replace("'", "\u2019")  # swap straight quote for a typographic one
    )


def cmd_add_audio(args: argparse.Namespace) -> None:
    input_path = str(Path(args.input).resolve())
    audio_path = str(Path(args.audio).resolve())
    for p in (input_path, audio_path):
        if not Path(p).exists():
            sys.exit(f"ERROR: file not found: {p}")
    output = str(Path(args.output).resolve())

    if args.mode == "replace":
        run(
            [
                "ffmpeg", "-y",
                "-i", input_path,
                "-i", audio_path,
                "-map", "0:v:0", "-map", "1:a:0",
                "-c:v", "copy", "-c:a", "aac",
                "-shortest",
                output,
            ]
        )
    else:  # mix
        filter_complex = (
            f"[1:a]volume={args.volume}[music];"
            "[0:a][music]amix=inputs=2:duration=first:dropout_transition=2[aout]"
        )
        run(
            [
                "ffmpeg", "-y",
                "-i", input_path,
                "-i", audio_path,
                "-filter_complex", filter_complex,
                "-map", "0:v:0", "-map", "[aout]",
                "-c:v", "copy", "-c:a", "aac",
                output,
            ]
        )
    print(f"Done: {output}")


def main() -> None:
    check_ffmpeg()
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    p_concat = sub.add_parser("concat", help="Concatenate multiple clips into one video")
    p_concat.add_argument("clips", nargs="+", help="Paths to input video clips, in order")
    p_concat.add_argument("-o", "--output", required=True)
    p_concat.add_argument("--transition", choices=["cut", "fade"], default="cut")
    p_concat.add_argument("--transition-duration", type=float, default=0.5)
    p_concat.set_defaults(func=cmd_concat)

    p_text = sub.add_parser("overlay-text", help="Overlay text on a video")
    p_text.add_argument("input")
    p_text.add_argument("-o", "--output", required=True)
    p_text.add_argument("--text", required=True)
    p_text.add_argument("--fontsize", type=int, default=48)
    p_text.add_argument("--color", default="white")
    p_text.add_argument("--position", choices=["top", "center", "bottom"], default="bottom")
    p_text.add_argument("--fontfile", default=None, help="Path to a .ttf/.otf file; omit to use ffmpeg's default")
    p_text.add_argument("--start", type=float, default=None, help="Seconds into the video when the text should appear")
    p_text.add_argument("--duration", type=float, default=None, help="How long the text stays on screen, in seconds")
    p_text.set_defaults(func=cmd_overlay_text)

    p_audio = sub.add_parser("add-audio", help="Replace or mix in a background audio track")
    p_audio.add_argument("input")
    p_audio.add_argument("-o", "--output", required=True)
    p_audio.add_argument("--audio", required=True)
    p_audio.add_argument("--mode", choices=["replace", "mix"], default="replace")
    p_audio.add_argument("--volume", type=float, default=0.3, help="Volume of the added track when --mode mix (0.0-1.0+)")
    p_audio.set_defaults(func=cmd_add_audio)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
