#!/bin/bash
# ============================================================================
# setup-hooks.sh — 一键安装 git pre-commit hook（本地 CI）
#
# 用法：./scripts/setup-hooks.sh
# 行为：把 .githooks/pre-commit 写入 .git/config core.hooksPath
#       之后每次 git commit 会自动跑 make test，FAIL 阻止 commit
# ============================================================================
set -e
cd "$(dirname "$0")/.." || exit 2

HOOKS_DIR=".githooks"
PRECOMMIT="$HOOKS_DIR/pre-commit"

mkdir -p "$HOOKS_DIR"

cat > "$PRECOMMIT" <<'EOF'
#!/bin/bash
# pre-commit hook: 跑 make test，FAIL 阻止 commit
# 安装：./scripts/setup-hooks.sh
set -e
echo "[pre-commit] 跑 make test 正确性回归..."

# 只在源码改动时跑 test
if git diff --cached --name-only | grep -qE '\.(c|h)$|Makefile$|scripts/'; then
    if [ -f Makefile ]; then
        make test >/tmp/precommit-test.log 2>&1 || {
            echo "[pre-commit] ❌ make test FAIL，commit 已阻止"
            tail -20 /tmp/precommit-test.log
            echo "[pre-commit] 完整日志: /tmp/precommit-test.log"
            echo "[pre-commit] 如要跳过（不推荐）: git commit --no-verify"
            exit 1
        }
        echo "[pre-commit] ✅ make test PASS"
    fi
else
    echo "[pre-commit] 无 .c/.h/Makefile 改动，跳过 test"
fi
EOF

chmod +x "$PRECOMMIT"

# 配置 git 使用 .githooks 目录
git config core.hooksPath "$HOOKS_DIR"

echo "✅ pre-commit hook 已安装"
echo "   hook 位置: $PRECOMMIT"
echo "   触发条件: git commit 时改动 .c/.h/Makefile/scripts/"
echo "   跳过方式: git commit --no-verify（不推荐）"
echo ""
echo "测试: git commit --allow-empty -m 'test hook'  # 应该跳过（无源码改动）"
