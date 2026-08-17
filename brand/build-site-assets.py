#!/usr/bin/env python3
"""Rebuild every shipped raster and the favicon SVG from the masters in brand/.

Run from the repo root:

    python3 brand/build-site-assets.py

Requires `rsvg-convert` and `cwebp` (both in the devcontainer; on macOS,
`brew install librsvg webp`). Everything it writes is checked in — this exists so
the assets can be regenerated after a master changes, not as a build step.

Not to be confused with the brand kit's own `generate.py`, which renders the full
multi-format kit and is deliberately not vendored here. See README.md.

Two things this handles that a bare `rsvg-convert -w N -h N` gets wrong:

* **Aspect.** The mark is 454x553. Passing both -w and -h stretches it ~22%
  horizontally. Every square icon here instead pads the viewBox out to a square
  and renders with width only.
* **Detail vs. size.** The simplified mark (vents and "H" painted out) is only
  valid at 24px and below; above that its crown outline shows stepped notches.
  So the ICO takes simplified frames at 16/24 and full frames at 32/48.
"""

import re
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BRAND = ROOT / "brand"
IMAGES = ROOT / "images"

MARK = BRAND / "happy-construction-mark.svg"
MARK_SIMPLE = BRAND / "happy-construction-mark-simplified.svg"
LOCKUP = BRAND / "happy-construction-lockup-horizontal-no-tagline.svg"
LOCKUP_TAGLINE = BRAND / "happy-construction-lockup-horizontal.svg"

GOLD = "#FDCB17"
WHITE = "#ffffff"

# Intrinsic geometry of the masters, needed to pad viewBoxes to a square.
MARK_W, MARK_H = 454.0, 553.0


def run(*args):
    subprocess.run([str(a) for a in args], check=True)


def squared(src: Path, dst: Path, content_fraction: float) -> Path:
    """Copy `src` with its viewBox padded to a square, art centered.

    `content_fraction` is how much of the square's height the art should occupy —
    1.0 is edge to edge, 0.7 leaves a maskable-icon safe margin.
    """
    side = MARK_H / content_fraction
    x = -(side - MARK_W) / 2
    y = -(side - MARK_H) / 2
    svg = src.read_text()
    svg, n = re.subn(
        r'viewBox="[^"]*"', f'viewBox="{x:.2f} {y:.2f} {side:.2f} {side:.2f}"', svg, count=1
    )
    assert n == 1, f"no viewBox in {src}"
    # Drop the authored width/height so the viewBox alone drives the aspect.
    svg = re.sub(r'\s+width="[\d.]+"', "", svg, count=1)
    svg = re.sub(r'\s+height="[\d.]+"', "", svg, count=1)
    dst.write_text(svg)
    return dst


def reversed_lockup(src: Path, dst: Path) -> Path:
    """Copy `src` with the wordmark knocked out to white, for the dark footer.

    A stylesheet rule beats the path's `fill="#000000"` presentation attribute,
    so this needs no path editing. Every path in the masters carries an `hc-*`
    class for exactly this.
    """
    svg = src.read_text()
    svg, n = re.subn(
        r"(<svg\b[^>]*>)", r"\1\n<style>.hc-wordmark{fill:#ffffff}</style>", svg, count=1
    )
    assert n == 1, f"no <svg> element in {src}"
    dst.write_text(svg)
    return dst


def strip_editor_cruft(svg: str) -> str:
    """Remove Inkscape/sodipodi leftovers. The masters are ~4% editor metadata."""
    svg = re.sub(r"<sodipodi:namedview\b.*?(?:/>|</sodipodi:namedview>)", "", svg, flags=re.S)
    svg = re.sub(r"<defs\b[^>]*/>", "", svg)
    svg = re.sub(r'\s+(?:inkscape|sodipodi):[a-zA-Z-]+="[^"]*"', "", svg)
    svg = re.sub(r'\s+xmlns:(?:inkscape|sodipodi|svg)="[^"]*"', "", svg)
    svg = re.sub(r'\s+id="(?:svg|defs|path|g|ellipse)\d+"', "", svg)
    return re.sub(r"\n\s*\n+", "\n", svg)


def png(src: Path, dst: Path, width: int, background: str | None = None):
    args = ["rsvg-convert", "-w", width, src, "-o", dst]
    if background:
        args[1:1] = ["-b", background]
    run(*args)


def webp(src: Path):
    run("cwebp", "-quiet", "-q", 90, "-alpha_q", 100, src, "-o", src.with_suffix(".webp"))


def build_ico(dst: Path, frames: list[tuple[int, Path]]):
    """Assemble a PNG-compressed ICO. Frames must be pre-rendered square PNGs."""
    blobs = [(size, path.read_bytes()) for size, path in frames]
    header = struct.pack("<HHH", 0, 1, len(blobs))
    offset = 6 + 16 * len(blobs)
    entries, payload = b"", b""
    for size, blob in blobs:
        entries += struct.pack(
            "<BBBBHHII", size % 256, size % 256, 0, 0, 1, 32, len(blob), offset
        )
        payload += blob
        offset += len(blob)
    dst.write_bytes(header + entries + payload)


def main():
    for tool in ("rsvg-convert", "cwebp"):
        if not subprocess.run(["which", tool], capture_output=True).returncode == 0:
            sys.exit(f"missing required tool: {tool}")

    with tempfile.TemporaryDirectory() as tmp:
        build(Path(tmp))
    print("rebuilt icons, logos, and share card from brand/")


def build(BUILD: Path):
    # --- favicon.svg -------------------------------------------------------
    # The simplified mark, because an SVG favicon is consumed in the tab strip
    # at 16-32px and that is exactly the range it was drawn for. Browsers old
    # enough to prefer the ICO get the full mark at 32/48 from there instead.
    square_simple = squared(MARK_SIMPLE, BUILD / "mark-simple-square.svg", 1.0)
    (ROOT / "favicon.svg").write_text(strip_editor_cruft(square_simple.read_text()))

    # --- favicon.ico -------------------------------------------------------
    square_full = squared(MARK, BUILD / "mark-square.svg", 1.0)
    ico_frames = []
    for size, source in ((16, square_simple), (24, square_simple), (32, square_full), (48, square_full)):
        frame = BUILD / f"ico-{size}.png"
        png(source, frame, size)
        ico_frames.append((size, frame))
    build_ico(ROOT / "favicon.ico", ico_frames)

    # --- app icons ---------------------------------------------------------
    # 0.90 leaves a hairline of breathing room so the outline isn't clipped.
    padded = squared(MARK, BUILD / "mark-padded.svg", 0.90)
    png(padded, ROOT / "icon-192.png", 192)
    png(padded, ROOT / "icon-512.png", 512)
    # iOS composites a transparent apple-touch-icon onto black, so flatten it.
    png(padded, ROOT / "apple-touch-icon.png", 180, background=WHITE)
    # Maskable icons get cropped to an OS-chosen shape; keep the art inside the
    # inner 70% and give it an opaque field to be cropped out of.
    maskable = squared(MARK, BUILD / "mark-maskable.svg", 0.70)
    png(maskable, ROOT / "icon-maskable-512.png", 512, background=WHITE)

    # --- header / footer logo ---------------------------------------------
    light = reversed_lockup(LOCKUP, BUILD / "lockup-reversed.svg")
    for source, stem in ((LOCKUP, "logo-horizontal"), (light, "logo-horizontal-light")):
        for width in (256, 512):
            out = IMAGES / f"{stem}-{width}.png"
            png(source, out, width)
            webp(out)

    # --- share card --------------------------------------------------------
    # 1200x630 PNG (not WebP — several unfurl pipelines reject WebP). Uses the
    # tagline lockup on a full-bleed gold field.
    card = BUILD / "og-card.svg"
    card.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630">\n'
        f'  <rect width="1200" height="630" fill="{GOLD}"/>\n'
        f'  <image x="168" y="154" width="864" height="322" href="{LOCKUP_TAGLINE.name}"/>\n'
        "</svg>\n"
    )
    (BUILD / LOCKUP_TAGLINE.name).write_text(LOCKUP_TAGLINE.read_text())
    run("rsvg-convert", "-w", 1200, "-b", GOLD, card, "-o", IMAGES / "og-card.png")


if __name__ == "__main__":
    main()
