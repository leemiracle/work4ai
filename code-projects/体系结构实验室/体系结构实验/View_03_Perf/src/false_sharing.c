/* View_03_Perf/src/false_sharing.c — 多核 false sharing demo
 *
 * 性能工程师经典坑：两个线程各自写自己的变量，
 * 但变量共享同一 cache line，导致 cache line 在核间反复 invalidated。
 * 即使逻辑上互不干扰，性能也跌 5-10×。
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <time.h>
#include <stdalign.h>

#define N_THREADS 2
#define ITERATIONS 100000000

/* —— 不安全：两线程数据在同一 cache line —— */
struct {
    volatile long value;
} bad_shared[N_THREADS] __attribute__((aligned(64)));   /* 但 sizeof < 64, 数组元素挤一行 */

/* —— 安全：每线程数据独占一行 —— */
struct {
    volatile long value;
    char pad[56];   /* 补齐到 64 字节 */
} good_padded[N_THREADS] __attribute__((aligned(64)));

struct timespec t0, t1;

static void *worker_bad(void *arg) {
    int tid = (int)(long)arg;
    for (long i = 0; i < ITERATIONS; i++) {
        bad_shared[tid].value++;
    }
    return NULL;
}

static void *worker_good(void *arg) {
    int tid = (int)(long)arg;
    for (long i = 0; i < ITERATIONS; i++) {
        good_padded[tid].value++;
    }
    return NULL;
}

static double run_test(void *(*worker)(void*)) {
    pthread_t threads[N_THREADS];
    clock_gettime(CLOCK_MONOTONIC, &t0);
    for (long i = 0; i < N_THREADS; i++)
        pthread_create(&threads[i], NULL, worker, (void*)i);
    for (int i = 0; i < N_THREADS; i++)
        pthread_join(threads[i], NULL);
    clock_gettime(CLOCK_MONOTONIC, &t1);
    return (t1.tv_sec - t0.tv_sec) + (t1.tv_nsec - t0.tv_nsec) / 1e9;
}

int main(void) {
    printf("=== false_sharing: 2 线程各写自己的变量 ===\n\n");
    printf("每线程迭代 %d 次\n\n", ITERATIONS);

    double t_bad = run_test(worker_bad);
    double t_good = run_test(worker_good);

    printf("struct 大小: bad=%zu B, good=%zu B (cache line=64B)\n\n",
           sizeof(bad_shared[0]), sizeof(good_padded[0]));
    printf("false sharing (bad): %.3f s\n", t_bad);
    printf("padding (good)      : %.3f s\n", t_good);
    printf("加速比              : %.1fx\n", t_bad / t_good);
    printf("\n结论: 多线程共享数据必须 padding 到 cache line (64B)\n");
    printf("      或用 alignas(64) / __cacheline_aligned\n");
    return 0;
}
