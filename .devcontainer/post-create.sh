#!/usr/bin/env bash
set -euo pipefail

echo "Installing system image tools..."
sudo apt-get update -qq
sudo apt-get install -y -qq \
  imagemagick \
  webp \
  optipng \
  jpegoptim \
  librsvg2-bin

echo "Installing Python image libs..."
pip install --quiet --no-warn-script-location \
  pillow \
  rembg[cpu]

echo "Versions:"
magick --version | head -1 || convert --version | head -1
cwebp -version
rsvg-convert --version
python3 -c "import PIL; print('pillow', PIL.__version__)"
python3 -c "import rembg; print('rembg ok')"

# CLI tools
curl -fsSL https://claude.ai/install.sh | bash

# Playwright (browser + system deps) so Claude can screenshot the dev site via the Playwright MCP server
echo "Installing Playwright Chromium..."
npx --yes playwright install --with-deps chromium

# Generate the Playwright MCP config. On Linux ARM64 (and anywhere Google Chrome
# isn't installed) @playwright/mcp defaults to /opt/google/chrome/chrome and
# fails; there's no --browser chromium CLI value and --executable-path is
# ignored (microsoft/playwright-mcp#976), so the only supported way to point
# at the bundled chromium is a config file with browser.launchOptions.executablePath
# (see https://playwright.dev/mcp/configuration/options). The chromium directory
# name includes a version suffix that drifts, so resolve it at install time.
echo "Writing Playwright MCP config..."
CHROME_PATH="$(ls -d "$HOME"/.cache/ms-playwright/chromium-*/chrome-linux/chrome 2>/dev/null | tail -1)"
if [ -n "$CHROME_PATH" ]; then
  cat > /workspaces/happyconstruction-site/.playwright-mcp.config.json <<EOF
{
  "browser": {
    "browserName": "chromium",
    "launchOptions": {
      "executablePath": "$CHROME_PATH"
    }
  }
}
EOF
  echo "  -> $CHROME_PATH"
else
  echo "  (skipped: no chromium binary found under \$HOME/.cache/ms-playwright)"
fi

echo "Done."
