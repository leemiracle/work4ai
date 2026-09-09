/*
 * Lab03/src/cache_sizes.c — 实测 Cache 容量
 *
 * 用 pointer chasing 探测各 cache 层级的边界和延迟。
 * 这是经典的 X/x86 上 Intel MLC / lm_bench 用过的技术。

 缓存容量转折点极度清晰：通过指针追逐测量延迟，可像“层析成像”一样精确定位每级缓存的大小。
    飞腾 FTC862 的延迟层级：L1 ~4 周期、L2 ~12–19 周期、L3 ~34–94 周期、L4 ~265 周期、DRAM ~306 周期。
    优化指导：对于访存密集且数据随机访问的程序，务必保证工作集 < 4 MB（塞进 L3），才能获得 < 40 ns 的延迟；若工作集在 4–8 MB，部分会落入 L4，延迟显著增大；超过 8 MB 则完全由内存性能决定，CPU 速度提升无法补偿。
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <time.h>
#include "bench.h"
#include "pmu.h"

#define N_ACCESS 10000000  /* 总访问次数 */

/* 前向声明 */
static const char *human_size(size_t bytes);

/* 构造一个乱序的链表，让 prefetcher 抓不到规律 */
static void build_permutation(size_t *perm, size_t n) {
    for (size_t i = 0; i < n; i++) perm[i] = i;
    /* Fisher-Yates 洗牌 */
    srand(42);
    for (size_t i = n - 1; i > 0; i--) {
        size_t j = (size_t)rand() % (i + 1);
        size_t t = perm[i]; perm[i] = perm[j]; perm[j] = t;
    }
}

/* 构造链表：nodes[perm[i]].next = &nodes[perm[i+1]] */
typedef struct node { struct node *next; char pad[56]; } node_t;
_Static_assert(sizeof(node_t) == 64, "node must be 64-byte cache line");

static node_t *build_chain(size_t n_nodes) {
    node_t *nodes = NULL;
    if (posix_memalign((void **)&nodes, 64, n_nodes * sizeof(node_t)) != 0) {
        perror("posix_memalign"); return NULL;
    }
    memset(nodes, 0, n_nodes * sizeof(node_t));

    size_t *perm = malloc(n_nodes * sizeof(size_t));
    build_permutation(perm, n_nodes);

    for (size_t i = 0; i < n_nodes - 1; i++) {
        nodes[perm[i]].next = &nodes[perm[i+1]];
    }
    nodes[perm[n_nodes-1]].next = &nodes[perm[0]];  /* 闭合环 */

    free(perm);
    return nodes;
}

static double measure_latency(node_t *head, size_t n_nodes) {
    /* warmup */
    node_t *p = head;
    for (size_t i = 0; i < 1000; i++) p = p->next;

    /* v2 修正：n_access 随数组大小调整，确保每节点被访问多圈。
     * v1 固定 N_ACCESS=10M，大数组(256M=4M nodes)只访问 2.5 圈，
     * 重复访问被缓存，延迟失真（实测 64M 比 16M 还快，反常）。
     * v2: 至少 5 圈，至少 1M，至多 30M（控时间）。 */
    size_t n_access = n_nodes * 5;
    if (n_access < 1000000) n_access = 1000000;
    if (n_access > 30000000) n_access = 30000000;

    uint64_t t0 = now_ns();
    p = head;
    for (size_t i = 0; i < n_access; i++) {
        p = p->next;
    }
    uint64_t t1 = now_ns();
    sink((uint64_t)p);
    return (double)(t1 - t0) / (double)n_access;
}

int main(void) {
    pin_to_cpu(0);

    printf("== Lab03.1: 实测 Cache 容量 (pointer chasing) ==\n\n");
    printf("  每次访问强制依赖，prefetcher 抓不到\n");
    printf("  N_access = %zu\n\n", (size_t)N_ACCESS);

    /* sweep 数组大小：从 4 KB 到 512 MB */
    size_t sizes[] = {
        4*1024, 8*1024, 16*1024, 32*1024, 64*1024,         /* L1 边界 */
        128*1024, 256*1024, 512*1024,                       /* L2 边界 */
        1024*1024, 2*1024*1024, 4*1024*1024, 8*1024*1024,  /* L3 边界 */
        16*1024*1024, 32*1024*1024, 64*1024*1024, 128*1024*1024, 256*1024*1024
    };
    int n_sizes = sizeof(sizes) / sizeof(sizes[0]);

    printf("%-12s %12s %16s %s\n",
           "size", "n_nodes", "latency(min/med)", "level");
    printf("%-12s %12s %16s %s\n",
           "----------", "----------", "----------------", "-----");

    for (int s = 0; s < n_sizes; s++) {
        size_t sz = sizes[s];
        size_t n_nodes = sz / sizeof(node_t);
        if (n_nodes < 100) continue;

        node_t *chain = build_chain(n_nodes);

        /* 多次测量取中位数 + min（latency 取 min 更真实反映无干扰延迟）*/
        double times[7];
        double tmin = 1e18;
        for (int r = 0; r < 7; r++) {
            times[r] = measure_latency(chain, n_nodes);
            if (times[r] < tmin) tmin = times[r];
        }
        /* 中位数 */
        for (int i = 1; i < 7; i++) {
            double k = times[i]; int j = i;
            while (j > 0 && times[j-1] > k) { times[j] = times[j-1]; j--; }
            times[j] = k;
        }
        double med = times[3];

        /* 判断层级（基于飞腾 D3000M 实测参数）*/
        const char *level;
        if (sz <= 64*1024)        level = "L1?";
        else if (sz <= 512*1024)  level = "L2?";
        else if (sz <= 8*1024*1024) level = "L3?";
        else                       level = "DRAM";

        printf("%-12s %12zu %6.2f/%6.2f ns  %s\n",
               human_size(sz), n_nodes, tmin, med, level);

        free(chain);
    }

    printf("\n  == 解读 ==\n");
    printf("  * latency 跳跃点对应 cache 边界\n");
    printf("  * 飞腾 D3000M 期望: L1=64K, L2=512K, L3=8M\n");
    printf("  * DRAM 延迟应该在 60-100 ns (DDR4-3200)\n");
    return 0;
}

static const char *human_size(size_t bytes) {
    static char buf[32];
    if (bytes < 1024) snprintf(buf, sizeof(buf), "%zuB", bytes);
    else if (bytes < 1024*1024) snprintf(buf, sizeof(buf), "%zuK", bytes/1024);
    else if (bytes < 1024*1024*1024) snprintf(buf, sizeof(buf), "%zuM", bytes/(1024*1024));
    else snprintf(buf, sizeof(buf), "%zuG", bytes/(1024*1024*1024));
    return buf;
}
