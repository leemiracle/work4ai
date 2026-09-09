#!/bin/bash
# ============================================================================
# bench-all.sh — 跑全套 benchmark，自动生成 markdown 报告
#
# 用法：./scripts/bench-all.sh   或   make bench
# 输出：results/bench-<YYYYmmdd-HHMM>.md（自动追加到 baseline.md 之后）
# ============================================================================
set -u
cd "$(dirname "$0")/.." || exit 2

BIN=bin
TS=$(date '+%Y%m%d-%H%M')
DATE=$(date '+%Y-%m-%d')
HOST=$(uname -n)
CPU=$(grep -m1 'model name' /proc/cpuinfo 2>/dev/null | cut -d: -f2 | xargs)
OUT="results/bench-$TS.md"

if [ ! -d results ]; then mkdir -p results; fi

{
echo "# Kernel-Lab 全套 Benchmark"
echo ""
echo "- **日期**: $DATE"
echo "- **机器**: $HOST / $CPU"
echo "- **内核**: $(uname -r)"
echo "- **编译器**: PhyGCC 12.3.2 / \`-O3 -march=armv8.2-a+fp16+dotprod\`"
echo ""
echo "---"
echo ""

# === GEMM 类 ===
echo "## 1. GEMM（1024³）"
echo ""
for t in gemm_f32 gemm_s8 gemm_f16 gemm_mr8_verify; do
    if [ -x "$BIN/$t" ]; then
        echo '```'
        echo "$ $BIN/$t"
        "$BIN/$t" 2>&1
        echo '```'
        echo ""
    fi
done

# === 多核 GEMM ===
echo "## 2. 多核 GEMM（OpenMP 扩展性）"
echo ""
if [ -x "$BIN/multicore" ]; then
    echo '```'
    "$BIN/multicore" 2>&1
    echo '```'
    echo ""
fi

# === 卷积类 ===
echo "## 3. 卷积（3×3 stride=1 pad=1）"
echo ""
for t in conv_winograd conv_winograd_f44 conv_sizes conv_dispatcher; do
    if [ -x "$BIN/$t" ]; then
        echo "### $t"
        echo '```'
        "$BIN/$t" 2>&1
        echo '```'
        echo ""
    fi
done

# === 多核 Winograd ===
echo "## 4. 多核 Winograd"
echo ""
if [ -x "$BIN/multicore_winograd" ]; then
    echo '```'
    "$BIN/multicore_winograd" 2>&1
    echo '```'
    echo ""
fi

# === Attention ===
echo "## 5. Attention（head_dim=64）"
echo ""
for t in attention attention_neon; do
    if [ -x "$BIN/$t" ]; then
        echo "### $t"
        echo '```'
        "$BIN/$t" 2>&1
        echo '```'
        echo ""
    fi
done

# === 微架构调优 ===
echo "## 6. 微架构调优"
echo ""
if [ -x "$BIN/gemm_tune" ]; then
    echo "### gemm_tune（MR × NR × KC sweep）"
    echo '```'
    "$BIN/gemm_tune" 2>&1
    echo '```'
    echo ""
fi

echo "---"
echo ""
echo "## 汇总要点"
echo ""
echo "- 自动生成于 $DATE，详见 [\`results/baseline.md\`](baseline.md)"
} > "$OUT"

echo ""
echo "✅ 报告已生成: $OUT"
echo "   共 $(wc -l < "$OUT") 行"
echo ""
echo "预览前 50 行:"
head -50 "$OUT"
