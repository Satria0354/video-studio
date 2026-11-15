from render import render_video
from canvas import ease_out_back, ease_in_out, clamp01

W, H, FPS, DURATION = 640, 360, 30, 4.0

LINES = ["BUILT FROM", "SCRATCH"]


def draw_frame(c, t, i):
    c.clear((8, 8, 18))

    # Background: a few slowly drifting circles for depth
    import math
    for n in range(5):
        phase = n * 1.3
        cx = W / 2 + math.sin(t * 0.5 + phase) * (150 + n * 20)
        cy = H / 2 + math.cos(t * 0.4 + phase) * (80 + n * 10)
        c.fill_circle(cx, cy, 40 - n * 4, (30, 30, 60), alpha=0.5)

    # Line 1 pops in with an overshoot ease between t=0.2..0.9
    t1 = clamp01((t - 0.2) / 0.7)
    scale1 = ease_out_back(t1) if t1 < 1 else 1.0
    if t1 > 0:
        s = max(0.1, scale1) * 5
        c.draw_text_centered(LINES[0], W // 2, int(H * 0.35 - (s * 7) / 2), (255, 255, 255), scale=max(1, int(s)))

    # Line 2 slides up + fades in between t=1.0..1.8
    t2 = clamp01((t - 1.0) / 0.8)
    ease2 = ease_in_out(t2)
    y_offset = int((1 - ease2) * 40)
    if t2 > 0:
        c.draw_text_centered(
            LINES[1], W // 2, int(H * 0.55) + y_offset, (0, 220, 255), scale=5, alpha=ease2
        )

    # A pulsing underline bar appears after t=2.0
    if t > 2.0:
        pulse = 0.5 + 0.5 * (0.5 + 0.5 * __import__("math").sin((t - 2.0) * 6))
        c.fill_rect(W // 2 - 120, int(H * 0.68), W // 2 + 120, int(H * 0.68) + 6, (255, 120, 60), alpha=pulse)


render_video(W, H, FPS, DURATION, draw_frame, "/tmp/test/kinetic_demo.mp4")
