# Brand masters

The five hand-authored SVGs that every shipped raster in this repo derives from.
Nothing on the site links to these directly — they're here so the repo can
rebuild its own assets without hunting down an external folder.

| File | Art |
| --- | --- |
| `happy-construction-mark.svg` | symbol alone (hard hat + smiley) — source for app icons and the 32/48 ICO frames |
| `happy-construction-mark-simplified.svg` | crown vents and the "H" painted out — source for `favicon.svg` and the 16/24 ICO frames |
| `happy-construction-lockup-horizontal-no-tagline.svg` | symbol + wordmark, 3.3:1 — **source for the header/footer logo** |
| `happy-construction-lockup-horizontal.svg` | symbol + wordmark + "Building with a smile", 2.7:1 — source for the OG card |
| `happy-construction-lockup-vertical.svg` | stacked, with tagline |
| `happy-construction-lockup-vertical-no-tagline.svg` | stacked, without tagline |

A "mark" is the symbol alone; a "lockup" is symbol plus type.

## Rebuilding the site's assets

```sh
python3 brand/build-site-assets.py     # from the repo root
```

Regenerates every shipped raster plus `favicon.svg`, deterministically — a rerun
with unchanged masters is byte-identical, so a dirty working tree afterwards
means a master actually changed. Needs `rsvg-convert` and `cwebp` (both in the
devcontainer; `brew install librsvg webp` on macOS). It writes intermediates to
a temp dir and leaves nothing behind.

Two traps it exists to avoid:

* **Aspect.** The mark is 454x553. `rsvg-convert -w N -h N` silently stretches
  it ~22% horizontally; the script pads the viewBox to a square instead and
  renders with width only. The first pass of `icon-192` and `icon-512` shipped
  stretched this way.
* **Detail vs. size.** `happy-construction-mark-simplified.svg` is only valid at
  24px and below — above roughly 48px, erasing the vents leaves visible stepped
  notches in the crown outline. So the ICO mixes sources: simplified at 16/24,
  full at 32/48. `favicon.svg` uses the simplified mark because an SVG favicon
  is consumed in the tab strip, right in the range it was drawn for.

## Palette

| Hex | Role |
| --- | --- |
| `#FDCB17` | base gold — helmet and face |
| `#E8A619` | shade |
| `#FEE9A3` | highlight |
| `#5D4214` | brim underside |
| `#000000` | wordmark, linework |

## Recoloring

Every path carries a class (`hc-base`, `hc-shade`, `hc-highlight`, `hc-under`,
`hc-ink`, `hc-ink-bg`, `hc-wordmark`, `hc-mark`, `hc-lockup`), so a one-colour
knockout is a fill override away — no path editing required.

The footer sits on `--ink` (`#17130F`), where the black wordmark reads at roughly
1.1:1. `build-site-assets.py` handles this by injecting a `<style>` rule that
overrides `.hc-wordmark` to white — a stylesheet rule beats the path's
`fill="#000000"` presentation attribute, so no path editing is needed. The
result ships as `images/logo-horizontal-light-*`.

Note that the original brand kit's `-white` and `-yellow` raster suffixes mean
*"flattened onto a white/yellow background plate"* — they are **not** reversed
artwork, so don't reach for those.

## Provenance

Copied from `happy-construction-brand/svg/` (a self-contained kit whose
`generate.py` renders `web/`, `social/`, `png/`, and `print/` from these masters,
each raster at its native size rather than downscaled from one big export).
That kit's `generate.py` was deliberately **not** vendored here — if you need the
full multi-format raster set, go back to the kit. `build-site-assets.py` in this
directory is a different, much smaller thing: it renders only what this site
ships.

`happy-construction-mark-simplified.svg` is *generated* by the kit, not
hand-authored. Editing it here is fine for a one-off, but a kit rerun overwrites
it — push changes upstream instead.

Excluded from the deploy via `.cfignore` and 302-bounced in `_redirects` — see
`CLAUDE.md` > Deploy for why both are needed.
