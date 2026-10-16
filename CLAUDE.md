# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Static landing page for Happy Construction, a commercial general contractor. No build step, no framework, no package manager. Plain HTML/CSS/JS served as files, deployed to Cloudflare Pages.

**The site is one page on purpose.** The owner asked for a single professional landing page customers can find, and supplied no photos, projects, credentials, team, or history. The original five-page scaffold (Services, Projects, About, Contact) was collapsed into `index.html` on 2026-10-16. The old paths 301 to `/` (and `/contact` to `/#contact`) in `_redirects`.

**The logo, icon set, share card, and palette are real**, generated from the brand masters in `brand/`. The tagline "Building with a smile." is the client's.

**Copy rule: generic and true, never invented.** The page describes what a commercial GC does in general terms: the three service cards and the four delivery phases. It names no projects and states no counts, years, ratings, license numbers, safety figures, or affiliations, and makes no process promises (response times, a single point of contact, warranty or after-service support). Don't add any of these unless the client supplies them, and drop any line the client can't substantiate rather than softening it. A fabricated EMR or license number looks plausible and would ship as a lie. The same rule covers imagery. **No AI-generated photos of buildings or jobsites**: on a contractor's site, any building pictured reads as their work. The hero uses the mark instead.

The structures that make a GC site read as qualified (proof strip, safety block, sector-labelled project tiles, team section) were deliberately removed rather than left empty. Bring them back only when real content exists for them. The pre-collapse versions are in git history (`15628e2`).

## Placeholders

Only the contact details are placeholders now. Replace them before launch.

| Placeholder | Where it appears (change all together) |
| --- | --- |
| `(555) 555-5555` / `+15555555555` | `js/components.js` (`PHONE_DISPLAY`, `PHONE_TEL`), `index.html` `#contact` section and JSON-LD `telephone` |
| `info@happyconstructionar.com` (mailbox not confirmed to exist) | `js/components.js` (`EMAIL`), `index.html` `#contact` (two `mailto:` links) and JSON-LD `email` |
| Service list | `index.html` "What We Take On" cards. The three are generic for a commercial GC but **not yet confirmed by the owner**. The same list is repeated in the meta and OG descriptions, the JSON-LD `description`, and the hero paragraph, and phase 02 assumes ground-up work. If a service is dropped, update all of them. |
| `.wip-banner` | Top of `index.html` `<main>`. Delete it and the `.wip-banner` rule in `css/main.css` once the contact details are real. |

No service area or office address appears anywhere, because none was given. Add them only if the owner provides them (see "Structured data").

The production domain is **https://www.happyconstructionar.com** (`happyconstruction.com` was not purchased). It is hardcoded in canonicals, OG `url`, `sitemap.xml`, `robots.txt`, and JSON-LD `@id`/`url`. If the domain ever changes, all five must change together.

## Commands

- `make serve` — Local dev server at http://localhost:8000. Runs `serve.py`, a thin wrapper around Python's `http.server` that mimics Cloudflare Pages' `.html` behavior: serves `/foo` from `/foo.html` and 308-redirects `/foo.html` → `/foo`. Keep that parity if you touch `serve.py` — the whole site relies on extensionless canonicals and local dev must match prod.
- Pushing to `main` deploys automatically via Cloudflare Pages.
- **Playwright MCP screenshots:** the `--output-dir .playwright-mcp` flag in `.mcp.json` is only honored when `filename` is omitted (the auto-named `page-{timestamp}.png` lands there correctly). Passing a bare relative `filename` writes to **repo root** instead and slips past the `/desktop-*.png` / `/mobile-*.png` gitignore patterns. Either omit `filename` or prefix it explicitly: `".playwright-mcp/<name>.png"`.

## Architecture

`index.html` is the whole site: hero, "What We Take On" (`#services`), "How a Project Runs" (`#approach`), and "Contact" (`#contact`). There is no nav. The header carries the logo, the phone number (hidden below 640px), and a Contact button that jumps to `#contact`. `html { scroll-padding-top }` keeps the sticky header from covering anchor targets.

If the site grows back to multiple pages, there is no template engine. Copy `index.html` and update:

1. `<title>`, `<meta name="description">`, OG/Twitter tags, and `<link rel="canonical">`. **Canonicals and all internal `href`s are extensionless** (`/about`, not `/about.html`) — Cloudflare Pages serves `/foo.html` under `/foo` and 308-redirects the `.html` form, so using `.html` URLs in canonicals creates a redirect loop with any reverse rule.
2. Add the page to `sitemap.xml` with its extensionless URL. **Do not add `<lastmod>`** unless you have a real per-page edit-tracking workflow — static or generation-time dates get ignored by Google and waste the signal.
3. Add a trailing-slash alias to `_redirects` (`/foo/ → /foo 301`). The extensionless URL is served natively by Pages; do **not** add `/foo → /foo.html` rules (they loop against Pages' built-in `.html` stripping).
4. Reintroduce a nav in `js/components.js`. The `NAV_LINKS` / hamburger version is in git history (`15628e2`). Remove the matching old-path redirect from `_redirects` first, or the new page will never be reachable.

**Shared chrome via web components.** Header and footer are custom elements defined in `js/components.js` (`<site-header>`, `<site-footer>`). The page includes `<script src="/js/components.js" defer>` and drops the elements into the body. Phone, email, and the logo geometry are module-level constants at the top of that file. The `#contact` section and JSON-LD in `index.html` repeat the phone and email in static HTML, so crawlers and no-JS visitors get them. Change all three places together.

Both logo variants render through a single `logoPicture(variant, attrs)` helper that emits a `<picture>` with a WebP `<source>` and a PNG fallback plus a 2x `srcset`. The header takes the black wordmark, the footer the white knockout. See `images/README.md`.

### Brand assets

`brand/` holds the hand-authored SVG masters. **Every shipped raster, `favicon.svg`, and the hero's `images/mark.svg` is generated from them** by `python3 brand/build-site-assets.py` — don't hand-edit the outputs. The script is deterministic, so a rerun leaving a dirty tree means a master actually changed. `brand/README.md` covers the two traps it encodes: aspect-ratio distortion on square icons, and the simplified-mark-below-24px rule for favicons.

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
| `--accent-light` | `#FFF1C2` | gold wash — currently unused |
| `--concrete` | `#FAF7F1` | warm off-white, alternating sections |

Two rules the sheet depends on:

* **`--accent` is never text on a light surface.** `#FDCB17` is 1.53:1 on white. It is a fill: buttons, rules, the footer's top border, and type on `--ink` (12.08:1 there). Gold *text* on light is `--accent-dark`. On `--ink`, even `--accent-dark` fails at 3.02:1 — that's why `.hero .eyebrow` and `.section-dark .eyebrow` both override to `--accent`.
* **`--accent-dark` must stay dark enough to carry white text**, because `.btn:hover` and `.header-phone:hover` reverse out of it.

Every pair is verified AA. If you change a token, re-audit — the fastest way is a headless pass that walks every text node's computed color against its composited background, since the failures that matter are the inherited ones (`.section-dark` inverting `.detail-list` and its links, a `.hero` eyebrow) rather than anything visible in `:root`.

**Four files hold color and drift silently.** A palette change means all four together: `:root` in `css/main.css`, `css/404.css` (hardcoded, standalone), `theme_color` in `site.webmanifest`, and `<meta name="theme-color">` in `index.html`. `theme-color` is currently the gold `#FDCB17`, not `--ink` — deliberate, so the mobile browser chrome carries the brand.

The white-knockout footer logo was built against `--ink`. If the footer ground changes materially, confirm the mark's black linework still separates.

### Visual direction

The brand is a yellow smiley face in a hard hat with the tagline "Building with a smile." Every commercial GC surveyed in this market reads sober — navy (Nabholz, Liberty), red (Crossland), neutral grey (Commerce, Oelke). None are playful.

**So let the logo be the only friendly thing on the page.** The gold does the warmth; everything around it — typography, project naming, numbers, safety language — stays as sober as the competition. That is why the hero and footer sit on near-black rather than on gold: the dark ground frames the mark instead of amplifying it. A site that is playful *everywhere* reads residential, and the buyer here is an owner or developer comparing bids.

That survey also found every competitor shows a proof strip, a safety block, named project tiles, and a team. Without real content those can't be filled honestly, so the one-page site leans on what is safe: the delivery-phase framing (which reads commercial) and a direct contact path. When the client can supply credentials or projects, adding them is the highest-value upgrade.

### Fonts

Currently the **system font stack** (`--font-body` / `--font-display`), chosen because no typeface has been selected. Nothing is downloaded, so there's no webfont cost yet.

When a typeface is chosen, self-host it rather than linking Google Fonts — the CSP in `_headers` sets `font-src 'self'` and would block a CDN. The procedure:

1. Drop WOFF2 subsets in a new `fonts/` directory.
2. Add `@font-face` blocks at the top of `css/main.css` with `font-display: swap` and explicit `unicode-range`.
3. Point `--font-body` / `--font-display` at them.
4. Add `<link rel="preload" as="font" type="font/woff2" crossorigin>` for the Latin subsets in each page head — and keep those in sync with the actual filenames, since a mismatch silently wastes the preload.

`_headers` already has an immutable-cache rule for `/fonts/*` waiting.

### Cache busting

**CSS is cache-busted, JS is not.** `css/main.css` is included as `/css/main.css?v=YYYYMMDDx`, so bumping the query string forces a refresh alongside the long immutable cache in `_headers`. Bump it on every CSS change. `js/components.js` has no version query and runs on a 1-day cache with stale-while-revalidate; if you make a breaking JS change that must go live immediately, either rename the file or temporarily shorten the cache in `_headers`.

**Don't add `Cache-Control` to the `/*` block in `_headers`.** Pages *concatenates* per-path header values with `/*` rather than overriding them, so a global `Cache-Control` gets merged into the per-path rules below it (immutable CSS, long-cache fonts/images) and the strictest directive wins — defeating the entire cache strategy. HTML already gets a sensible `public, max-age=0, must-revalidate` from Pages by default when nothing is set, so leave it off.

### Structured data

`index.html` carries `Organization` JSON-LD with `@id: https://www.happyconstructionar.com/#organization`. Keep `name`, `url`, `telephone`, and `email` in step with `js/components.js`.

It is `Organization` rather than `GeneralContractor` on purpose. `GeneralContractor` is a `LocalBusiness` subtype, and Google expects a full `address` for those. No office address has been given. If the owner provides a public address, switch the type to `GeneralContractor` and add `address` and `areaServed`.

`index.html` points `og:image` / `twitter:image` at `/images/og-card.png` (1200x630), with `og:image:type`, dimensions, and both `alt` variants set. **Keep it `.png`, not `.webp`** — LinkedIn's scraper and several link-unfurl pipelines (older Slack, some iMessage edge cases, WhatsApp) reject WebP and fall back to a no-image card. The card is the brand lockup on a gold field.

## Deploy

Cloudflare Pages, Git Integration, `main` branch. Build command: none. Build output directory: `/` (repo root).

**`.cfignore` is NOT honored by the Git Integration deploy** — only by `wrangler pages deploy` direct uploads. Since this site deploys via `git push → main`, the entire repo bundle ships, and tooling files have to be blocked at the request layer instead. `_redirects` does that by 302-bouncing tooling paths (`CLAUDE.md`, `serve.py`, `Makefile`, dotfile dirs, `images/README.md`) to `/`. We use 302 (not 301) because Pages `_redirects` only supports 301/302/303/307/308 — there's no 4xx rewrite — and a temporary redirect avoids permanent browser/SEO caching of the mapping. The files still physically ship in the deploy bundle, so this is exposure-reduction (no direct fetch returns the contents), not true filtering. **Anything new you don't want publicly fetchable must be added to that list in `_redirects`.** `.cfignore` is kept in the repo as a reference list of "things that aren't part of the site," so the `_redirects` block stays in sync with it. (For true bundle-level filtering, switch the deploy to a GitHub Action running `wrangler pages deploy .` — `.cfignore` then takes effect as documented.)

`_headers` and `_redirects` are Cloudflare Pages configuration files (path-based, no build step). `_headers` sets a strict CSP (`script-src 'self'` — **no inline scripts or inline event handlers**, so any new JS must be an external file referenced from `/js/`) plus per-path cache policies. Note `form-action 'self'` and `connect-src 'self'`: wiring up a third-party contact-form endpoint means relaxing both to that specific host.

`_redirects` is path-only, so the apex→www redirect (`happyconstructionar.com` → `www.happyconstructionar.com`) must be configured as a zone-level Redirect Rule in the Cloudflare dashboard, not here.

## Setup still outstanding

- [x] Cloudflare Pages project created and connected to this repo (`happyconstruction-site.pages.dev` serves `main`)
- [x] Domain registered, on Cloudflare nameservers
- [ ] Custom domain `www.happyconstructionar.com` added in Pages (no DNS records resolve yet, checked 2026-10-16)
- [ ] Apex → www Redirect Rule created at the zone level
- [x] Real logo, icon set, and share card dropped in
- [x] Palette re-derived from the brand gold
- [x] Site collapsed to one landing page with generic, non-fabricated copy (2026-10-16)
- [ ] Real phone and email, and the mailbox actually set up
- [ ] Owner confirms the three service cards
- [ ] `.wip-banner` removed
- [ ] `X-Robots-Tag: noindex` line removed from `_headers` (launch-day, see the comment there)
- [ ] Optional later: credentials, projects, team, service area, contact form, self-hosted typeface
