# -*- coding: utf-8 -*-
"""VAAYU hero clip — rendered here, frame by frame, then piped to ffmpeg.

Same construction as the demo's CSS .field, but with the depth you cannot get
from four stacked gradients: three streak layers travelling at different rates,
two breathing glows, and a gust that crosses once per loop. Every drift covers a
whole number of periods across the clip, so it loops seamlessly.
"""
import numpy as np, subprocess, math, sys

W, H, FPS, DUR = 1280, 720, 24, 6
N = FPS * DUR
FF = "/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2"
OUT = sys.argv[1]

INK  = np.array([0, 0, 0],      dtype=np.float32)
LIME = np.array([204, 255, 0],  dtype=np.float32)
BONE = np.array([237, 234, 227], dtype=np.float32)

y, x = np.mgrid[0:H, 0:W].astype(np.float32)
th = math.radians(102.0)
u = x * math.cos(th) + y * math.sin(th)          # distance along the streak normal
nx, ny = x / W, y / H

def glow(cx, cy, rad):
    d = np.sqrt(((nx - cx) * (W / H)) ** 2 + (ny - cy) ** 2) / rad
    return np.clip(1.0 - d * d, 0.0, 1.0) ** 2

G1, G2 = glow(0.78, 0.10, 0.72), glow(0.12, 0.92, 0.80)

# corner falloff, so the type always sits on a quiet ground
vig = 0.42 + 0.58 * np.clip(1.0 - (((nx - .5) * 1.55) ** 2 + ((ny - .5) * 1.45) ** 2), 0.0, 1.0) ** .5

def streaks(spacing, width, phase):
    m = np.mod(u + phase, spacing)
    d = np.minimum(m, spacing - m)
    return np.exp(-((d / width) ** 2))

# spacing, line width, colour, amplitude, periods travelled per loop
LAYERS = [
    (38.0,  0.80, LIME, 0.30, 3),
    (140.0, 1.40, BONE, 0.20, 1),
    (430.0, 3.00, LIME, 0.15, 1),
]
uspan = float(u.max() - u.min())

rng = np.random.default_rng(4)
p = subprocess.Popen(
    [FF, "-hide_banner", "-loglevel", "error", "-y",
     "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
     "-c:v", "libx264", "-profile:v", "main", "-level", "4.0", "-pix_fmt", "yuv420p",
     "-crf", "26", "-preset", "medium", "-g", "6", "-keyint_min", "6",
     "-sc_threshold", "0", "-an", "-movflags", "+faststart", OUT],
    stdin=subprocess.PIPE)

for i in range(N):
    t = i / N                                     # 0..1, wraps exactly
    frame = np.repeat(INK[None, None, :], H, 0).repeat(W, 1).astype(np.float32)

    b1 = 0.55 + 0.45 * math.sin(2 * math.pi * t)
    b2 = 0.55 + 0.45 * math.sin(2 * math.pi * t + math.pi)
    frame += (G1 * (0.17 * b1))[..., None] * LIME
    frame += (G2 * (0.11 * b2))[..., None] * BONE

    for spacing, width, col, amp, periods in LAYERS:
        s = streaks(spacing, width, -t * spacing * periods)
        frame += (s * amp)[..., None] * col

    # one gust crossing the frame per loop
    gpos = u.min() + t * uspan
    gust = np.exp(-(((u - gpos) / (uspan * 0.085)) ** 2))
    frame += (gust * 0.34)[..., None] * (BONE * .55 + LIME * .45)

    frame *= vig[..., None]
    frame += rng.normal(0.0, 2.0, (H, W, 1)).astype(np.float32)   # grain
    p.stdin.write(np.clip(frame, 0, 255).astype(np.uint8).tobytes())

p.stdin.close()
p.wait()
print("frames:", N, "->", OUT)
