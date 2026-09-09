/*
 * Lab04/src/rob_size.c — 反推 ROB / LDQ 容量
 *
 * 方法：N 条独立的 pointer-chasing 链，每条链内部串行 miss 到 DRAM，
 *       N 条链之间相互独立 → 可并行"在飞"。
 *       - N ≤ window (= min(ROB, LDQ))：N 条链并行飞，每步总延迟 ≈ 1 次 DRAM miss
 *       - N > window：window 满，前端 stall，每步延迟线性增长
 *       拐点 N* ≈ min(ROB, LDQ)
 *
 * ⚠ 关键设计修正（v2，相对初版）：
 *   初版用固定 stride=2KB 的规则环（arr[x]=(x+STRIDE)%ARR），飞腾实测发现：
 *   L2/L3 prefetcher 能识别这种"大步长顺序"模式，提前预取，导致 N≤32 时
 *   miss/step≈0（load 没真 miss），拐点失真（测的是 prefetcher 容量，非 ROB）。
 *   v2 用 Fisher-Yates 随机置换环：每个节点的下一个地址随机，prefetcher 无法
 *   预测，每步真 miss。N 条链从环上等距点出发，step k 时访问 N 个随机地址。
 *
 * 重要陷阱（README 修正点）：load 类实验的窗口上限 = min(ROB, LDQ)，
 *       通常 LDQ 比 ROB 小。所以本实验测得的是 LDQ 上界，是 ROB 的下界。
 *
 * 参考：Henry Wong et al., "Measuring the ROB Capacity of Modern Processors"
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include "bench.h"
#include "pmu.h"

#define ARR_NODES    (4*1024*1024)     /* 4M nodes × 4B = 16 MB > L3 */
#define MAX_CHAINS   128
#define N_STEPS      2000
#define REPS         11

static uint32_t *g_arr  = NULL;        /* 16 MB chasing 数组 */
static uint32_t *g_perm = NULL;        /* 随机置换表（决定链起点 + 环结构）*/

/* 构造随机置换环：
 *   1. Fisher-Yates 洗牌得 perm[]
 *   2. arr[perm[i]] = perm[(i+1) % ARR_NODES]
 * 从 perm[0] 出发：perm[0]→perm[1]→...→perm[N-1]→perm[0]，地址随机跳
 * prefetcher 无法预测 → 每步真 miss
 */
static void build_random_ring(void) {
    g_perm = (uint32_t*) malloc((size_t)ARR_NODES * sizeof(uint32_t));
    if (!g_perm) { perror("malloc perm"); exit(1); }
    for (uint32_t i = 0; i < ARR_NODES; i++) g_perm[i] = i;
    srand(42);   /* 固定种子，可复现 */
    for (uint32_t i = ARR_NODES - 1; i > 0; i--) {
        uint32_t j = (uint32_t)rand() % (i + 1);
        uint32_t t = g_perm[i]; g_perm[i] = g_perm[j]; g_perm[j] = t;
    }
    for (uint32_t i = 0; i < ARR_NODES; i++) {
        g_arr[g_perm[i]] = g_perm[(i + 1) % ARR_NODES];
    }
}

/* N 条独立并行追逐链。
 * 链 i 起点 = perm[i × (ARR/N)]（环上等距分布）；
 * 每步 idx[i] = arr[idx[i]]，沿环前进 1。
 * N 条链在环上等距 → step k 时访问环上连续 N 个点 → N 个随机地址（都 miss，互不冲突）。
 * 内层 i 循环的 N 个 load 互不相关 → 硬件可并行发射。
 */
static uint64_t __attribute__((noinline,optimize("no-fast-math")))
chase_n(uint32_t *idx, int n_chains) {
    uint64_t s = 0;
    for (int step = 0; step < N_STEPS; step++) {
        for (int i = 0; i < n_chains; i++) {
            idx[i] = g_arr[idx[i]];
            s += idx[i];
        }
    }
    return s;
}

static void stats_u64(uint64_t *arr, size_t n,
                      uint64_t *pmin, uint64_t *pmed, uint64_t *p90) {
    if (n == 0) { if(pmin)*pmin=0; if(pmed)*pmed=0; if(p90)*p90=0; return; }
    uint64_t tmp[1024];
    size_t m = n < 1024 ? n : 1024;
    memcpy(tmp, arr, m * sizeof(uint64_t));
    for (size_t i = 1; i < m; i++) {
        uint64_t k = tmp[i]; size_t j = i;
        while (j > 0 && tmp[j-1] > k) { tmp[j] = tmp[j-1]; j--; }
        tmp[j] = k;
    }
    if (pmin) *pmin = tmp[0];
    if (pmed) *pmed = tmp[m/2];
    if (p90)  *p90  = tmp[(size_t)(m * 0.9)];
}

int main(void) {
    pin_to_cpu(0);

    g_arr = (uint32_t*) aligned_alloc(64, (size_t)ARR_NODES * sizeof(uint32_t));
    if (!g_arr) { perror("aligned_alloc"); return 1; }
    build_random_ring();

    /* warmup：建 page table，触发首次 DRAM 访问，填充分支预测器 */
    uint32_t widx[8];
    for (int i = 0; i < 8; i++) widx[i] = g_perm[(uint64_t)i * ARR_NODES / 8];
    volatile uint64_t w = chase_n(widx, 8);
    sink((uint64_t)w);

    pmu_group_t pmu = {0};
    int have_pmu = 1;
    if (pmu_add_hw(&pmu, PERF_COUNT_HW_CPU_CYCLES,   "cyc")   != 0) have_pmu = 0;
    if (pmu_add_hw(&pmu, PERF_COUNT_HW_INSTRUCTIONS, "ins")   != 0) have_pmu = 0;
    if (pmu_add_hw(&pmu, PERF_COUNT_HW_CACHE_MISSES, "cmiss") != 0) have_pmu = 0;
    if (pmu_add_raw(&pmu, FTC_STALL_BACKEND,         "be_stall") != 0) { /* 容错 */ }

    printf("== Lab04.2: ROB / LDQ 容量反推 (v2, 随机置换环) ==\n\n");
    printf("  数组 %.1f MB (> L3 8MB), 随机置换环 (Fisher-Yates, seed=42), 每链 %d 步\n",
           (double)ARR_NODES*4/(1024*1024), N_STEPS);
    printf("  v1 固定 stride 被 prefetcher 预取，miss/step≈0；v2 随机环每步真 miss。\n");
    printf("  拐点 N* = min(ROB, LDQ)。LDQ 通常更小 → 此为 ROB 下界。\n\n");

    printf("%-9s %9s %9s %9s %11s %11s %9s\n",
           "n_chains", "T_med(ms)", "T_min(ms)", "T_p90(ms)",
           "cycles", "cmiss", "miss/step");
    printf("%-9s %9s %9s %9s %11s %11s %9s\n",
           "-------", "---------", "---------", "---------",
           "-----------", "-----------", "-------");

    int ns[] = {1,2,4,8,12,16,24,32,40,48,56,64,80,96,128};
    uint32_t idx[MAX_CHAINS];
    double prev_per_step = 0;
    int detected_knee = -1;

    for (size_t k = 0; k < sizeof(ns)/sizeof(ns[0]); k++) {
        int n = ns[k];
        uint64_t ts[REPS], cs[REPS], ms[REPS];
        for (int r = 0; r < REPS; r++) {
            for (int i = 0; i < n; i++)
                idx[i] = g_perm[(uint64_t)i * ARR_NODES / (uint32_t)n];
            if (have_pmu) pmu_start(&pmu);
            uint64_t t0 = now_ns();
            uint64_t s = chase_n(idx, n);
            uint64_t t1 = now_ns();
            sink((uint64_t)s);
            if (have_pmu) {
                pmu_stop(&pmu);
                uint64_t vs[PMU_MAX_EVENTS] = {0};
                pmu_read(&pmu, vs);
                cs[r] = vs[0];
                ms[r] = (pmu.n >= 3) ? vs[2] : 0;
            }
            ts[r] = t1 - t0;
        }
        uint64_t tmin, tmed, t90, cmed, cmmed;
        stats_u64(ts, REPS, &tmin, &tmed, &t90);
        stats_u64(cs, REPS, NULL, &cmed, NULL);
        stats_u64(ms, REPS, NULL, &cmmed, NULL);
        double per_step_ns = (double)tmed / (double)N_STEPS;
        double miss_per_step = (double)cmmed / (double)(N_STEPS * n);
        printf("%-9d %9.2f %9.2f %9.2f %11llu %11llu %9.2f\n",
               n, tmed/1e6, tmin/1e6, t90/1e6,
               (unsigned long long)cmed,
               (unsigned long long)cmmed,
               miss_per_step);

        /* 拐点判定：per_step 显著跳升 AND miss/step 真的高（确认真 miss）*/
        if (prev_per_step > 0 && per_step_ns > prev_per_step * 1.6
            && miss_per_step > 0.6 && detected_knee < 0) {
            detected_knee = n;
            printf("   ↑ per_step %.0f→%.0f ns + miss/step=%.2f：窗口上限在 N≈%d\n",
                   prev_per_step, per_step_ns, miss_per_step, n);
        }
        prev_per_step = per_step_ns;
    }

    if (have_pmu) pmu_close(&pmu);
    free(g_arr);
    free(g_perm);

    printf("\n  == 解读 ==\n");
    printf("  * miss/step 应 ≈ 1.0（每步每链 1 次 DRAM miss）。v1 因 prefetcher 此值≈0。\n");
    printf("  * N ≤ window: N 个 miss 并行飞，per_step ≈ 1 次 DRAM 延迟（平稳）\n");
    printf("  * N > window: ROB/LDQ 满，前端 stall，per_step 线性上涨\n");
    printf("  * 拐点 N* ≈ window = min(ROB, LDQ)\n");
    if (detected_knee > 0) {
        printf("  * 检测到拐点 N* ≈ %d\n", detected_knee);
        printf("    → load 窗口 ≈ %d，即 min(ROB, LDQ) ≈ %d\n",
               detected_knee, detected_knee);
    } else {
        printf("  * 未检测到明显拐点：可能 window > %d（最大测试 N），或 prefetcher 残留干扰。\n",
               ns[sizeof(ns)/sizeof(ns[0]) - 1]);
    }
    printf("  * 关键陷阱：load 类实验撞的是 LDQ (32-64)，不是 ROB (128-224)\n");
    printf("    要测纯 ROB 上界，需对照 rename_capacity 的 ALU 链（不占 LSQ）。\n");
    printf("  * 对照：Skylake ROB=224/LDQ=72；M1 ROB~600/LDQ~340；Alpha 21264 用 PRF=72。\n");
    return 0;
}
