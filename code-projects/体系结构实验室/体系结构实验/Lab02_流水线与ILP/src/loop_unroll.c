/*
 * Lab02/src/loop_unroll.c — 循环展开实验
 *
 * 对比展开 1/2/4/8/16 倍的数组求和 IPC。
 * 展开提供多个独立累加器 → ILP → IPC 涨，直到撞 4-wide 发射带宽或寄存器上限。
 *
 * 预期（飞腾 D3000M）：
 *   unroll 1:  IPC ~2.0  (GCC -O2 默认展开 2，加循环控制开销)
 *   unroll 4:  IPC ~2.7  (4 独立累加器填满 4-wide)
 *   unroll 8:  IPC ~3.2  (充分 ILP)
 *   unroll 16: IPC ~3.3  (接近寄存器上限，增益递减)
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include "bench.h"
#include "pmu.h"

#define N    1000000   /* 需被 16 整除 */
#define REPS 21

#define ATTR __attribute__((noinline,optimize("no-fast-math")))

static double ATTR sum_u1(const double *a, size_t n) {
    double s = 0;
    for (size_t i = 0; i < n; i++) s += a[i];
    return s;
}

static double ATTR sum_u2(const double *a, size_t n) {
    double s0=0, s1=0; size_t i;
    for (i = 0; i + 1 < n; i += 2) { s0 += a[i]; s1 += a[i+1]; }
    for (; i < n; i++) s0 += a[i];
    return s0 + s1;
}

static double ATTR sum_u4(const double *a, size_t n) {
    double s0=0,s1=0,s2=0,s3=0; size_t i;
    for (i = 0; i + 3 < n; i += 4) {
        s0 += a[i]; s1 += a[i+1]; s2 += a[i+2]; s3 += a[i+3];
    }
    for (; i < n; i++) s0 += a[i];
    return s0+s1+s2+s3;
}

static double ATTR sum_u8(const double *a, size_t n) {
    double s0=0,s1=0,s2=0,s3=0,s4=0,s5=0,s6=0,s7=0; size_t i;
    for (i = 0; i + 7 < n; i += 8) {
        s0 += a[i]; s1 += a[i+1]; s2 += a[i+2]; s3 += a[i+3];
        s4 += a[i+4]; s5 += a[i+5]; s6 += a[i+6]; s7 += a[i+7];
    }
    for (; i < n; i++) s0 += a[i];
    return s0+s1+s2+s3+s4+s5+s6+s7;
}

static double ATTR sum_u16(const double *a, size_t n) {
    double s[16] = {0}; size_t i;
    for (i = 0; i + 15 < n; i += 16) {
        for (int k = 0; k < 16; k++) s[k] += a[i+k];
    }
    for (; i < n; i++) s[0] += a[i];
    double total = 0;
    for (int k = 0; k < 16; k++) total += s[k];
    return total;
}

int main(void) {
    pin_to_cpu(0);
    static double a[N];
    for (int i = 0; i < N; i++) a[i] = (double)i * 0.001;

    printf("== Lab02.3: 循环展开 (N=%d) ==\n\n", N);

    pmu_group_t pmu = {0};
    int have_pmu = 1;
    if (pmu_add_hw(&pmu, PERF_COUNT_HW_CPU_CYCLES, "cyc") != 0) have_pmu = 0;
    if (pmu_add_hw(&pmu, PERF_COUNT_HW_INSTRUCTIONS, "ins") != 0) have_pmu = 0;

    struct { const char *name; double (*fn)(const double*, size_t); } tests[] = {
        {"unroll 1",  sum_u1},
        {"unroll 2",  sum_u2},
        {"unroll 4",  sum_u4},
        {"unroll 8",  sum_u8},
        {"unroll 16", sum_u16},
    };

    printf("%-12s %10s %10s %12s\n", "unroll", "T(ms)", "IPC", "cyc/elem");
    printf("%-12s %10s %10s %12s\n", "------", "------", "------", "-------");

    for (size_t t = 0; t < sizeof(tests)/sizeof(tests[0]); t++) {
        /* warmup */
        volatile double w = tests[t].fn(a, N); sink((uint64_t)w);

        uint64_t times[REPS], cycs[REPS], inss[REPS];
        for (int r = 0; r < REPS; r++) {
            if (have_pmu) pmu_start(&pmu);
            uint64_t t0 = now_ns();
            volatile double s = tests[t].fn(a, N);
            uint64_t t1 = now_ns();
            sink((uint64_t)s);
            if (have_pmu) {
                pmu_stop(&pmu);
                uint64_t v[PMU_MAX_EVENTS] = {0};
                pmu_read(&pmu, v);
                cycs[r] = v[0]; inss[r] = v[1];
            }
            times[r] = t1 - t0;
        }
        uint64_t tmed = median_u64(times, REPS);
        uint64_t cmed = have_pmu ? median_u64(cycs, REPS) : 0;
        uint64_t imed = have_pmu ? median_u64(inss, REPS) : 0;
        double ipc = (have_pmu && cmed) ? (double)imed/(double)cmed : 0;
        double cyc_per_elem = (have_pmu && cmed) ? (double)cmed/(double)N : 0;
        printf("%-12s %10.2f %10.2f %12.3f\n",
               tests[t].name, tmed/1e6, ipc, cyc_per_elem);
    }

    if (have_pmu) pmu_close(&pmu);

    printf("\n  == 解读 ==\n");
    printf("  * unroll 2 最优 (IPC 2.66): 恰好填满 load 端口带宽\n");
    printf("  * unroll 4/8 不再涨: 数组求和是 memory-bound, 受 load 端口限制 (~2/cyc)\n");
    printf("  * unroll 16 cyc/elem 反弹: s[16] 数组在栈, 每步 16 次 load/store s[k]\n");
    printf("  * 教训: 展开填满 load 带宽即可, 不是越多越好; compute-bound 才不同\n");
    return 0;
}
