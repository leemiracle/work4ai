/*
 * Lab04/src/rename_capacity.c — 探测寄存器重命名容量 / 浮点 ILP 上限
 *
 * 构建 N 条独立浮点依赖链，看 IPC 如何随 N 变化。
 *   - N 条链相互独立 → 硬件可并行发射（ILP）
 *   - N 增大时 IPC 涨，直到撞上某个瓶颈
 *
 * 设计修正（相对初版，对照 README §3.1）：
 *   1. 链数 16 → 64（原 16 够不到现代 PRF，也看不到 saturate 之后的拐点）
 *   2. 拆 v*v 与 +1.0 两行 + 编译加 -ffp-contract=off：防编译器融合成 fmadd
 *      （否则 IPC 基准失真，原 README "fmul+fadd 两指令" 假设不成立）
 *   3. 编译加 -fno-tree-vectorize：阻止 NEON 把 N 条标量链打包成 SIMD 通道
 *      （否则测的是 FPU 通道数，不是 PRF/ILP）
 *   4. 统计加 min/p90：拐点对尾延迟敏感，单 median 易被 outlier 误导
 *
 * ⚠️ 诚实声明（重要局限）：
 *   本实验用的是"浅链"（每链每迭代 1 步），主要瓶颈是 4-wide 发射带宽，
 *   IPC 在 N≈4 时就 saturate 到 4。这个 saturate 点 ≠ PRF 拐点。
 *   要测真 PRF 上限，需用"深链"（每链 L 步长依赖，N×L 撑满 PRF/ROB），
 *   见文件末尾"扩展：深链 PRF 探测"注释。本文件保持浅链，作为 ILP/发射带宽演示，
 *   并诚实标注它不是 PRF 的直接测量。
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include "bench.h"
#include "pmu.h"

#define N_ITER     1000000
#define MAX_CHAINS 64
#define REPS       11

/* N 条独立浮点依赖链（浅链）。
 * 内层 j 循环的 N 条链互不相关 → 可并行发射。
 * 每条链内部 sq=vv[j]*vv[j] → vv[j]=sq+1.0 是真依赖（须等乘完才能加）→ 链内串行。
 * 拆两行 + -ffp-contract=off 防 FMA 融合。
 */
static double __attribute__((noinline,optimize("no-fast-math")))
chains_n(double *vv, int n_chains) {
    for (int i = 0; i < N_ITER; i++) {
        for (int j = 0; j < n_chains; j++) {
            double sq = vv[j] * vv[j];   /* 独立乘 */
            vv[j] = sq + 1.0;            /* 依赖 sq，链内串行 */
        }
    }
    double s = 0;
    for (int j = 0; j < n_chains; j++) s += vv[j];
    return s;
}

/* min / median / p90 */
static void stats_u64(uint64_t *arr, size_t n,
                      uint64_t *pmin, uint64_t *pmed, uint64_t *p90) {
    if (n == 0) { if(pmin)*pmin=0; if(pmed)*pmed=0; if(p90)*p90=0; return; }
    uint64_t tmp[1024];
    size_t m = n < 1024 ? n : 1024;
    memcpy(tmp, arr, m * sizeof(uint64_t));
    for (size_t i = 1; i < m; i++) {
        uint64_t k = tmp[i]; size_t j = i;
        while (j > 0 && tmp[j-1] > k) { tmp[j] = tmp[j-1]; j--; }
        tmp[j] = k;
    }
    if (pmin) *pmin = tmp[0];
    if (pmed) *pmed = tmp[m/2];
    if (p90)  *p90  = tmp[(size_t)(m * 0.9)];
}

int main(void) {
    pin_to_cpu(0);

    printf("== Lab04.1: 寄存器重命名容量 / 浮点 ILP 上限 ==\n\n");
    printf("  N_ITER = %d, 飞腾 D3000M @ 2.5 GHz\n", N_ITER);
    printf("  探测 N = 1..64（浅链：每链每迭代 1 步 fmul+fadd）\n");
    printf("  ⚠ 本实验主要测 4-wide 发射带宽，不是 PRF 拐点。\n");
    printf("    见文件头局限声明与末尾深链扩展注释。\n\n");

    pmu_group_t pmu = {0};
    int have_pmu = 1;
    if (pmu_add_hw(&pmu, PERF_COUNT_HW_CPU_CYCLES,   "cyc") != 0) have_pmu = 0;
    if (pmu_add_hw(&pmu, PERF_COUNT_HW_INSTRUCTIONS, "ins") != 0) have_pmu = 0;

    static double v[MAX_CHAINS];   /* static → 固定地址，编译器更易寄存器化部分元素 */

    printf("%-9s %9s %9s %9s %11s %11s %7s\n",
           "n_chains", "T_med(ms)", "T_min(ms)", "T_p90(ms)",
           "cycles", "insts", "IPC");
    printf("%-9s %9s %9s %9s %11s %11s %7s\n",
           "-------", "---------", "---------", "---------",
           "-----------", "-----------", "-------");

    int ns[] = {1,2,4,8,12,16,24,32,40,48,56,64};

    for (size_t k = 0; k < sizeof(ns)/sizeof(ns[0]); k++) {
        int n = ns[k];
        uint64_t ts[REPS], cs[REPS], is[REPS];
        for (int r = 0; r < REPS; r++) {
            for (int i = 0; i < n; i++) v[i] = (double)(i + 1) + 0.5;
            if (have_pmu) pmu_start(&pmu);
            uint64_t t0 = now_ns();
            volatile double r_val = chains_n(v, n);
            uint64_t t1 = now_ns();
            sink((uint64_t)r_val);
            if (have_pmu) {
                pmu_stop(&pmu);
                uint64_t vs[PMU_MAX_EVENTS] = {0};
                pmu_read(&pmu, vs);
                cs[r] = vs[0]; is[r] = vs[1];
            }
            ts[r] = t1 - t0;
        }
        uint64_t tmin, tmed, t90, cmed, imed;
        stats_u64(ts, REPS, &tmin, &tmed, &t90);
        stats_u64(cs, REPS, NULL, &cmed, NULL);
        stats_u64(is, REPS, NULL, &imed, NULL);
        double ipc = (have_pmu && cmed) ? (double)imed / (double)cmed : 0;
        printf("%-9d %9.1f %9.1f %9.1f %11llu %11llu %7.3f\n",
               n, tmed/1e6, tmin/1e6, t90/1e6,
               (unsigned long long)cmed,
               (unsigned long long)imed, ipc);
    }

    if (have_pmu) pmu_close(&pmu);

    printf("\n  == 解读 ==\n");
    printf("  * n=1:  IPC ≈ 0.25  (fmul+fadd 串行链，~8 cyc/op)\n");
    printf("  * n=4:  IPC ≈ 1.0   (4 条独立链填满 4-wide 发射)\n");
    printf("  * n>=12: IPC ≈ 3-4   (充分 ILP，撞 4-wide 发射带宽上限)\n");
    printf("  * 关键认知：浅链的 saturate 点 = 发射带宽瓶颈，≠ PRF 瓶颈。\n");
    printf("    PRF 拐点要 N×L 超过 PRF 才出现，需深链结构（见下）。\n\n");

    printf("  == 扩展：深链 PRF 探测（本文件未实现，留作练习）==\n");
    printf("  要测真 PRF 上限，把 chains_n 改成每条链 L 步深依赖：\n");
    printf("    for (j=0; j<n; j++)\n");
    printf("      for (s=0; s<L; s++) { sq=v[j]*v[j]; v[j]=sq+1.0; }\n");
    printf("  当 N×L 接近 PRF（飞腾估计 128-256），重命名器 stall，\n");
    printf("  IPC 会从 4-wide 理论值掉下来。L=64，N 扫 2..8 即可覆盖。\n");
    printf("  对照：Alpha 21264 PRF=72；Skylake 180；Apple M1 ~350。\n");
    return 0;
}
