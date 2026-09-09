/* View_01_Compiler/src/opt_compare.c — 同一段代码，-O0..-Ofast 对比
 *
 * 这是一段"教科书典型"代码：点积 + 循环 + 数学运算。
 * 用同一份源码，不同 -O 等级编译，反汇编 + 计时对比，
 * 让你直接看到编译器在做什么、省了多少指令。
 *
 * 编译示例：
 *   for O in 0 1 2 3 s fast; do
 *       gcc -$O opt_compare.c -o opt_compare -$O -lm
 *       objdump -d opt_compare > opt_compare.O$O.s
 *       ./opt_compare
 *   done
 */
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define N 4096

static float A[N], B[N];

/* —— 测试 1: 简单点积（最容易向量化）—— */
float dot_product(const float *a, const float *b, int n) {
    float sum = 0.0f;
    for (int i = 0; i < n; i++) {
        sum += a[i] * b[i];
    }
    return sum;
}

/* —— 测试 2: 条件累加（带分支，难向量化）—— */
float conditional_sum(const float *a, int n, float threshold) {
    float sum = 0.0f;
    for (int i = 0; i < n; i++) {
        if (a[i] > threshold) {
            sum += a[i];
        }
    }
    return sum;
}

/* —— 测试 3: 多项式求值（依赖链）—— */
float poly_eval(const float *coef, int n, float x) {
    /* Horner 法: c0 + x*(c1 + x*(c2 + ...)) */
    float result = 0.0f;
    for (int i = n - 1; i >= 0; i--) {
        result = result * x + coef[i];
    }
    return result;
}

/* —— 测试 4: 死代码（编译器会消除吗？）—— */
float dead_code_test(float x) {
    volatile float sink;        /* volatile 阻止 DCE */
    float y = x * 3.14f;        /* 这个 y 是否被消除？ */
    sink = y;
    float z = x * 2.71f;        /* 这个 z 完全没用 */
    return y;
}

/* —— 测试 5: 循环展开（手写 vs 编译器）—— */
void manual_unroll(float *out, const float *in, int n) {
    int i;
    for (i = 0; i + 3 < n; i += 4) {     /* 4 路手展开 */
        out[i]   = in[i]   * 2.0f;
        out[i+1] = in[i+1] * 2.0f;
        out[i+2] = in[i+2] * 2.0f;
        out[i+3] = in[i+3] * 2.0f;
    }
    for (; i < n; i++) {
        out[i] = in[i] * 2.0f;
    }
}

/* —— 测试 6: 整数溢出（UB）—— */
int bad_loop(int n) {
    int sum = 0;
    for (int i = 0; i < n; i++) {
        sum += i;
    }
    return sum;       /* n 大时溢出；-O2 会做何假设？ */
}

int main(void) {
    /* 初始化 */
    srand(42);
    for (int i = 0; i < N; i++) {
        A[i] = (float)rand() / RAND_MAX;
        B[i] = (float)rand() / RAND_MAX;
    }

    /* 跑各测试，记录结果 */
    float r1 = dot_product(A, B, N);
    float r2 = conditional_sum(A, N, 0.5f);
    float coef[5] = {1, 2, 3, 4, 5};
    float r3 = poly_eval(coef, 5, 2.0f);
    float r4 = dead_code_test(1.5f);

    float out[N];
    manual_unroll(out, A, N);

    /* 计时（重复跑减少噪声）*/
    struct timespec t0, t1;
    clock_gettime(CLOCK_MONOTONIC, &t0);
    volatile float sink = 0;
    for (int iter = 0; iter < 1000; iter++) {
        sink += dot_product(A, B, N);
    }
    clock_gettime(CLOCK_MONOTONIC, &t1);
    double elapsed_ms = (t1.tv_sec - t0.tv_sec) * 1000.0 +
                        (t1.tv_nsec - t0.tv_nsec) / 1e6;

    printf("=== opt_compare (用同一代码，不同 -O 编译对比) ===\n");
    printf("dot_product   = %.4f\n", r1);
    printf("conditional_s = %.4f\n", r2);
    printf("poly_eval     = %.4f\n", r3);
    printf("dead_code     = %.4f\n", r4);
    printf("manual_unroll out[0..3] = %.4f %.4f %.4f %.4f\n",
           out[0], out[1], out[2], out[3]);
    printf("\n");
    printf("1000 次 dot_product 耗时: %.3f ms\n", elapsed_ms);
    printf("\n");
    printf("== 反汇编提示 ==\n");
    printf("  objdump -d opt_compare | grep -A 30 '<dot_product>:'\n");
    printf("  -O0: 看到完整栈帧、内存加载/存储\n");
    printf("  -O2: 大量消除、寄存器分配\n");
    printf("  -O3 -ftree-vectorize: NEON fmla 指令\n");
    printf("  -Ofast: 可能允许 FP fast-math 重关联\n");

    (void)sink;
    return 0;
}
