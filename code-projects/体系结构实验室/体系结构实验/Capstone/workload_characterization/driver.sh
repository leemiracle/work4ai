#!/bin/bash
# driver.sh — 跑工作负载 + perf stat 自动采集
#
# 用法：
#   ./driver.sh              # 跑全部
#   ./driver.sh gemm_only    # 只跑 GEMM
#   ./driver.sh zstd_only    # 只跑 zstd
#
# 输出：data/<workload>_<config>.perf

set -e

# 切换到脚本所在目录
cd "$(dirname "$0")"
mkdir -p data

# 项目根目录（脚本位于 Capstone/workload_characterization/）
ROOT="../.."
LAB05="$ROOT/Lab05_并行与SIMD/src"
GEMM="$LAB05/gemm_full_stack"
ZSTD_INPUT="/tmp/zstd_test.bin"

# 准备 zstd 测试数据（64MB 随机数据 + 64MB 可压缩数据）
prepare_zstd_data() {
    if [ ! -f "$ZSTD_INPUT" ]; then
        echo "[setup] generating 64MB random data..."
        dd if=/dev/urandom of="$ZSTD_INPUT" bs=1M count=64 status=none
    fi
    if [ ! -f "${ZSTD_INPUT}.text" ]; then
        echo "[setup] generating 64MB text-like data..."
        # 重复文本，zstd 可压缩
        yes "The quick brown fox jumps over the lazy dog. " |
            head -c $((64*1024*1024)) > "${ZSTD_INPUT}.text"
    fi
}

# perf stat 包装：固定事件列表 + 绑核
# 参数：output_perf_file  cpu_core  command...
run_perf() {
    local out=$1; shift
    local cpu=$1; shift
    echo "[run] $* -> $out (cpu=$cpu)"
    perf stat -e cycles,instructions,cache-misses,cache-references,branch-misses,L1-dcache-load-misses \
        taskset -c "$cpu" "$@" >"$out.stdout" 2>"$out" || true
    # 把程序的 stdout 附加到 perf 输出末尾，便于参考
    echo "" >> "$out"
    echo "=== program stdout ===" >> "$out"
    cat "$out.stdout" >> "$out"
    rm -f "$out.stdout"
}

# ============================================================================
# GEMM：6 个变体在同一进程跑（受限于现有 Lab05 程序结构）
# 我们仍跑整体 perf，作为"工作负载混合"参考；同时记录程序自己输出的分变体 GFLOPS
# ============================================================================

run_gemm() {
    echo "=== GEMM workload ==="
    run_perf data/gemm_single_core.perf 0 "$GEMM"
    # 多核变体
    # run_perf data/gemm_8core.perf 0-7 "$GEMM"   # 需 gemm 程序支持多核调度
}

# ============================================================================
# zstd：单核绑核，跑 -1/-3/-9/-19 四个压缩级别
# 同时区分 random（不可压缩）vs text（可压缩）
# ============================================================================

run_zstd() {
    echo "=== zstd workload ==="
    prepare_zstd_data

    # 随机数据：不可压缩，zstd 必须"尽力"找模式但找不到
    for level in 1 3 9 19; do
        run_perf "data/zstd_random_L${level}.perf" 0 \
            zstd "-${level}" -f "$ZSTD_INPUT" -o /dev/null
    done

    # 文本数据：高度可压缩，zstd 主要在编码 + 哈希
    for level in 1 3 9 19; do
        run_perf "data/zstd_text_L${level}.perf" 0 \
            zstd "-${level}" -f "${ZSTD_INPUT}.text" -o /dev/null
    done
}

# ============================================================================
# 主控
# ============================================================================

case "${1:-all}" in
    gemm|gemm_only) run_gemm ;;
    zstd|zstd_only) run_zstd ;;
    all) run_gemm; run_zstd ;;
    *) echo "Usage: $0 [all|gemm_only|zstd_only]"; exit 1 ;;
esac

echo
echo "=== Done. Files in data/: ==="
ls -la data/
echo
echo "Next: python3 collect.py 'data/*.perf' -o profile_report.md"
