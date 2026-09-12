repo: tincturein-dot/GatewayDesignWebsite.
branch: main

## Last sync
date: 2026-07-26
note: Synced to the repo. The design export `The Gateway Designs.dc.html` lands
in the repo as `index.html`; everything else keeps its export filename.

### Updated in this project
- Hero rebuilt with animated WebGL mesh gradient (blue palette) + CSS fallback
- GSAP + ScrollTrigger drive all hero/scroll motion
- Mobile hero sizing fixed (≤900px breakpoint, top-aligned, content-height)
- Velorah CTA mockup redesigned in Archivo/mono editorial style; AI chat panel removed
- SEO meta + JSON-LD, sitemap.xml, robots.txt added

### Content pass (2026-07-26)
- Studio relocated to Delhi throughout (was Jaipur).
- All unsupported claims removed: launch counts, founding date, stats band,
  client-count copy, six invented client projects, Instagram grid and handle,
  phone number, "six weeks" promise, placeholder social links.
- Work page is now three self-initiated concept studies, labelled as concepts.
- New journal at /journal/ — index + three articles as static pages, outside the
  Design Component so they have real, crawlable URLs.

### Changed after export
Re-apply these after a fresh export — details in README.
- `componentDidUpdate` now tracks previous state itself (`this._prevState`); the
  runtime passes only `prevProps`, so reading `prevState.page` threw on every
  update.
- Contact form actually submits: named fields, `FORM_ENDPOINT` JSON POST,
  sending/sent/error states, prefilled `mailto:` fallback.
- Fallback font stacks added to every `Archivo` and `Hanken Grotesk`
  declaration (headings previously fell back to the default serif).
- Favicon set, `og-image.jpg` and the matching og/twitter/JSON-LD image tags.

## Screen map
| Screen | Built from |
| --- | --- |
| Home / Work / About / Contact | index.html (single Design Component, internal page switcher) |
| Hero background shader | mesh-gradient.js |
| Journal index + 3 articles | journal/*.html — hand-built static pages, not part of the Design Component |
