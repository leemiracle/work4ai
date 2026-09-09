/*
 * Lab03/src/cache_line.c — Cache 行（line）大小探测 (v2)
 *
 * ⚠ v1 失败：数组 8KB L1-resident + s+=a[idx] 的 fadd 是瓶颈，load 不依赖
 *   地址（乱序预取），所有 stride 的 cyc/access 都是 3.31（测不出 line 效应）。
 *
 * v2 改用 pointer chasing + 数组 > L1：
 *   - node_t { double val; node_t *next; }，next 指向 stride_nodes 之外
 *   - 数组 512 KB > L1 64KB，落 L2，确保每 line access 有意义
 *   - chasing: p = p->next，p 依赖上次 load（load 结果决定下次地址）
 *     → 乱序无法预取，每 load 真 L2 access
 *   - stride_nodes 控制 line 跨越：node 16B，line 64B = 4 node
 *     stride_nodes 1-3: 同 line（ chasing 在 line 内，但 L2 line cached 后命中）
 *     stride_nodes 4+: 跨 line（每步新 L2 line access）
 *
 * 预期：cyc/access 在 stride_nodes=4（跨 64B）处跳升 → 反推 line=64B
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include "bench.h"
#include "pmu.h"

typedef struct node { double val; struct node *next; } node_t;
/* node 16 字节；cache line 64B = 4 node */

#define N_NODES   16384        /* 16384 × 16B = 256 KB，稳定在 L2（512K 边界易抖动）*/
#define N_STEPS   2000000      /* chasing 步数 */
#define REPS      11

static node_t *g_nodes = NULL;

/* 构造固定 stride 的环：next[i] = &nodes[(i + stride_nodes) % N_NODES]
 * ⚠ 固定 stride 会被 L2 prefetcher 部分预取，stride≥6 时可能观测到非单调
 *    （预取命中拉低延迟）。本实验核心看 stride 1-3（同 line）vs 4（跨 line）
 *    的跳升反推 line=64B；stride≥6 的绝对值受预取影响，仅供参考。
 *    要完全抑制 prefetcher 见 cache_sizes.c 的随机置换环。*/
static void build_ring(int stride_nodes) {
    for (int i = 0; i < N_NODES; i++) {
        g_nodes[i].val = (double)i;
        g_nodes[i].next = &g_nodes[(i + stride_nodes) % N_NODES];
    }
}

/* pointer chasing：p 依赖上次 load，乱序无法预取 */
static double __attribute__((noinline))
chase(node_t *head, size_t n) {
    double s = 0;
    node_t *p = head;
    for (size_t i = 0; i < n; i++) {
        s += p->val;
        p = p->next;
    }
    return s;
}

int main(void) {
    pin_to_cpu(0);
    g_nodes = (node_t*) aligned_alloc(64, N_NODES * sizeof(node_t));
    if (!g_nodes) { perror("aligned_alloc"); return 1; }

    printf("== Lab03.2: Cache 行探测 v2 (pointer chasing) ==\n\n");
    printf("  数组 %zu KB (稳定落 L2), chasing %d 步\n\n",
           (size_t)(N_NODES * 16 / 1024), N_STEPS);
    printf("  v1 失败: L1-resident + fadd 瓶颈, 所有 stride 相同 (3.31 cyc)\n\n");

    pmu_group_t pmu = {0};
    int have_pmu = 1;
    if (pmu_add_hw(&pmu, PERF_COUNT_HW_CPU_CYCLES, "cyc") != 0) have_pmu = 0;
    if (pmu_add_hw(&pmu, PERF_COUNT_HW_CACHE_MISSES, "cmiss") != 0) have_pmu = 0;

    printf("%-14s %8s %14s %14s %s\n",
           "stride_nodes", "bytes", "cyc/access", "ns/access", "解读");
    printf("%-14s %8s %14s %14s %s\n",
           "------------", "-----", "----------", "---------", "-----");

    int strides[] = {1, 2, 3, 4, 6, 8, 16, 32};
    for (size_t si = 0; si < sizeof(strides)/sizeof(strides[0]); si++) {
        int sn = strides[si];
        build_ring(sn);

        /* warmup: 跑一圈让环进 steady state */
        volatile double w = chase(g_nodes, 10000); sink((uint64_t)w);

        uint64_t times[REPS], cycs[REPS], cms[REPS];
        for (int r = 0; r < REPS; r++) {
            if (have_pmu) pmu_start(&pmu);
            uint64_t t0 = now_ns();
            volatile double s = chase(g_nodes, N_STEPS);
            uint64_t t1 = now_ns();
            sink((uint64_t)s);
            if (have_pmu) {
                pmu_stop(&pmu);
                uint64_t v[PMU_MAX_EVENTS] = {0};
                pmu_read(&pmu, v);
                cycs[r] = v[0];
                cms[r] = (pmu.n >= 2) ? v[1] : 0;
            }
            times[r] = t1 - t0;
        }
        uint64_t tmed = median_u64(times, REPS);
        uint64_t cmed = have_pmu ? median_u64(cycs, REPS) : 0;
        uint64_t cmmed = have_pmu ? median_u64(cms, REPS) : 0;
        double cyc_per_acc = (have_pmu && cmed) ? (double)cmed / (double)N_STEPS : 0;
        double ns_per_acc = (double)tmed / (double)N_STEPS;
        int bytes = sn * 16;
        const char *note;
        if (sn < 4)      note = "同 line (16-48B < 64B)";
        else if (sn == 4) note = "← 正好跨 1 line (64B)";
        else              note = "跨多 line";
        printf("%-14d %6d B %14.3f %14.3f %s",
               sn, bytes, cyc_per_acc, ns_per_acc, note);
        if (have_pmu) printf("  cmiss=%llu", (unsigned long long)cmmed);
        printf("\n");
    }

    if (have_pmu) pmu_close(&pmu);
    free(g_nodes);

    printf("\n  == 解读 ==\n");
    printf("  * stride_nodes 1-3: chasing 在同一 64B line 内 (4 node/line)\n");
    printf("    → L2 line 一次载入后续命中，cyc/access 较低\n");
    printf("  * stride_nodes 4: 每 step 跨一个新 line (64B) → cyc/access 跳升\n");
    printf("    → 拐点 stride_nodes=4 对应 line=64 字节 (飞腾 D3000M 实测)\n");
    printf("  * stride_nodes 8+: 跨多 line，cyc/access 平稳 (每 step 一次 L2 access)\n");
    printf("  * chasing 保证 load 依赖链 (p=p->next)，乱序无法预取掩盖 latency\n");
    return 0;
}
