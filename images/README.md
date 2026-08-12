# Images

## Placeholders — replace these

Everything currently in this directory is a stand-in generated during scaffolding.
None of it is the client's real brand.

| File | What it is | Replace with |
| --- | --- | --- |
| `logo-placeholder.svg` | Generic A-frame mark + wordmark, **dark artwork** for the white header | The real logo, dark variant |
| `logo-placeholder-light.svg` | Same mark, **light artwork** for the dark footer | The real logo, light/reversed variant |
| `/favicon.svg` (repo root) | Same mark, square | Favicon derived from the real logo |
| `/icon-192.png`, `/icon-512.png`, `/apple-touch-icon.png` (repo root) | Rasterized from `favicon.svg` via `rsvg-convert` | Re-render from the real mark |

## Adding the real logo

**Two variants are required.** The header sits on white and the footer sits on
charcoal, so a single-color logo will disappear on one of them — that is exactly
what happened with the first pass of the placeholder. Ask the client (or their
designer) for both a standard and a reversed/knockout version.

The files should land here as:

```
logo-horizontal-256.png / .webp          # 1x header + footer, dark artwork
logo-horizontal-512.png / .webp          # 2x retina, dark artwork
logo-horizontal-light-256.png / .webp    # 1x footer, light artwork
logo-horizontal-light-512.png / .webp    # 2x retina, light artwork
```

Then update `js/components.js`: the `LOGO_SRC` and `LOGO_SRC_LIGHT` constants at
the top of the file, and swap each `<img>` for a `<picture>` with a WebP
`<source>` and a PNG fallback.

**Keep the header logo's height definite.** `.header-logo` sets an explicit
`height` (not `max-height`) because the logo lives in a flex row — an image
sized `width: auto; max-height: N` there has no definite flex basis and collapses
to 0x0. Match the `width`/`height` attributes on the `<img>` to the rendered
aspect ratio so there's no layout shift.

The devcontainer ships `imagemagick`, `webp`, `optipng`, `jpegoptim`, `pillow`,
and `rembg` for this work. Typical pipeline from a high-res source:

```sh
magick logo-source.png -resize 256x logo-horizontal-256.png
magick logo-source.png -resize 512x logo-horizontal-512.png
cwebp -q 90 logo-horizontal-256.png -o logo-horizontal-256.webp
cwebp -q 90 logo-horizontal-512.png -o logo-horizontal-512.webp
optipng -o5 logo-horizontal-*.png
```

Then pull the brand colors out of the logo and set them as the `:root` tokens at
the top of `css/main.css` — see the "Design tokens" section of `CLAUDE.md`.

## Source / archive

High-resolution masters and working files belong here too, but they aren't part
of the shipped site. Add them to `.cfignore` alongside this README so the
intent stays documented, and add a `_redirects` bounce rule for anything you
don't want directly fetchable (see `CLAUDE.md` > Deploy for why both are needed).

## Share cards

Open Graph / Twitter cards are not built yet. When they are, export them at
1200x630 as **PNG** — several link-unfurl pipelines reject WebP and fall back to
a no-image card. See the OG notes in `CLAUDE.md`.
