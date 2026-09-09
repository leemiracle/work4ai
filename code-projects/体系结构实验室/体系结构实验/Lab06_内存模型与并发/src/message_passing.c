/*
 * Lab06/src/message_passing.c — ARM 内存模型 Message Passing litmus
 *
 * 经典 MP litmus (Maranget PLDI 2012)：
 *   CPU0 (producer):  data = 1;  flag = 1;
 *   CPU1 (consumer):  while(flag!=1);  r = data;   // r==0 即"重排证据"
 *
 * ARM 是 RCpc（relaxed），store-store / load-load 都可能重排：
 *   - relaxed (普通 str/ldr): producer 的 data/flag store 可能重排，
 *     consumer 的 flag/data load 也可能重排 → r==0 出现（重排证据）
 *   - release/acquire (stlr/ldar): 强制 data 先于 flag 可见，flag 先于 data 读取
 *     → r==0 永不出现（正确同步）
 *
 * 本实验对比两种模式的重排次数，实证 ARM 弱内存模型。
 * 与 store_store_reorder.c 互补：那个测 store-store，本实验测 store-load（MP）。
 *
 * 设计要点（避免假阳/假阴）:
 *   - data/flag 在不同 cacheline（alignas64），排除同 line 屏蔽
 *   - producer/consumer 绑不同核
 *   - per-trial barrier 同步，consumer 读到的 data==0 必为真重排
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdint.h>
#include <pthread.h>
#include "bench.h"

#define N_TRIALS 2000000

/* data/flag 不同 cacheline */
static _Alignas(64) volatile int g_data;
static _Alignas(64) volatile int g_flag;
static int g_reorder_count;
static int g_use_acquire;  /* 1=stlr/ldar, 0=普通 str/ldr */
static pthread_barrier_t g_bar;

static void* producer(void *a) {
    (void)a; pin_to_cpu(0);
    for (int t = 0; t < N_TRIALS; t++) {
        pthread_barrier_wait(&g_bar);          /* 阶段1: 同步起点 */
        g_data = 0; g_flag = 0;
        __asm__ __volatile__("dmb ish":::"memory");  /* reset 可见 */
        pthread_barrier_wait(&g_bar);          /* 阶段2: reset 完成 */

        g_data = 1;
        if (g_use_acquire) {
            __asm__ __volatile__("stlr %w0, [%1]"::"r"(1), "r"(&g_flag):"memory");  /* store-release */
        } else {
            g_flag = 1;  /* 普通 store，可能与 data store 重排 */
        }
        pthread_barrier_wait(&g_bar);          /* 阶段3: 等 consumer 读完 */
    }
    return NULL;
}

static void* consumer(void *a) {
    (void)a; pin_to_cpu(1);
    for (int t = 0; t < N_TRIALS; t++) {
        pthread_barrier_wait(&g_bar);          /* 阶段1 */
        pthread_barrier_wait(&g_bar);          /* 阶段2 */

        int f;
        if (g_use_acquire) {
            do { __asm__ __volatile__("ldar %w0, [%1]":"=r"(f):"r"(&g_flag):"memory"); }
            while (f != 1);
            int d;
            __asm__ __volatile__("ldar %w0, [%1]":"=r"(d):"r"(&g_data):"memory");
            if (d == 0) __atomic_fetch_add(&g_reorder_count, 1, __ATOMIC_RELAXED);
        } else {
            do { f = g_flag; } while (f != 1);  /* 普通 load */
            int d = g_data;                      /* 普通 load，可能与 flag load 重排 */
            if (d == 0) __atomic_fetch_add(&g_reorder_count, 1, __ATOMIC_RELAXED);
        }
        pthread_barrier_wait(&g_bar);          /* 阶段3 */
    }
    return NULL;
}

static void run(int use_acq, const char *label) {
    g_use_acquire = use_acq;
    g_reorder_count = 0;
    g_data = g_flag = 0;
    pthread_barrier_init(&g_bar, NULL, 2);
    pthread_t tp, tc;
    pthread_create(&tp, NULL, producer, NULL);
    pthread_create(&tc, NULL, consumer, NULL);
    pthread_join(tp, NULL);
    pthread_join(tc, NULL);
    pthread_barrier_destroy(&g_bar);
    printf("  %-32s 重排(data==0) = %d / %d (%.4f%%)\n",
           label, g_reorder_count, N_TRIALS,
           100.0 * g_reorder_count / N_TRIALS);
}

int main(void) {
    printf("== Lab06.3: Message Passing litmus (ARM RCpc 重排实测) ==\n\n");
    printf("  producer: data=1; flag=1;   consumer: spin(flag); r=data;\n");
    printf("  r==0 = 重排证据(ARM 允许 store-load 重排)\n");
    printf("  N=%d trials/模式, producer核0/consumer核1, data/flag 不同 cacheline\n\n",
           N_TRIALS);

    run(0, "relaxed (普通 str/ldr):");
    run(1, "release/acquire (stlr/ldar):");

    printf("\n  == 解读 ==\n");
    printf("  * relaxed 重排 > 0: 飞腾真发生 store-load 重排（ARM RCpc 允许）\n");
    printf("  * relaxed 重排 == 0: 飞腾微架构对此模式保守（不违反 ISA，只是更严）\n");
    printf("  * stlr/ldar 后重排应 == 0: acquire/release 强制 data 先于 flag 可见\n");
    printf("  * 与 store_store_reorder.c 对比: 那个测 store-store，本实验测 store-load\n");
    printf("    通常 store-load(MP) 比	store-store 更容易观测到重排\n");
    printf("  * 实战: 无锁队列/单生产者-消费者必须用 stlr/ldar，否则 consumer 可能\n");
    printf("    看到 flag=1 但读到旧 data（经典并发 bug）\n");
    return 0;
}
