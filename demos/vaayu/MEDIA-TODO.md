# Vaayu — where the hero clip came from, and how to replace it

`media/hero.mp4` is a seamless 6s loop **rendered for this page**, not filmed and
not model-generated. The renderer is kept at
`assets/source/vaayu/render_hero.py`: three streak layers travelling at
different rates, two breathing glows, and a gust crossing once per loop. Every
drift covers a whole number of periods across the clip, so it wraps without a
seam. It screen-blends over the CSS `.field` in `index.html`, which remains the
real background — if the clip fails to decode, nothing is missing.

Re-render it with:

    python3 assets/source/vaayu/render_hero.py demos/vaayu/media/hero.mp4

It already encodes to the repo's standard (`+faststart`, `-g 6`), so no second
pass is needed. 660 KB for 6s at 720p.

## If you want model-generated footage instead

A cinematic plate of the actual motorcycle would be a different, and in some
ways better, hero. It could not be produced in the session that built this page,
because every generation route was blocked:

| Route | What happened |
| --- | --- |
| Hugging Face Spaces — Wan 2.2, including `kulkas2pintu/wan555` | `invoke` is disabled connector-side. The error is literal: *"The invoke operation is disabled because gradio=none is set."* Schemas read fine; nothing runs. |
| Higgs — Wan 2.7, FLUX.2, Seedream, Nano Banana | *"Out of credits in the selected workspace."* Wan 2.7 quotes 7.5 credits for 5s at 720p, an image 1. Balance 0, trial allowance `available: false`. |
| Running a model locally from GitHub | No GPU (4 CPUs, 15 GB RAM), and every weights host is unreachable from the sandbox — `huggingface.co`, `modelscope.cn`, `hf-mirror.com`, `civitai.com` all refuse the connection. GitHub serves code, not multi-gigabyte weights. |
| Shutterstock | Search returns preview URLs and, per its own tool contract, "does not handle licensing/downloads". Not shippable. |
| Canva | Template graphics, not cinematic product footage. |

The first two are settings, not code:

- **Hugging Face** — the connector sets a header `gradio=none`. Remove it, or set
  it to a space id (`gradio=kulkas2pintu/wan555`), and `invoke` works.
- **Higgs** — top up the workspace. About 9 credits covers the whole set below.

### The two steps

Wan 2.2 and 2.7 are both **image-to-video**; they animate a still rather than
inventing one. So generate the still first, at 1280×720:

> Editorial product photograph of a minimal electric motorcycle on wet black
> asphalt at night, three-quarter rear view, matte charcoal bodywork, no engine
> visible, a single thin acid-lime light strip along the tank. 85mm lens,
> shallow depth of field, hard rim light from camera left, deep blue-black
> ambient, wet ground reflections, fine rain haze, high-contrast cinematic
> grade.

Then animate it. The model's server fetches the image itself, so a path on the
live site works even when the sandbox cannot reach that host:

```json
{
  "operation": "invoke",
  "space_name": "kulkas2pintu/wan555",
  "parameters": {
    "input_image": "https://www.thegatewaydesigns.com/demos/vaayu/media/hero-poster.webp",
    "prompt": "slow cinematic dolly right, fine rain drifting through the rim light, reflections shifting on the wet asphalt, the bike itself still",
    "duration_seconds": 4,
    "steps": 6,
    "quality": 7
  }
}
```

Keep the bike still and move the light and the rain. A hero loop that moves the
subject will fight the wordmark sitting on top of it.

### Then

1. **Re-encode** — non-negotiable, and the root README explains why: exports land
   with the `moov` atom at the end of the file and almost no keyframes, which is
   unusable on a phone.

   ```sh
   ffmpeg -i raw.mp4 -vf scale=1280:720 -c:v libx264 -profile:v main -level 4.0 \
     -pix_fmt yuv420p -crf 27 -preset medium -g 6 -keyint_min 6 \
     -sc_threshold 0 -an -movflags +faststart demos/vaayu/media/hero.mp4
   ```

   Check with `grep -abo moov demos/vaayu/media/hero.mp4` — the offset should be tiny.
2. Swap `#herovid`'s `mix-blend-mode` from `screen` to `luminosity` and drop the
   opacity to about `.45`. Screen is correct for the rendered loop, which is black
   except where it is bright; it would wash out a photographic plate.
