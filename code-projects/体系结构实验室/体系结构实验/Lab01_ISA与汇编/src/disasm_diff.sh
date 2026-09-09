#!/bin/bash
# Lab01/src/disasm_diff.sh — 对比不同 -O 级别下的汇编
#
# 用法: ./disasm_diff.sh <function_name> [source.c]
#   默认 source = c_to_asm.c
set -e
FN=${1:-sum_array}
SRC=${2:-c_to_asm.c}
COMMON=$(cd $(dirname $0)/../..; pwd)/common

cd $(dirname $0)
echo "=== 比较函数 $FN 在不同 -O 级别下的汇编 ==="
echo

for opt in O0 O1 O2 O3 Ofast; do
    out=/tmp/${FN}.${opt}.s
    gcc -std=gnu11 -S -fno-asynchronous-unwind-tables \
        -I${COMMON} -mcpu=native -$opt $SRC -o $out 2>/dev/null
    echo "===== -$opt ====="
    awk "/^${FN}:/{flag=1} flag{print; if (/ret/){exit}}" $out | head -40
    echo
done
