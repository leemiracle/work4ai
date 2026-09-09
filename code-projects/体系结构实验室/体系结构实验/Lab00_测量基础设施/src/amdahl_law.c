/*
 * Lab00/src/amdahl_law.c — Amdahl 定律实证
 *
 * 工作负载：W = p 部分并行 + (1-p) 部分串行
 * 加速比 S(N) = T(1) / T(N)
 * 理论：S(N) = 1 / ((1-p) + p/N)
 *
 * 用法: ./amdahl_law <p> [N_work]
 *   p       = 并行比例 (0.0-1.0)
 *   N_work  = 总工作量，默认 1e8
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <math.h>
#include <omp.h>

#include "bench.h"

#define REPS 7

static uint64_t W = 100000000ULL;

/* 用一个"看起来无意义但不会被消除"的工作负载 
纯 CPU 计算，不含 I/O、锁、内存竞争，非常适合验证 Amdahl 定律的“纯粹计算”场景。
选取 Xorshift 随机数运算，因为：
    编译器无法将其优化为常数（序列依赖强）。
    在优化等级 -O2 下不会被简化掉。
    每条指令都依赖上一条，让 CPU 的指令级并行难以隐藏延迟，更接近 真实计算的串行依赖。
工作量就是循环次数：to - from 控制任务大小。


*/
static inline uint64_t busy_work(uint64_t from, uint64_t to) {
    uint64_t s = 0x9E3779B97F4A7C15ULL;  /* 黄金分割常数 */
    for (uint64_t i = from; i < to; i++) {
        /* xorshift 让编译器无法简化 */
        s ^= s << 13;
        s ^= s >> 7;
        s ^= s << 17;
        s += i;
    }
    return s;
}

static uint64_t run_experiment(double p, int nthreads) {
    omp_set_num_threads(nthreads);
    uint64_t n_parallel = (uint64_t)(W * p);
    uint64_t n_serial   = W - n_parallel;

    uint64_t acc = 0;

    /* 串行部分 */
    acc += busy_work(0, n_serial);

    /* 并行部分 */
    #pragma omp parallel reduction(+:acc)
    {
        int tid = omp_get_thread_num();
        int nth = omp_get_num_threads();
        uint64_t chunk = n_parallel / nth;
        uint64_t from = (uint64_t)tid * chunk;
        uint64_t to   = (tid == nth-1) ? n_parallel : from + chunk;
        acc += busy_work(from, to);
    }
    /* 减少同步：acc 是 reduction，omp 自动加 fork-join */

    return acc;
}

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "Usage: %s <p> [N_work]\n", argv[0]);
        fprintf(stderr, "  p       = parallel fraction (0.0-1.0)\n");
        return 1;
    }
    double p = atof(argv[1]);
    if (argc > 2) W = strtoull(argv[2], NULL, 0);

    /* ⚠ 不在此处 pin_to_cpu(0)！
     * 旧版在此 pin 核0，导致 OpenMP 所有子线程继承 {0} 掩码全挤单核，
     * "多核加速比"实为单核 time-slicing 开销比，Amdahl 实验彻底失效。
     * 正确做法：主线程不限制亲和性，让 OpenMP 调度到多核。
     * 如需绑核避免漂移，用环境变量：OMP_PLACES=cores OMP_PROC_BIND=close
     * 或运行时 taskset -c 0-7 ./amdahl_law 限制到核集合（而非单核）。*/
    int max_threads = omp_get_max_threads();
    printf("== Amdahl 实验: p = %.4f, W = %llu, max_threads = %d ==\n\n",
           p, (unsigned long long)W, max_threads);

    printf("%-8s %14s %14s %14s %14s\n",
           "N", "T_med(ns)", "Speedup_meas", "Speedup_theory", "ratio");
    printf("%-8s %14s %14s %14s %14s\n",
           "------", "----------", "----------", "----------", "-----");

    /* 先测 N=1，作为基准 */
    uint64_t times_n1[REPS];
    for (int r = 0; r < REPS; r++) {
        uint64_t t0 = now_ns();
        uint64_t acc = run_experiment(p, 1);
        uint64_t t1 = now_ns();
        times_n1[r] = t1 - t0;
        sink(acc);
    }
    uint64_t t1 = median_u64(times_n1, REPS);

    /* 1, 2, 3, 4, 6, 8 */
    int nths[] = { 1, 2, 3, 4, 6, 8, 12, 16 };
    int nnth = sizeof(nths)/sizeof(nths[0]);
    if (nths[nnth-1] > max_threads) nnth--;
    /* 强制保证 N=1 也测 */
    printf("%-8d %14llu %14.2f %14.2f %14.2f\n",
           1, (unsigned long long)t1, 1.0, 1.0, 1.0);

    for (int i = 1; i < nnth; i++) {
        int N = nths[i];
        if (N > max_threads) continue;
        uint64_t times[REPS];
        for (int r = 0; r < REPS; r++) {
            uint64_t t0 = now_ns();
            uint64_t acc = run_experiment(p, N);
            uint64_t t1n = now_ns();
            times[r] = t1n - t0;
            sink(acc);
        }
        uint64_t med = median_u64(times, REPS); // 中位数避免单次 OS 抖动影响
        double s_meas = (double)t1 / (double)med;
        double s_theo = 1.0 / ((1.0 - p) + p / (double)N);
        printf("%-8d %14llu %14.2f %14.2f %14.2f\n",
               N, (unsigned long long)med, s_meas, s_theo, s_meas / s_theo);
    }

    printf("\n== 解读 ==\n");
    printf("  * p = %.4f, 串行部分 = %.2f%%\n", p, (1.0-p)*100);
    printf("  * 即使无限并行，最大加速 = %.2f\n", 1.0/(1.0-p));
    printf("  * ratio < 1 是正常的：OpenMP 同步 + 共享 L3 contention + DDR 带宽\n");

    return 0;
}
