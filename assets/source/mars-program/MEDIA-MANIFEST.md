# Media Manifest

Original Higgsfield filenames, kept as generated. Video: Seedance 2.5. Stills: Seedream 5 Lite. All monochrome 16:9.

Stills are shipped as **1920px WebP** (quality 90) rather than the full-resolution PNGs, to keep the set under 30 MB. Total: ~16.7 MB.

## Video

| File | Used for | Section | Size |
| --- | --- | --- | --- |
| `hf_20260812_191533_597e2cab-2325-45b8-8176-5e64d580d015.mp4` | Hero — pad ignition through liftoff. The only eagerly-loaded clip. | `#hero` | 3.2 MB |
| `hf_20260812_191928_a2bb967b-b06f-4a48-a3ef-a42e21936bc4.mp4` | "Six parts, one vehicle" — rocket disassembling into an exploded view. | `#explode` | 1.3 MB |
| `hf_20260812_191930_bbe05d45-276e-4838-a20c-5701f3260684.mp4` | "It comes apart on cue" — hot-stage separation with telemetry readout. | `#sep` | 4.6 MB |
| `hf_20260812_191933_cc9ded5a-c006-4c6d-9e86-7391b8ba9252.mp4` | Inline 16:9 frame captioned "03 — Engine bay teardown". | inside `#specs` | 4.7 MB |
| `hf_20260813_184639_fbeadd21-cfe2-4708-8dca-27cbde0a758a.mp4` | "Every part, on its own" — slow orbit around the separated stack. | `#teardown` | 1.5 MB |

All five are scroll-scrubbed (scroll position drives `currentTime`), 10–15s each.

## Stills

| File | Used for | Size |
| --- | --- | --- |
| `hf_20260812_183055_35968279-c439-410a-8224-a9b5388c4dd3.webp` | Poster frame for the hero clip — first thing visible before video decodes. | 0.22 MB |
| `hf_20260812_183055_712c03b1-b07a-47a4-9b68-edfece1269c7.webp` | Vehicle figure 01 "Raptor-class cluster". Also poster for the exploded and engine-teardown clips. | 0.38 MB |
| `hf_20260812_183055_e5207482-c9a0-4e02-b5df-4b1fa557a691.webp` | Vehicle figure 02 "Parking orbit". Also poster for the separation clip. | 0.06 MB |
| `hf_20260812_183055_eecd7c69-6129-4c46-b5df-38db33d14a52.webp` | Left half of the "Eight minutes back home" split panel (3:4 portrait, kept at 1728×2304). | 0.15 MB |
| `hf_20260812_183055_e861e977-43ee-451b-b36d-37ccd217898f.webp` | Full-bleed background of the "Somewhere flat and cold" landing-site section. | 0.53 MB |

## Source

All served from one CloudFront prefix, filenames unchanged:

```
https://d8j0ntlcm91z4.cloudfront.net/user_3HmSnuni6n6rAaPZw41wetwAObx/
```

To serve locally, swap that prefix for your own path. Two attributes carry video sources — `src` on the hero clip, `data-lazysrc` on the other four (the loader promotes it to `src` about one viewport ahead of the section). The host must send permissive CORS headers or scrubbing fails silently in some browsers.

## Before shipping

The stills are already web-ready at 1920px WebP. If you need the untouched 2848×1600 PNGs, re-download them from the CloudFront prefix above — the filenames match, only the extension differs.

The clips are still as generated. Re-encode at CRF 24–26 with a keyframe every 0.5s before going live: dense keyframes matter more than bitrate here, since scrubbing seeks constantly and sparse keyframes are what makes it feel jittery.
