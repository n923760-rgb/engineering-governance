#!/usr/bin/env bash
set -euo pipefail

OUT_DIR="${1:-.evidence/git-state}"
mkdir -p "$OUT_DIR"

git remote -v > "$OUT_DIR/remotes.txt"
git branch --show-current > "$OUT_DIR/branch.txt"
git rev-parse HEAD > "$OUT_DIR/local-head.txt"
git status --short > "$OUT_DIR/status.txt"
git log -1 --decorate --oneline > "$OUT_DIR/head-summary.txt"
git diff > "$OUT_DIR/working-tree.diff"
git diff --cached > "$OUT_DIR/index.diff"

if command -v sha256sum >/dev/null 2>&1; then
  find "$OUT_DIR" -type f -maxdepth 1 -print0 | sort -z | xargs -0 sha256sum > "$OUT_DIR/SHA256SUMS"
elif command -v shasum >/dev/null 2>&1; then
  find "$OUT_DIR" -type f -maxdepth 1 -print0 | sort -z | xargs -0 shasum -a 256 > "$OUT_DIR/SHA256SUMS"
fi

echo "Evidence written to $OUT_DIR"
