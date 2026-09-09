/*
 * Lab00/src/null_loop.c — 空"什么都不做"循环的代价
 *
 * 学习目标：让你亲眼看到编译器如何"作弊"消除无副作用代码，
 *         以及 volatile 也未必能完全防住。
 *
 * 用法: ./null_loop [N]
 *   N = 循环次数，默认 1e8
 *
 * 测量：每次循环平均多少 cycles / 多少 ns
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <inttypes.h>
#include <string.h>

#include "bench.h"
#include "pmu.h"

#define REPS 21   /* 取 21 个样本的中位数 */

/* ----- 三个不同强度的"防 DCE"循环 ----- */

/* 版本 A：纯空循环（-O2 下会被消除） */
static uint64_t loop_empty(uint64_t N) {
    uint64_t dummy = 0;
    for (uint64_t i = 0; i < N; i++) {
        /* nothing */
        dummy += 0;  /* 防止编译器看到 i 没用 */
    }
    return dummy;
}

/* 版本 B：volatile sink 强制副作用 */
static volatile uint64_t g_sink;
static uint64_t loop_volatile(uint64_t N) {
    uint64_t acc = 0;
    for (uint64_t i = 0; i < N; i++) {
        g_sink = acc;
        acc += 1;
    }
    return acc;
}

/* 版本 C：内联 NOP（编译器无法消除） */
static uint64_t loop_nop(uint64_t N) {
    uint64_t acc = 0;
    for (uint64_t i = 0; i < N; i++) {
        __asm__ __volatile__("nop");
        acc += 1;
    }
    return acc;
}

/* 版本 D：内联 ADD（看纯 ALU 吞吐） */
static uint64_t loop_add(uint64_t N) {
    uint64_t acc = 0;
    for (uint64_t i = 0; i < N; i++) {
        __asm__ __volatile__("add %0, %0, #1" : "+r"(acc));
    }
    return acc;
}

/* ----- 测量函数 ----- */
typedef struct {
    const char *name;
    uint64_t   (*fn)(uint64_t);
} variant_t;

static void measure_variant(const variant_t *v, uint64_t N,
                            pmu_group_t *pmu) {
    uint64_t times[REPS];
    uint64_t cyc[REPS], insts[REPS];

    /* warmup */
    for (int i = 0; i < 3; i++) v->fn(N);

    for (int i = 0; i < REPS; i++) {
        if (pmu) pmu_start(pmu);
        uint64_t t0 = now_ns();
        uint64_t r = v->fn(N);
        uint64_t t1 = now_ns();
        if (pmu) pmu_stop(pmu);

        times[i] = t1 - t0;
        if (pmu) {
            uint64_t vals[PMU_MAX_EVENTS] = {0};
            pmu_read(pmu, vals);
            cyc[i]  = vals[0];
            insts[i] = vals[1];
        }
        sink(r);  /* 防止整段被 DCE */
    }

    uint64_t med_t  = median_u64(times, REPS);
    double   cyc_pL = pmu ? (double)median_u64(cyc, REPS)  / (double)N : 0;
    double   ns_pL  = (double)med_t / (double)N;
    double   ipc    = pmu ? (double)median_u64(insts, REPS) / (double)median_u64(cyc, REPS) : 0;

    printf("  %-25s  %9.2f ns/iter  %7.2f cyc/iter  IPC=%4.2f\n",
           v->name, ns_pL, cyc_pL, ipc);
}

int main(int argc, char **argv) {
    uint64_t N = (argc > 1) ? strtoull(argv[1], NULL, 0) : 100000000ULL;

    if (pin_to_cpu(0) != 0) {
        fprintf(stderr, "warn: pin_to_cpu(0) failed\n");
    }

    printf("== null_loop: N = %" PRIu64 " ==\n", N);
    printf("  (run `objdump -d ./null_loop | grep -A 50 <loop_xxx>` to verify the loop exists)\n\n");

    pmu_group_t pmu = {0};
    int have_pmu = 1;
    if (pmu_add_hw(&pmu, PERF_COUNT_HW_CPU_CYCLES, "cyc")  != 0) have_pmu = 0;
    if (pmu_add_hw(&pmu, PERF_COUNT_HW_INSTRUCTIONS, "inst") != 0) have_pmu = 0;

    variant_t vs[] = {
        { "loop_empty (-O2 DCE?)",  loop_empty   },
        { "loop_volatile",          loop_volatile },
        { "loop_nop",               loop_nop     },
        { "loop_add (inline asm)",  loop_add     },
    };

    printf("  %-25s  %18s  %15s  %8s\n",
           "variant", "per_iter", "per_iter", "");
    for (size_t i = 0; i < sizeof(vs)/sizeof(vs[0]); i++) {
        measure_variant(&vs[i], N, have_pmu ? &pmu : NULL);
    }

    printf("\n== 反汇编验证 ==\n");
    printf("  检查 loop_empty 是否被消除：\n");
    printf("    objdump -d %s | sed -n '/<loop_empty>:/,/ret/p'\n", argv[0]);
    printf("  检查 loop_volatile 的实际指令数：\n");
    printf("    objdump -d %s | sed -n '/<loop_volatile>:/,/ret/p'\n", argv[0]);

    if (have_pmu) pmu_close(&pmu);
    return 0;
}
