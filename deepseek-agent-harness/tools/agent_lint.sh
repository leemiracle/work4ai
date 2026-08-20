#!/bin/bash
# rl_lint.sh — L1：语法+风格（ruff 有则用，无则 py_compile 兜底）
T="${1:-.}"
if command -v ruff >/dev/null 2>&1; then
  ruff check "$T" && echo "[L1] ruff OK"
else
  find "$T" -name '*.py' -not -path '*/node_modules/*' -not -path '*/__pycache__/*' \
    | xargs -I{} python3 -m py_compile {} && echo "[L1] py_compile OK（ruff 未装，仅语法级）"
fi
