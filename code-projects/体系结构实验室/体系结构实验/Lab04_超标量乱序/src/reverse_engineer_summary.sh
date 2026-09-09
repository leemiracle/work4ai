#!/bin/bash
# Lab04/src/reverse_engineer_summary.sh — 汇总 Lab04 三实验输出，填微架构参数表
#
# 用法：
#   make
#   ./reverse_engineer_summary.sh
#
# 输出：依次跑 rename_capacity / rob_size / load_store_spec，
#       并在末尾打印"飞腾 D3000M 微架构参数反推表"模板，供人工据拐点填写。

set -u
cd "$(dirname "$0")"

run() {
    local name="$1"; local bin="$2"; local tail="${3:-30}"
    echo "============================================================"
    echo "  [$name]"
    echo "============================================================"
    if [ ! -x "./$bin" ]; then
        echo "  [警告] ./$bin 不存在或不可执行，请先 make"
        echo
        return
    fi
    ./"$bin" 2>&1 | tail -n "$tail"
    echo
}

echo "############################################################"
echo "#  飞腾 D3000M 微架构参数反推汇总"
echo "#  生成时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "############################################################"
echo

run "1/3] rename_capacity — PRF 容量拐点" rename_capacity 30
run "2/3] rob_size — ROB/LDQ 窗口拐点"   rob_size 22
run "3/3] load_store_spec — Memory Disambiguation" load_store_spec 12

echo "============================================================"
echo "  飞腾 D3000M 微架构参数反推表（人工据拐点填写）"
echo "============================================================"
cat <<'EOF'
| 参数                   | 推测值       | 验证方法                       |
|------------------------|--------------|--------------------------------|
| Issue Width            | 4-wide       | Lab00 null_loop IPC=4          |
| ALU 端口数             | ?            | Lab02 loop_add IPC             |
| ROB 大小（上界）       | ?            | rob_size load 拐点（≥ LDQ）    |
| LDQ (Load Queue)       | ?            | rob_size load 拐点（= 真撞点） |
| PRF (物理寄存器数)     | ?            | rename_capacity 拐点 + 32 ARF  |
| L1 D-Cache latency     | ? cyc        | Lab03 cache_sizes              |
| 分支预测失败惩罚       | ? cyc        | Lab02 branch_predict           |
| Store-forwarding 延迟  | ? cyc        | load_store_spec A 模式 CPI     |
| Memory 推测策略        | 激进/保守?   | load_store_spec C 模式 CPI     |
| 推测失败惩罚           | ? cyc        | load_store_spec (D-B)×16       |

横向对照：
| 处理器            | ROB  | PRF  | LDQ | 物理寄存器(整/浮) |
|-------------------|------|------|-----|-------------------|
| Alpha 21264       | 无ROB| -    | 32  | 72 (统一)         |
| Intel Skylake     | 224  | 180  | 72  | 180               |
| Apple M1 Firestorm| ~600 | ~350 | ~340| ~350              |
| 飞腾 D3000M (实测)| ?    | ?    | ?   | ? ← 你来填        |

研究性结论模板：
  本实验通过 [rename_capacity / rob_size / load_store_spec] 三组微基准，
  反推飞腾 D3000M (FTC862) 的乱序窗口参数。关键发现：
  1. PRF 容量 ≈ [拐点+32]，[低于/持平/高于] Intel Skylake 的 180
  2. load 窗口 ≈ [rob_size 拐点]，受 [LDQ/ROB] 限制
  3. memory disambiguator 表现为 [激进/保守]，store-forwarding 延迟 ≈ [X] cyc
  局限：load 实验无法分离 ROB 与 LDQ；要纯 ROB 上界需 ALU 长延迟链对照。
EOF
echo
echo "📌 完成。把上面表格填好后，对比姚永斌《超标量处理器设计》Ch10 的 Alpha 21264。"
