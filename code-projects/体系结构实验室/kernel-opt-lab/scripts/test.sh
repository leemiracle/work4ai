#!/bin/bash
# ============================================================================
# test.sh — 正确性回归测试（CI ready）
#
# 用法：./scripts/test.sh   或   make test
# 行为：跑所有带正确性检查的目标，抓 ✅/❌ 关键字，任一 FAIL 退出码非 0
# 退出码：0=全部 PASS，1=有 FAIL
# ============================================================================
set -u
cd "$(dirname "$0")/.." || exit 2

BIN=bin
PASS=0
FAIL=0
FAILED_TARGETS=""

run_check() {
    local name="$1"
    local cmd="$2"
    local out
    out=$($cmd 2>&1)
    # 抓 "❌" 或 "FAIL"
    if echo "$out" | grep -qE "❌|FAIL\b"; then
        echo "❌ $name"
        echo "$out" | grep -E "❌|FAIL" | head -5 | sed 's/^/    /'
        FAIL=$((FAIL+1))
        FAILED_TARGETS="$FAILED_TARGETS $name"
    else
        # 抓 "✅" 计数（如果没有任何 ✅ 也没 ❌，视为无正确性检查）
        n_ok=$(echo "$out" | grep -c "✅" || true)
        if [ "$n_ok" -gt 0 ]; then
            echo "✅ $name  ($n_ok 项 PASS)"
            PASS=$((PASS+1))
        else
            echo "⚠️  $name  (无 ✅/❌ 标记，跳过)"
        fi
    fi
}

echo "=== Kernel-Lab 正确性回归测试 ==="
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "机器: $(uname -n) / $(grep -m1 'model name' /proc/cpuinfo 2>/dev/null | cut -d: -f2 | xargs)"
echo ""

# === GEMM 类（都含 8×8 vs scalar 正确性检查）===
[ -x "$BIN/gemm_f32" ]          && run_check "gemm_f32 (FP32 GEMM v5 MR=8)"        "$BIN/gemm_f32"
[ -x "$BIN/gemm_s8" ]           && run_check "gemm_s8  (INT8 GEMM v5 MR=8)"        "$BIN/gemm_s8"
[ -x "$BIN/gemm_f16" ]          && run_check "gemm_f16 (FP16 GEMM v5 MR=8)"        "$BIN/gemm_f16"
[ -x "$BIN/asm_kernel" ]        && run_check "asm_kernel (asm vs C inline)"        "$BIN/asm_kernel"

# === 卷积类（都含 vs Direct 正确性检查）===
[ -x "$BIN/conv_winograd" ]     && run_check "conv_winograd (F(2,3) vs Direct)"    "$BIN/conv_winograd"
[ -x "$BIN/conv_winograd_f44" ] && run_check "conv_winograd_f44 (F(4,4) vs Direct)" "$BIN/conv_winograd_f44"
[ -x "$BIN/conv_dispatcher" ]   && run_check "conv_dispatcher (策略选择)"          "$BIN/conv_dispatcher"

# === Attention 类（含 NEON Flash vs Scalar 正确性）===
[ -x "$BIN/attention_neon" ]    && run_check "attention_neon (Flash vs Naive)"     "$BIN/attention_neon"

# === 多核类（含 vs 单核正确性）===
[ -x "$BIN/multicore" ]         && run_check "multicore (1/2/4/8 核 GEMM)"          "$BIN/multicore"
[ -x "$BIN/multicore_winograd" ]&& run_check "multicore_winograd (多核 Winograd)"  "$BIN/multicore_winograd"

echo ""
echo "=== 汇总 ==="
echo "  ✅ PASS: $PASS"
echo "  ❌ FAIL: $FAIL"
if [ "$FAIL" -gt 0 ]; then
    echo "  失败目标:$FAILED_TARGETS"
    exit 1
fi
echo "  全部 PASS ✅"
exit 0
