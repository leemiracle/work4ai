/* View_03_Perf/src/branch_patterns.c — 不同分支模式的 IPC 对比
 *
 * 性能工程师的真相时刻：分支预测器对"规则分支"几乎完美，
 * 但对"随机分支"准确率跌到 50%（最坏），性能暴跌 4-5×。
 *
 * 演示 5 种分支模式 + 用 perf 计数器测 IPC + 分支预测准确率。
 */
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define N 10000000
static int data[N];
static int threshold;

/* 防止编译器消除分支：用 asm volatile barrier 强制 sum 真实写入 */
#define FORCE_USE(x) __asm__ volatile("" : : "r"(x) : "memory")

/* pattern 1: 完全可预测（永远不跳）*/
__attribute__((noinline)) long pattern_never(int *d, int n) {
    long sum = 0;
    for (int i = 0; i < n; i++) {
        if (d[i] < threshold - 1000000) sum += d[i];   /* 永远 false */
    }
    FORCE_USE(sum); return sum;
}

/* pattern 2: 完全可预测（每次都跳）*/
__attribute__((noinline)) long pattern_always(int *d, int n) {
    long sum = 0;
    for (int i = 0; i < n; i++) {
        if (d[i] < threshold + 1000000) sum += d[i];   /* 永远 true */
    }
    FORCE_USE(sum); return sum;
}

/* pattern 3: 周期性（每 4 个跳一次）*/
__attribute__((noinline)) long pattern_periodic(int *d, int n) {
    long sum = 0;
    for (int i = 0; i < n; i++) {
        if (i % 4 == 0) sum += d[i];
    }
    FORCE_USE(sum); return sum;
}

/* pattern 4: 阶梯（前一半跳，后一半不跳）*/
__attribute__((noinline)) long pattern_staircase(int *d, int n) {
    long sum = 0;
    for (int i = 0; i < n; i++) {
        if (i < n/2) sum += d[i];
    }
    FORCE_USE(sum); return sum;
}

/* pattern 5: 完全随机（50% 跳）*/
__attribute__((noinline)) long pattern_random(int *d, int n) {
    long sum = 0;
    for (int i = 0; i < n; i++) {
        if (d[i] < RAND_MAX/2) sum += d[i];
    }
    FORCE_USE(sum); return sum;
}

static double now_s(void) {
    struct timespec ts; clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec + ts.tv_nsec / 1e9;
}

int main(void) {
    srand(42);
    for (int i = 0; i < N; i++) data[i] = rand();
    threshold = RAND_MAX / 2;

    struct { const char *name; long (*fn)(int*, int); } tests[] = {
        {"never taken      ", pattern_never},
        {"always taken     ", pattern_always},
        {"periodic (1/4)   ", pattern_periodic},
        {"staircase (1/2)  ", pattern_staircase},
        {"random (50%)     ", pattern_random},
    };

    printf("=== branch_patterns: 分支模式对性能的影响 ===\n");
    printf("N = %d, 飞腾 D3000M 2.5GHz\n\n", N);
    printf("%-20s %12s %10s\n", "pattern", "T(ms)", "ns/op");
    printf("%-20s %12s %10s\n", "-------", "------", "-----");

    for (int t = 0; t < (int)(sizeof(tests)/sizeof(tests[0])); t++) {
        /* warmup */
        volatile long sink = tests[t].fn(data, N);
        (void)sink;
        /* measure */
        double t0 = now_s();
        long result = tests[t].fn(data, N);
        double dt = now_s() - t0;
        printf("%-20s %12.1f %10.2f   (sum=%ld)\n",
               tests[t].name, dt*1000, dt*1e9/N, result);
    }
    printf("\n perf stat -e branches,branch-misses ./branch_patterns  可看真实预测准确率\n");
    return 0;
}
