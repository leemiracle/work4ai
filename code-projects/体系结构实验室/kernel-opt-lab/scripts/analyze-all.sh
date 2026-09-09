#!/bin/bash
# ============================================================================
# analyze-all.sh — 跑全套 lens 多视角分析，自动落地 markdown 报告
#
# 用法：./scripts/analyze-all.sh   或   make analyze
# 输出：results/lenses/lens-<name>.md + 汇总 results/lenses/SUMMARY.md
# ============================================================================
set -u
cd "$(dirname "$0")/.." || exit 2

BIN=bin
OUT_DIR=results/lenses
mkdir -p "$OUT_DIR"

TS=$(date '+%Y-%m-%d %H:%M')
LENS_LIST=(
    "lens-roofline:视角1:Roofline Model（compute/memory bound）"
    "lens-pmu:视角2:PMU 微架构计数器（IPC/cache/branch）"
    "lens-thermal:视角3:Thermal + DVFS（热设计）"
    "lens-precision:视角4:数值精度（FP16/INT8 误差分布）"
    "lens-latency:视角5:延迟分布 p50/p90/p99"
)

run_lens() {
    local bin="$1"
    local title="$2"
    local desc="$3"
    local out="$OUT_DIR/${bin}.md"
    echo "  → $bin ($desc) ..."
    {
        echo "# $title"
        echo ""
        echo "> $desc"
        echo "> 自动生成: $TS  机器: $(uname -n) / $(grep -m1 'model name' /proc/cpuinfo | cut -d: -f2 | xargs)"
        echo ""
        "$BIN/$bin" 2>&1
    } > "$out"
}

echo "=== Kernel-Lab 多视角分析（5 lens）==="
echo "时间: $TS"
echo ""

for entry in "${LENS_LIST[@]}"; do
    IFS=":" read -r bin title desc <<< "$entry"
    if [ -x "$BIN/$bin" ]; then
        run_lens "$bin" "$title" "$desc"
    else
        echo "  ⚠️  $bin 不存在，跳过"
    fi
done

# 汇总索引
SUMMARY="$OUT_DIR/SUMMARY.md"
{
echo "# Kernel-Lab 多视角分析汇总"
echo ""
echo "生成时间: $TS"
echo ""
echo "## 技术维度 lens（来自项目自身）"
echo ""
echo "| Lens | 视角 | 文件 |"
echo "|---|---|---|"
for entry in "${LENS_LIST[@]}"; do
    IFS=":" read -r bin title desc <<< "$entry"
    echo "| \`$bin\` | $desc | [\`$bin.md\`]($bin.md) |"
done
echo ""
echo "## 专家角色 lens（来自多视角审查）"
echo ""
echo "详见 [\`docs/lenses/\`](../../docs/lenses/) 目录："
echo "- 性能架构师视角"
echo "- 首席算法科学家视角"
echo "- OS/Runtime 专家视角"
echo "- 编译器专家视角"
echo "- 硬件设计专家视角"
echo "- 应用集成工程师视角"
echo "- 安全/可靠性专家视角"
echo ""
echo "---"
echo "每个 lens 独立可跑：\`\`\`bash"
echo "make bin/lens-roofline && ./bin/lens-roofline"
echo "\`\`\`"
} > "$SUMMARY"

echo ""
echo "✅ 全部 lens 跑完，报告位置: $OUT_DIR/"
ls -la "$OUT_DIR/"
