"""Grade a still so acid lime is the only colour: python grade.py <src> <dst>"""
import sys
import numpy as np
from PIL import Image


def grade(img: Image.Image) -> Image.Image:
    rgb = img.convert("RGB")
    im = np.asarray(rgb).astype(np.float32) / 255
    hsv = np.asarray(rgb.convert("HSV")).astype(np.float32) / 255
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
    out = np.clip(out, 0, 1)
    out = out * out * (3 - 2 * out) * 0.55 + out * 0.45
    return Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8))


if __name__ == "__main__":
    grade(Image.open(sys.argv[1])).save(sys.argv[2], quality=92)
