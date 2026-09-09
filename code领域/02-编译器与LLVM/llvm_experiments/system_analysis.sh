#!/bin/bash

echo "=== 计算机系统层次结构分析实验 ==="
echo

echo "实验1: 编译并运行系统层次实验"
echo
clang -g system_levels.c -o system_levels
if [ $? -eq 0 ]; then
    echo "✓ 编译成功"
    echo
    ./system_levels
else
    echo "✗ 编译失败"
fi
echo

echo "实验2: 分析内存布局"
echo
echo "--- 查看生成的IR中的内存分配 ---"
clang -S -emit-llvm -O0 system_levels.c -o system_levels.ll 2>/dev/null
grep -A 5 "define.*memory_experiment" system_levels.ll | head -10
echo

echo "实验3: 分析函数调用"
echo
echo "--- add_numbers 函数的IR ---"
grep -A 10 "define.*add_numbers" system_levels.ll | head -15
echo

echo "--- add_numbers 的汇编代码 ---"
clang -S system_levels.c -o system_levels.s 2>/dev/null
grep -A 20 "^_Z12add_numbers:" system_levels.s | head -25
echo

echo "实验4: 对比不同优化级别"
echo
for opt in -O0 -O2 -O3; do
    echo "--- $opt 优化级别 ---"
    clang -S $opt system_levels.c -o system_levels_${opt#-}.s 2>/dev/null
    
    # 统计指令数量
    inst_count=$(grep -vE "^\.|^\s*\.|^$|^//|^L|^@|File:" system_levels_${opt#-}.s | wc -l)
    echo "指令数: $inst_count"
    
    # 查看recursive_fibonacci函数的复杂度
    fib_lines=$(grep -A 100 "^_Z21recursive_fibonacci:" system_levels_${opt#-}.s | grep -E "retq|callq" | wc -l)
    echo "fibonacci函数中的调用/返回数: $fib_lines"
    echo
done

echo "实验5: 分析内联汇编的生成"
echo
echo "--- inline_asm_experiment 的汇编 ---"
grep -A 30 "^inline_asm_experiment:" system_levels.s | head -35
echo

echo "实验6: 理解数据对齐和内存布局"
echo
echo "--- normal_struct 的内存布局 ---"
cat << 'EOF' > struct_test.c
#include <stdio.h>

struct normal_struct {
    char c;
    int i;
    short s;
};

struct packed_struct {
    char c;
    int i;
    short s;
} __attribute__((packed));

int main() {
    printf("normal_struct offsets:\n");
    printf("  c: %zu\n", __builtin_offsetof(struct normal_struct, c));
    printf("  i: %zu\n", __builtin_offsetof(struct normal_struct, i));
    printf("  s: %zu\n", __builtin_offsetof(struct normal_struct, s));
    printf("  size: %zu\n", sizeof(struct normal_struct));
    
    printf("packed_struct offsets:\n");
    printf("  c: %zu\n", __builtin_offsetof(struct packed_struct, c));
    printf("  i: %zu\n", __builtin_offsetof(struct packed_struct, i));
    printf("  s: %zu\n", __builtin_offsetof(struct packed_struct, s));
    printf("  size: %zu\n", sizeof(struct packed_struct));
    
    return 0;
}
EOF
clang struct_test.c -o struct_test
./struct_test
echo

echo "实验7: 使用gdb调试查看运行时行为"
echo
cat << 'EOF' > gdb_commands.txt
break memory_experiment
run
print stack_var
print &stack_var
print heap_var
print *heap_var
continue
quit
EOF
echo "GDB命令已准备，运行: gdb -x gdb_commands.txt ./system_levels"
echo

echo "实验8: 分析分支预测的影响"
echo
cat << 'EOF' > branch_test.c
#include <stdio.h>
#include <time.h>
#include <stdlib.h>

#define N 10000000

// 可预测的分支
int predictable_branch(int* arr) {
    int sum = 0;
    for (int i = 0; i < N; i++) {
        sum += arr[i % 100];
    }
    return sum;
}

// 不可预测的分支
int unpredictable_branch(int* arr) {
    int sum = 0;
    for (int i = 0; i < N; i++) {
        if (arr[i % 100] > 50) {
            sum += arr[i % 100];
        }
    }
    return sum;
}

int main() {
    int arr[100];
    for (int i = 0; i < 100; i++) {
        arr[i] = rand() % 100;
    }
    
    clock_t start, end;
    double cpu_time_used;
    
    start = clock();
    int result1 = predictable_branch(arr);
    end = clock();
    cpu_time_used = ((double)(end - start)) / CLOCKS_PER_SEC;
    printf("Predictable: %.6f seconds, result: %d\n", cpu_time_used, result1);
    
    start = clock();
    int result2 = unpredictable_branch(arr);
    end = clock();
    cpu_time_used = ((double)(end - start)) / CLOCKS_PER_SEC;
    printf("Unpredictable: %.6f seconds, result: %d\n", cpu_time_used, result2);
    
    return 0;
}
EOF
clang -O2 branch_test.c -o branch_test
echo "✓ 编译完成"
echo "运行分支预测实验..."
./branch_test
echo

echo "实验9: 查看volatile变量的优化"
echo
echo "--- -O0 时的volatile实验 ---"
clang -S -O0 system_levels.c -o volatile_O0.s 2>/dev/null
grep -A 30 "^volatile_experiment:" volatile_O0.s | head -35
echo

echo "--- -O3 时的volatile实验 ---"
clang -S -O3 system_levels.c -o volatile_O3.s 2>/dev/null
grep -A 30 "^volatile_experiment:" volatile_O3.s | head -35
echo

echo "实验10: 使用objdump分析二进制文件"
echo
echo "--- 符号表 ---"
objdump -t system_levels | grep -E "memory|branch|add_numbers|fibonacci"
echo

echo "--- section信息 ---"
objdump -h system_levels
echo

echo "=== 系统层次分析实验完成 ==="
echo
echo "总结要点："
echo "1. 不同类型变量的内存分配位置不同（栈、堆、数据段）"
echo "2. 函数调用遵循特定的调用约定（x86_64: 前6个参数通过寄存器）"
echo "3. 编译器优化可以显著改变生成的代码"
echo "4. 数据对齐影响内存布局和访问效率"
echo "5. 分支预测影响程序性能"
echo "6. volatile关键字防止编译器优化"
