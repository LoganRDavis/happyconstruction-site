# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Static marketing site for Happy Construction — a commercial general contractor. No build step, no framework, no package manager. Plain HTML/CSS/JS served as files, deployed to Cloudflare Pages.

**This repo is currently a scaffold.** The Pages plumbing, shared chrome, and design-token system are real and working. **The logo, icon set, share card, and palette are real** — the brand assets come from the client's kit and are generated from the masters in `brand/`; the palette is derived from the brand gold. Every piece of *content* — copy, photography, phone, email, address, service list, project list, and every number in the proof strip and safety block — is a deliberate placeholder awaiting client direction. Do not treat any of it as fact, and do not invent replacements: if you need a value that isn't in the "Placeholders" table below, ask.

**Never invent a credential.** The proof strip (`index.html`) and safety block (`about.html`) hold fake figures — EMR, project counts, license number, years in business. These are the highest-risk placeholders in the repo: unlike lorem copy, a fabricated EMR or license number looks plausible and would ship as a lie. Drop any line the client can't substantiate rather than softening it.

## Placeholders

Nothing in this table is real. Replace each before launch.

| Placeholder | Where it appears |
| --- | --- |
| `(555) 555-5555` / `+15555555555` | `js/components.js` (`PHONE_DISPLAY`, `PHONE_TEL`), `contact.html`, `index.html` JSON-LD |
| `info@happyconstructionar.com` | `js/components.js` (`EMAIL`), `contact.html`, `index.html` JSON-LD |
| Office address, hours | `contact.html` ("Address pending" / "Hours pending") |
| Proof-strip figures (`00` years, `000+` projects, `0.00` EMR, `AR License #000000`) | `index.html` `.proof-strip`. **Fabricating any of these would ship a false credential** — see the warning above. |
| Safety figures (EMR, recordable rate, OSHA hours, affiliations) | `about.html` `.section-dark` safety block. Same warning. |
| Service categories | `services.html` cards + the matching three cards on `index.html` — keep them in sync |
| Delivery-phase descriptions | `services.html` "How We Work". The four phase *names* are industry-standard and can stay; every description is placeholder. |
| Project tiles | `projects.html`, `index.html` — striped `.tile-media` frames stand in for photography; sector, name, city, and year are all placeholder. Ask whether any project is under NDA or needs owner sign-off. |
| Footer "Service Areas" | `js/components.js` `SiteFooter` |
| All body copy | Every `.html` file. Every paragraph is marked "Placeholder". |
| `.wip-banner` | Top of each page's `<main>`. **Delete the `<p class="wip-banner">` from all five pages before launch**, and the `.wip-banner` rule from `css/main.css`. |

Search for `Placeholder`, `placeholder`, `pending`, and `TODO` to find them all.

The production domain is **https://www.happyconstructionar.com** (`happyconstruction.com` was not purchased). It is hardcoded in canonicals, OG `url`, `sitemap.xml`, `robots.txt`, and JSON-LD `@id`/`url`. If the domain ever changes, all five must change together.

## Commands

- `make serve` — Local dev server at http://localhost:8000. Runs `serve.py`, a thin wrapper around Python's `http.server` that mimics Cloudflare Pages' `.html` behavior: serves `/foo` from `/foo.html` and 308-redirects `/foo.html` → `/foo`. Keep that parity if you touch `serve.py` — the whole site relies on extensionless canonicals and local dev must match prod.
- Pushing to `main` deploys automatically via Cloudflare Pages.
- **Playwright MCP screenshots:** the `--output-dir .playwright-mcp` flag in `.mcp.json` is only honored when `filename` is omitted (the auto-named `page-{timestamp}.png` lands there correctly). Passing a bare relative `filename` writes to **repo root** instead and slips past the `/desktop-*.png` / `/mobile-*.png` gitignore patterns. Either omit `filename` or prefix it explicitly: `".playwright-mcp/<name>.png"`.

## Architecture

Each page is a fully self-contained HTML file — there is no template engine. To add a page, copy an existing page (e.g. `about.html`) and update:

1. `<title>`, `<meta name="description">`, OG/Twitter tags, and `<link rel="canonical">`. **Canonicals and all internal `href`s are extensionless** (`/about`, not `/about.html`) — Cloudflare Pages serves `/foo.html` under `/foo` and 308-redirects the `.html` form, so using `.html` URLs in canonicals creates a redirect loop with any reverse rule.
2. Add the page to `sitemap.xml` with its extensionless URL. **Do not add `<lastmod>`** unless you have a real per-page edit-tracking workflow — static or generation-time dates get ignored by Google and waste the signal.
3. Add a trailing-slash alias to `_redirects` (`/foo/ → /foo 301`). The extensionless URL is served natively by Pages; do **not** add `/foo → /foo.html` rules (they loop against Pages' built-in `.html` stripping).
4. If the page should appear in primary nav, add it to `NAV_LINKS` in `js/components.js` using the extensionless href.

**Shared chrome via web components.** Header and footer are custom elements defined in `js/components.js` (`<site-header>`, `<site-footer>`). Pages must include `<script src="/js/components.js" defer>` and drop the elements into the body. Active nav state is derived from `window.location.pathname`, so nav links use absolute paths from root. Phone, email, and the logo geometry are module-level constants at the top of that file — change them in one place, not per page (except the JSON-LD blocks, which are per-page and must be updated separately).

Both logo variants render through a single `logoPicture(variant, attrs)` helper that emits a `<picture>` with a WebP `<source>` and a PNG fallback plus a 2x `srcset`. The header takes the black wordmark, the footer the white knockout. See `images/README.md`.

### Brand assets

`brand/` holds the hand-authored SVG masters. **Every shipped raster and `favicon.svg` is generated from them** by `python3 brand/build-site-assets.py` — don't hand-edit the outputs. The script is deterministic, so a rerun leaving a dirty tree means a master actually changed. `brand/README.md` covers the two traps it encodes: aspect-ratio distortion on square icons, and the simplified-mark-below-24px rule for favicons.

`brand/` is excluded from the deploy via `.cfignore` and 302-bounced in `_redirects`, same as the other tooling paths.

**Asset paths are absolute** (`/css/main.css`, `/images/...`) — relative paths will break because the dev server and Cloudflare Pages both serve from root.

`404.html` is standalone — it uses `/css/404.css`, not `main.css`, and does not include `<site-header>`/`<site-footer>`. Edit it directly without touching shared chrome. Its colors are hardcoded hex, not tokens, so a palette change has to be applied there by hand. Pages auto-serves `404.html` as the fallback for any non-existent path *with a real 404 status* (the desired behavior). One quirk: a direct visit to the extensionless `/404` returns 200 (Pages' `.html`-stripping makes it addressable as a normal page), which is technically a "soft 404." Fixing it would require a Pages Function — `_redirects` only supports 301/302/303/307/308, not 4xx rewrites. Accepted as an edge case; revisit if Search Console ever flags it.

### Design tokens

CSS custom properties in `:root` at the top of `css/main.css` are the single source of truth for color, type, elevation, and geometry. **Nothing below `:root` hardcodes a hex** — that is intentional, so the whole site re-skins from that one block. Keep it that way.

**The palette is real**, derived from the brand gold. The neutrals are deliberately warm-shifted; the original cool blue-greys fought the gold.

| Token | Hex | Role |
| --- | --- | --- |
| `--ink` | `#17130F` | warm near-black — headings, hero and footer ground |
| `--slate` | `#574F45` | body copy, 8.05:1 on white |
| `--slate-light` | `#6E6459` | muted labels, 5.78:1 on white |
| `--accent` | `#FDCB17` | brand gold — **fill only** |
| `--accent-dark` | `#7A5E00` | gold that survives as text, 6.12:1 on white |
| `--accent-light` | `#FFF1C2` | gold wash — proof strip, sector badges |
| `--concrete` | `#FAF7F1` | warm off-white, alternating sections |

Two rules the sheet depends on:

* **`--accent` is never text on a light surface.** `#FDCB17` is 1.53:1 on white. It is a fill: buttons, rules, the CTA band, the proof strip, and type on `--ink` (12.08:1 there). Gold *text* on light is `--accent-dark`. On `--ink`, even `--accent-dark` fails at 3.02:1 — that's why `.hero .eyebrow` and `.section-dark .eyebrow` both override to `--accent`.
* **`--accent-dark` must stay dark enough to carry white text**, because `.btn:hover` and `.header-phone:hover` reverse out of it.

Every pair is verified AA. If you change a token, re-audit — the fastest way is a headless pass that walks every text node's computed color against its composited background, since the failures that matter are the inherited ones (`.section-dark` inverting `.detail-list`, a `.hero` eyebrow) rather than anything visible in `:root`.

**Four files hold color and drift silently.** A palette change means all four together: `:root` in `css/main.css`, `css/404.css` (hardcoded, standalone), `theme_color` in `site.webmanifest`, and `<meta name="theme-color">` in all five page heads. `theme-color` is currently the gold `#FDCB17`, not `--ink` — deliberate, so the mobile browser chrome carries the brand.

The white-knockout footer logo was built against `--ink`. If the footer ground changes materially, confirm the mark's black linework still separates.

### Visual direction

The brand is a yellow smiley face in a hard hat with the tagline "Building with a smile." Every commercial GC surveyed in this market reads sober — navy (Nabholz, Liberty), red (Crossland), neutral grey (Commerce, Oelke). None are playful.

**So let the logo be the only friendly thing on the page.** The gold does the warmth; everything around it — typography, project naming, numbers, safety language — stays as sober as the competition. That is why the hero and footer sit on near-black rather than on gold: the dark ground frames the mark instead of amplifying it. A site that is playful *everywhere* reads residential, and the buyer here is an owner or developer comparing bids.

The structural additions (proof strip, safety block, sector-labelled project tiles, delivery-phase framing) all come from that survey — they exist because every competitor has them and their absence reads as an unqualified firm. Don't remove them to save space; fill them in.

### Fonts

Currently the **system font stack** (`--font-body` / `--font-display`), chosen because no typeface has been selected. Nothing is downloaded, so there's no webfont cost yet.

When a typeface is chosen, self-host it rather than linking Google Fonts — the CSP in `_headers` sets `font-src 'self'` and would block a CDN. The procedure:

1. Drop WOFF2 subsets in a new `fonts/` directory.
2. Add `@font-face` blocks at the top of `css/main.css` with `font-display: swap` and explicit `unicode-range`.
3. Point `--font-body` / `--font-display` at them.
4. Add `<link rel="preload" as="font" type="font/woff2" crossorigin>` for the Latin subsets in each page head — and keep those in sync with the actual filenames, since a mismatch silently wastes the preload.

`_headers` already has an immutable-cache rule for `/fonts/*` waiting.

### Cache busting

**CSS is cache-busted, JS is not.** `css/main.css` is included as `/css/main.css?v=YYYYMMDDx` on every page, so bumping the query string forces a refresh alongside the long immutable cache in `_headers`. All five pages carry the same version string — bump them together. `js/components.js` has no version query and runs on a 1-day cache with stale-while-revalidate; if you make a breaking JS change that must go live immediately, either rename the file or temporarily shorten the cache in `_headers`.

**Don't add `Cache-Control` to the `/*` block in `_headers`.** Pages *concatenates* per-path header values with `/*` rather than overriding them, so a global `Cache-Control` gets merged into the per-path rules below it (immutable CSS, long-cache fonts/images) and the strictest directive wins — defeating the entire cache strategy. HTML already gets a sensible `public, max-age=0, must-revalidate` from Pages by default when nothing is set, so leave it off.

### Structured data

`GeneralContractor` JSON-LD with `@id: https://www.happyconstructionar.com/#organization` lives on `index.html`. Other pages use page-specific schema (`Service`, `CollectionPage`, `AboutPage`, `ContactPage`) that references it via that `@id`. Keep `name`, `url`, `telephone`, and `email` consistent across all of them.

`GeneralContractor` is a `LocalBusiness` subtype, which means Google expects a full `address` for rich results. There is no `address` yet because the office location is unconfirmed — add `address` and `areaServed` once the client provides them. If it turns out they're a service-area business with no public storefront, drop back to plain `Organization` instead, which has no address requirement.

All five pages point `og:image` / `twitter:image` at `/images/og-card.png` (1200x630), with `og:image:type`, dimensions, and both `alt` variants set. **Keep it `.png`, not `.webp`** — LinkedIn's scraper and several link-unfurl pipelines (older Slack, some iMessage edge cases, WhatsApp) reject WebP and fall back to a no-image card. The card is currently the brand lockup on a gold field; per-page art would be better once real photography exists.

## Deploy

Cloudflare Pages, Git Integration, `main` branch. Build command: none. Build output directory: `/` (repo root).

**`.cfignore` is NOT honored by the Git Integration deploy** — only by `wrangler pages deploy` direct uploads. Since this site deploys via `git push → main`, the entire repo bundle ships, and tooling files have to be blocked at the request layer instead. `_redirects` does that by 302-bouncing tooling paths (`CLAUDE.md`, `serve.py`, `Makefile`, dotfile dirs, `images/README.md`) to `/`. We use 302 (not 301) because Pages `_redirects` only supports 301/302/303/307/308 — there's no 4xx rewrite — and a temporary redirect avoids permanent browser/SEO caching of the mapping. The files still physically ship in the deploy bundle, so this is exposure-reduction (no direct fetch returns the contents), not true filtering. **Anything new you don't want publicly fetchable must be added to that list in `_redirects`.** `.cfignore` is kept in the repo as a reference list of "things that aren't part of the site," so the `_redirects` block stays in sync with it. (For true bundle-level filtering, switch the deploy to a GitHub Action running `wrangler pages deploy .` — `.cfignore` then takes effect as documented.)

`_headers` and `_redirects` are Cloudflare Pages configuration files (path-based, no build step). `_headers` sets a strict CSP (`script-src 'self'` — **no inline scripts or inline event handlers**, so any new JS must be an external file referenced from `/js/`) plus per-path cache policies. Note `form-action 'self'` and `connect-src 'self'`: wiring up a third-party contact-form endpoint means relaxing both to that specific host.

`_redirects` is path-only, so the apex→www redirect (`happyconstructionar.com` → `www.happyconstructionar.com`) must be configured as a zone-level Redirect Rule in the Cloudflare dashboard, not here.

## Setup still outstanding

- [ ] Cloudflare Pages project created and connected to this repo
- [ ] Custom domain `www.happyconstructionar.com` added in Pages
- [ ] Apex → www Redirect Rule created at the zone level
- [x] Real logo, icon set, and share card dropped in
- [x] Palette re-derived from the brand gold
- [ ] Real credentials for the proof strip and safety block (EMR, license #, counts)
- [ ] Real contact details, service list, and project list from the client
- [ ] Team section on `about.html` — named people with roles (competitors all have one)
- [ ] Service-area page(s) — declined during scaffolding, worth revisiting
- [ ] Contact form approach decided (Pages Function vs. third-party vs. mailto)
- [ ] Typeface chosen and self-hosted (the wordmark is a heavy condensed grotesque)
- [ ] `.wip-banner` removed from all pages
