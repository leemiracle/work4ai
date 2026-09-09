#!/bin/bash

echo "=== LLVM 调试和分析实验 ==="
echo

echo "实验1: 使用llvm-objdump分析可执行文件"
echo
echo "生成带符号的可执行文件..."
clang -g simple.c -o simple_debug
echo
echo "=== 符号表 ==="
objdump -t simple_debug | grep -E "add|factorial|main"
echo

echo "=== 反汇编main函数 ==="
objdump -d simple_debug | grep -A 30 "<main>:"
echo

echo "实验2: 分析优化级别的影响"
echo
for opt in -O0 -O1 -O2 -O3 -Os; do
    echo "--- 使用 $opt 编译 ---"
    clang -S -emit-llvm $opt simple.c -o simple_${opt#-}.ll 2>/dev/null
    echo "factorial 函数IR行数: $(grep -c "factorial" simple_${opt#-}.ll)"
    echo "基本块数量: $(grep -E "^([0-9]+:)" simple_${opt#-}.ll | wc -l)"
    echo
done

echo "实验3: 查看优化后的factorial实现"
echo
echo "--- -O3 优化版本 ---"
grep -A 50 "define.*factorial" simple_O3.ll | head -50
echo

echo "实验4: 使用opt工具进行特定优化（如果可用）"
echo
if command -v opt &> /dev/null; then
    echo "✓ opt工具可用"
    echo "运行死代码消除优化..."
    opt -passes=dce simple.ll -o simple_dce.ll
    echo "运行常量传播..."
    opt -passes=constprop simple.ll -o simple_constprop.ll
else
    echo "✗ opt工具不可用（需要构建LLVM）"
fi

echo
echo "实验5: 分析汇编代码差异"
echo
echo "--- -O0 vs -O3 add函数汇编 ---"
echo "O0:"
clang -S -O0 simple.c -o add_O0.s 2>/dev/null
grep -A 15 "^add:" add_O0.s | head -15
echo
echo "O3:"
clang -S -O3 simple.c -o add_O3.s 2>/dev/null
grep -A 15 "^add:" add_O3.s | head -15
echo

echo "实验6: 函数内联分析"
echo
echo "--- -O3 时的内联情况 ---"
echo "检查add函数是否被内联..."
grep -E "call.*add|add\(" simple_O3.ll | head -5
echo

echo "实验7: 查看生成的位码文件"
echo
clang -emit-llvm -c simple.c -o simple.bc
echo "生成的位码文件: simple.bc"
file simple.bc
echo

echo "使用llvm-dis反汇编位码（如果可用）..."
if command -v llvm-dis &> /dev/null; then
    llvm-dis simple.bc -o simple_from_bc.ll
    echo "✓ 反汇编成功"
else
    echo "✗ llvm-dis不可用"
fi

echo
echo "=== 调试实验完成 ==="
