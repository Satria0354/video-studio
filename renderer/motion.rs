use std::io::Write;
use std::process::{Command, Stdio};

pub type Color = (u8, u8, u8);

// ---------------------------------------------------------------------
// Canvas: a raw RGB24 frame buffer, origin top-left.
// ---------------------------------------------------------------------

pub struct Canvas {
    pub w: usize,
    pub h: usize,
    pub buf: Vec<u8>,
}

impl Canvas {
    pub fn new(w: usize, h: usize, bg: Color) -> Self {
        let mut buf = Vec::with_capacity(w * h * 3);
        for _ in 0..(w * h) {
            buf.push(bg.0);
            buf.push(bg.1);
            buf.push(bg.2);
        }
        Canvas { w, h, buf }
    }

    pub fn clear(&mut self, bg: Color) {
        for px in self.buf.chunks_mut(3) {
            px[0] = bg.0;
            px[1] = bg.1;
            px[2] = bg.2;
        }
    }

    pub fn set_pixel(&mut self, x: i64, y: i64, color: Color, alpha: f64) {
        if x < 0 || y < 0 || x as usize >= self.w || y as usize >= self.h {
            return;
        }
        let idx = (y as usize * self.w + x as usize) * 3;
        if alpha >= 1.0 {
            self.buf[idx] = color.0;
            self.buf[idx + 1] = color.1;
            self.buf[idx + 2] = color.2;
        } else if alpha > 0.0 {
            let r0 = self.buf[idx] as f64;
            let g0 = self.buf[idx + 1] as f64;
            let b0 = self.buf[idx + 2] as f64;
            self.buf[idx] = (r0 * (1.0 - alpha) + color.0 as f64 * alpha) as u8;
            self.buf[idx + 1] = (g0 * (1.0 - alpha) + color.1 as f64 * alpha) as u8;
            self.buf[idx + 2] = (b0 * (1.0 - alpha) + color.2 as f64 * alpha) as u8;
        }
    }

    pub fn fill_rect(&mut self, x0: i64, y0: i64, x1: i64, y1: i64, color: Color, alpha: f64) {
        let (x0, x1) = if x0 < x1 { (x0, x1) } else { (x1, x0) };
        let (y0, y1) = if y0 < y1 { (y0, y1) } else { (y1, y0) };
        let y_start = y0.max(0);
        let y_end = y1.min(self.h as i64);
        let x_start = x0.max(0);
        let x_end = x1.min(self.w as i64);
        let mut y = y_start;
        while y < y_end {
            let mut x = x_start;
            while x < x_end {
                self.set_pixel(x, y, color, alpha);
                x += 1;
            }
            y += 1;
        }
    }

    pub fn fill_circle(&mut self, cx: f64, cy: f64, radius: f64, color: Color, alpha: f64) {
        let r2 = radius * radius;
        let x0 = (cx - radius).floor() as i64;
        let x1 = (cx + radius).ceil() as i64;
        let y0 = (cy - radius).floor() as i64;
        let y1 = (cy + radius).ceil() as i64;
        let y_start = y0.max(0);
        let y_end = y1.min(self.h as i64);
        let x_start = x0.max(0);
        let x_end = x1.min(self.w as i64);
        let mut y = y_start;
        while y < y_end {
            let mut x = x_start;
            while x < x_end {
                let dx = x as f64 - cx;
                let dy = y as f64 - cy;
                if dx * dx + dy * dy <= r2 {
                    self.set_pixel(x, y, color, alpha);
                }
                x += 1;
            }
            y += 1;
        }
    }

    pub fn draw_line(&mut self, x0: i64, y0: i64, x1: i64, y1: i64, color: Color, alpha: f64, width: i64) {
        let mut x0 = x0;
        let mut y0 = y0;
        let dx = (x1 - x0).abs();
        let dy = (y1 - y0).abs();
        let sx: i64 = if x0 < x1 { 1 } else { -1 };
        let sy: i64 = if y0 < y1 { 1 } else { -1 };
        let mut err = dx - dy;
        let hw = width / 2;
        loop {
            if width <= 1 {
                self.set_pixel(x0, y0, color, alpha);
            } else {
                self.fill_rect(x0 - hw, y0 - hw, x0 + hw + 1, y0 + hw + 1, color, alpha);
            }
            if x0 == x1 && y0 == y1 {
                break;
            }
            let e2 = 2 * err;
            if e2 > -dy {
                err -= dy;
                x0 += sx;
            }
            if e2 < dx {
                err += dx;
                y0 += sy;
            }
        }
    }

    /// Draws `text` (case-insensitive; unsupported characters render as a
    /// blank glyph) and returns the pixel width drawn.
    pub fn draw_text(&mut self, text: &str, x: i64, y: i64, color: Color, scale: i64, alpha: f64, spacing: i64) -> i64 {
        let mut cursor_x = x;
        for ch in text.chars() {
            let rows = glyph_rows(ch);
            for (row, line) in rows.iter().enumerate() {
                for (col, px) in line.chars().enumerate() {
                    if px == '#' {
                        let gx = cursor_x + col as i64 * scale;
                        let gy = y + row as i64 * scale;
                        self.fill_rect(gx, gy, gx + scale, gy + scale, color, alpha);
                    }
                }
            }
            cursor_x += 5 * scale + spacing * scale;
        }
        cursor_x - x
    }

    pub fn text_width(&self, text: &str, scale: i64, spacing: i64) -> i64 {
        text.chars().count() as i64 * (5 * scale + spacing * scale)
    }

    pub fn draw_text_centered(&mut self, text: &str, cx: i64, y: i64, color: Color, scale: i64, alpha: f64, spacing: i64) {
        let w = self.text_width(text, scale, spacing);
        self.draw_text(text, cx - w / 2, y, color, scale, alpha, spacing);
    }
}

// ---------------------------------------------------------------------
// 5x7 bitmap font — an original, simple geometric alphabet (not a
// reproduction of any specific commercial font), enough for captions
// and kinetic-typography titles. '#' = lit pixel, '.' = empty.
// ---------------------------------------------------------------------

pub fn glyph_rows(ch: char) -> [&'static str; 7] {
    match ch.to_ascii_uppercase() {
        'A' => [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
        'B' => ["####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."],
        'C' => [".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."],
        'D' => ["####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."],
        'E' => ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
        'F' => ["#####", "#....", "#....", "####.", "#....", "#....", "#...."],
        'G' => [".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".###."],
        'H' => ["#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
        'I' => [".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."],
        'J' => ["..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."],
        'K' => ["#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"],
        'L' => ["#....", "#....", "#....", "#....", "#....", "#....", "#####"],
        'M' => ["#...#", "##.##", "#.#.#", "#...#", "#...#", "#...#", "#...#"],
        'N' => ["#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"],
        'O' => [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
        'P' => ["####.", "#...#", "#...#", "####.", "#....", "#....", "#...."],
        'Q' => [".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"],
        'R' => ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
        'S' => [".####", "#....", "#....", ".###.", "....#", "....#", "####."],
        'T' => ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
        'U' => ["#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
        'V' => ["#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."],
        'W' => ["#...#", "#...#", "#...#", "#.#.#", "#.#.#", "#.#.#", ".#.#."],
        'X' => ["#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"],
        'Y' => ["#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."],
        'Z' => ["#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"],
        '0' => [".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."],
        '1' => ["..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."],
        '2' => [".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"],
        '3' => [".###.", "#...#", "....#", "..##.", "....#", "#...#", ".###."],
        '4' => ["...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."],
        '5' => ["#####", "#....", "####.", "....#", "....#", "#...#", ".###."],
        '6' => [".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."],
        '7' => ["#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."],
        '8' => [".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."],
        '9' => [".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."],
        ' ' => [".....", ".....", ".....", ".....", ".....", ".....", "....."],
        '.' => [".....", ".....", ".....", ".....", ".....", "..#..", "....."],
        ',' => [".....", ".....", ".....", ".....", "..#..", "..#..", ".#..."],
        '!' => ["..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."],
        '?' => [".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."],
        '\'' => ["..#..", "..#..", ".....", ".....", ".....", ".....", "....."],
        '-' => [".....", ".....", ".....", "#####", ".....", ".....", "....."],
        ':' => [".....", "..#..", ".....", ".....", "..#..", ".....", "....."],
        _ => [".....", ".....", ".....", ".....", ".....", ".....", "....."],
    }
}

// ---------------------------------------------------------------------
// Animation helpers
// ---------------------------------------------------------------------

pub fn lerp(a: f64, b: f64, t: f64) -> f64 {
    a + (b - a) * t
}

pub fn clamp01(t: f64) -> f64 {
    t.max(0.0).min(1.0)
}

/// Smoothstep: gentle ease in and out, no overshoot.
pub fn ease_in_out(t: f64) -> f64 {
    t * t * (3.0 - 2.0 * t)
}

/// Eases in with a slight overshoot past 1.0 before settling — good for
/// "pop in" effects on text/shapes.
pub fn ease_out_back(t: f64) -> f64 {
    let overshoot = 1.70158;
    let t = t - 1.0;
    t * t * ((overshoot + 1.0) * t + overshoot) + 1.0
}

// ---------------------------------------------------------------------
// Rendering: draw_frame is called once per frame, then piped to ffmpeg
// as raw rgb24 and encoded to an MP4 (h264 + yuv420p for broad
// compatibility, including most phones/socials).
// ---------------------------------------------------------------------

pub fn render_video<F: FnMut(&mut Canvas, f64, usize)>(
    width: usize,
    height: usize,
    fps: usize,
    duration_s: f64,
    mut draw_frame: F,
    output_path: &str,
    bg: Color,
) -> std::io::Result<()> {
    let total_frames = (duration_s * fps as f64).round() as usize;

    let args: Vec<String> = vec![
        "-y".to_string(),
        "-f".to_string(),
        "rawvideo".to_string(),
        "-pix_fmt".to_string(),
        "rgb24".to_string(),
        "-s".to_string(),
        format!("{}x{}", width, height),
        "-r".to_string(),
        fps.to_string(),
        "-i".to_string(),
        "-".to_string(),
        "-c:v".to_string(),
        "libx264".to_string(),
        "-pix_fmt".to_string(),
        "yuv420p".to_string(),
        output_path.to_string(),
    ];

    let mut child = Command::new("ffmpeg")
        .args(&args)
        .stdin(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()?;

    {
        let mut stdin = child.stdin.take().expect("failed to open ffmpeg stdin");
        for i in 0..total_frames {
            let t = i as f64 / fps as f64;
            let mut canvas = Canvas::new(width, height, bg);
            draw_frame(&mut canvas, t, i);
            stdin.write_all(&canvas.buf)?;
        }
        // `stdin` is dropped here, closing the pipe so ffmpeg knows input
        // has ended. This must happen BEFORE wait_with_output(), or the
        // two processes deadlock waiting on each other.
    }

    let output = child.wait_with_output()?;
    if !output.status.success() {
        let err = String::from_utf8_lossy(&output.stderr);
        eprintln!("ffmpeg failed:\n{}", err);
        std::process::exit(1);
    }
    println!(
        "Wrote {} ({} frames, {}s @ {}fps)",
        output_path, total_frames, duration_s, fps
    );
    Ok(())
}
