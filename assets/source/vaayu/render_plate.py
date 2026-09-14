"""Vaayu hero plate: a seamless 6 s loop built from one still and its depth map.

Inputs  plate/flux-still.webp -> plate/grade.py -> a 1280x720 still where lime is the only colour
        plate/depth16.png  Depth Anything V2 Small on that graded still (plate/depth.py), near = bright
Output  a near-lossless mp4; re-encode with the README's ffmpeg line before it ships

What shipped (run from assets/source/vaayu/plate, with numpy, pillow, imageio-ffmpeg):
    python grade.py flux-still.webp graded.png
    python ../render_plate.py raw.mp4 graded.png depth16.png 290 1010 0.6 0.000001
The four numbers are the bike's x-range for masking, the rain density, and the
grain amount (effectively off: per-frame noise costs bitrate and does not show
at the page's .45 luminosity blend).

The bike never moves. Everything that does move is periodic in t = i / FRAMES,
so frame FRAMES is frame 0 and the clip wraps without a seam:
  1. background parallax  - the plate behind the bike drifts on a closed ellipse,
                            scaled by depth, so near and far separate a few px
  2. road shimmer         - wet-asphalt reflections wobble sideways; the phase
                            advances a whole number of cycles per loop
  3. rain                 - three streak layers, each travelling a whole number
                            of tile heights per loop, brightest in the rim light
"""
import sys, time
import numpy as np
from PIL import Image, ImageDraw
import imageio_ffmpeg

W, H, FPS, SECONDS = 1280, 720, 24, 6
FRAMES = FPS * SECONDS
rng = np.random.default_rng(7)

# usage: proto_render.py <out.mp4> [still.png depth16.png bbox_x0 bbox_x1 rain_scale grain]
ARGS = sys.argv[1:] + [None] * 7
STILL = ARGS[1] or "still_s7_graded.png"
DEPTH = ARGS[2] or "depth16.png"
BX0, BX1 = int(ARGS[3] or 380), int(ARGS[4] or 900)
RAIN = float(ARGS[5] or 1.0)                                  # density/brightness scale
GRAIN = float(ARGS[6] or 0.012)                               # 0 for web: per-frame noise costs bitrate
still = np.asarray(Image.open(STILL).convert("RGB"), np.float32) / 255
depth = np.asarray(Image.open(DEPTH), np.float32) / 65535
assert still.shape[:2] == (H, W) and depth.shape == (H, W)


def box_blur(a, r):
    """Separable box blur with edge clamping (cumulative sums, no scipy)."""
    if r < 1:
        return a
    pad = [(r, r), (0, 0)] + [(0, 0)] * (a.ndim - 2)
    for axis in (0, 1):
        p = np.pad(a, pad if axis == 0 else [(0, 0), (r, r)] + [(0, 0)] * (a.ndim - 2), mode="edge")
        c = np.cumsum(p, axis=axis, dtype=np.float64)
        c = np.concatenate([np.zeros_like(np.take(c, [0], axis=axis)), c], axis=axis)
        n = a.shape[axis]
        a = ((np.take(c, np.arange(2 * r + 1, 2 * r + 1 + n), axis=axis)
              - np.take(c, np.arange(0, n), axis=axis)) / (2 * r + 1)).astype(np.float32)
    return a


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


# ── bike mask ────────────────────────────────────────────────────────────────
# Ground depth rises smoothly toward the camera. Estimate it per row from the
# columns either side of the bike, and call anything clearly nearer the bike.
ys, xs = np.mgrid[0:H, 0:W].astype(np.float32)
side = np.r_[0:max(40, BX0 - 20), min(W - 40, BX1 + 40):W]
ground_row = np.median(depth[:, side], axis=1)[:, None]
bbox = (xs > BX0) & (xs < BX1) & (ys > 60)
bike = ((depth - ground_row) > 0.07) & bbox
bike = box_blur(bike.astype(np.float32), 2) > 0.5           # close pinholes
bike_soft = np.clip(box_blur(bike.astype(np.float32), 3) * 1.6 - 0.3, 0, 1)
bike_wide = box_blur(bike.astype(np.float32), 14) > 0.02    # region the plate may reveal

# ── clean background plate (bike removed) ────────────────────────────────────
# Pull-push fill: repeatedly blur the known pixels and take the blurred colour
# where the bike was. Only a band a few px wide ever becomes visible.
known = (~bike_wide).astype(np.float32)[..., None]
plate = still * known
weight = known.copy()
fill = np.zeros_like(still)
for r in (2, 4, 8, 16, 32, 64):
    num = box_blur(plate, r)
    den = box_blur(weight, r)
    est = num / np.maximum(den, 1e-4)
    take = (den > 1e-3) & (fill.sum(-1, keepdims=True) == 0)
    fill = np.where(take & (known == 0), est, fill)
plate = np.where(known > 0, still, fill)

# ── fields for parallax and shimmer ──────────────────────────────────────────
bike_depth = float(np.median(depth[bike]))
parallax_gain = (depth - bike_depth)                          # 0 at the bike's plane
horizon = 0.46 * H
road = smoothstep(horizon, horizon + 60, ys) * (1 - box_blur(bike.astype(np.float32), 10))
road_depthward = smoothstep(horizon, H, ys)                   # stronger near camera
col_phase = box_blur(rng.random((1, W), np.float32).repeat(8, 0), 24)[0] * 2 * np.pi
col_phase = np.broadcast_to(col_phase, (H, W))
highlights = smoothstep(0.18, 0.55, still.mean(-1))           # wet sheen only


def sample(img, x, y):
    """Bilinear sample img at float coords, clamped."""
    x = np.clip(x, 0, W - 1.001); y = np.clip(y, 0, H - 1.001)
    x0 = x.astype(np.int32); y0 = y.astype(np.int32)
    fx = (x - x0)[..., None]; fy = (y - y0)[..., None]
    a = img[y0, x0]; b = img[y0, x0 + 1]; c = img[y0 + 1, x0]; d = img[y0 + 1, x0 + 1]
    return (a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy


# ── rain tiles ───────────────────────────────────────────────────────────────
# Each layer is a W x H tile of antialiased streaks, drawn at 2x and reduced.
def rain_tile(count, length, width, alpha, angle_deg, blur):
    S = 2
    im = Image.new("L", (W * S, H * S), 0)
    dr = ImageDraw.Draw(im)
    dx = np.tan(np.radians(angle_deg))
    for _ in range(count):
        x, y = rng.uniform(0, W * S), rng.uniform(0, H * S)
        L = length * S * rng.uniform(0.6, 1.3)
        a = int(255 * alpha * rng.uniform(0.35, 1.0))
        for ox in (-W * S, 0, W * S):                      # wrap horizontally
            for oy in (-H * S, 0, H * S):                  # and vertically
                dr.line([(x + ox, y + oy), (x + ox + dx * L, y + oy + L)], fill=a, width=max(1, int(width * S)))
    t = np.asarray(im.resize((W, H), Image.LANCZOS), np.float32) / 255
    return box_blur(t, blur)


layers = [  # (tile, tile heights travelled per loop)
    (rain_tile(int(900 * RAIN), 26, 0.7, 0.55 * RAIN ** 0.5, 7, 0), 5),    # far: fine and quick
    (rain_tile(int(360 * RAIN), 60, 1.1, 0.50 * RAIN ** 0.5, 8, 1), 8),    # mid
    (rain_tile(int(70 * RAIN), 150, 2.2, 0.30 * RAIN ** 0.5, 9, 2), 12),   # near: long, soft, few
]
# Rain is visible where the rim light (camera left, above) catches it.
rim = np.exp(-(((xs - 0.30 * W) / (0.42 * W)) ** 2 + ((ys - 0.25 * H) / (0.55 * H)) ** 2))
rain_light = (0.18 + 0.82 * rim)[..., None] * np.array([0.93, 0.95, 0.97], np.float32)

grain = [box_blur(rng.normal(0, 1, (H // 2, W // 2)).astype(np.float32), 0) for _ in range(FRAMES)]

# ── render ───────────────────────────────────────────────────────────────────
out = ARGS[0] or "proto_raw.mp4"
writer = imageio_ffmpeg.write_frames(out, (W, H), fps=FPS, codec="libx264", quality=None,
                                     output_params=["-crf", "12", "-pix_fmt", "yuv420p"], macro_block_size=1)
writer.send(None)
t0 = time.time()
for i in range(FRAMES):
    t = i / FRAMES
    ang = 2 * np.pi * t
    ox, oy = 9.0 * np.cos(ang), 2.5 * np.sin(ang)             # closed ellipse
    sh = 1.6 * np.sin(2 * np.pi * (ys / 23.0 - 3 * t) + col_phase) * road * road_depthward
    bg = sample(plate, xs - ox * parallax_gain + sh, ys - oy * parallax_gain)
    # sheen breathes on the wet road, two whole cycles per loop
    bg = bg * (1 + 0.10 * road[..., None] * highlights[..., None]
               * np.sin(2 * np.pi * (xs / 170.0 + 2 * t) + col_phase)[..., None])
    frame = bg * (1 - bike_soft[..., None]) + still * bike_soft[..., None]
    rain = np.zeros((H, W), np.float32)
    for tile, k in layers:
        shift = k * H * t
        s0 = int(np.floor(shift)); f = shift - s0
        rain += np.roll(tile, s0, axis=0) * (1 - f) + np.roll(tile, s0 + 1, axis=0) * f
    frame = 1 - (1 - frame) * (1 - np.clip(rain, 0, 1)[..., None] * rain_light)   # screen
    g = np.asarray(Image.fromarray(grain[i]).resize((W, H), Image.BILINEAR))[..., None]
    frame = np.clip(frame + g * GRAIN, 0, 1)
    writer.send((frame * 255 + 0.5).astype(np.uint8).tobytes())
    if i % 24 == 0:
        print(f"frame {i}/{FRAMES}  {time.time() - t0:.1f}s", flush=True)
writer.close()
Image.fromarray((bike_soft * 255).astype(np.uint8)).save(out.replace(".mp4", "_bikemask.png"))
Image.fromarray((plate * 255).astype(np.uint8)).save(out.replace(".mp4", "_plate.png"))
print(f"done {out} in {time.time() - t0:.1f}s")
