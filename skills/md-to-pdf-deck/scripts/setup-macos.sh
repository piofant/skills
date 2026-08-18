#!/usr/bin/env bash
# Provision macOS dependencies for md-to-pdf-deck.
# Idempotent: safe to re-run.
#
# Fixes two known macOS gotchas:
#   1. pyexpat in brew Python 3.13/3.14 links against macOS Tahoe's
#      /usr/lib/libexpat.1.dylib which lacks symbols that newer brew Python
#      builds expect. We install brew expat and point DYLD_LIBRARY_PATH at it.
#   2. macOS only ships specialized Noto fonts (Tamil, Myanmar…) but not the
#      core Noto Sans / Inter / Noto Color Emoji that the skill assumes. Brew
#      casks fix that.
#
# After running this once, scripts/build.py auto-detects the .venv next to
# scripts/ and re-execs under it with DYLD_LIBRARY_PATH set — no env vars
# needed at call time.

set -euo pipefail

cd "$(dirname "$0")"
SKILL_DIR="$(cd .. && pwd)"

if [[ "$(uname)" != "Darwin" ]]; then
  echo "This script targets macOS. On Linux, follow the apt/npm install block in SKILL.md."
  exit 1
fi

if ! command -v brew >/dev/null 2>&1; then
  echo "Homebrew not found. Install from https://brew.sh and re-run."
  exit 1
fi

echo "→ brew formulas (pandoc, weasyprint, expat, python@3.13, imagemagick)"
brew install pandoc weasyprint expat python@3.13 imagemagick 2>&1 \
  | grep -vE "already installed|outdated|^$" || true

echo "→ brew casks (fonts)"
brew install --cask font-inter font-noto-sans font-noto-color-emoji 2>&1 \
  | grep -vE "already installed|It seems there is already|^$" || true

echo "→ font cache refresh"
fc-cache -f 2>/dev/null || true

if ! command -v mmdc >/dev/null 2>&1; then
  echo "→ mermaid-cli via npm (global)"
  npm install -g @mermaid-js/mermaid-cli
else
  echo "✓ mmdc already present"
fi

VENV_DIR="$SKILL_DIR/.venv"
EXPAT_LIB="/opt/homebrew/opt/expat/lib"

if [[ ! -x "$VENV_DIR/bin/python3" ]]; then
  echo "→ creating venv at $VENV_DIR"
  DYLD_LIBRARY_PATH="$EXPAT_LIB" /opt/homebrew/bin/python3.13 -m venv "$VENV_DIR"
fi

echo "→ pip install weasyprint pillow into venv"
DYLD_LIBRARY_PATH="$EXPAT_LIB" "$VENV_DIR/bin/pip" install --quiet --upgrade \
  weasyprint pillow

echo "→ sanity check"
DYLD_LIBRARY_PATH="$EXPAT_LIB" "$VENV_DIR/bin/python3" -c \
  "import weasyprint, xml.etree.ElementTree as ET; ET.fromstring('<a/>'); print('  weasyprint', weasyprint.__version__, '+ expat OK')"

echo ""
echo "✅ All set. Run:"
echo "    python3 $(realpath build.py) src.md out.pdf 'Title' 'Subtitle' 'Author' --layout longread"
echo ""
echo "build.py auto-detects the venv at $VENV_DIR — no extra flags needed."
