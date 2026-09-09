/*
 * Lab02/src/ooo_magic.c — 乱序执行的"魔法"
 *
 * 对比两种访存模式，展示乱序引擎如何隐藏 latency：
 *   1. parallel_loads: 4 个独立累加器，4 路并行 load → 乱序重叠 → IPC 高
 *   2. serial_chasing: 链表追逐，每次 load 依赖上一次指针 → 真依赖链 → IPC 极低
 *
 * ⚠ 设计修正（2026-07-02）：
 *   旧版 serial 用 4096 节点 L1-resident 顺序环，每步仅 L1 ~4cyc + 被 prefetcher
 *   预取，实测 IPC≈1.25，与"乱序极限"教学目的（预期 IPC~0.01）严重不符。
 *   现改为 >L3 的随机置换环（Fisher-Yates，防 prefetcher），每步真 DRAM miss
 *   (~130ns/~325cyc)，serial IPC 能降到 ~0.01，真正展示"信息论极限"。
 *   parallel 仍用顺序数组（L1 resident，展示乱序隐藏 latency）。
 *
 * 预期（飞腾 D3000M）：
 *   parallel: IPC ~2-4  (4 load 并行，乱序隐藏 L1 latency)
 *   serial:   IPC ~0.01 (每步等 DRAM ~130ns，信息论极限)
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include "bench.h"
#include "pmu.h"

#define N_PARALLEL 1000000
#define N_SERIAL   200000      /* DRAM miss ~130ns/步，20万步 ≈ 26ms，够测 */
#define N_NODES    (1<<20)     /* 1M 节点 × 16B = 16MB > L3(8MB)，每步真 DRAM miss */
#define REPS 11

typedef struct node { double val; struct node *next; } node_t;

/* Fisher-Yates 随机置换环：next[i] 形成随机排列的环，prefetcher 抓不到规律 */
static void build_random_ring(node_t *nodes, int n) {
    for (int i = 0; i < n; i++) { nodes[i].val = (double)i; nodes[i].next = &nodes[i]; }
    /* 洗牌：把 nodes[0..n-1] 顺序打成随机环 */
    int *idx = (int*)malloc(n * sizeof(int));
    for (int i = 0; i < n; i++) idx[i] = i;
    srand(42);
    for (int i = n - 1; i > 0; i--) {
        int j = rand() % (i + 1);
        int t = idx[i]; idx[i] = idx[j]; idx[j] = t;
    }
    for (int i = 0; i < n; i++) nodes[idx[i]].next = &nodes[idx[(i+1)%n]];
    free(idx);
}

/* 4 路独立 load，乱序可并行 */
static double __attribute__((noinline))
parallel_loads(const double *a, size_t n) {
    double s0=0,s1=0,s2=0,s3=0;
    for (size_t i = 0; i + 3 < n; i += 4) {
        s0 += a[i]; s1 += a[i+1]; s2 += a[i+2]; s3 += a[i+3];
    }
    return s0+s1+s2+s3;
}

/* 链表追逐，每次 p = p->next 依赖上一次 load → 串行（DRAM miss）*/
static double __attribute__((noinline))
serial_chasing(node_t *head, size_t n) {
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

    static double arr[N_PARALLEL];
    for (int i = 0; i < N_PARALLEL; i++) arr[i] = (double)i;

    node_t *nodes = (node_t*) aligned_alloc(64, N_NODES * sizeof(node_t));
    build_random_ring(nodes, N_NODES);   /* 随机置换环，>L3，防 prefetcher */

    printf("== Lab02.4: 乱序执行的魔法 ==\n\n");
    printf("  parallel: %d 元素, 4 路独立 load (L1 resident)\n", N_PARALLEL);
    printf("  serial:   %d 步追逐, %d 节点随机环 (%.0fMB > L3, 每步 DRAM miss)\n\n",
           N_SERIAL, N_NODES, (double)N_NODES*sizeof(node_t)/(1024*1024));

    pmu_group_t pmu = {0};
    int have_pmu = 1;
    if (pmu_add_hw(&pmu, PERF_COUNT_HW_CPU_CYCLES, "cyc") != 0) have_pmu = 0;
    if (pmu_add_hw(&pmu, PERF_COUNT_HW_INSTRUCTIONS, "ins") != 0) have_pmu = 0;
    if (pmu_add_hw(&pmu, PERF_COUNT_HW_CACHE_MISSES, "cmiss") != 0) have_pmu = 0;

    printf("%-22s %10s %10s %12s %12s\n", "mode", "T(ms)", "IPC", "cyc/op", "cmiss");
    printf("%-22s %10s %10s %12s %12s\n", "-----", "------", "------", "-------", "-------");

    /* parallel_loads */
    {
        volatile double w = parallel_loads(arr, N_PARALLEL); sink((uint64_t)w);
        uint64_t times[REPS], cycs[REPS], inss[REPS], cms[REPS];
        for (int r = 0; r < REPS; r++) {
            if (have_pmu) pmu_start(&pmu);
            uint64_t t0 = now_ns();
            volatile double s = parallel_loads(arr, N_PARALLEL);
            uint64_t t1 = now_ns();
            sink((uint64_t)s);
            if (have_pmu) {
                pmu_stop(&pmu);
                uint64_t v[PMU_MAX_EVENTS] = {0};
                pmu_read(&pmu, v);
                cycs[r] = v[0]; inss[r] = v[1];
                cms[r] = (pmu.n >= 3) ? v[2] : 0;
            }
            times[r] = t1 - t0;
        }
        uint64_t tmed = median_u64(times, REPS);
        uint64_t cmed = have_pmu ? median_u64(cycs, REPS) : 0;
        uint64_t imed = have_pmu ? median_u64(inss, REPS) : 0;
        uint64_t cmmed = have_pmu ? median_u64(cms, REPS) : 0;
        double ipc = (have_pmu && cmed) ? (double)imed/(double)cmed : 0;
        printf("%-22s %10.2f %10.2f %12.2f %12llu\n",
               "parallel (4 indep)", tmed/1e6, ipc,
               (have_pmu && cmed) ? (double)cmed/N_PARALLEL : 0,
               (unsigned long long)cmmed);
    }

    /* serial_chasing */
    {
        volatile double w = serial_chasing(nodes, N_SERIAL); sink((uint64_t)w);
        uint64_t times[REPS], cycs[REPS], inss[REPS], cms[REPS];
        for (int r = 0; r < REPS; r++) {
            if (have_pmu) pmu_start(&pmu);
            uint64_t t0 = now_ns();
            volatile double s = serial_chasing(nodes, N_SERIAL);
            uint64_t t1 = now_ns();
            sink((uint64_t)s);
            if (have_pmu) {
                pmu_stop(&pmu);
                uint64_t v[PMU_MAX_EVENTS] = {0};
                pmu_read(&pmu, v);
                cycs[r] = v[0]; inss[r] = v[1];
                cms[r] = (pmu.n >= 3) ? v[2] : 0;
            }
            times[r] = t1 - t0;
        }
        uint64_t tmed = median_u64(times, REPS);
        uint64_t cmed = have_pmu ? median_u64(cycs, REPS) : 0;
        uint64_t imed = have_pmu ? median_u64(inss, REPS) : 0;
        uint64_t cmmed = have_pmu ? median_u64(cms, REPS) : 0;
        double ipc = (have_pmu && cmed) ? (double)imed/(double)cmed : 0;
        printf("%-22s %10.2f %10.2f %12.2f %12llu\n",
               "serial (chasing)", tmed/1e6, ipc,
               (have_pmu && cmed) ? (double)cmed/N_SERIAL : 0,
               (unsigned long long)cmmed);
    }

    if (have_pmu) pmu_close(&pmu);
    free(nodes);

    printf("\n  == 解读 ==\n");
    printf("  * parallel IPC 高: 4 个独立 load，乱序引擎并行发射，隐藏 L1 latency\n");
    printf("  * serial IPC 极低: p=p->next 是真依赖链，每步必须等上一次 load 完成\n");
    printf("  * 这就是'信息论极限': 真依赖链无法并行，硬件再强也没用\n");
    printf("  * 优化启示: 把 chasing 改成多个独立 chasing (N 链并行) 可恢复 ILP\n");
    printf("    (这正是 Lab04 rob_size 实验的原理)\n");
    printf("  * cmiss: serial 每步应 ~1 次 DRAM miss（环 16MB > L3）；parallel 应很低\n");
    return 0;
}
