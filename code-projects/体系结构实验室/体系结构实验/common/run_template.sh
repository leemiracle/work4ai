#!/bin/bash
# common/run_template.sh — 用 perf 包装实验的标准模板
#
# 用法：
#   ./run_template.sh <executable> [args...]
#
# 默认行为：
#   1. 锁定 CPU 频率（需要 root）
#   2. 绑核到 CPU 0
#   3. 跑 5 次 warmup + 20 次 measured
#   4. 同时用 perf stat 采集关键 PMU 事件
#   5. 输出中位数 + IPC + L1D/L2/分支 miss 率

set -e

# ============== 可配置变量 ==============
REPS=${REPS:-20}
WARMUP=${WARMUP:-5}
CPU=${CPU:-0}
PERF_EVENTS=${PERF_EVENTS:-\
cycles,instructions,\
L1-dcache-loads,L1-dcache-load-misses,\
L1-icache-load-misses,\
branch-instructions,branch-misses,\
dTLB-loads,dTLB-load-misses,\
iTLB-loads,iTLB-load-misses,\
cache-references,cache-misses,\
mem_inst_retired.all_stores,\
stalled-cycles-frontend,stalled-cycles-backend}

# ============== 前置检查 ==============
if [ $# -lt 1 ]; then
    echo "Usage: $0 <executable> [args...]"
    exit 1
fi
APP="$1"; shift

command -v perf >/dev/null 2>&1 || { echo "[ERR] perf not found"; exit 1; }
[ -x "$APP" ] || { echo "[ERR] $APP not executable"; exit 1; }

# ============== CPU 频率锁定（需要 root） ==============
if [ "$(id -u)" -eq 0 ]; then
    governor_old=$(cat /sys/devices/system/cpu/cpu$CPU/cpufreq/scaling_governor 2>/dev/null || echo "?")
    if [ "$governor_old" != "?" ] && [ -w /sys/devices/system/cpu/cpu$CPU/cpufreq/scaling_governor ]; then
        echo "[run] setting cpu$CPU governor -> performance (was: $governor_old)"
        echo performance > /sys/devices/system/cpu/cpu$CPU/cpufreq/scaling_governor
    fi
else
    echo "[run] warning: not root, CPU governor unchanged"
fi

# ============== 运行 ==============
echo "[run] app=$APP reps=$REPS warmup=$WARMUP cpu=$CPU"
echo "[run] ------------------------------------------------"

# Warmup
for i in $(seq 1 $WARMUP); do
    taskset -c $CPU "$APP" "$@" >/dev/null 2>&1 || true
done

# Measured: 用 perf stat 跑一次完整测量（多事件聚合）
echo "[run] === perf stat (single run, all events) ==="
taskset -c $CPU perf stat -e $PERF_EVENTS "$APP" "$@" 2>&1 | tail -30

# 多次运行，记录 wall-clock 时间，取中位数
echo "[run] === timing ($REPS reps) ==="
times=()
for i in $(seq 1 $REPS); do
    t=$( { /usr/bin/time -f "%e" taskset -c $CPU "$APP" "$@" >/dev/null; } 2>&1 )
    times+=("$t")
    printf "  rep %2d: %s s\n" "$i" "$t"
done

# 中位数计算（bash + sort）
IFS=$'\n' sorted=($(sort -n <<<"${times[*]}")); unset IFS
mid=$((REPS / 2))
echo "[run] ------------------------------------------------"
echo "[run] median wall-time: ${sorted[$mid]} s"
echo "[run] min: ${sorted[0]} s,  max: ${sorted[$((REPS-1))]} s"
