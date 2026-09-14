"""Build the Vaayu demo's shipped media from the plate sources in this folder.

Run from this folder with Pillow + numpy:  python build_media.py <encoded hero mp4>

vercel.json serves /demos/*/media/* as immutable for a year, so every shipped
file is named <name>-<sha256[:8]>.<ext>: a changed image gets a new URL instead
of hiding behind a year of browser cache. The script prints the names to paste
into demos/vaayu/index.html and removes the files it replaces.

Inputs
  flux-still.webp   the FLUX.1-schnell still (prompted for a sealed pack, no exhaust)
  hero mp4          render_plate.py's loop after the README's ffmpeg encode
Outputs in demos/vaayu/media/
  plate-<h>.mp4           hero loop
  plate-poster-<h>.webp   graded still, the video's poster
  fig-pack-<h>.webp       4:5, the lime-outlined structural pack   (03 The machine, Fig. 01)
  fig-hub-<h>.webp        3:2, rear hub and swingarm              (03 The machine, Fig. 02)
  model-street-<h>.webp   3:2, the whole bike                     (04 Street card)
  model-long-<h>.webp     3:2, the front end                      (04 Long card)
  model-zero-<h>.webp     3:2, seat, tail and tank line           (04 Zero card)
Every image is a crop of the one still, so the page reads as one machine, and
no crop is enlarged more than about 2x at its largest display size on a 2x screen.
"""
import hashlib, shutil, sys
from pathlib import Path
from PIL import Image, ImageFilter

from grade import grade

HERE = Path(__file__).resolve().parent
MEDIA = HERE.parents[3] / "demos" / "vaayu" / "media"   # plate -> vaayu -> source -> assets -> repo
CROPS = {  # name: (box in the 1280x720 graded still, output size)
    "fig-pack": ((560, 110, 940, 585), (760, 950)),
    "fig-hub": ((300, 330, 690, 590), (780, 520)),
    "model-street": ((250, 90, 1070, 637), (1200, 800)),
    "model-long": ((640, 150, 1100, 457), (920, 614)),
    "model-zero": ((380, 150, 800, 430), (840, 560)),
}


def ship(src: Path, stem: str, ext: str) -> str:
    h = hashlib.sha256(src.read_bytes()).hexdigest()[:8]
    for old in MEDIA.glob(f"{stem}-*.{ext}"):
        old.unlink()
    name = f"{stem}-{h}.{ext}"
    shutil.copyfile(src, MEDIA / name)
    return name


def main():
    tmp = HERE / ".build"
    tmp.mkdir(exist_ok=True)
    graded = grade(Image.open(HERE / "flux-still.webp").convert("RGB"))
    names = {}
    poster = tmp / "poster.webp"
    graded.save(poster, "WEBP", quality=62, method=6)
    names["poster"] = ship(poster, "plate-poster", "webp")
    for stem, (box, size) in CROPS.items():
        out = tmp / f"{stem}.webp"
        card = graded.crop(box).resize(size, Image.LANCZOS)
        card = card.filter(ImageFilter.UnsharpMask(radius=1.2, percent=45, threshold=2))
        card.save(out, "WEBP", quality=74, method=6)
        names[stem] = ship(out, stem, "webp")
    if len(sys.argv) > 1:
        names["hero"] = ship(Path(sys.argv[1]), "plate", "mp4")
    shutil.rmtree(tmp)
    for k, v in names.items():
        print(f"{k:14s} {v:34s} {(MEDIA / v).stat().st_size / 1024:8.1f} KB")


if __name__ == "__main__":
    main()
