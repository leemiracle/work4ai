#!/bin/bash
# ============================================================================
# pmu-stat.sh — 单次 PMU 完整统计（不开 trace_processor）
#
# 用法:
#   ./pmu-stat.sh                 # 测 bench_gemm
#   ./pmu-stat.sh <binary>
# ============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TARGET=${1:-$PROJECT_ROOT/bin/bench_gemm}

[ ! -x "$TARGET" ] && { echo "❌ 缺 $TARGET，先 ./scripts/build.sh"; exit 1; }

echo "=== D3000 (FTC862) 完整 PMU 统计 ==="
echo "目标: $TARGET"
echo ""

sudo perf stat -e \
cycles,instructions,inst_spec,\
stalled-cycles-frontend,stalled-cycles-backend,\
armv8_pmuv3_0/l1d_cache/,armv8_pmuv3_0/l1d_cache_refill/,\
armv8_pmuv3_0/l2d_cache/,armv8_pmuv3_0/l2d_cache_refill/,\
armv8_pmuv3_0/l3d_cache/,armv8_pmuv3_0/l3d_cache_refill/,\
armv8_pmuv3_0/mem_access/,armv8_pmuv3_0/bus_access/,\
armv8_pmuv3_0/stall_frontend/,armv8_pmuv3_0/stall_backend/,\
branch-misses,\
armv8_pmuv3_0/l1d_tlb_refill/,armv8_pmuv3_0/l2d_tlb_refill/ \
-- "$TARGET" 2>&1

echo ""
echo "=== 关键指标速算 ==="
echo "  IPC          = instructions / cycles  (D3000 上限 ≈ 4-8)"
echo "  L2 miss%     = l2d_cache_refill / l2d_cache"
echo "  backend stl% = stalled-cycles-backend / cycles"
