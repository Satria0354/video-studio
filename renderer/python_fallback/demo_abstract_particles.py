import math
from render import render_video

W, H, FPS, DURATION = 640, 640, 30, 5.0
NUM_PARTICLES = 24


def draw_frame(c, t, i):
    c.clear((6, 4, 16))
    cx, cy = W / 2, H / 2

    for n in range(NUM_PARTICLES):
        frac = n / NUM_PARTICLES
        angle = frac * math.tau + t * 0.8
        radius = 100 + 120 * abs(math.sin(frac * math.tau * 2 + t * 1.3))
        x = cx + math.cos(angle) * radius
        y = cy + math.sin(angle) * radius

        r = int(128 + 127 * math.sin(frac * math.tau + t))
        g = int(128 + 127 * math.sin(frac * math.tau + t + 2.1))
        b = int(128 + 127 * math.sin(frac * math.tau + t + 4.2))

        size = 6 + 4 * abs(math.sin(t * 2 + frac * 10))
        c.fill_circle(x, y, size, (r, g, b), alpha=0.85)
        c.fill_circle(x, y, size * 2.2, (r, g, b), alpha=0.12)

    pulse = 0.4 + 0.3 * abs(math.sin(t * 1.5))
    c.fill_circle(cx, cy, 40 + 20 * pulse, (255, 255, 255), alpha=0.08)


if __name__ == "__main__":
    render_video(W, H, FPS, DURATION, draw_frame, "abstract_particles_output.mp4")
