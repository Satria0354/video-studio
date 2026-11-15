#[path = "../motion.rs"]
mod motion;
use motion::*;

const W: usize = 640;
const H: usize = 360;
const FPS: usize = 30;
const DURATION: f64 = 4.0;

const LINE1: &str = "BUILT FROM";
const LINE2: &str = "SCRATCH";

fn draw_frame(c: &mut Canvas, t: f64, _i: usize) {
    c.clear((8, 8, 18));

    // Background: a few slowly drifting translucent circles for depth.
    for n in 0..5 {
        let phase = n as f64 * 1.3;
        let cx = W as f64 / 2.0 + (t * 0.5 + phase).sin() * (150.0 + n as f64 * 20.0);
        let cy = H as f64 / 2.0 + (t * 0.4 + phase).cos() * (80.0 + n as f64 * 10.0);
        c.fill_circle(cx, cy, 40.0 - n as f64 * 4.0, (30, 30, 60), 0.5);
    }

    // Line 1 pops in with an overshoot ease between t=0.2..0.9s.
    let t1 = clamp01((t - 0.2) / 0.7);
    if t1 > 0.0 {
        let scale1 = if t1 < 1.0 { ease_out_back(t1) } else { 1.0 };
        let s = (scale1.max(0.1) * 5.0) as i64;
        let s = s.max(1);
        c.draw_text_centered(LINE1, (W / 2) as i64, (H as f64 * 0.35) as i64 - (s * 7) / 2, (255, 255, 255), s, 1.0, 1);
    }

    // Line 2 slides up + fades in between t=1.0..1.8s.
    let t2 = clamp01((t - 1.0) / 0.8);
    if t2 > 0.0 {
        let eased = ease_in_out(t2);
        let y_offset = ((1.0 - eased) * 40.0) as i64;
        c.draw_text_centered(
            LINE2,
            (W / 2) as i64,
            (H as f64 * 0.55) as i64 + y_offset,
            (0, 220, 255),
            5,
            eased,
            1,
        );
    }

    // A pulsing underline bar appears after t=2.0s.
    if t > 2.0 {
        let pulse = 0.5 + 0.5 * (0.5 + 0.5 * ((t - 2.0) * 6.0).sin());
        let cx = (W / 2) as i64;
        let y = (H as f64 * 0.68) as i64;
        c.fill_rect(cx - 120, y, cx + 120, y + 6, (255, 120, 60), pulse);
    }
}

fn main() {
    render_video(W, H, FPS, DURATION, draw_frame, "kinetic_typography_output.mp4", (0, 0, 0))
        .expect("render failed");
}
