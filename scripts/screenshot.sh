#!/usr/bin/env bash
# Headless screenshots (desktop 1400px + mobile 400px) of a local HTML file for visual QA.
# Usage: screenshot.sh <file.html> <out_dir>
# Finds a Chromium: system chromium/chrome, else Playwright's cached headless shell.
# Note: do NOT append #anchors to the URL; headless anchor-scrolling leaves a blank area above sticky headers.
set -euo pipefail
f="$(realpath "$1")"; out="${2:-.}"; mkdir -p "$out"
BIN=""
for c in chromium chromium-browser google-chrome google-chrome-stable; do
  command -v "$c" >/dev/null 2>&1 && { BIN="$(command -v "$c")"; break; }
done
if [ -z "$BIN" ]; then
  BIN="$(find "$HOME/.cache/ms-playwright" -type f \( -name chrome-headless-shell -o -name chrome \) 2>/dev/null | head -1 || true)"
fi
[ -z "$BIN" ] && { echo "no chromium found; skip visual check (or install chromium)"; exit 2; }
if ldd "$BIN" 2>/dev/null | grep -q "not found"; then
  echo "chromium is missing shared libraries:"; ldd "$BIN" | grep "not found"
  echo "(on Debian/Ubuntu: apt-get install libatk1.0-0t64 libatk-bridge2.0-0t64 libcups2t64 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libpango-1.0-0 libcairo2 libasound2t64)"
  exit 3
fi
"$BIN" --no-sandbox --hide-scrollbars --window-size=1400,3200 --virtual-time-budget=20000 \
  --screenshot="$out/desktop.png" "file://$f" >/dev/null 2>&1
"$BIN" --no-sandbox --hide-scrollbars --window-size=400,3000 --virtual-time-budget=20000 \
  --screenshot="$out/mobile.png" "file://$f" >/dev/null 2>&1
echo "wrote $out/desktop.png $out/mobile.png"
