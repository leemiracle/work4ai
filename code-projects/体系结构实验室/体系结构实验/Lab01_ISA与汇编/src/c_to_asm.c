/*
 * Lab01/src/c_to_asm.c — C 到 ARM64 汇编反向工程实验
 *
 * 每个函数都是一个小测试案例，用 `gcc -S` 或 `objdump -d` 观察汇编。
 * 用法:
 *   ./c_to_asm                # 跑功能验证
 *   make disasm_sum_array     # 看不同 -O 级别下 sum_array 的汇编
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <stdlib.h>
#include "bench.h"

/* ============================================================
 * 实验 1.1: 求和（看 -O 级别差异）
 * ============================================================ */
double sum_array(const double *a, int n) {
    double s = 0;
    for (int i = 0; i < n; i++) s += a[i];
    return s;
}

/* 用 __restrict 标注无别名 */
double sum_array_restrict(const double * __restrict a, int n) {
    double s = 0;
    for (int i = 0; i < n; i++) s += a[i];
    return s;
}

/* 浮点 vs 整数 */
int sum_array_int(const int *a, int n) {
    int s = 0;
    for (int i = 0; i < n; i++) s += a[i];
    return s;
}

/* ============================================================
 * 实验 1.2: 调用约定（前 8 个参数 vs 第 9 个）
 * ============================================================ */
int test_9args(int a1, int a2, int a3, int a4, int a5,
               int a6, int a7, int a8, int a9) {
    return a1 + a9;  // a1=X0, a9 在栈上
}

double test_4doubles(double a, double b, double c, double d) {
    return a + b + c + d;  // 全走 V0-V3
}

/* callee-saved 寄存器探针：被调用方必须保存 X19-X28 */
int __attribute__((noinline)) use_x19(int v) {
    register int x asm("x19") = v;  /* 强制用 X19 */
    asm volatile("nop" ::: "memory");
    return x;
}

/* 一个会"消耗"很多寄存器的复杂函数 */
double complex_op(double a, double b, double c, double d,
                  double e, double f, double g, double h) {
    return (a*b + c*d) - (e*f + g*h);
}

/* ============================================================
 * 实验 1.3: NEON 内联汇编 vs intrinsic
 * ============================================================
 restrict 不是银弹：盲目添加可能干扰编译器已有的优化。
    调用开销会淹没微计算：测 SIMD 加速比时，务必让计算量远大于函数调用开销。
    延迟测量必须用依赖链：你的实验 1.4 正确构造了依赖链，给出了可信的指令延迟。反之，若用独立操作测吞吐量，结果会小得多。

 */
#ifdef __ARM_NEON
#include <arm_neon.h>

/* 朴素 C：4 个 float 加法 */
float dot4_scalar(const float *a, const float *b) {
    return a[0]*b[0] + a[1]*b[1] + a[2]*b[2] + a[3]*b[3];
}

/* NEON intrinsic */
float dot4_intrin(const float *a, const float *b) {
    float32x4_t va = vld1q_f32(a);
    float32x4_t vb = vld1q_f32(b);
    float32x4_t prod = vmulq_f32(va, vb);
    return vaddvq_f32(prod);
}

/* NEON 内联汇编（教学用）
 * 内联汇编里"输出"用 NEON 寄存器约束 "+w"，避免栈存储语法问题。
 * 演示 ld1 / fmul / faddp 的最小用法。
 */
float dot4_inline(const float *a, const float *b) {
    float32x4_t va, vb, prod;
    /* 用 asm 把 4 路 mul 显式表达 */
    __asm__ __volatile__(
        "ld1 {%[va].4s}, [%[a]]\n\t"
        "ld1 {%[vb].4s}, [%[b]]\n\t"
        "fmul %[prod].4s, %[va].4s, %[vb].4s\n\t"
        : [va] "=w"(va), [vb] "=w"(vb), [prod] "=w"(prod)
        : [a] "r"(a), [b] "r"(b)
        : "memory"
    );
    /* 水平加用 intrinsic，更可靠 */
    return vaddvq_f32(prod);
}
#endif /* __ARM_NEON */

/* ============================================================
 * 实验 1.4: 整数 / 浮点算术 latency
 * ============================================================ */
uint64_t latency_int_mul(uint64_t x, int n) {
    for (int i = 0; i < n; i++)
        __asm__ __volatile__("mul %0, %0, %0" : "+r"(x));
    return x;
}

uint64_t latency_int_div(uint64_t x, int n) {
    for (int i = 0; i < n; i++) {
        volatile uint64_t y = 7;
        __asm__ __volatile__("udiv %0, %0, %1" : "+r"(x) : "r"(y));
    }
    return x;
}

double latency_fadd(double x, int n) {
    for (int i = 0; i < n; i++)
        __asm__ __volatile__("fadd %d0, %d0, %d0" : "+w"(x));
    return x;
}

double latency_fmul(double x, int n) {
    for (int i = 0; i < n; i++)
        __asm__ __volatile__("fmul %d0, %d0, %d0" : "+w"(x));
    return x;
}

double latency_fdiv(double x, int n) {
    for (int i = 0; i < n; i++)
        __asm__ __volatile__("fdiv %d0, %d0, %d0" : "+w"(x));
    return x;
}

/* ============================================================
 * 测量框架（每个实验内联测量，避免函数指针陷阱）
 * ============================================================ */
#define N_ARRAY 1000000
#define N_LAT 1000
#define REPS 21

#define MEASURE(BODY_NS_VAR, BLOCK) do {           \
    uint64_t _ts[REPS];                            \
    for (int _r = 0; _r < REPS; _r++) {            \
        uint64_t _t0 = now_ns();                   \
        BLOCK;                                     \
        uint64_t _t1 = now_ns();                   \
        _ts[_r] = _t1 - _t0;                       \
    }                                              \
    BODY_NS_VAR = (double)median_u64(_ts, REPS);   \
} while (0)

int main(void) {
    pin_to_cpu(0);

    /* 准备数据 */
    static double da[N_ARRAY];
    static int ia[N_ARRAY];
    for (int i = 0; i < N_ARRAY; i++) {
        da[i] = (double)i * 0.001;
        ia[i] = i;
    }

    printf("== Lab01: C → ARM64 汇编 ==\n\n");

    /* 实验 1.1 */
    printf("[实验 1.1] sum_array 性能（不同 -O 级别对比）\n");
    printf("  数组大小 = %d\n", N_ARRAY);
    printf("  -- 编译时跑 'make disasm_sum_array' 看汇编差异 --\n");
    {
        double t_sa, t_sar, t_si;
        MEASURE(t_sa,  { volatile double r = sum_array(da, N_ARRAY); sink((uint64_t)r); });
        MEASURE(t_sar, { volatile double r = sum_array_restrict(da, N_ARRAY); sink((uint64_t)r); });
        MEASURE(t_si,  { volatile int r = sum_array_int(ia, N_ARRAY); sink((uint64_t)r); });
        printf("  sum_array(double)        = %7.1f us\n", t_sa/1000.0);
        printf("  sum_array_restrict       = %7.1f us\n", t_sar/1000.0);
        printf("  sum_array_int(int)       = %7.1f us\n\n", t_si/1000.0);
    }

    /* 实验 1.2 */
    printf("[实验 1.2] 调用约定（看 objdump）\n");
    volatile int r9 = test_9args(1,2,3,4,5,6,7,8,9);
    volatile double r4d = test_4doubles(1,2,3,4);
    volatile int rx = use_x19(42);
    printf("  test_9args result = %d (expect 10)\n", r9);
    printf("  test_4doubles result = %.0f (expect 10)\n", r4d);
    printf("  use_x19 result = %d (expect 42)\n\n", rx);

    /* 实验 1.3 NEON */
#ifdef __ARM_NEON
    printf("[实验 1.3] NEON vs 朴素 C\n");
    {
        float a[4] __attribute__((aligned(16))) = {1,2,3,4};
        float b[4] __attribute__((aligned(16))) = {1,2,3,4};
        volatile float rs = dot4_scalar(a, b);   /* expect 30 */
        volatile float ri = dot4_intrin(a, b);   /* expect 30 */
        volatile float rl = dot4_inline(a, b);   /* expect 30 */
        printf("  dot4_scalar = %.1f (expect 30)\n", rs);
        printf("  dot4_intrin = %.1f (expect 30)\n", ri);
        printf("  dot4_inline = %.1f (expect 30)\n", rl);

        /* 性能对比：跑 1000 万次 */
        int N_test = 10000000;
        double t_s, t_i, t_l;
        MEASURE(t_s, {
            float acc = 0;
            for (int k = 0; k < N_test; k++) acc += dot4_scalar(a, b);
            sink((uint64_t)acc);
        });
        MEASURE(t_i, {
            float acc = 0;
            for (int k = 0; k < N_test; k++) acc += dot4_intrin(a, b);
            sink((uint64_t)acc);
        });
        MEASURE(t_l, {
            float acc = 0;
            for (int k = 0; k < N_test; k++) acc += dot4_inline(a, b);
            sink((uint64_t)acc);
        });
        printf("  scalar:  %8.1f us / %d calls\n", t_s/1000.0, N_test);
        printf("  intrin:  %8.1f us / %d calls\n", t_i/1000.0, N_test);
        printf("  inline:  %8.1f us / %d calls\n\n", t_l/1000.0, N_test);
    }
#endif

    /* 实验 1.4 latency */
    printf("[实验 1.4] 算术 latency (依赖链长度 %d)\n", N_LAT);
    {
        struct { const char *name; uint64_t (*fn)(uint64_t, int); uint64_t seed; } tests[] = {
            { "int_mul",  latency_int_mul,  0x1234ULL },
            { "int_div",  latency_int_div,  0xDEADBEEF123ULL },
        };
        for (size_t i = 0; i < sizeof(tests)/sizeof(tests[0]); i++) {
            double t;
            MEASURE(t, { volatile uint64_t v = tests[i].fn(tests[i].seed, N_LAT); sink(v); });
            printf("  %-10s : %5.2f ns/op  (×0.4=cyc at 2.5GHz)\n", tests[i].name, t/(double)N_LAT);
        }
        struct { const char *name; double (*fn)(double, int); double seed; } ftests[] = {
            { "fadd", latency_fadd, 1.5 },
            { "fmul", latency_fmul, 1.5 },
            { "fdiv", latency_fdiv, 1.5 },
        };
        for (size_t i = 0; i < sizeof(ftests)/sizeof(ftests[0]); i++) {
            double t;
            MEASURE(t, { volatile double v = ftests[i].fn(ftests[i].seed, N_LAT); sink((uint64_t)v); });
            printf("  %-10s : %5.2f ns/op\n", ftests[i].name, t/(double)N_LAT);
        }
    }

    return 0;
}
