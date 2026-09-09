#!/bin/bash

echo "=== LLVM 实验：从源码到机器码 ==="
echo

echo "实验1: 生成LLVM IR"
echo "命令: clang -S -emit-llvm simple.c -o simple.ll"
clang -S -emit-llvm simple.c -o simple.ll
if [ $? -eq 0 ]; then
    echo "✓ 成功生成 simple.ll"
    echo
    echo "--- simple.ll 内容 ---"
    cat simple.ll
else
    echo "✗ 生成失败"
fi
echo

echo "实验2: 生成优化的IR"
echo "命令: clang -S -emit-llvm -O2 simple.c -o simple_opt.ll"
clang -S -emit-llvm -O2 simple.c -o simple_opt.ll
if [ $? -eq 0 ]; then
    echo "✓ 成功生成 simple_opt.ll"
    echo
    echo "--- 简单对比 (文件行数) ---"
    echo "未优化: $(wc -l < simple.ll) 行"
    echo "优化后: $(wc -l < simple_opt.ll) 行"
fi
echo

echo "实验3: 编译为汇编代码"
echo "命令: clang -S simple.c -o simple.s"
clang -S simple.c -o simple.s
if [ $? -eq 0 ]; then
    echo "✓ 成功生成 simple.s"
    echo
    echo "--- simple.s 内容 ---"
    cat simple.s
else
    echo "✗ 生成失败"
fi
echo

echo "实验4: 编译并运行"
echo "命令: clang simple.c -o simple && ./simple"
clang simple.c -o simple
if [ $? -eq 0 ]; then
    echo "✓ 编译成功"
    ./simple
else
    echo "✗ 编译失败"
fi
echo

echo "实验5: 使用 -g 生成调试信息"
echo "命令: clang -g -S -emit-llvm simple.c -o simple_debug.ll"
clang -g -S -emit-llvm simple.c -o simple_debug.ll
if [ $? -eq 0 ]; then
    echo "✓ 成功生成带调试信息的IR"
    echo
    echo "--- 调试信息示例 (前30行) ---"
    head -30 simple_debug.ll
fi
echo

echo "实验6: 分析生成的IR差异"
echo "比较 factorial 函数的IR生成"
echo
echo "--- 未优化版本 ---"
grep -A 20 "define.*factorial" simple.ll | head -20
echo
echo "--- 优化版本 ---"
grep -A 20 "define.*factorial" simple_opt.ll | head -20
echo

echo "=== 实验完成 ==="
