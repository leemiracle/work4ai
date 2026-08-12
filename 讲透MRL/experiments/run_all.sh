#!/bin/bash
# 讲透MRL 全部实验一键运行
# 用法: bash run_all.sh
set -e
cd "$(dirname "$0")"

echo "================================================"
echo "讲透MRL 全部实验一键运行"
echo "================================================"

for f in 0*.py; do
    echo ""
    echo "========== 跑 $f =========="
    OMP_NUM_THREADS=1 python3 "$f"
done

echo ""
echo "================================================"
echo "全部实验完成. 生成的 png:"
ls -la *.png 2>/dev/null || echo "(无 png 生成)"
