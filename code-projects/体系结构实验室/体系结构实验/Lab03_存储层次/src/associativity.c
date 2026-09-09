/*
 * Lab03/src/associativity.c — Cache 关联度（way 数）反推实测
 *
 * 飞腾 D3000M L1D: 64KB / 4-way / 64B line / 256 sets（Lab00 arch_probe 实测）。
 *   set index = addr[6:13]（line offset 6 位后 8 位）
 *   → 同 set 地址间隔 = 256 sets × 64B = 16KB
 *
 * 构造 N 个间隔 16KB 的地址（全映射同一 set），pointer chasing 测 cyc/access：
 *   - N ≤ 4（way 数）: 4 个地址都在 set 的 4-way 内，全命中 L1
 *   - N ≥ 5         : 超过 way 数，每次访问 evict 前一个（thrashing），miss 到 L2
 * 拐点 N* = way 数（飞腾应为 4）。
 *
 * 关联度 vs 容量 miss 的隔离：N 个地址只占 N 个 line（N×64B ≪ 64KB L1），
 * 远不触及容量上限，所以 miss 纯来自 associativity 限制，不是容量不够。
 *
 * 对偶：CPU 用 set-associative 解决 cache 结构冒险（本实验），
 *      用 forwarding 单元解决数据冒险 RAW（Expert_03 的 forward_a/forward_b RTL），
 *      用分支预测器解决控制冒险（Lab02 branch_predict）。
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include "bench.h"
#include "pmu.h"

#define SET_STRIDE  (256 * 64)    /* 256 sets × 64B = 16KB，同 set 地址间隔 */
#define N_STEPS     2000000
#define REPS        11

/* 构造 N 个同 set 地址（间隔 16KB），Fisher-Yates 随机连接成环（防 stride prefetcher），
 * pointer chasing 测 cyc/access + cache miss。*/
static double measure_assoc(char *base, int n, double *cmiss_out, double *cyc_out) {
    char **slot = malloc(n * sizeof(char*));
    for (int i = 0; i < n; i++) slot[i] = base + (size_t)i * SET_STRIDE;
    srand(42);
    for (int i = n - 1; i > 0; i--) {
        int j = rand() % (i + 1);
        char *t = slot[i]; slot[i] = slot[j]; slot[j] = t;
    }
    for (int i = 0; i < n; i++) *(char**)slot[i] = slot[(i + 1) % n];
    char *head = slot[0];
    free(slot);

    /* warmup: 让 N 个 line 进 steady state（纯读 chase，绝不写——写会破坏 next 指针）*/
    { char *q = head; for (int i = 0; i < 5000; i++) q = *(char**)q; sink((uint64_t)q); }

    pmu_group_t pmu = {0}; int hp = 1;
    if (pmu_add_hw(&pmu, PERF_COUNT_HW_CPU_CYCLES, "cyc")) hp = 0;
    if (pmu_add_hw(&pmu, PERF_COUNT_HW_CACHE_MISSES, "cm")) hp = 0;

    uint64_t ts[REPS], cs[REPS], cms[REPS];
    for (int r = 0; r < REPS; r++) {
        char *q = head;
        if (hp) pmu_start(&pmu);
        uint64_t t0 = now_ns();
        for (int s = 0; s < N_STEPS; s++) q = *(char**)q;
        uint64_t t1 = now_ns();
        sink((uint64_t)q);
        if (hp) { pmu_stop(&pmu); uint64_t v[8]={0}; pmu_read(&pmu, v); cs[r]=v[0]; cms[r]=v[1]; }
        ts[r] = t1 - t0;
    }
    if (hp) pmu_close(&pmu);
    for (int i=1;i<REPS;i++){uint64_t k=ts[i];int j=i;while(j>0&&ts[j-1]>k){ts[j]=ts[j-1];j--;}ts[j]=k;}
    for (int i=1;i<REPS;i++){uint64_t k=cs[i];int j=i;while(j>0&&cs[j-1]>k){cs[j]=cs[j-1];j--;}cs[j]=k;}
    for (int i=1;i<REPS;i++){uint64_t k=cms[i];int j=i;while(j>0&&cms[j-1]>k){cms[j]=cms[j-1];j--;}cms[j]=k;}

    *cmiss_out = hp ? (double)cms[REPS/2] / N_STEPS : -1;  /* miss/step */
    *cyc_out   = hp ? (double)cs[REPS/2] / N_STEPS : -1;
    return (double)ts[REPS/2] / N_STEPS;  /* ns/step */
}

int main(void) {
    pin_to_cpu(0);
    /* N_max=9 时跨度 9×16KB=144KB，分配 256KB 够用。每地址只 1 line，N×64B ≪ L1。*/
    size_t total = 16 * SET_STRIDE;  /* 256 KB */
    char *buf = aligned_alloc(64, total);
    if (!buf) { perror("aligned_alloc"); return 1; }

    printf("== Lab03.3: Cache 关联度反推 (L1D 4-way, 同 set 间隔 16KB) ==\n\n");
    printf("  构造 N 个间隔 16KB 的地址(同 set), pointer chasing 测 cyc/access\n");
    printf("  拐点 N* = way 数(飞腾预期 4), N>N* 触发 eviction thrashing\n\n");

    printf("%-6s %12s %12s %12s %s\n", "N", "ns/step", "cyc/step", "miss/step", "解读");
    printf("%-6s %12s %12s %12s %s\n", "----", "----------", "----------", "----------", "-----");

    for (int n = 1; n <= 9; n++) {
        double cm, cyc, ns = measure_assoc(buf, n, &cm, &cyc);
        const char *note;
        if (n <= 4)      note = "≤4-way, 全 L1 命中";
        else if (n == 5) note = "← 超 way 数, 开始 eviction";
        else             note = "thrashing, 每 step miss L2";
        printf("%-6d %12.2f %12.2f %12.2f %s\n", n, ns, cyc, cm, note);
    }
    free(buf);

    printf("\n  == 解读 ==\n");
    printf("  * N ≤ 4: 4 个地址都在 set 的 4-way 内，pointer chasing 全 L1 命中（低 cyc）\n");
    printf("  * N = 5 起: 超过 way 数，每次访问 evict 前一个 → miss 到 L2（cyc/miss 暴涨）\n");
    printf("  * 拐点 N* = 飞腾 L1D way 数（实测应为 4，与 Lab00 arch_probe 一致）\n");
    printf("  * 容量隔离: N 地址只占 N line (N×64B ≪ 64KB), miss 纯来自 associativity\n");
    printf("  * 对偶: 这是 cache 结构冒险的硬件解法(set-associative)；\n");
    printf("    数据冒险(RAW)用 forwarding(Expert_03 的 forward_a/forward_b RTL)，\n");
    printf("    控制冒险用分支预测器(Lab02 branch_predict)——CPU 设计处处是'冲突→机制'\n");
    printf("  * 实战陷阱: power-of-2 stride 是性能杀手(大量地址撞同 set)，\n");
    printf("    矩阵列遍历、hash 表桶数选 2^k 都可能触发\n");
    return 0;
}
