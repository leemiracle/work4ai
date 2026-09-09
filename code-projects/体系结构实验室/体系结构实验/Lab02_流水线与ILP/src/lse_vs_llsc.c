/*
 * Lab02/src/lse_vs_llsc.c — ARMv8.1 LSE 原子 vs 传统 LL/SC 对比
 *
 * 飞腾 D3000 实测支持 LSE（v8.1）。
 * 这个实验对比两种原子操作实现的性能：
 *   1. LSE 原子指令（ldadd, cas）—— 硬件总线仲裁，无失败
 *   2. LL/SC（ldxr/stxr）—— load-linked + store-conditional，失败重试
 *
 * 单线程下 LSE 略快（避免 retry），多线程争用下 LSE 大胜。
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <pthread.h>
#include <sys/auxv.h>
#include "bench.h"

#ifndef HWCAP_ATOMICS
#define HWCAP_ATOMICS (1 << 8)
#endif

#define N_OPS 10000000
#define N_THREADS_LIST 1, 2, 4, 8

/* 全局共享计数器 */
static volatile uint64_t g_counter = 0;
static uint64_t N_PER_THREAD;

/* ----- 方法 1: LSE ldadd 原子加（单线程/多线程通用） ----- */
static void* worker_lse(void *arg) {
    uint64_t tid = (uint64_t)arg;
    /* 多线程时每个 worker 绑不同核，争用才真实 */
    if (tid < 64) pin_to_cpu((int)(tid % 8));
    uint64_t *counter = (uint64_t*)&g_counter;
    /* LSE: ldadd (单条指令) */
    for (uint64_t i = 0; i < N_PER_THREAD; i++) {
        uint64_t old;
        __asm__ __volatile__(
            "ldadd %w[v], %w[o], [%[c]]\n"
            : [o] "=r"(old)
            : [v] "r"((uint64_t)1), [c] "r"(counter)
            : "memory"
        );
    }
    return NULL;
}

/* ----- 方法 2: LL/SC 原子加（传统 ARMv8 实现） ----- */
static void* worker_llsc(void *arg) {
    uint64_t tid = (uint64_t)arg;
    if (tid < 64) pin_to_cpu((int)(tid % 8));
    uint64_t *counter = (uint64_t*)&g_counter;
    for (uint64_t i = 0; i < N_PER_THREAD; i++) {
        uint64_t old, new_val;
        int result;  /* int 而非 uint64_t，避免与 new_val 混入同寄存器 */
        do {
            __asm__ __volatile__("ldxr %0, [%[c]]" : "=r"(old) : [c] "r"(counter));
            new_val = old + 1;
            /* stxr Ws,Wt,[Xn]: Ws(状态) 与 Wt(值) 必须不同寄存器。
             * 用 "=&r"(early-clobber) 强制 result 与 new_val 分配不同寄存器，
             * 修复旧版 stxr w0,w0,[x1] 的 UNPREDICTABLE。*/
            __asm__ __volatile__(
                "stxr %w[res], %w[nv], [%[c]]"
                : [res] "=&r"(result)
                : [nv] "r"(new_val), [c] "r"(counter)
                : "memory"
            );
        } while (result != 0);
    }
    return NULL;
}

/* ----- 方法 3: GCC __atomic 内建（编译器自动选 LSE 或 LL/SC） ----- */
static void* worker_gcc_atomic(void *arg) {
    uint64_t tid = (uint64_t)arg;
    if (tid < 64) pin_to_cpu((int)(tid % 8));
    uint64_t *counter = (uint64_t*)&g_counter;
    for (uint64_t i = 0; i < N_PER_THREAD; i++) {
        __atomic_add_fetch(counter, 1, __ATOMIC_RELAXED);
    }
    return NULL;
}

/* ----- 测量 ----- */
static double time_atomic_op(int n_threads, void *(*worker)(void *)) {
    g_counter = 0;
    N_PER_THREAD = N_OPS / n_threads;

    pthread_t threads[64];
    uint64_t t0 = now_ns();
    for (int i = 0; i < n_threads; i++) {
        pthread_create(&threads[i], NULL, worker, (void*)(uint64_t)i);
    }
    for (int i = 0; i < n_threads; i++) {
        pthread_join(threads[i], NULL);
    }
    uint64_t t1 = now_ns();

    return (double)(t1 - t0) / (double)N_OPS;  /* ns/op */
}

int main(void) {
    unsigned long hw = getauxval(AT_HWCAP);
    /* 主线程不 pin 核0：否则 worker 继承 {0} 掩码全挤单核，争用测不出。
     * worker 在各自入口按 tid pin。*/

    printf("== Lab02.5: LSE 原子 vs LL/SC ==\n\n");
    printf("  HWCAP.ATOMICS = %s\n\n", (hw & HWCAP_ATOMICS) ? "✓ 支持 LSE" : "✗ 仅 LL/SC");

    int nths[] = { N_THREADS_LIST };
    int n_n = sizeof(nths) / sizeof(nths[0]);

    printf("%-10s %15s %15s %15s\n", "threads", "LSE(ns/op)", "LL/SC(ns/op)", "GCC atomic");
    printf("%-10s %15s %15s %15s\n", "------", "----------", "----------", "----------");

    for (int i = 0; i < n_n; i++) {
        int n = nths[i];
        double t_lse = time_atomic_op(n, worker_lse);
        double t_llsc = time_atomic_op(n, worker_llsc);
        double t_gcc = time_atomic_op(n, worker_gcc_atomic);
        printf("%-10d %15.2f %15.2f %15.2f\n", n, t_lse, t_llsc, t_gcc);
    }

    printf("\n  == 解读 ==\n");
    printf("  * 单线程: LSE 略快于 LL/SC (实测 LSE ~10ns, LL/SC ~15ns)\n");
    printf("  * 多线程: LSE 与 LL/SC 接近 (实测 8 线程均 ~7.6-7.7 ns/op)\n");
    printf("  * ⚠ LL/SC 未出现预期 thrashing: 临界区太短 (ldxr+add+stxr),\n");
    printf("    冲突窗口小, stxr 失败率低; 飞腾 LL/SC 对短临界区友好\n");
    printf("    要触发 thrashing 需加长临界区 (ldxr/stxr 间插延迟指令)\n");
    printf("  * GCC __atomic 会自动选最优（kpgcc 应该选 LSE）\n");
    printf("  * 验证: counter 最终值 = %llu (期望 %llu)\n",
           (unsigned long long)g_counter, (unsigned long long)N_OPS);
    return 0;
}
