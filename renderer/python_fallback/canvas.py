"""
Prototype canvas + 5x7 bitmap font, to validate the drawing/animation logic
in Python before porting it to Rust. Not part of the final skill deliverable
by itself — this is the scratch/verification step.
"""

import math

# A small original 5x7 pixel font — not a reproduction of any specific
# commercial/copyrighted font, just simple geometric block letters designed
# to be legible at small sizes (similar in spirit to countless LED-matrix
# alphabets). '#' = lit pixel, '.' = empty.
FONT_5X7 = {
    "A": [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "B": ["####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."],
    "C": [".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."],
    "D": ["####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."],
    "E": ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
    "F": ["#####", "#....", "#....", "####.", "#....", "#....", "#...."],
    "G": [".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".###."],
    "H": ["#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "I": [".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."],
    "J": ["..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."],
    "K": ["#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"],
    "L": ["#....", "#....", "#....", "#....", "#....", "#....", "#####"],
    "M": ["#...#", "##.##", "#.#.#", "#...#", "#...#", "#...#", "#...#"],
    "N": ["#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"],
    "O": [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "P": ["####.", "#...#", "#...#", "####.", "#....", "#....", "#...."],
    "Q": [".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"],
    "R": ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
    "S": [".####", "#....", "#....", ".###.", "....#", "....#", "####."],
    "T": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    "U": ["#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "V": ["#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."],
    "W": ["#...#", "#...#", "#...#", "#.#.#", "#.#.#", "#.#.#", ".#.#."],
    "X": ["#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"],
    "Y": ["#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."],
    "Z": ["#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"],
    "0": [".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."],
    "1": ["..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."],
    "2": [".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"],
    "3": [".###.", "#...#", "....#", "..##.", "....#", "#...#", ".###."],
    "4": ["...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."],
    "5": ["#####", "#....", "####.", "....#", "....#", "#...#", ".###."],
    "6": [".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."],
    "7": ["#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."],
    "8": [".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."],
    "9": [".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."],
    " ": [".....", ".....", ".....", ".....", ".....", ".....", "....."],
    ".": [".....", ".....", ".....", ".....", ".....", "..#..", "....."],
    ",": [".....", ".....", ".....", ".....", "..#..", "..#..", ".#..."],
    "!": ["..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."],
    "?": [".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."],
    "'": ["..#..", "..#..", ".....", ".....", ".....", ".....", "....."],
    "-": [".....", ".....", ".....", "#####", ".....", ".....", "....."],
    ":": [".....", "..#..", ".....", ".....", "..#..", ".....", "....."],
}


class Canvas:
    """RGB24 raster canvas, origin top-left, used as a raw frame buffer."""

    def __init__(self, width: int, height: int, bg=(0, 0, 0)):
        self.w = width
        self.h = height
        self.buf = bytearray(bg * (width * height))

    def clear(self, color):
        r, g, b = color
        self.buf[:] = bytes((r, g, b)) * (self.w * self.h)

    def set_pixel(self, x, y, color, alpha=1.0):
        if x < 0 or y < 0 or x >= self.w or y >= self.h:
            return
        idx = (y * self.w + x) * 3
        if alpha >= 1.0:
            self.buf[idx], self.buf[idx + 1], self.buf[idx + 2] = color
        elif alpha > 0.0:
            r0, g0, b0 = self.buf[idx], self.buf[idx + 1], self.buf[idx + 2]
            r1, g1, b1 = color
            self.buf[idx] = int(r0 * (1 - alpha) + r1 * alpha)
            self.buf[idx + 1] = int(g0 * (1 - alpha) + g1 * alpha)
            self.buf[idx + 2] = int(b0 * (1 - alpha) + b1 * alpha)

    def fill_rect(self, x0, y0, x1, y1, color, alpha=1.0):
        x0, x1 = sorted((int(x0), int(x1)))
        y0, y1 = sorted((int(y0), int(y1)))
        for y in range(max(y0, 0), min(y1, self.h)):
            for x in range(max(x0, 0), min(x1, self.w)):
                self.set_pixel(x, y, color, alpha)

    def fill_circle(self, cx, cy, radius, color, alpha=1.0):
        r2 = radius * radius
        x0, x1 = int(cx - radius), int(cx + radius)
        y0, y1 = int(cy - radius), int(cy + radius)
        for y in range(max(y0, 0), min(y1, self.h)):
            for x in range(max(x0, 0), min(x1, self.w)):
                dx, dy = x - cx, y - cy
                if dx * dx + dy * dy <= r2:
                    self.set_pixel(x, y, color, alpha)

    def draw_line(self, x0, y0, x1, y1, color, alpha=1.0, width=1):
        x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        hw = width // 2
        while True:
            if width <= 1:
                self.set_pixel(x0, y0, color, alpha)
            else:
                self.fill_rect(x0 - hw, y0 - hw, x0 + hw + 1, y0 + hw + 1, color, alpha)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def draw_text(self, text, x, y, color, scale=1, alpha=1.0, spacing=1):
        cursor_x = x
        for ch in text.upper():
            glyph = FONT_5X7.get(ch, FONT_5X7[" "])
            for row, line in enumerate(glyph):
                for col, px in enumerate(line):
                    if px == "#":
                        self.fill_rect(
                            cursor_x + col * scale,
                            y + row * scale,
                            cursor_x + col * scale + scale,
                            y + row * scale + scale,
                            color,
                            alpha,
                        )
            cursor_x += (5 * scale) + (spacing * scale)
        return cursor_x - x  # total width drawn

    def text_width(self, text, scale=1, spacing=1):
        return len(text) * (5 * scale + spacing * scale)

    def draw_text_centered(self, text, cx, y, color, scale=1, alpha=1.0, spacing=1):
        w = self.text_width(text, scale, spacing)
        self.draw_text(text, cx - w // 2, y, color, scale, alpha, spacing)


def lerp(a, b, t):
    return a + (b - a) * t


def ease_in_out(t):
    return t * t * (3 - 2 * t)


def ease_out_back(t, overshoot=1.70158):
    t -= 1
    return t * t * ((overshoot + 1) * t + overshoot) + 1


def clamp01(t):
    return max(0.0, min(1.0, t))
