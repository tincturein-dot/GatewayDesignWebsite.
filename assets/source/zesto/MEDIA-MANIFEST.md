# Media Manifest

The export pointed at eight CloudFront assets on an account-scoped path. None
of the original filenames carried any meaning, so the mapping below was worked
out from where each URL is used in `ZESTO.dc.html` and re-derived names were
given on the way in. Keep this file: without it a re-export cannot be matched
back to the shipped media.

Stills ship as **WebP** (quality 90) rather than the delivered PNGs — 13.2 MB
down to 2.3 MB, all at 825×1100 so no resize was needed.

## Video

| Shipped as | Original | Used for | Section |
| --- | --- | --- | --- |
| `zesto-film-20s.mp4` | `hf_20260811_194519_2f6665ab-88e6-4230-9b06-3a938123ba7a.mp4` | The 20s opening film. Scroll-scrubbed across a 520vh sticky stage. | `#film` |
| `zesto-pour-5s.mp4` | `hf_20260811_192935_0b03bc0b-1317-419c-8868-f080ee05287e.mp4` | Oil pouring into the jar, scrubbed through five captioned beats. | `#scrub` |

Both are **re-encoded before shipping** — see the README. As delivered they had
the `moov` atom at the end of the file and one or two keyframes in the whole
clip, which makes them effectively unusable on a phone. Ship them with
`-movflags +faststart` and `-g 6`, and give each one a poster frame; the two
posters below were extracted from frame 0 of each clip.

| Poster | From | Size |
| --- | --- | --- |
| `film-poster.webp` | `zesto-film-20s.mp4` frame 0 | 0.04 MB |
| `pour-poster.webp` | `zesto-pour-5s.mp4` frame 0 | 0.11 MB |

## Stills

| Shipped as | Original | Used for | Size |
| --- | --- | --- | --- |
| `01-hero-jar.webp` | `hf_20260811_192743_dbc13448-97a0-4154-a164-35a85dae3c5a.png` | `image-slot#hero-jar` — the bobbing jar beside the headline. | 0.49 MB |
| `02-pour-still.webp` | `hf_20260811_192743_8c1c3c54-9760-4cbc-92a6-3d6b48cc129e.png` | `image-slot#scrub-jar` — shown until the pour video reports metadata. | 0.38 MB |
| `03-jar-original.webp` | `f855e072-0bdd-4902-8fd2-9d2c72917214.png` | Jar 1, "Original Aam". | 0.32 MB |
| `04-jar-chilli.webp` | `740ac014-79ed-4afb-b2c7-6735a69ae497.png` | Jar 2, "Chilli Riot". | 0.52 MB |
| `05-jar-sweet-sour.webp` | `97c9a8ea-e979-4f55-9455-66b9e6270060.png` | Jar 3, "Sweet & Sour". | 0.17 MB |
| `06-sun-curing.webp` | `hf_20260811_192743_6549c6fb-7d80-475f-967b-597f2b75627a.png` | `image-slot#process-shot` — terrace shot beside the four method steps. | 0.50 MB |

## A trap in the rewrite

Five of the eight are written as whole URLs and rewrite cleanly. The last three
are **not**: the script builds them by concatenating a hash onto a prefix
constant, so a search-and-replace over full URLs silently leaves them pointing
at CloudFront.

    const IMG = 'https://…cloudfront.net/user_…/hf_20260811_192743_';
    { slotId: 'jar-1', img: IMG + 'f855e072-….png', … }

Both halves have to change — `IMG` becomes `'media/'` and each concatenated
hash becomes its friendly name. Grep the built file for `cloudfront` before
shipping; it should return nothing.

## Source

Claude Design export, `ZESTO.dc.html` plus `support.js` and `image-slot.js`.
Built from the `.dc.html`, **not** the `-recordable-` build — the README
records why that build renders its own runtime source as page text.
