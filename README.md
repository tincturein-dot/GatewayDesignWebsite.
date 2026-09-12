# The Gateway Designs — website

Marketing site for The Gateway Designs, a Delhi web design studio. Static site,
no build step: `index.html` is the site, plus a set of plain static pages under
`journal/`.

## Structure

| Path | What it is |
| --- | --- |
| `index.html` | The site. One Design Component (`<x-dc>` template + `DCLogic` class) with an internal page switcher for Home / Work / Studio / Contact. |
| `support.js` | Design Component runtime — parses the `<x-dc>` template, loads React from CDN, and mounts the component into `#dc-root`. Generated; don't hand-edit. |
| `mesh-gradient.js` | WebGL animated mesh gradient behind the hero (simplex-noise shader). Falls back to the CSS `heroDrift` gradient if WebGL is unavailable. |
| `journal/` | The journal: an index and three articles as plain static HTML + `journal.css`. No runtime — each article is a real, crawlable URL. |
| `robots.txt`, `sitemap.xml` | SEO. Both reference `https://www.thegatewaydesigns.com`. |
| `favicon.svg`, `favicon-32.png`, `apple-touch-icon.png` | The arch mark on the deep-blue brand gradient. |
| `og-image.jpg` | 1200×630 link-preview card — the hero shader plate with the headline set in Archivo. |
| `vercel.json`, `.vercelignore` | Cache + security headers, and the list of files kept out of the deploy. |
| `assets/source/` | Original design source material (After Effects project for the gradient, reference renders, hero mock). Not referenced by the site — kept for archive only. |
| `github.md` | Sync log from the design tool: what changed after each export, and the list of edits to re-apply on a fresh export. Not deployed. |
| `.gitignore` | Excludes `node_modules/`, OS cruft, `.vercel/` and `.env*`. |

Content claims: everything on the site is either a statement about how the
studio works or clearly-labelled concept work. There are no launch counts,
founding dates, client names or testimonials, because there is nothing yet to
put behind them.

`index.html` is the export from the design tool, where it is named
`The Gateway Designs.dc.html`. When re-exporting, copy the new export over
`index.html` — the runtime derives its root name from the filename and works
fine as `index.html`.

> **One divergence from the export.** `componentDidUpdate` was changed to track
> the previous state on `this._prevState` instead of reading a `prevState`
> second argument — the runtime only passes `prevProps`, so the original threw
> on every update and silently skipped re-init of the hero shader, the CTA
> layout and the scroll animations after a page change. Re-apply this after any
> fresh export.

## Run locally

Any static file server works; it must be served over HTTP (the runtime fetches
its own document, so `file://` won't do).

```sh
python3 -m http.server 8000
# → http://localhost:8000
```

## Deploy

Vercel, repo root as the publish directory. No framework, no build command, no
output directory — `vercel.json` only sets cache and security headers, and
`.vercelignore` keeps `assets/source/` and the docs out of the deploy.

`vercel.json` carries two Cache-Control rules for the same document: one for
`/` and one for `/index.html`. That is deliberate, not duplication — a `source`
of `/index.html` does not match the URL the homepage is actually served at, and
`/(index.html)?` does not match `/` either. Two rules is the only spelling that
covers both.

**Production deploys from `main`.** Pushing to `main` updates the live site at
www.thegatewaydesigns.com; any other branch gets a preview deployment. If a push
does not appear on the live site, check that the Vercel project serving the
custom domain is the one connected to this repository — a second project
pointing at the same repo will happily build the same commits without ever
touching the domain.

Any other static host works the same way (Netlify, Cloudflare Pages, GitHub
Pages); there is nothing to build.

## Demos

`demos/<slug>/index.html` holds a self-contained Claude Design export — the
**recordable** build, which inlines its own runtime, so it needs no `support.js`
next to it and cannot collide with the site's copy (they are different
versions). Each demo is a normal page at `/demos/<slug>/`.

Live now: `demos/mars-program/` — *Aphelion, Mars Program*, a scroll-cinema
product site. It is embedded in the Work page as a lazy-loaded `<iframe>` and
also opens full screen.

**Two edits are applied to every export** and must be re-applied after a fresh
one:

1. A `<title>`, description, `robots: noindex, follow` and the favicon links —
   exports ship with none, and a demo should not compete with the studio in
   search.
2. A back-link to `/`, hidden unless the demo is the top-level document
   (`window.self === window.top`). Full screen it is the only way back; inside
   the Work-page embed the studio header is already on screen.

The embed renders live but with `pointer-events: none` until the visitor clicks
it. The piece is 13,000px of scroll-driven cinema, so left interactive it would
swallow the page's own scroll the moment a cursor crossed it.

**Media is self-hosted.** The export originally pointed at ten CloudFront
assets on an account-scoped path — one URL expiry from an empty black page. All
ten now live in `demos/mars-program/media/` and every reference was rewritten to
a relative path, so the demo has no external dependency beyond React and the
fonts. Being same-origin also removes the CORS requirement the export's manifest
warns about, which is what makes scrub-seeking fail silently in some browsers.

Stills ship as 1920px WebP (1.4 MB) rather than the untouched 2848x1600 PNGs
(9.9 MB); the filenames differ only by extension, so the rewrite maps `.png` to
`.webp`. Media filenames are content-stamped and never change, so `vercel.json`
caches `/demos/*/media/*` for a year as immutable while the demo page itself
stays on a one-hour revalidate.

Video sources sit on two attributes: `src` on the hero clip, `data-lazysrc` on
the other four, which a loader promotes about a viewport ahead. The clips are
scroll-scrubbed — scroll position drives `currentTime` — so if scrubbing ever
feels jittery the cause is keyframe spacing, not bitrate. The asset manifest in
`assets/source/mars-program/MEDIA-MANIFEST.md` recommends re-encoding at CRF
24-26 with a keyframe every 0.5s; the clips ship as generated.

Design source for each demo is archived in `assets/source/<slug>/`, which is not
deployed.

## Contact form

`index.html` defines two constants at the top of the logic script:

```js
const FORM_ENDPOINT = '';                          // where submissions POST
const CONTACT_EMAIL = 'hello@thegatewaydesigns.com';
```

Set `FORM_ENDPOINT` to any URL that accepts a JSON body — Formspree, Basin, a
Vercel function, your own API. Submissions POST as:

```json
{ "name": "…", "email": "…", "need": "…", "message": "…" }
```

A 2xx response shows the "Thank you" panel. While `FORM_ENDPOINT` is empty, or
if the request fails, the form shows a fallback panel with a **prefilled
`mailto:`** to `CONTACT_EMAIL` — so inquiries still reach the studio and the
site never claims to have sent something it didn't.

## Adding a journal article

Copy any file in `journal/`, then update, in order: `<title>`, the description,
`<link rel="canonical">`, the og/twitter title and description, the `Article`
JSON-LD (`headline`, `description`, `datePublished`, `url`, `mainEntityOfPage`),
the third `BreadcrumbList` item, and the "Next" link at the foot. Then add the
entry to three places: `journal/index.html` (the `.entries` list and the `Blog`
JSON-LD's `blogPost` array), `sitemap.xml`, and the `articles` array in
`index.html` if it should appear on the home page.

## Known gaps

- **Only `/` and the journal pages are indexable.** Work, Studio and Contact are
  rendered by a client-side page switcher that never changes the URL, so a
  crawler only ever sees Home. Giving them their own URLs means real routes —
  separate HTML files, or a router plus prerendering. Worth doing before any
  paid traffic lands on the site.
- **No social profiles.** The footer and JSON-LD `sameAs` previously pointed at
  `instagram.com` and `dribbble.com` homepages, which is why they were removed.
  Send real handles and they go back into the footer, the menu and `sameAs`.
- **No phone number.** The one in the export (`+91 141 555 0192`) was a fake
  Jaipur number and was removed. Email is the only contact route right now.
- **Concept studies are described, not shown.** The three studies on the Work
  page have copy and a gradient panel, no imagery. Real screens would make that
  page considerably stronger.

## Where the content lives

Copy, project lists and nav all live in the `renderVals()` method of the
`<script type="text/x-dc">` block at the bottom of `index.html`:

- `projects` — the concept studies (all three also feed the home grid)
- `services` — the "What we make" rows
- `steps` — the "How we work" rows
- `articles` — the three journal entries shown on the home page

## External dependencies

Loaded at runtime from third-party CDNs — the page needs network access for
these, and they are points of failure worth knowing about:

- React + ReactDOM 18.3.1 and `@babel/standalone` from unpkg (fetched by
  `support.js`, with SRI hashes)
- GSAP + ScrollTrigger 3.13.0 from jsDelivr
- Archivo, Hanken Grotesk, Instrument Serif, Spline Sans Mono from Google Fonts
- The CTA mockup video from a CloudFront URL

Motion degrades gracefully: without GSAP the reveal animations simply don't run,
and `prefers-reduced-motion: reduce` disables animation throughout.
