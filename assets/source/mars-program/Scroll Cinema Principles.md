# Scroll-Cinema Design System

A transferable set of principles for building single-page product sites that feel like a film reel rather than a brochure. Extracted from the Aphelion Mars Program build; written to be re-skinned for any brand.

---

## 1. The core idea

The page is a **timeline**, not a stack of blocks. Scroll position is the only clock: it drives video playback, 3D geometry, counters, and reveals. The visitor is not reading a page, they are advancing a sequence. Every heavy element earns its keep by responding to that one input.

Two rules keep this honest:

- **One scroll, one story.** The sequence has a beginning (product exists), a middle (product works, taken apart), and an end (act on it). If a section does not move the story forward, cut it.
- **Motion is deterministic.** Nothing auto-plays a narrative. Scrub instead of loop, so the visitor is always the one advancing time. Reserve autonomous motion for ambient accents (a ticker, a blinking indicator).

---

## 2. Visual system

### Palette
Two values plus one paper colour. In the reference build: near-black `#050505`, near-white `#f2f2f2`, and a mid-grey `#8c8c8c` for all secondary text. Everything else is a transparency of those three. A restricted palette is what lets full-bleed media and giant type coexist without competing.

For other brands: keep the same *structure* — one ground colour, one figure colour, one muted tint for metadata — and substitute the brand's own values. Introduce brand colour as an accent on interactive states only (buttons, active labels), never as a background wash. Avoid multi-stop gradient backgrounds; use a single radial vignette when a section needs depth.

### Type
A two-family system, each with one job:

| Role | Treatment |
| --- | --- |
| Display | One heavy grotesque (800–900 weight), uppercase, `letter-spacing: -.04em`, `line-height: .84–.9`. Sized with `clamp()` from ~34px to ~170px. |
| Metadata | One monospace, 9–12px, `letter-spacing: .16em–.3em`, uppercase, always in the muted tint. Timestamps, spec labels, section numbers, captions. |
| Body | The display family at 400 weight, 15–21px, `line-height: 1.5–1.6`, `max-width: 44ch`, `text-wrap: pretty`. |

The tension between an enormous headline and tiny monospace metadata is what makes the layout feel engineered instead of decorated. Preserve the *ratio* when swapping fonts: display should be 8–12× the metadata size.

### Density and space
Sections breathe with `clamp()` padding (roughly `80px` mobile → `170px` desktop vertical, `16px` → `56px` horizontal). Use one consistent horizontal inset for every section so overlaid text on media lines up with text on solid backgrounds. Hairline rules at 14% opacity separate sections and table rows; they carry the structure so boxes and cards are rarely needed.

### Imagery
Full-bleed or nothing. Media either fills a sticky viewport or sits in a plain `16:9` frame with a monospace caption beneath — no rounded corners, no shadows, no floating cards. Normalise all imagery through one filter (`grayscale(1) contrast(1.1)` in the reference) so mixed sources read as one shoot.

---

## 3. Layout patterns worth reusing

**Adaptive header.** Transparent and generous at rest (26px padding, tagline visible); on first scroll it compacts (14px), gains a blurred translucent background and a hairline border, and drops the tagline. One primary action stays filled at all times.

**Sticky scrub stage.** A tall section (`height: 210–340vh`) containing a `position: sticky; top: 0; height: 100vh` child. The child holds the media; the extra height is the scrub runway. Progress is `-section.getBoundingClientRect().top / (section.offsetHeight - innerHeight)` — never `offsetTop`, which silently breaks if any wrapper gains padding.

**Overlay text on media.** Gradient scrim (`rgba(ground,.7)` at top → `.05` at 45% → `.85` at bottom) between media and copy. Copy anchored bottom-left, headline over metadata line, stat row beneath.

**Spec table.** Three columns (`label / value / qualifier`), monospace, hairline top border per row, qualifier right-aligned and muted. More credible than icon cards and a fraction of the markup.

**Split panel.** Half full-bleed media, half copy centred vertically, using `repeat(auto-fit, minmax(320px, 1fr))` so it stacks with no media query.

**Ticker strip.** A single-line marquee of live-status fragments between major sections. Cheap, and it makes the page feel instrumented.

**Terminal CTA.** The final section is centred, oversized, and offers exactly two actions: commit, and learn more. Nothing else on screen.

---

## 4. Motion rules

- **Scrub, don't play.** Map scroll progress to `video.currentTime` through a lerp (`cur += (target - cur) * 0.17`) so the frame settles instead of snapping. Only seek when the delta exceeds ~40ms of footage; never seek while `video.seeking` is true.
- **Ease the story beats, not the media.** Use a cubic in-out on derived values (3D explode distance, label highlighting, counters) while the underlying video stays linear against scroll.
- **Reveals are one gesture.** `opacity 0→1` plus `translateY(34px)→0` over ~0.9s on a single ease, fired once by IntersectionObserver at 16% visibility. No stagger cascades, no scale, no blur.
- **Ambient motion stays under 2 seconds** and never competes with the scrubbed subject.
- **Respect short viewports.** Hide scroll hints and secondary chrome below ~660px height rather than letting them collide with CTAs.

---

## 5. Media loading discipline

Scroll-cinema pages are heavy by nature. The load order is part of the design:

1. **Exactly one clip is eager.** The hero video gets `preload="auto"`. Every other clip carries its URL in `data-lazysrc` with `preload="metadata"` and a poster still.
2. **Promote on approach.** An IntersectionObserver with `rootMargin: 150%` assigns `.src` and calls `.load()` about one viewport before the section arrives; it only starts after the hero clip reaches `canplaythrough` (with a ~5s timeout fallback).
3. **Every scrub target has a poster** so a cold section shows a frame, never a black rectangle.
4. **Large stills get `loading="lazy"` and `decoding="async"`** so they do not compete with the hero clip for bandwidth during first paint.
5. **Clamp to the buffer.** When seeking, cap the target time just inside `buffered.end(...)` to avoid stalling the decoder on a cold range.

Skipping any of these produces the same failure: four 1080p clips fighting for the connection and a hero that stays black for tens of seconds.

---

## 6. Demo & capture mode (for social and recording)

A production-grade nicety that costs little and pays back every time the site is filmed:

- A corner control starts a **hands-free scroll** at a constant *pixels-per-second* rate (time-based, so dropped frames change nothing) with an optional multiplier through the hero so a slow launch sequence does not drag.
- A **record action** enters fullscreen *first*, waits for the transition to settle, then requests display capture, composites frames onto a 1920×1080 canvas, and records at a high bitrate. It scrolls once top to bottom and saves automatically.
- Keyboard shortcuts for both, a blinking REC badge with elapsed time, and the demo chrome hides itself while recording.
- Screen capture is blocked inside embedded iframes; detect that case and offer a top-level tab instead of failing silently.

---

## 7. Three.js: a capability, not a requirement

Real-time 3D belongs in this system **only when the product has geometry worth exploring**. Machines, hardware, packaging, architecture, vehicles: yes. Software, services, and editorial: almost never — a scrubbed video does the same job at a fraction of the weight and risk.

When it does apply, two patterns cover most needs:

- **Scroll-driven teardown.** A sticky WebGL stage where scroll progress separates named assemblies along one axis while the camera pulls back. Label the parts in monospace beside the canvas and show a percentage readout. Allow drag-to-rotate with inertia so the model feels live.
- **Piloted object.** A fixed, `pointer-events: none` full-viewport canvas layered above the page, off by default and enabled by an explicit control, where the visitor flies or manipulates an object across the whole site. Delightful as an easter egg, hostile as a default.

Discipline either way: procedural geometry over downloaded assets when the form is simple (cylinders, cones, rings, and instanced repeats go a long way); metalness ~0.95 with roughness ~0.25 and three hard lights for a monochrome studio look; cap `pixelRatio` at 2; dispose renderers on teardown; and always ship a non-3D fallback because the section must still read if WebGL fails.

If a 3D model is supplied rather than generated, compress it (Draco/meshopt, 1K textures) and host it somewhere CORS-permissive. Consumer file-sharing links will not serve it to a browser.

---

## 8. Copy voice

Short declaratives, concrete numbers, no adjectives doing the work of facts. Headlines are two or three words per line, split deliberately across lines for shape. Metadata reads like telemetry (`T+02:41 · Hot-stage separation · 68 km`). Body copy states what the thing does and what it costs, then stops. No "revolutionary", no rhetorical questions, no sentence that could appear on any other company's site.

---

## 9. Adaptation checklist

When applying this to a new brand:

1. Swap the three palette values; keep the ground/figure/muted structure.
2. Swap the two type families; keep the display-to-metadata size ratio and the uppercase monospace metadata.
3. Decide the story beats (usually 5–7), then assign each a pattern from §3.
4. Choose exactly one hero scrub subject and shoot or generate it as a single continuous shot, 10–15s, locked-off camera.
5. Decide whether 3D earns its place (§7). Default to no.
6. Wire the loading discipline (§5) before adding the second clip, not after.
7. Ship demo/capture mode if the site will be filmed for social.
