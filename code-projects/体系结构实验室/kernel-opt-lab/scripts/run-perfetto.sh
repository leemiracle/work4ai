#!/bin/bash
# ============================================================================
# run-perfetto.sh — 一键 perf record + trace_processor 服务
#
# 用法:
#   ./run-perfetto.sh                # 采 bench_gemm
#   ./run-perfetto.sh <binary>       # 采任意二进制
#   ./run-perfetto.sh <binary> "arg1 arg2"
# ============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BIN_DIR="$PROJECT_ROOT/bin"
TRACE_DIR="$PROJECT_ROOT/traces"
mkdir -p "$TRACE_DIR"

# 默认目标
TARGET=${1:-$BIN_DIR/bench_gemm}
ARGS=${2:-}

if [ ! -x "$TARGET" ]; then
    echo "❌ 找不到可执行: $TARGET"
    echo "   先跑 ./scripts/build.sh"
    exit 1
fi

# 生成本次 trace 文件名
TS=$(date +%Y%m%d_%H%M)
BASENAME=$(basename "$TARGET")
TRACE_FILE="$TRACE_DIR/${BASENAME}_${TS}.perf.data"

echo "=== [1/4] perf record（频率 999Hz，含调用栈）==="
sudo perf record -F 999 -g --call-graph dwarf \
    -o "$TRACE_FILE" -- "$TARGET" $ARGS 2>&1 | tail -5

sudo chown "$USER":"$USER" "$TRACE_FILE"

echo ""
echo "=== [2/4] 停旧 trace_processor 服务 ==="
sudo systemctl stop tp-http.service 2>/dev/null || true

echo ""
echo "=== [3/4] 启动 trace_processor HTTP 服务（systemd 守护）==="
sudo systemd-run --unit=tp-http \
    --working-directory="$TRACE_DIR" \
    /usr/local/bin/trace_processor_shell server http "$TRACE_FILE"

sleep 2

echo ""
echo "=== [4/4] 浏览器连接说明 ==="
echo ""
echo "  📂 trace: $TRACE_FILE ($(du -h "$TRACE_FILE" | cut -f1))"
echo ""
echo "  ─────────────────────────────────────────────────────────"
echo "  1. 浏览器打开 https://ui.perfetto.dev"
echo "  2. 左侧菜单 → 'Open trace from local trace_processor'"
echo "  3. 输入: http://localhost:9001"
echo "  ─────────────────────────────────────────────────────────"
echo ""
echo "  ⚠️  Chrome 混合内容拦截解决:"
echo "     chrome://flags/#unsafely-treat-insecure-origin-as-secure"
echo "     添加 http://localhost:9001 → 重启 Chrome"
echo ""
echo "  日志: sudo journalctl -u tp-http.service -f"
echo "  停止: sudo systemctl stop tp-http.service"
