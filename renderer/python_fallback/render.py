import subprocess
import sys
from canvas import Canvas


def render_video(width, height, fps, duration_s, draw_frame, output_path, bg=(0, 0, 0)):
    """
    draw_frame(canvas, t_seconds, frame_index) is called once per frame.
    Frames are piped to ffmpeg as raw rgb24 -> encoded to an mp4 (h264).
    """
    total_frames = int(round(duration_s * fps))
    cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{width}x{height}", "-r", str(fps),
        "-i", "-",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        output_path,
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        for i in range(total_frames):
            t = i / fps
            canvas = Canvas(width, height, bg=bg)
            draw_frame(canvas, t, i)
            proc.stdin.write(bytes(canvas.buf))
        proc.stdin.close()
    except BrokenPipeError:
        pass
    proc.wait()
    if proc.returncode != 0:
        err = proc.stderr.read().decode(errors="replace")
        sys.exit(f"ffmpeg failed:\n{err[-1000:]}")
    print(f"Wrote {output_path} ({total_frames} frames, {duration_s}s @ {fps}fps)")
