import sys, numpy as np
from PIL import Image
src, dst = sys.argv[1], sys.argv[2]
im = np.asarray(Image.open(src).convert("RGB")).astype(np.float32) / 255
hsv = np.asarray(Image.open(src).convert("RGB").convert("HSV")).astype(np.float32) / 255
h, s, v = hsv[..., 0] * 360, hsv[..., 1], hsv[..., 2]
# Lime/green band (roughly 60-160deg) keeps its colour; everything else goes to ink.
d = np.minimum(np.abs(h - 100), 360 - np.abs(h - 100))
keep = np.clip(1 - (d - 45) / 20, 0, 1) * np.clip((s - .18) / .15, 0, 1)
lum = (0.2126 * im[..., 0] + 0.7152 * im[..., 1] + 0.0722 * im[..., 2])[..., None]
# Neutral grade with the faintest cool cast in the shadows (the brief's blue-black ambient).
cool = np.array([0.94, 0.98, 1.06], dtype=np.float32)
neutral = np.clip(lum * cool, 0, 1)
# Recolour the kept band to acid lime #CCFF00 at the pixel's own brightness.
lime = np.array([0xCC, 0xFF, 0x00], dtype=np.float32) / 255
limed = np.clip(lime * (v[..., None] * 1.15) + (v[..., None] ** 3) * 0.25, 0, 1)
out = neutral * (1 - keep[..., None]) + limed * keep[..., None]
# High-contrast S-curve, ink blacks.
out = np.clip(out, 0, 1); out = out * out * (3 - 2 * out) * 0.55 + out * 0.45
Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8)).save(dst, quality=92)
