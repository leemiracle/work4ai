/*
 * Lab03/src/false_sharing.c — False Sharing 实测（多核 cache 一致性代价）
 *
 * 现象：两个线程各自更新"自己的"计数器，但如果两个变量在同一 cache line，
 * 每次写都触发跨核 cache line 失效/迁移（MESI 协议），性能暴跌 10-50×。
 * 用 alignas(64) 把变量隔到不同 line 即可消除。
 *
 * 这是多线程性能优化最经典、最隐蔽的陷阱：
 *   - 单线程看完全正确
 *   - 多线程不崩溃、结果对
 *   - 但慢得离谱，且 profiler 里看不出（只显示 cache miss 高）
 *
 * 飞腾 D3000M: L1D 64B line, 2 核以上有 MESI 一致性。
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdint.h>
#include <pthread.h>
#include "bench.h"

#define N_INC  200000000ULL   /* 每线程 inc 次数 */
#define REPS   5

/* ---- bad: 两个 long 在同一 64B cacheline ---- */
static struct {
    volatile long x;
    volatile long y;
} bad;

/* ---- good: alignas(64) 隔到不同 cacheline ---- */
static struct {
    _Alignas(64) volatile long x;
    char _pad0[64 - sizeof(long)];
    _Alignas(64) volatile long y;
    char _pad1[64 - sizeof(long)];
} good;

/* worker：各自 inc 自己的变量。arg=0 用 x，arg=1 用 y。
 * volatile 防编译器合并/消除；asm clobber 防把 inc 优化成加法。*/
static void* worker_bad_x(void *a){ (void)a; pin_to_cpu(0);
    for(uint64_t i=0;i<N_INC;i++){ bad.x++; asm volatile("":::"memory"); } return NULL; }
static void* worker_bad_y(void *a){ (void)a; pin_to_cpu(1);
    for(uint64_t i=0;i<N_INC;i++){ bad.y++; asm volatile("":::"memory"); } return NULL; }
static void* worker_good_x(void *a){ (void)a; pin_to_cpu(0);
    for(uint64_t i=0;i<N_INC;i++){ good.x++; asm volatile("":::"memory"); } return NULL; }
static void* worker_good_y(void *a){ (void)a; pin_to_cpu(1);
    for(uint64_t i=0;i<N_INC;i++){ good.y++; asm volatile("":::"memory"); } return NULL; }

/* 单线程基线（无跨核一致性，纯 L1）*/
static void* worker_bad_x_solo(void *a){ (void)a; pin_to_cpu(0);
    for(uint64_t i=0;i<N_INC;i++){ bad.x++; asm volatile("":::"memory"); } return NULL; }

static double run_2thread(void *(*fx)(void*), void *(*fy)(void*)) {
    pthread_t t1, t2;
    uint64_t ts[REPS];
    for (int r = 0; r < REPS; r++) {
        bad.x = bad.y = good.x = good.y = 0;
        uint64_t t0 = now_ns();
        pthread_create(&t1, NULL, fx, NULL);
        pthread_create(&t2, NULL, fy, NULL);
        pthread_join(t1, NULL);
        pthread_join(t2, NULL);
        uint64_t t1n = now_ns();
        ts[r] = t1n - t0;
    }
    for (int i=1;i<REPS;i++){ uint64_t k=ts[i]; int j=i; while(j>0&&ts[j-1]>k){ts[j]=ts[j-1];j--;} ts[j]=k; }
    return (double)ts[REPS/2];
}

int main(void) {
    printf("== Lab03.5: False Sharing (N=%llu inc/线程, 2核) ==\n\n",
           (unsigned long long)N_INC);
    printf("  飞腾 D3000M L1D line=64B，bad 版 x/y 同 line，good 版 alignas(64) 隔离\n\n");

    /* 单线程基线：纯 L1 命中，无一致性开销 */
    double t_solo = run_2thread(worker_bad_x_solo, worker_bad_x_solo) / 2.0;
    /* ↑ 两线程都写 x（同变量，单核跑），取一半近似单线程 N_INC 的时间 */

    double t_bad  = run_2thread(worker_bad_x, worker_bad_y);
    double t_good = run_2thread(worker_good_x, worker_good_y);

    double ns_inc_solo = t_solo  / (double)N_INC;
    double ns_inc_bad  = t_bad   / (double)N_INC;
    double ns_inc_good = t_good  / (double)N_INC;

    printf("%-28s %12s %12s %10s\n", "mode", "总T(ms)", "ns/inc", "慢x倍");
    printf("%-28s %12s %12s %10s\n", "----------------------------", "----------", "----------", "------");
    printf("%-28s %12.1f %12.2f %10s\n", "单线程 (纯 L1 基线)", t_solo/1e6, ns_inc_solo, "1.0x");
    printf("%-28s %12.1f %12.2f %9.1fx\n", "2线程 false sharing (同 line)", t_bad/1e6, ns_inc_bad, ns_inc_bad/ns_inc_solo);
    printf("%-28s %12.1f %12.2f %9.1fx\n", "2线程 隔离 (alignas64)", t_good/1e6, ns_inc_good, ns_inc_good/ns_inc_solo);

    printf("\n  == 解读 ==\n");
    printf("  * false sharing: 两个变量同 cacheline，任一核写都让另一核的 line 失效，\n");
    printf("    每次 inc 触发跨核 MESI 迁移（飞腾实测 ns/inc 显著高于基线）。\n");
    printf("  * alignas(64) 隔离后: 两变量独立 line，互不干扰，ns/inc 接近单线程基线。\n");
    printf("  * 慢x倍 = false_sharing_ns / 单线程基线_ns，体现一致性代价。\n");
    printf("  * 实战陷阱: 多线程计数器、per-thread 统计、结构体数组相邻元素\n");
    printf("    全可能 false sharing。修法: alignas(64) / padding / per-thread 缓存。\n");
    printf("  * 验证: perf stat -e cache-misses ./false_sharing 看 bad 版 miss 暴涨。\n");
    return 0;
}
