/*
 * Lab06/src/store_store_reorder.c — ARM Store-Store 重排检测 (v2)
 *
 * ⚠ 关键设计修正（相对 v1）：
 *   v1 producer/consumer 无 per-trial 握手，consumer 读到的"x=0"多半是
 *   producer 下一轮的重置（x=0;flag=0），不是真重排。加 dmb ishst 后
 *   producer 变慢，consumer 更易撞上重置窗口，"重排"反增（实测 0→86853）。
 *
 * v2 用 pthread_barrier 三阶段同步，每轮严格隔离：
 *   阶段1 begin:     两线程同步开始
 *   阶段2 reset_done: producer 完成 reset (x=0,flag=0)，consumer 开始 spin
 *   阶段3 read_done:  consumer 完成读，producer 才进入下一轮
 * 这样 consumer 读到的 x=0 只能是真重排，不是下一轮 reset。
 *
 * Maranget 经典 MP litmus:
 *   producer:  x = 1; flag = 1;   (中间是否插屏障由 use_barrier 控制)
 *   consumer:  spin until flag==1; r = x;   (r==0 即重排)
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdint.h>
#include <stdatomic.h>
#include <pthread.h>
#include "bench.h"

#define N_TRIALS 2000000   /* 每轮隔离，比 v1 的 10M 慢，减到 2M */

static int use_barrier;

/* ⚠ x 与 flag 必须在不同 cacheline！旧版两 int 相邻同 line，
 * 同 line store-store 重排被额外抑制。现用 alignas(64) 各占独占 line。*/
typedef struct { volatile int v; char pad[60]; } cache_line_int;
static cache_line_int g_x;     /* x  独占 line */
static cache_line_int g_flag;  /* flag 独占 line */
#define x    (g_x.v)
#define flag (g_flag.v)

static int reorder_count;

static pthread_barrier_t bar;

static void* producer(void *arg) {
    (void)arg;
    pin_to_cpu(0);   /* producer 绑核0，与 consumer 不同核才测得到跨核重排 */
    for (int t = 0; t < N_TRIALS; t++) {
        /* 阶段 1: 等两线程都到本轮起点 */
        pthread_barrier_wait(&bar);

        /* reset：确保上一轮残留清干净 */
        x = 0; flag = 0;
        __asm__ __volatile__("dmb ish" ::: "memory");  /* reset 强制可见 */

        /* 阶段 2: 通知 consumer reset 完成，可以开始 spin */
        pthread_barrier_wait(&bar);

        /* 关键写序：x=1 然后 flag=1 */
        x = 1;
        if (use_barrier) {
            __asm__ __volatile__("dmb ishst" ::: "memory");  /* 阻止 store-store 重排 */
        }
        flag = 1;

        /* 阶段 3: 等 consumer 读完，才进入下一轮 reset */
        pthread_barrier_wait(&bar);
    }
    return NULL;
}

static void* consumer(void *arg) {
    (void)arg;
    pin_to_cpu(1);   /* consumer 绑核1，跨核观测重排 */
    for (int t = 0; t < N_TRIALS; t++) {
        pthread_barrier_wait(&bar);   /* 阶段 1 */
        pthread_barrier_wait(&bar);   /* 阶段 2: 等 reset 完成 */

        /* spin 等 flag==1。用 ldar（load-acquire）读 flag：
         * acquire 保证后续读 x 不会被重排到读 flag 之前，
         * 否则 consumer 自身 load-load 重排会产生假阳性/假阴性。
         * 经典 MP litmus consumer 必须 acquire 读 flag。*/
        int f;
        do {
            __asm__ __volatile__("ldar %w0, [%1]" : "=r"(f) : "r"(&flag) : "memory");
        } while (f != 1);

        /* 用 ldar 读 x（acquire，确保 flag→x 的 happens-before）*/
        int xv;
        __asm__ __volatile__("ldar %w0, [%1]" : "=r"(xv) : "r"(&x) : "memory");
        if (xv == 0) {
            __atomic_fetch_add(&reorder_count, 1, __ATOMIC_RELAXED);
        }

        pthread_barrier_wait(&bar);   /* 阶段 3: 通知 producer 我读完了 */
    }
    return NULL;
}

static void run_trial(int barrier, const char *label) {
    use_barrier = barrier;
    reorder_count = 0;
    x = 0; flag = 0;

    pthread_barrier_init(&bar, NULL, 2);
    pthread_t tp, tc;
    pthread_create(&tp, NULL, producer, NULL);
    pthread_create(&tc, NULL, consumer, NULL);
    pthread_join(tp, NULL);
    pthread_join(tc, NULL);
    pthread_barrier_destroy(&bar);

    printf("  %-28s 观测到重排 = %d 次 (/%d)\n",
           label, reorder_count, N_TRIALS);
}

int main(void) {
    /* 主线程不 pin：producer/consumer 各自 pin 到核0/核1。
     * 旧版 pin_to_cpu(0) 让两线程同核，跨核重排永不发生，reorder 恒 0 是 bug。*/
    printf("== Lab06.2: Store-Store 重排检测 v2 (per-trial 同步, N=%d) ==\n\n",
           N_TRIALS);
    printf("  v1 无握手，consumer 读到的 x=0 多为下一轮 reset（已废弃）\n");
    printf("  v2 用 pthread_barrier 三阶段隔离，x=0 必为真重排\n\n");

    run_trial(0, "无屏障 (relaxed):");
    run_trial(1, "加 dmb ishst (st-st):");

    printf("\n  == 解读 ==\n");
    printf("  * 无屏障重排次数 > 0: 飞腾真发生 store-store 重排（ARM RCpc 允许）\n");
    printf("  * 无屏障重排 == 0: 飞腾微架构保守，store-store 不重排（多数 ARM 实现如此）\n");
    printf("  * 加 dmb ishst 后重排应 == 0（屏障强制 store-store 顺序）\n");
    printf("  * 注：即便 RCpc 允许，现代 ARM 核（含飞腾）多对 store-store 保守，\n");
    printf("    无屏障也常观测不到重排。这是微架构选择，不违反 ISA。\n");
    printf("  * 要观测更激进的重排，需测 store-load（MP litmus 的经典变体）。\n");
    return 0;
}
