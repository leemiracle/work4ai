#!/bin/bash
# rl_test.sh — L2：单测（pytest 有则用，无则 unittest discover）
T="${1:-}"
if command -v pytest >/dev/null 2>&1; then
  pytest -q ${T:+"$T"}
else
  python3 -m unittest discover -s "${T:-.}" -p 'test_*.py' -v
fi
