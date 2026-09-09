#!/bin/bash
# ============================================================================
# runtime-tune.sh — 一键 OS/Runtime 调优（OS 专家 P0 共识）
#
# 用法：source scripts/runtime-tune.sh   或   bash scripts/runtime-tune.sh
# 需要：sudo 权限（部分操作）
# 作用：锁 CPU governor / 配 hugepage / 停 irqbalance / 导出 OMP 调优环境变量
# ============================================================================

echo "=== Kernel-Lab Runtime 调优（OS 专家 P0）==="

# 1. 钉死 CPU governor = performance（避免 DVFS 爬坡）
echo "[1/4] 锁 CPU governor = performance..."
NEED_SUDO=0
for c in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do
    cur=$(cat $c 2>/dev/null)
    if [ "$cur" != "performance" ]; then
        if [ -w "$c" ]; then
            echo performance > $c
        else
            echo performance | sudo tee $c > /dev/null 2>&1 || NEED_SUDO=1
        fi
    fi
done
if [ "$NEED_SUDO" = "1" ]; then
    echo "  ⚠️  部分 governor 需 sudo，已尝试；剩余请手动："
    echo "    for c in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do echo performance | sudo tee \$c; done"
else
    cur_gov=$(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor 2>/dev/null)
    cur_freq=$(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq 2>/dev/null)
    max_freq=$(cat /sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq 2>/dev/null)
    echo "  ✓ governor=$cur_gov, freq=$(echo "scale=2; $cur_freq/1000000" | bc) GHz (max=$(echo "scale=2; $max_freq/1000000" | bc))"
fi

# 2. 配 hugepage（>=200 个 2MB hugepage 用于大矩阵）
echo "[2/4] 配 hugepage（200 × 2MB = 400MB）..."
HP_CURRENT=$(cat /proc/sys/vm/nr_hugepages 2>/dev/null)
if [ "$HP_CURRENT" -lt 200 ] 2>/dev/null; then
    echo 200 | sudo tee /proc/sys/vm/nr_hugepages > /dev/null 2>&1 && echo "  ✓ nr_hugepages=200" || echo "  ⚠️  需要 root，跳过（当前 $HP_CURRENT）"
else
    echo "  ✓ 当前 hugepage=$HP_CURRENT（已充足）"
fi

# 3. 停 irqbalance（避免 SoftIRQ 抢占算子核）
echo "[3/4] 停 irqbalance..."
if systemctl is-active irqbalance > /dev/null 2>&1; then
    sudo systemctl stop irqbalance > /dev/null 2>&1 && echo "  ✓ irqbalance stopped" || echo "  ⚠️  需要 root 跳过"
else
    echo "  ✓ irqbalance 已停或不运行"
fi

# 4. 导出 OpenMP 调优环境变量（用户脚本会继承）
echo "[4/4] 导出 OpenMP 调优环境变量..."
# 注意：OMP_PROC_BIND 在 D3000 实测反而变慢（03-os-runtime-expert.md 附录 A.1）
# 这里给两种预设，让用户自选
export OMP_WAIT_POLICY=active       # busy-wait，避免 futex 睡眠
export OMP_DYNAMIC=FALSE            # 禁动态线程数
export GOMP_SPINCOUNT=100000        # libgomp 自旋次数
echo "  ✓ OMP_WAIT_POLICY=active"
echo "  ✓ OMP_DYNAMIC=FALSE"
echo "  ✓ GOMP_SPINCOUNT=100000"
echo ""
echo "  ⚠️  OMP_PROC_BIND 未默认设置（v0.9 实测 close 在 D3000 反而慢）"
echo "     如要试 spread（线程散开）：export OMP_PROC_BIND=spread OMP_PLACES=cores"

echo ""
echo "=== 调优完成。跑 bench 时建议： ==="
echo "  taskset -c 0-7 ./bin/multicore_tiled    # 4 核 tiled 143 GFLOPS 配置"
echo "  make analyze                            # 跑全套 lens 验证"
