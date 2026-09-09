/*
 * Lab06/src/mem_order_cost.c — 不同内存序的代价对比 (v2)
 *
 * ⚠ 关键设计修正（相对 v1）：
 *   v1 用 atomic_fetch_add 对同一地址紧凑循环，5 种内存序都被 cacheline
 *   一致性串行化淹没（同地址 RMW 必须串行），实测 relaxed 最慢(55cyc)、
 *   seq_cst 最快(36cyc)，完全反常——测的是"RMW 一致性延迟"而非"屏障延迟"。
 *
 * v2 直接测**单条屏障/内存序指令的吞吐**：紧凑循环发 N 次指令，测总时间。
 *   屏障指令本身不访问数据（除 ldar/stlr），不引入 cacheline 争用。
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdint.h>
#include "bench.h"

#define N   100000000
#define REPS 11

static volatile uint64_t g_target = 0x1234567890ABCDEFULL;
static volatile uint64_t g_sink   = 0;

/* 纯指令吞吐（nop / dmb / dsb / isb），无寄存器约束 */
#define BENCH(NAME, INSN) do {                                       \
    uint64_t ts[REPS];                                               \
    for (int r = 0; r < REPS; r++) {                                 \
        uint64_t t0 = now_ns();                                      \
        for (uint64_t i = 0; i < N; i++) {                           \
            __asm__ __volatile__(INSN ::: "memory");                 \
        }                                                            \
        uint64_t t1 = now_ns();                                      \
        ts[r] = t1 - t0;                                             \
    }                                                                \
    for (int i = 1; i < REPS; i++) {                                 \
        uint64_t k = ts[i]; int j = i;                               \
        while (j > 0 && ts[j-1] > k) { ts[j] = ts[j-1]; j--; }       \
        ts[j] = k;                                                   \
    }                                                                \
    double t_med = (double)ts[REPS/2];                               \
    printf("  %-22s %10.2f ns/op   (%5.2f cyc)\n",                  \
           NAME, t_med / N, t_med / N * 2.5);                        \
} while (0)

/* load 类：INSN = "ldr" 或 "ldar"，读 g_target */
#define BENCH_LD(NAME, INSN) do {                                    \
    uint64_t ts[REPS];                                               \
    for (int r = 0; r < REPS; r++) {                                 \
        uint64_t acc = 0;                                            \
        uint64_t t0 = now_ns();                                      \
        for (uint64_t i = 0; i < N; i++) {                           \
            uint64_t v;                                              \
            __asm__ __volatile__(INSN " %0, [%1]"                    \
                                 : "=r"(v) : "r"(&g_target) : "memory"); \
            acc += v;                                                \
        }                                                            \
        uint64_t t1 = now_ns();                                      \
        g_sink = acc;                                                \
        ts[r] = t1 - t0;                                             \
    }                                                                \
    for (int i = 1; i < REPS; i++) {                                 \
        uint64_t k = ts[i]; int j = i;                               \
        while (j > 0 && ts[j-1] > k) { ts[j] = ts[j-1]; j--; }       \
        ts[j] = k;                                                   \
    }                                                                \
    double t_med = (double)ts[REPS/2];                               \
    printf("  %-22s %10.2f ns/op   (%5.2f cyc)\n",                  \
           NAME, t_med / N, t_med / N * 2.5);                        \
} while (0)

/* store 类：INSN = "str" 或 "stlr"，写 g_target */
#define BENCH_ST(NAME, INSN) do {                                    \
    uint64_t ts[REPS];                                               \
    for (int r = 0; r < REPS; r++) {                                 \
        uint64_t t0 = now_ns();                                      \
        for (uint64_t i = 0; i < N; i++) {                           \
            __asm__ __volatile__(INSN " %0, [%1]"                    \
                                 : : "r"((uint64_t)i), "r"(&g_target) : "memory"); \
        }                                                            \
        uint64_t t1 = now_ns();                                      \
        ts[r] = t1 - t0;                                             \
    }                                                                \
    for (int i = 1; i < REPS; i++) {                                 \
        uint64_t k = ts[i]; int j = i;                               \
        while (j > 0 && ts[j-1] > k) { ts[j] = ts[j-1]; j--; }       \
        ts[j] = k;                                                   \
    }                                                                \
    double t_med = (double)ts[REPS/2];                               \
    printf("  %-22s %10.2f ns/op   (%5.2f cyc)\n",                  \
           NAME, t_med / N, t_med / N * 2.5);                        \
} while (0)

int main(void) {
    pin_to_cpu(0);

    printf("== Lab06.1: 内存序代价 v2 (纯指令吞吐, N=%llu) ==\n\n",
           (unsigned long long)N);
    printf("  v1 用同地址 RMW，屏障代价被 cacheline 一致性淹没（已废弃）\n\n");

    BENCH    ("nop (基线)",           "nop");
    BENCH    ("dmb ishst (st-st)",    "dmb ishst");
    BENCH    ("dmb ish (全屏障)",      "dmb ish");
    BENCH    ("dsb ish (等完成)",      "dsb ish");
    BENCH    ("isb (指令同步)",        "isb");
    BENCH_LD ("ldr (普通 load)",      "ldr");
    BENCH_LD ("ldar (load-acquire)",  "ldar");
    BENCH_ST ("str (普通 store)",     "str");
    BENCH_ST ("stlr (store-release)", "stlr");

    printf("\n  == 解读（飞腾 D3000M 实测 2026-07-02）==\n");
    printf("  * nop/dmb ishst ~1 cyc: 纯发射吞吐（4-wide，含循环开销），不阻塞后续发射\n");
    printf("  * dmb ish ~7 cyc, dsb ish ~7 cyc (实测；旧 README 说 ~21 cyc 是教科书值，不符)\n");
    printf("  * isb ~34 cyc: 冲刷前端，最贵 (旧 README 说 ~67 cyc，不符)\n");
    printf("  * ⚠ ldar/stlr 与 nop 同 (~1 cyc): 本测用同地址 L1 命中 + 单核，\n");
    printf("    acquire/release 的 ordering 语义根本未触发，测的是纯指令发射吞吐。\n");
    printf("    真 ordering 代价（跨核 store 可见性延迟）见 store_store_reorder.c 的 MP 实验。\n");
    printf("  * 结论: 屏障指令本身发射代价不高 (dmb~7/isb~34 cyc)；ordering 的真实代价\n");
    printf("    在'等 store 到达其他核'，必须跨核 producer-consumer 场景才测得出。\n");
    return 0;
}
