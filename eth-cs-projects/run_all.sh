#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
echo "=== ETH Zürich CS 全课程项目一键运行 ==="
for d in topic*/; do
    echo "--- $d ---"
    (cd "$d" && python3 *.py)
done
echo "--- supplementary ---"
python3 supplementary/undergrad_projects.py
python3 supplementary/grad_projects.py
python3 supplementary/micro_projects.py
echo "=== ✅ 全部完成 ==="
