#!/bin/bash
# ============================================================================
# Perfetto trace_processor 本地 HTTP 服务 helper
# 用法:
#   ./tp-serve.sh                    # 加载最新的 perf.data
#   ./tp-serve.sh <trace_file>       # 加载指定 trace
#
# 工作原理:
#   trace_processor_shell 直接解析 perf.data / .perfetto-trace / systrace
#   浏览器 ui.perfetto.dev 通过 RPC 直连本地 127.0.0.1:9001
#   无需上传云，trace 越大优势越明显
# ============================================================================
set -e

TRACE=${1:-$(ls -t /data/usershare/ai/飞腾/perfetto-traces/*.perf.data 2>/dev/null | head -1)}
[ -z "$TRACE" ] && { echo "❌ 请指定 trace 文件"; exit 1; }

# 停旧实例
sudo systemctl stop tp-http.service 2>/dev/null || true

# systemd-run 起后台（脱离当前 shell，不会随终端关闭）
sudo systemd-run --unit=tp-http \
  --working-directory="$(dirname "$TRACE")" \
  /usr/local/bin/trace_processor_shell server http "$TRACE"

sleep 2

echo ""
echo "✅ trace_processor 已起，监听 http://127.0.0.1:9001"
echo "📂 加载: $TRACE"
echo ""
echo "────────────────────────────────────────────────────────"
echo "下一步（浏览器）:"
echo "  1. 打开 https://ui.perfetto.dev"
echo "  2. 左侧菜单 → 'Open trace from local trace_processor'"
echo "  3. 输入: http://localhost:9001"
echo "────────────────────────────────────────────────────────"
echo ""
echo "⚠️  Chrome 混合内容拦截解决:"
echo "     chrome://flags/#unsafely-treat-insecure-origin-as-secure"
echo "     添加 http://localhost:9001 → 重启"
echo ""
echo "停止: sudo systemctl stop tp-http.service"
echo "日志: sudo journalctl -u tp-http.service -f"
