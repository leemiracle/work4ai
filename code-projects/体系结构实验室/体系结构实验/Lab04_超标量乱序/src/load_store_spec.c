/*
 * Lab04/src/load_store_spec.c — Memory Disambiguation 探测
 *
 * 4 种紧凑循环模式，对比 CPI，揭示乱序引擎对 store/load 的推测能力。
 *
 * ⚠ 关键设计修正（v2，相对初版）：
 *   初版用普通 C 的 `*p = v; x = *p`，编译器会：
 *     - 常量传播消除同址 load（A 模式 store 后 load 同址，编译器知道值就是 store 的值）
 *     - 别名分析重排异址 load/store
 *   导致 A/B CPI 几乎相同，实验失去区分力（飞腾实测初版 A/B CPI 均为 0.37）。
 *   v2 用内联汇编 fld()/fst() 强制 volatile 访问，编译器不能消除/传播/重排，
 *   硬件 disambiguator 行为才真显现。
 *
 *   A. 同址依赖：  store→load 同地址且 load 结果被用（依赖链），等 forwarding
 *   B. 异址独立：  store→load 不同地址（地址都早定），load 推测并行
 *   C. 地址依赖：  store 地址慢定（mul 链），load 地址早定且实际不冲突；
 *                  保守 disambiguator 阻塞 load，激进的放行推测
 *   D. 推测误判：  每 16 次让 load 与 store alias，迫使推测失败 → 冲刷
 *
 * 解读矩阵：
 *   CPI(A) > CPI(B)   → store-forwarding 真实代价
 *   CPI(C) ≈ CPI(A)   → 飞腾保守（地址未定阻塞 load）
 *   CPI(C) ≈ CPI(B)   → 飞腾激进推测
 *   CPI(D) - CPI(B)   → 推测失败单次惩罚 ×16
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include "bench.h"
#include "pmu.h"

#define N_ITER   4000000
#define REPS     11
#define MASK     1023             /* 4 KB 范围，L1 内 */
#define B_OFFSET 1536             /* load 固定源，与 store 区 [0..1023] 不相交 */

static uint32_t g_buf[2048] __attribute__((aligned(64)));
static volatile uint32_t g_poison = 0x9E3779B9u;
static volatile uint64_t g_sink = 0;

/* === 强制 volatile load/store：阻止编译器常量传播/消除/重排 === */
static inline uint32_t fld(const volatile uint32_t *p) {
    uint32_t v;
    __asm__ __volatile__("ldr %w0, [%1]" : "=r"(v) : "r"(p) : "memory");
    return v;
}
static inline void fst(volatile uint32_t *p, uint32_t v) {
    __asm__ __volatile__("str %w0, [%1]" : : "r"(v), "r"(p) : "memory");
}

/* ---------- 模式 A：store→load 同址依赖链 ---------- */
/* store 后 load 同址，load 结果推进 k → 形成真依赖链，
 * 每轮 load 必须等 store buffer forwarding（~3-5 cyc）。 */
static uint64_t __attribute__((noinline))
mode_a_load_after_store_same(void) {
    uint32_t k = 0;
    uint64_t s = 0;
    for (uint32_t i = 1; i <= N_ITER; i++) {
        fst(&g_buf[k], i);
        uint32_t x = fld(&g_buf[k]);   /* 等 forwarding */
        k = x & MASK;                  /* 依赖 x，强依赖链 */
        s += x;
    }
    return s;
}

/* ---------- 模式 B：store→load 异址独立 ---------- */
/* store 落 [0..1023]，load 固定从 1536 读，地址都早定且不冲突。
 * disambiguator 一眼判断安全 → load 推测与 store 并行。 */
static uint64_t __attribute__((noinline))
mode_b_load_indep_store(void) {
    uint64_t s = 0;
    for (uint32_t i = 1; i <= N_ITER; i++) {
        fst(&g_buf[i & MASK], i);
        uint32_t x = fld(&g_buf[B_OFFSET]);  /* 固定异址 */
        s += x;
    }
    return s;
}

/* ---------- 模式 C：store 地址慢定，load 地址早定 ---------- */
/* store 地址经 4 步 mul 链算出（~12 cyc 才定），load 地址固定且绝不冲突。
 * 保守 disambiguator：load 必须等 store 地址定 → 阻塞
 * 激进 disambiguator：直接放行 load（赌不冲突）→ 推测成功 */
static uint64_t __attribute__((noinline))
mode_c_store_addr_slow(void) {
    uint64_t s = 0;
    for (uint32_t i = 1; i <= N_ITER; i++) {
        uint32_t a = i ^ g_poison;
        a = a * 2654435761u + 1;
        a = a * 2654435761u + 2;
        a = a * 2654435761u + 3;
        a = a * 2654435761u + 4;
        a &= MASK;                     /* store 落 [0..1023] */
        fst(&g_buf[a], i);             /* store，地址刚算出 */
        uint32_t x = fld(&g_buf[B_OFFSET]);  /* load 地址早定，与 store 实际不冲突 */
        s += x;
    }
    return s;
}

/* ---------- 模式 D：推测误判（每 16 次 alias 1 次）---------- */
static uint64_t __attribute__((noinline))
mode_d_mispredict_alias(void) {
    uint64_t s = 0;
    for (uint32_t i = 1; i <= N_ITER; i++) {
        uint32_t store_addr = i & MASK;
        fst(&g_buf[store_addr], i);
        /* 每 16 次让 load 指向 store 地址，迫使推测失败 */
        uint32_t load_addr = ((i & 15) == 0) ? store_addr : B_OFFSET;
        uint32_t x = fld(&g_buf[load_addr]);
        s += x;
    }
    return s;
}

/* ---------- 通用测量 ---------- */
static void measure(const char *name, uint64_t (*fn)(void),
                    pmu_group_t *pmu, int have_pmu) {
    uint64_t ts[REPS], cs[REPS], is[REPS];
    g_sink = fn();   /* warmup */
    for (int r = 0; r < REPS; r++) {
        if (have_pmu) pmu_start(pmu);
        uint64_t t0 = now_ns();
        uint64_t s = fn();
        uint64_t t1 = now_ns();
        g_sink = s;
        if (have_pmu) {
            pmu_stop(pmu);
            uint64_t vs[PMU_MAX_EVENTS] = {0};
            pmu_read(pmu, vs);
            cs[r] = vs[0]; is[r] = vs[1];
        }
        ts[r] = t1 - t0;
    }
    uint64_t tmed = median_u64(ts, REPS);
    uint64_t cmed = have_pmu ? median_u64(cs, REPS) : 0;
    uint64_t imed = have_pmu ? median_u64(is, REPS) : 0;
    double ipc = (have_pmu && cmed) ? (double)imed / (double)cmed : 0;
    double cpi = (have_pmu && imed) ? (double)cmed / (double)imed : 0;
    double ns_per_iter = (double)tmed / (double)N_ITER;
    printf("%-34s %9.2f %11llu %11llu %7.3f %7.3f\n",
           name, ns_per_iter * 1000,
           (unsigned long long)cmed,
           (unsigned long long)imed, ipc, cpi);
}

int main(void) {
    pin_to_cpu(0);
    for (int i = 0; i < 2048; i++) g_buf[i] = (uint32_t)i;

    pmu_group_t pmu = {0};
    int have_pmu = 1;
    if (pmu_add_hw(&pmu, PERF_COUNT_HW_CPU_CYCLES,   "cyc") != 0) have_pmu = 0;
    if (pmu_add_hw(&pmu, PERF_COUNT_HW_INSTRUCTIONS, "ins") != 0) have_pmu = 0;

    printf("== Lab04.3: Memory Disambiguation (v2, asm-forced) ==\n\n");
    printf("  N_ITER = %d, buf 8KB (L1-resident), 内联汇编强制 volatile 访问\n\n",
           N_ITER);
    printf("%-34s %9s %11s %11s %7s %7s\n",
           "mode", "ns/iter", "cycles", "insts", "IPC", "CPI");
    printf("%-34s %9s %11s %11s %7s %7s\n",
           "-----", "-------", "-----------", "-----------",
           "-------", "-------");

    measure("A load_after_store (same addr)",   mode_a_load_after_store_same, &pmu, have_pmu);
    measure("B load_indep     (different addr)", mode_b_load_indep_store,      &pmu, have_pmu);
    measure("C store_addr_slow(load waits?)",   mode_c_store_addr_slow,       &pmu, have_pmu);
    measure("D mispredict     (1/16 alias)",    mode_d_mispredict_alias,      &pmu, have_pmu);

    if (have_pmu) pmu_close(&pmu);

    printf("\n  == 解读 ==\n");
    printf("  * A 应 CPI 最高：每轮 load 等 store buffer forwarding (~3-5 cyc)\n");
    printf("  * B 应 CPI 最低：load 与 store 异址，硬件推测并行发射\n");
    printf("  * C 若 CPI ≈ A → 飞腾 disambiguator 保守（地址未定就阻塞 load）\n");
    printf("      若 CPI ≈ B → 飞腾激进推测（赌 load 与未定址 store 不冲突）\n");
    printf("  * D CPI 介于 A/B 之间；推测失败率 1/16，惩罚 ≈ (CPI_D - CPI_B) × 16\n");
    printf("  * v1 用普通 C，编译器常量传播消除同址 load，A/B CPI 相同（0.37），实验失效。\n");
    printf("    v2 用 fld/fst 内联汇编强制访问，差异才真显现。\n");
    return 0;
}
