# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Static marketing site for Happy Construction — a commercial general contractor. No build step, no framework, no package manager. Plain HTML/CSS/JS served as files, deployed to Cloudflare Pages.

**This repo is currently a scaffold.** The Pages plumbing, shared chrome, and design-token system are real and working. Every piece of *content* — copy, palette, logo, photography, phone, email, address, service list, project list — is a deliberate placeholder awaiting client direction. Do not treat any of it as fact, and do not invent replacements: if you need a value that isn't in the "Placeholders" table below, ask.

## Placeholders

Nothing in this table is real. Replace each before launch.

| Placeholder | Where it appears |
| --- | --- |
| `(555) 555-5555` / `+15555555555` | `js/components.js` (`PHONE_DISPLAY`, `PHONE_TEL`), `contact.html`, `index.html` JSON-LD |
| `info@happyconstructionar.com` | `js/components.js` (`EMAIL`), `contact.html`, `index.html` JSON-LD |
| Office address, hours | `contact.html` ("Address pending" / "Hours pending") |
| Amber/charcoal palette | `:root` in `css/main.css`, `css/404.css`, `theme_color` in `site.webmanifest`, `<meta name="theme-color">` in every page head |
| `images/logo-placeholder.svg` (dark) + `images/logo-placeholder-light.svg` (reversed), `/favicon.svg`, `/icon-*.png`, `/apple-touch-icon.png` | Generated stand-ins — see `images/README.md`. **Two logo variants are required**: the header is white, the footer is charcoal. |
| Service categories | `services.html` cards + the matching three cards on `index.html` — keep them in sync |
| Project tiles | `projects.html`, `index.html` — striped `.tile-media` frames stand in for photography |
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

**Shared chrome via web components.** Header and footer are custom elements defined in `js/components.js` (`<site-header>`, `<site-footer>`). Pages must include `<script src="/js/components.js" defer>` and drop the elements into the body. Active nav state is derived from `window.location.pathname`, so nav links use absolute paths from root. Phone, email, and the logo path are module-level constants at the top of that file — change them in one place, not per page (except the JSON-LD blocks, which are per-page and must be updated separately).

**Asset paths are absolute** (`/css/main.css`, `/images/...`) — relative paths will break because the dev server and Cloudflare Pages both serve from root.

`404.html` is standalone — it uses `/css/404.css`, not `main.css`, and does not include `<site-header>`/`<site-footer>`. Edit it directly without touching shared chrome. Its colors are hardcoded hex, not tokens, so a palette change has to be applied there by hand. Pages auto-serves `404.html` as the fallback for any non-existent path *with a real 404 status* (the desired behavior). One quirk: a direct visit to the extensionless `/404` returns 200 (Pages' `.html`-stripping makes it addressable as a normal page), which is technically a "soft 404." Fixing it would require a Pages Function — `_redirects` only supports 301/302/303/307/308, not 4xx rewrites. Accepted as an edge case; revisit if Search Console ever flags it.

### Design tokens

CSS custom properties in `:root` at the top of `css/main.css` are the single source of truth for color, type, elevation, and geometry. **Nothing below `:root` hardcodes a hex** — that is intentional, so the whole site re-skins from that one block once the real brand lands. Keep it that way.

The current values are a neutral commercial-GC stand-in (charcoal `--ink`, safety amber `--accent`, concrete greys), *not* Happy Construction's brand. When the logo arrives:

1. Pull the actual colors out of it and replace the Brand and Surface tokens.
2. Update `css/404.css` (hardcoded, standalone).
3. Update `theme_color` in `site.webmanifest` and the `<meta name="theme-color">` in all five page heads — these are separate hardcoded hexes that will silently drift.

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

**OG/Twitter `image` URLs must point to a `.png`, not `.webp`,** once share cards exist. LinkedIn's scraper and several link-unfurl pipelines (older Slack, some iMessage edge cases, WhatsApp) reject WebP and fall back to a no-image card. Set `og:image:type` to `image/png` to match, and give every page an `og:image:alt` and `twitter:image:alt`. No page has an `og:image` yet — each has a TODO comment where it goes.

## Deploy

Cloudflare Pages, Git Integration, `main` branch. Build command: none. Build output directory: `/` (repo root).

**`.cfignore` is NOT honored by the Git Integration deploy** — only by `wrangler pages deploy` direct uploads. Since this site deploys via `git push → main`, the entire repo bundle ships, and tooling files have to be blocked at the request layer instead. `_redirects` does that by 302-bouncing tooling paths (`CLAUDE.md`, `serve.py`, `Makefile`, dotfile dirs, `images/README.md`) to `/`. We use 302 (not 301) because Pages `_redirects` only supports 301/302/303/307/308 — there's no 4xx rewrite — and a temporary redirect avoids permanent browser/SEO caching of the mapping. The files still physically ship in the deploy bundle, so this is exposure-reduction (no direct fetch returns the contents), not true filtering. **Anything new you don't want publicly fetchable must be added to that list in `_redirects`.** `.cfignore` is kept in the repo as a reference list of "things that aren't part of the site," so the `_redirects` block stays in sync with it. (For true bundle-level filtering, switch the deploy to a GitHub Action running `wrangler pages deploy .` — `.cfignore` then takes effect as documented.)

`_headers` and `_redirects` are Cloudflare Pages configuration files (path-based, no build step). `_headers` sets a strict CSP (`script-src 'self'` — **no inline scripts or inline event handlers**, so any new JS must be an external file referenced from `/js/`) plus per-path cache policies. Note `form-action 'self'` and `connect-src 'self'`: wiring up a third-party contact-form endpoint means relaxing both to that specific host.

`_redirects` is path-only, so the apex→www redirect (`happyconstructionar.com` → `www.happyconstructionar.com`) must be configured as a zone-level Redirect Rule in the Cloudflare dashboard, not here.

## Setup still outstanding

- [ ] Cloudflare Pages project created and connected to this repo
- [ ] Custom domain `www.happyconstructionar.com` added in Pages
- [ ] Apex → www Redirect Rule created at the zone level
- [ ] Real logo dropped in and palette re-derived from it
- [ ] Real contact details, service list, and project list from the client
- [ ] Contact form approach decided (Pages Function vs. third-party vs. mailto)
- [ ] Share card (1200x630 PNG) + `og:image` tags on all five pages
- [ ] `.wip-banner` removed from all pages
