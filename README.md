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

Any other static host works the same way (Netlify, Cloudflare Pages, GitHub
Pages); there is nothing to build.

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

## Templates

The studio sells premium Framer website templates alongside client work. The
Templates page lives in `index.html` behind the `isTemplates` page state and is
reachable from the nav overlay (03), the footer menu, the hero CTA, and the
teaser section on the home page.

One constant controls checkout:

```js
const CHECKOUT_URL = '';                           // paste your checkout link here
const TEMPLATE_PRICE = '$59';
```

Set `CHECKOUT_URL` to the payment link your processor gives you and the
**Buy — $59** button points straight at it. While it is empty the button falls
back to a **prefilled `mailto:`** to `CONTACT_EMAIL` asking for a payment link
— the same pattern the contact form uses, so the button is never dead and the
page never advertises a checkout that doesn't exist. The small line under the
buttons switches wording to match.

Product copy lives in two places: the `templateFeatures` array in
`renderVals()` (the seven-item feature list) and the markup of the Templates
page itself (name, price, blurb). The live-demo URL is a plain `href` in the
markup on both the Templates page and the home teaser.

**Adding a second template** means turning the single hard-coded product block
into an `sc-for` over a `templates` array, the way `projects` and `services`
already work — the page was written so that is a contained change.

The Templates page has a direct URL: **`/#templates`**. See Routing below.

## Routing

Every page is component state, not a path, so the site uses hash routing to
give each one a linkable URL:

| URL | Page |
|---|---|
| `/` | Home |
| `/#work` | Work |
| `/#templates` | Templates |
| `/#studio` | Studio |
| `/#contact` | Contact |

Two tables at the top of the logic script are the whole mapping — `SLUG_TO_PAGE`
and `PAGE_TO_SLUG`. Home is deliberately the bare path with no fragment, and an
unrecognised fragment falls back to Home rather than rendering nothing.

Navigation uses `history.pushState` rather than assigning `location.hash`,
because assigning fires a `hashchange` the app would then have to ignore.
pushState fires neither event, so the `popstate`/`hashchange` listener only ever
hears the back button and hand-typed URLs — never the app's own navigation.

Two consequences worth knowing. A fragment is **never sent to the server**, so
every URL above is one request for `index.html` and no Vercel rewrite is needed.
And search engines generally treat `/#templates` as the same document as `/`, so
these are good links to give a person and are not separate entries for
`sitemap.xml`.

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
