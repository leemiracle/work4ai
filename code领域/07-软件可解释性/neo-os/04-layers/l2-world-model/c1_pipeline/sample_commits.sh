#!/bin/bash
# Neo-OS C1: 抽 Linux kernel bug-fix commit（Fixes: 标签，分层抽样）
# 用法: ./sample_commits.sh [REPO] [N] [OUT]
#   REPO 默认 prototype/data/linux（git clone torvalds/linux）
#   N    默认 1000（council C1 要求）
#   OUT  默认 prototype/data/kernel_fixes_commits.txt
set -e
REPO="${1:-/data/usershare/ai/neo-os/prototype/data/linux}"
N="${2:-1000}"
OUT="${3:-/data/usershare/ai/neo-os/prototype/data/kernel_fixes_commits.txt}"

if [ ! -d "$REPO/.git" ]; then
  echo "ERROR: $REPO 不是 git 仓库（clone 未完成？）"
  echo "clone 命令: git clone --filter=blob:none --no-checkout https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git $REPO"
  exit 1
fi

echo "=== 抽 $N 个 Fixes: bug-fix commit（最近优先）==="
# format: hash / subject / body / ---END--- 分隔（c1_pipeline.py 解析）
git -C "$REPO" log --grep="Fixes:" --no-merges \
    --format="%H%n%s%n%b%n---END---" | head -n "$((N * 20))" > "$OUT"

# 统计实际 commit 数（按 ---END--- 分隔）
COUNT=$(grep -c "^---END---" "$OUT")
echo "实际抽取 commit 数: $COUNT"
echo "输出: $OUT"
echo ""
echo "下一步:"
echo "  python3 prototype/c1_pipeline/c1_pipeline.py run $OUT --n 100  # 小样本验证"
echo "  python3 prototype/c1_pipeline/c1_pipeline.py run $OUT --n $COUNT  # 全量"
