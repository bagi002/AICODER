#!/bin/bash
set -euo pipefail

# Rebuilds the main venv (project root) and docs_venv (Automation/) so that
# a freshly cloned repo gets working environments without committing them to git.

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
AUTO_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "[1/2] Creating main venv at $ROOT_DIR/venv"
python3 -m venv "$ROOT_DIR/venv"
"$ROOT_DIR/venv/bin/pip" install --upgrade pip >/dev/null

echo "[2/2] Creating docs_venv at $AUTO_DIR/docs_venv"
python3 -m venv "$AUTO_DIR/docs_venv"
"$AUTO_DIR/docs_venv/bin/pip" install --upgrade pip >/dev/null
"$AUTO_DIR/docs_venv/bin/pip" install pyyaml requests >/dev/null

cat <<EOT

Environments ready.
- Activate main venv:   source "$ROOT_DIR/venv/bin/activate"
- Activate docs_venv:   source "$AUTO_DIR/docs_venv/bin/activate"  # for docs_builder.py
EOT
