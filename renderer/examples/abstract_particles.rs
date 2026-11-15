#[path = "../motion.rs"]
mod motion;
use motion::*;

const W: usize = 640;
const H: usize = 640;
const FPS: usize = 30;
const DURATION: f64 = 5.0;
const NUM_PARTICLES: usize = 24;

fn draw_frame(c: &mut Canvas, t: f64, _i: usize) {
    c.clear((6, 4, 16));

    let cx = W as f64 / 2.0;
    let cy = H as f64 / 2.0;

    for n in 0..NUM_PARTICLES {
        let frac = n as f64 / NUM_PARTICLES as f64;
        let angle = frac * std::f64::consts::TAU + t * 0.8;
        let radius = 100.0 + 120.0 * (frac * std::f64::consts::TAU * 2.0 + t * 1.3).sin().abs();
        let x = cx + angle.cos() * radius;
        let y = cy + angle.sin() * radius;

        // Color cycles smoothly around a hue-ish gradient using simple
        // sine waves per channel (no HSL conversion needed).
        let r = (128.0 + 127.0 * (frac * std::f64::consts::TAU + t).sin()) as u8;
        let g = (128.0 + 127.0 * (frac * std::f64::consts::TAU + t + 2.1).sin()) as u8;
        let b = (128.0 + 127.0 * (frac * std::f64::consts::TAU + t + 4.2).sin()) as u8;

        let size = 6.0 + 4.0 * (t * 2.0 + frac * 10.0).sin().abs();
        c.fill_circle(x, y, size, (r, g, b), 0.85);

        // A faint trailing glow, drawn slightly larger and more transparent.
        c.fill_circle(x, y, size * 2.2, (r, g, b), 0.12);
    }

    // Soft pulsing center glow.
    let pulse = 0.4 + 0.3 * (t * 1.5).sin().abs();
    c.fill_circle(cx, cy, 40.0 + 20.0 * pulse, (255, 255, 255), 0.08);
}

fn main() {
    render_video(W, H, FPS, DURATION, draw_frame, "abstract_particles_output.mp4", (0, 0, 0))
        .expect("render failed");
}
