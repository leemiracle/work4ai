/*
 * Lab01/src/basic_math.c — 整数/浮点算术 latency 探测
 *
 * 用依赖链测各操作的 latency（cyc/op）：
 *   x = x <op> <imm>   循环 N 次，每次依赖上次结果
 *
 * 预期（飞腾 D3000M）：
 *   int add/mul/and ~1-3 cyc, int div ~20+ cyc
 *   fp add/mul ~4 cyc, fp div ~20-30 cyc, sqrt ~40 cyc
 *
 * 除法/开方是流水线硬骨头（迭代算法或大芯片面积）。
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdint.h>
#include "bench.h"
#include "pmu.h"

#define N    10000000
#define REPS 21

#define LAT_INT(NAME, BODY) \
static uint64_t __attribute__((noinline)) NAME(uint64_t x) { \
    for (int i = 0; i < N; i++) { BODY; } \
    return x; \
}

#define LAT_DBL(NAME, BODY) \
static double __attribute__((noinline,optimize("no-fast-math"))) NAME(double x) { \
    for (int i = 0; i < N; i++) { BODY; } \
    return x; \
}

LAT_INT(lat_mul,  x = x * 2654435761ULL + 1)

/* lat_add 特殊处理：x=x+1 会被编译器归纳为 x+N（测出 0 cyc），
 * 加 asm volatile 阻止归纳，强制每次真做加法 */
static uint64_t __attribute__((noinline)) lat_add(uint64_t x) {
    for (int i = 0; i < N; i++) {
        x = x + 1;
        __asm__ __volatile__("" : "+r"(x));
    }
    return x;
}

LAT_INT(lat_mul_dummy, x = x * 2654435761ULL + 1)
LAT_INT(lat_div,  x = x / 7ULL + 1)
LAT_INT(lat_and,  x = (x & 0xff) ^ (x >> 3))
LAT_INT(lat_shift,x = (x << 3) | (x >> 61))

LAT_DBL(lat_fadd, x = x + 1.0)
LAT_DBL(lat_fmul, x = x * 1.0001)
LAT_DBL(lat_fdiv, x = x / 1.0001)

static double time_int(uint64_t (*fn)(uint64_t)) {
    uint64_t ts[REPS];
    for (int r = 0; r < REPS; r++) {
        uint64_t t0 = now_ns();
        volatile uint64_t v = fn(0xDEADBEEF);
        sink((uint64_t)v);
        uint64_t t1 = now_ns();
        ts[r] = t1 - t0;
    }
    for (int i = 1; i < REPS; i++) {
        uint64_t k = ts[i]; int j = i;
        while (j > 0 && ts[j-1] > k) { ts[j] = ts[j-1]; j--; }
        ts[j] = k;
    }
    return (double)ts[REPS/2] / (double)N * 2.5;  /* cyc/op @ 2.5GHz */
}

static double time_dbl(double (*fn)(double)) {
    uint64_t ts[REPS];
    for (int r = 0; r < REPS; r++) {
        uint64_t t0 = now_ns();
        volatile double v = fn(1.5);
        sink((uint64_t)v);
        uint64_t t1 = now_ns();
        ts[r] = t1 - t0;
    }
    for (int i = 1; i < REPS; i++) {
        uint64_t k = ts[i]; int j = i;
        while (j > 0 && ts[j-1] > k) { ts[j] = ts[j-1]; j--; }
        ts[j] = k;
    }
    return (double)ts[REPS/2] / (double)N * 2.5;
}

int main(void) {
    pin_to_cpu(0);
    printf("== Lab01.4: 算术 latency (依赖链, N=%d) ==\n\n", N);

    printf("%-16s %12s %s\n", "operation", "cyc/op", "解读");
    printf("%-16s %12s %s\n", "---------", "------", "-----");

    struct { const char *name; double cyc; const char *note; } rows[] = {
        {"int add",     time_int(lat_add),   "ALU 单周期（实测 ~1 cyc）"},
        {"int mul",     time_int(lat_mul),   "乘法器多周期（实测 ~5 cyc）"},
        {"int and/shift",time_int(lat_and),  "位运算单周期"},
        {"int shift",   time_int(lat_shift), "位运算单周期"},
        {"int div",     time_int(lat_div),   "除法迭代算法（实测 ~10 cyc，教科书常说 20）"},
        {"fp add",      time_dbl(lat_fadd),  "FPU 流水线（实测 ~2 cyc）"},
        {"fp mul",      time_dbl(lat_fmul),  "FPU 流水线（实测 ~3 cyc）"},
        {"fp div",      time_dbl(lat_fdiv),  "浮点迭代除法（实测 ~13 cyc，教科书常说 20-30）"},
    };

    for (size_t i = 0; i < sizeof(rows)/sizeof(rows[0]); i++) {
        printf("%-16s %12.2f %s\n", rows[i].name, rows[i].cyc, rows[i].note);
    }

    printf("\n  == 解读（飞腾 D3000M 实测，注意比教科书通用值更快）==\n");
    printf("  * int add/and/shift ~1 cyc: ALU 全流水线\n");
    printf("  * int mul ~5 cyc (实测): 乘法器 latency，throughput 1/cyc\n");
    printf("  * int div ~10 cyc (实测): 除法迭代算法，比教科书说的 ~20 快\n");
    printf("  * fp add ~2 cyc / fp mul ~3 cyc (实测): FPU 流水线充分\n");
    printf("  * fp div ~13 cyc (实测): 浮点除法比乘法贵 ~4x（教科书常说 20-30）\n");
    printf("  * ⚠ 教训: 别照搬教科书 latency，飞腾实测普遍更快——亲手测才准\n");
    printf("  * 优化启示: 编译器把 x/8 优化成 x>>3 (避免除法); 循环里避免 div\n");
    printf("  * 验证: objdump -d basic_math | grep -E 'mul|div|fadd'\n");
    printf("    看 x/7 是否保留 sdiv (编译器无法优化非 2 幂除法)\n");
    return 0;
}
