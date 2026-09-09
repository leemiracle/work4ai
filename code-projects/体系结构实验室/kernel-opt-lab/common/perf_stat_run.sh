#!/bin/bash
# common/perf_stat_run.sh — 飞腾/麒麟内核下 perf_event_open 受限的解决方案
#
# 背景:
#   飞腾/麒麟 5.4 内核 CONFIG_SECURITY_PERF_EVENTS_RESTRICT=y
#   导致普通用户态进程 perf_event_open() 系统调用被拒绝。
#   但 `sudo perf stat` 命令行能工作（因为 perf 内部用了特定 attr）。
#
# 用法:
#   sudo ./perf_stat_run.sh <executable> [args...]
#
# 输出:
#   - perf stat 完整输出（cycles/insts/cache/branch 等）
#   - 解析后输出 IPC / L1D miss rate / Branch MPKI 等关键指标

set -e
if [ $# -lt 1 ]; then
    echo "Usage: $0 <executable> [args...]"
    exit 1
fi
APP="$1"; shift

if [ "$(id -u)" -ne 0 ]; then
    echo "[ERR] $0 需要 root 权限。请用 sudo 运行，或降低 perf_event_paranoid。"
    exit 1
fi

EVENTS=${EVENTS:-\
cycles,\
instructions,\
L1-dcache-loads,\
L1-dcache-load-misses,\
L1-icache-load-misses,\
branch-instructions,\
branch-misses,\
dTLB-loads,\
dTLB-load-misses,\
iTLB-load-misses,\
cache-references,\
cache-misses}

REPS=${REPS:-5}

echo "[perf_stat_run] app=$APP events=$(echo $EVENTS | tr ',' ' ' | wc -w) reps=$REPS"
echo "------------------------------------------------------------------------"

# Warmup
"$APP" "$@" >/dev/null 2>&1 || true

# 跑多次 perf stat，取中位数 cycles
declare -a cyc_arr ins_arr l1m_arr brm_arr
for i in $(seq 1 $REPS); do
    out=$(perf stat -x, -e $EVENTS "$APP" "$@" 2>&1 >/dev/null)
    cyc=$(echo "$out" | grep -E "^cycles," | awk -F, '{print $1}')
    ins=$(echo "$out" | grep -E "^instructions," | awk -F, '{print $1}')
    l1m=$(echo "$out" | grep -E "^L1-dcache-load-misses," | awk -F, '{print $1}')
    brm=$(echo "$out" | grep -E "^branch-misses," | awk -F, '{print $1}')
    cyc_arr+=($cyc)
    ins_arr+=($ins)
    l1m_arr+=($l1m)
    brm_arr+=($brm)
done

# 排序取中位数（bash sort -n）
IFS=$'\n'
cyc_sorted=($(sort -n <<<"${cyc_arr[*]}"))
ins_sorted=($(sort -n <<<"${ins_arr[*]}"))
l1m_sorted=($(sort -n <<<"${l1m_arr[*]}"))
brm_sorted=($(sort -n <<<"${brm_arr[*]}"))
unset IFS

mid=$((REPS / 2))
cyc_med=${cyc_sorted[$mid]}
ins_med=${ins_sorted[$mid]}
l1m_med=${l1m_sorted[$mid]}
brm_med=${brm_sorted[$mid]}

echo "[median] cycles=$cyc_med instructions=$ins_med l1d_miss=$l1m_med br_miss=$brm_med"
echo

# 计算派生指标
if [ -n "$ins_med" ] && [ "$ins_med" -gt 0 ] 2>/dev/null; then
    ipc=$(awk "BEGIN { printf \"%.2f\", $ins_med / $cyc_med }")
    cpi=$(awk "BEGIN { printf \"%.2f\", $cyc_med / $ins_med }")
    l1_mpki=$(awk "BEGIN { printf \"%.2f\", $l1m_med * 1000 / $ins_med }")
    br_mpki=$(awk "BEGIN { printf \"%.2f\", $brm_med * 1000 / $ins_med }")
    br_mispr=$(awk "BEGIN { printf \"%.2f%%\", $brm_med * 100 / $ins_med }")
    echo "IPC          = $ipc"
    echo "CPI          = $cpi"
    echo "L1D MPKI     = $l1_mpki   (每千条指令 L1D 缺失数)"
    echo "Branch MPKI  = $br_mpki   (每千条指令分支预测失败数)"
    echo "Branch miss% = $br_mispr  (相对指令数)"
fi
