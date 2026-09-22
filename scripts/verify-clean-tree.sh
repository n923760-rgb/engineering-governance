#!/usr/bin/env bash
set -euo pipefail

git rev-parse --is-inside-work-tree >/dev/null 2>&1 || { echo "STOP: not inside a Git worktree"; exit 11; }
if [[ -n "$(git status --porcelain)" ]]; then
  echo "STOP: working tree is not clean"
  git status --short
  exit 22
fi
echo "WORKTREE=clean"
