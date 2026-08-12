#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
echo "=== CMU SCS 全课程项目一键运行 ==="
echo ""

# Core topics
for d in topic*/; do
    if ls "$d"*.py >/dev/null 2>&1; then
        echo "--- $d ---"
        (cd "$d" && python3 *.py)
        echo ""
    fi
done

echo "--- supplementary ---"
python3 supplementary/undergrad_projects.py
echo ""
python3 supplementary/grad_projects.py
echo ""
python3 supplementary/micro_projects.py

echo ""
echo "=== ✅ 全部完成 ==="
