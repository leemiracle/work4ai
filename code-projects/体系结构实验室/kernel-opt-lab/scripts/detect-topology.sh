#!/bin/bash
# ============================================================================
# detect-topology.sh — D3000 拓扑探测（OS 专家 P2.1）
#
# 用法：./scripts/detect-topology.sh > results/topology.md
# 作用：dump CPU/cache/NUMA/governor 拓扑，bench 报告必须附带（可复现性）
# ============================================================================
set -u
HOST=$(uname -n)
DATE=$(date '+%Y-%m-%d %H:%M')

echo "# D3000 拓扑快照"
echo ""
echo "- **主机**: $HOST"
echo "- **时间**: $DATE"
echo "- **内核**: $(uname -r)"
echo "- **CPU**: $(grep -m1 'model name' /proc/cpuinfo | cut -d: -f2 | xargs)"
echo ""

echo "## 1. CPU 概况"
echo ""
echo '```'
lscpu 2>/dev/null | grep -E "^(Architecture|CPU\(s\)|Model name|Thread|Core|Socket|CPU max|CPU min|BogoMIPS|Vulnerability)" || echo "lscpu 不可用"
echo '```'
echo ""

echo "## 2. CPU 频率（每核 governor + 当前/最大频率）"
echo ""
echo "| CPU | governor | cur GHz | max GHz | min GHz |"
echo "|---|---|---|---|---|"
for d in /sys/devices/system/cpu/cpu[0-9]*; do
    c=$(basename $d)
    cnum=$(echo $c | tr -dc '0-9')
    gov=$(cat $d/cpufreq/scaling_governor 2>/dev/null || echo "N/A")
    cur=$(cat $d/cpufreq/scaling_cur_freq 2>/dev/null || echo 0)
    max=$(cat $d/cpufreq/cpuinfo_max_freq 2>/dev/null || echo 0)
    min=$(cat $d/cpufreq/cpuinfo_min_freq 2>/dev/null || echo 0)
    printf "| %s | %s | %.2f | %.2f | %.2f |\n" \
        "$c" "$gov" \
        "$(echo "scale=2; $cur/1000000" | bc 2>/dev/null)" \
        "$(echo "scale=2; $max/1000000" | bc 2>/dev/null)" \
        "$(echo "scale=2; $min/1000000" | bc 2>/dev/null)"
done
echo ""

echo "## 3. Cache 层级 + 共享 CPU 拓扑（关键：D3000 L3 双段）"
echo ""
echo "每个 cache index 的 shared_cpu_list 揭示真实的 cache 共享边界："
echo ""
echo "| CPU | index | level | type | size | shared with |"
echo "|---|---|---|---|---|---|"
for d in /sys/devices/system/cpu/cpu0/cache/index*; do
    idx=$(basename $d)
    lvl=$(cat $d/level 2>/dev/null)
    type=$(cat $d/type 2>/dev/null)
    size=$(cat $d/size 2>/dev/null)
    shared=$(cat $d/shared_cpu_list 2>/dev/null)
    echo "| cpu0 | $idx | L$lvl | $type | $size | $shared |"
done
echo ""
echo "**解读**：shared_cpu_list 显示哪些核共享同一 cache。D3000 典型："
echo "- L1/L2: 单核私有（每核一个 list）"
echo "- L3-1: 核 0-3 共享 4MB"
echo "- L3-2: 核 0-7 共享 8MB"
echo ""

echo "## 4. NUMA topology（D3000 应该是 UMA）"
echo ""
echo '```'
numactl -H 2>/dev/null || echo "numactl 不可用（可能未安装）"
echo '```'
echo ""

echo "## 5. Hugepage 配置"
echo ""
HP=$(cat /proc/sys/vm/nr_hugepages 2>/dev/null)
HPSIZE=$(grep Hugepagesize /proc/meminfo 2>/dev/null | awk '{print $2, $3}')
echo "- nr_hugepages: $HP"
echo "- Hugepagesize: $HPSIZE"
echo ""

echo "## 6. IRQ / irqbalance 状态"
echo ""
if systemctl is-active irqbalance > /dev/null 2>&1; then
    echo "- irqbalance: **active** ⚠️（建议跑 bench 前 stop）"
else
    echo "- irqbalance: stopped/inactive ✓"
fi
echo ""

echo "## 7. perf_event 可用性"
echo ""
PEP=$(cat /proc/sys/kernel/perf_event_paranoid 2>/dev/null)
echo "- perf_event_paranoid: $PEP"
if [ "$PEP" = "0" ]; then echo "  → 所有事件可访问（含 kernel）"
elif [ "$PEP" = "1" ]; then echo "  → 用户态事件可访问（当前）✓"
elif [ "$PEP" = "2" ]; then echo "  → 仅 kernel 访问 ⚠️"
elif [ "$PEP" = "3" ]; then echo "  → 禁用 ❌"
fi
echo ""

echo "---"
echo ""
echo "本快照应作为 bench 报告的附属（性能数字的可复现性依赖于拓扑）"
