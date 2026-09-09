#!/bin/bash
# ============================================================================
# build.sh — 一键编译 Kernel-Lab 全部 16 个 C 程序
# ============================================================================
set -e

PHYGCC=${PHYGCC:-/opt/apps/phygcc-12.3.2/bin/gcc}
GCC=${GCC:-gcc}

if [ -x "$PHYGCC" ]; then
    CC="$PHYGCC"
    echo "[build] 用 PhyGCC: $CC"
else
    CC="$GCC"
    echo "[build] PhyGCC 不可用，回退系统 gcc: $CC"
fi

ARCH_FLAGS="-march=armv8.2-a+fp16+dotprod"
OPT_FLAGS="-O3 -fno-omit-frame-pointer -g -fno-inline-functions"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SRC_DIR="$SCRIPT_DIR/../src"
BIN_DIR="$SCRIPT_DIR/../bin"
mkdir -p "$BIN_DIR"

# (文件名, 二进制名, 需要的额外 flags)
TARGETS=(
    "gemm_f32.c:gemm_f32:"
    "gemm_s8.c:gemm_s8:"
    "gemm_f16.c:gemm_f16:"
    "gemm_tune.c:gemm_tune:"
    "gemm_mr8_verify.c:gemm_mr8_verify:"
    "conv_benchmark.c:conv_benchmark:"
    "conv_winograd.c:conv_winograd:"
    "conv_winograd_f44.c:conv_winograd_f44:"
    "conv_sizes.c:conv_sizes:"
    "conv_dispatcher.c:conv_dispatcher:-fopenmp"
    "multicore.c:multicore:-fopenmp"
    "multicore_winograd.c:multicore_winograd:-fopenmp"
    "attention.c:attention:"
    "attention_neon.c:attention_neon:-fopenmp"
    "asm_kernel.c:asm_kernel:"
    "bench_gemm.c:bench_gemm:"
)

i=0
for entry in "${TARGETS[@]}"; do
    i=$((i+1))
    IFS=":" read -r src bin extra <<< "$entry"
    echo "=== [$i/${#TARGETS[@]}] $bin ==="
    $CC $ARCH_FLAGS $OPT_FLAGS $extra "$SRC_DIR/$src" -o "$BIN_DIR/$bin" -lm
done

echo ""
echo "✅ 全部编完，位置: $BIN_DIR/"
ls -lh "$BIN_DIR/"
