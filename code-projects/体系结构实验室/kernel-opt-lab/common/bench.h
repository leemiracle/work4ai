/*
 * common/bench.h — 高精度计时、统计、防优化工具集
 *
 * 用法：在所有实验里 #include "bench.h"
 *
 * 提供：
 *   - now_ns()           : 单调时间戳（纳秒）
 *   - now_cycles()       : 读 CPU 周期计数器（aarch64 的 cntvct_el0）
 *   - median / mean / stdev: 基本统计
 *   - escape() / sink()  : 防止编译器消除"无副作用"代码
 *   - pin_to_cpu()       : 绑定到指定 CPU 核心
 *   - prefetch_l3()      : 预热缓存（warmup）
 *
 * 设计原则：
 *   1. 不依赖第三方库（仅 libc）
 *   2. 全部 inline 或 static，避免符号冲突
 *   3. 跨架构（aarch64/x86_64）兼容，但有针对飞腾的 fast path
 */
#ifndef BENCH_H
#define BENCH_H

#include <stdint.h>
#include <stddef.h>
#include <time.h>
#include <sched.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* ============================================================ */
/* 1. 时间测量                                                   */
/* ============================================================ */

/* 纳秒级单调时间（推荐用法，足够精确到 ~ns 级别） */
static inline uint64_t now_ns(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC_RAW, &ts);  /* RAW: 不受 NTP 调整影响 */
    return (uint64_t)ts.tv_sec * 1000000000ULL + (uint64_t)ts.tv_nsec;
}

/* 直接读硬件周期计数器（最精确，但需要注意：
 *   1. 必须先发 isb 同步流水线
 *   2. 在用户态需要内核开启允许访问：/sys/devices/system/cpu/.../cpuidle 之外，
 *      通常 perf 才能用；可能需要 setting PR_SET_TSC_AUX 等
 *   3. 飞腾 D3000 上可能受 PMU 配置影响，先用 now_ns() 兜底
 */
static inline uint64_t now_cycles(void) {
#if defined(__aarch64__)
    uint64_t v;
    __asm__ __volatile__("isb          \n"
                         "mrs %0, cntvct_el0 \n"
                         : "=r"(v)
                         :
                         : "memory");
    return v;
#elif defined(__x86_64__)
    uint32_t lo, hi;
    __asm__ __volatile__("rdtsc" : "=a"(lo), "=d"(hi));
    return ((uint64_t)hi << 32) | lo;
#else
    return now_ns();  /* fallback */
#endif
}

/* 读取频率（cntvct 的频率，单位 Hz） */
static inline uint64_t cntfrq_hz(void) {
#if defined(__aarch64__)
    uint64_t v;
    __asm__ __volatile__("mrs %0, cntfrq_el0" : "=r"(v));
    return v;
#else
    return 1000000000ULL;  /* 假设 1 GHz */
#endif
}

/* ============================================================ */
/* 2. 防止编译器优化掉"无用"代码                                */
/* ============================================================ */

/* 让编译器认为 v 有副作用，无法被消除 */
static inline void escape(const void *p) {
    __asm__ __volatile__("" : : "g"(p) : "memory");
}

/* 让编译器认为 sink 是一个不透明函数，强制把 p 写出去 */
static inline void sink(uint64_t v) {
    __asm__ __volatile__("" : : "r"(v) : "memory");
}

/* memory clobber：强制所有寄存器内容写回，且重新加载 */
static inline void full_fence(void) {
    __asm__ __volatile__("" : : : "memory");
}

/* ============================================================ */
/* 3. CPU 亲和性（绑核）                                         */
/* ============================================================ */

static inline int pin_to_cpu(int cpu) {
    cpu_set_t mask;
    CPU_ZERO(&mask);
    CPU_SET(cpu, &mask);
    return sched_setaffinity(0, sizeof(mask), &mask);
}

/* 设置调度策略为 SCHED_FIFO，减少被抢占（需要 root 或 CAP_SYS_NICE） */
static inline int set_realtime_priority(void) {
    struct sched_param sp;
    memset(&sp, 0, sizeof(sp));
    sp.sched_priority = sched_get_priority_max(SCHED_FIFO);
    return sched_setscheduler(0, SCHED_FIFO, &sp);
}

/* ============================================================ */
/* 4. 基本统计                                                   */
/* ============================================================ */

static inline uint64_t median_u64(uint64_t *arr, size_t n) {
    /* 简单选择中位数（避免破坏原数组） */
    /* 对小数组（n<=1024）做完整排序足够 */
    if (n == 0) return 0;
    uint64_t tmp[1024];
    size_t m = n < 1024 ? n : 1024;
    memcpy(tmp, arr, m * sizeof(uint64_t));

    /* 插入排序（对实验场景下<100 个样本足够） */
    for (size_t i = 1; i < m; i++) {
        uint64_t k = tmp[i];
        size_t j = i;
        while (j > 0 && tmp[j-1] > k) {
            tmp[j] = tmp[j-1];
            j--;
        }
        tmp[j] = k;
    }
    return tmp[m / 2];
}

static inline double mean_d(const uint64_t *arr, size_t n) {
    if (n == 0) return 0.0;
    double s = 0;
    for (size_t i = 0; i < n; i++) s += (double)arr[i];
    return s / (double)n;
}

static inline double stdev_d(const uint64_t *arr, size_t n) {
    if (n <= 1) return 0.0;
    double m = mean_d(arr, n);
    double s = 0;
    for (size_t i = 0; i < n; i++) {
        double d = (double)arr[i] - m;
        s += d * d;
    }
    return __builtin_sqrt(s / (double)(n - 1));
}

/* ============================================================ */
/* 5. 便捷输出宏                                                 */
/* ============================================================ */

#define bench_log(tag, fmt, ...) \
    fprintf(stderr, "[%-12s] " fmt "\n", tag, ##__VA_ARGS__)

#define bench_assert(cond, msg) do { \
    if (!(cond)) { \
        fprintf(stderr, "ASSERT FAIL: %s:%d: %s\n", __FILE__, __LINE__, msg); \
        exit(1); \
    } \
} while (0)

/* ============================================================ */
/* 6. 简易实验结果表格输出                                       */
/* ============================================================ */

typedef struct {
    const char *name;
    double      mean_ns;
    double      stdev_ns;
    double      mean_cyc;     /* 若用 cycles 计时填这个 */
    double      ipc;          /* 可选：通过 PMU 同步测得 */
} bench_result_t;

static inline void bench_print_header(void) {
    printf("%-30s %12s %12s %12s %8s\n",
           "experiment", "mean_ns", "stdev_ns", "mean_cyc", "IPC");
    printf("%-30s %12s %12s %12s %8s\n",
           "------------------------------",
           "------------", "------------", "------------", "--------");
}

static inline void bench_print_result(const bench_result_t *r) {
    printf("%-30s %12.1f %12.1f %12.1f %8.2f\n",
           r->name, r->mean_ns, r->stdev_ns, r->mean_cyc, r->ipc);
}

#endif /* BENCH_H */
