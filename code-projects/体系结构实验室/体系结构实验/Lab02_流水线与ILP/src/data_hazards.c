/*
 * Lab02/src/data_hazards.c — 数据相关 RAW/WAW/WAR 实验
 *
 * 通过构建不同长度的依赖链，反推飞腾 D3000M 浮点单元的 latency。
 * 通过对比独立链和依赖链，理解 ILP 的极限。
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include "bench.h"
#include "pmu.h"

#define N 10000000
#define REPS 21

/* 单条依赖链：1 个变量不断自更新 (强依赖) */
double __attribute__((noinline,optimize("no-fast-math")))
dep_chain_1(double x, int n) {
    for (int i = 0; i < n; i++) {
        x = x * x + 1.0;
    }
    return x;
}

/* 双链：2 个独立变量 */
double __attribute__((noinline,optimize("no-fast-math")))
dep_chain_2(double x, int n) {
    double y = x + 1.0;
    for (int i = 0; i < n; i++) {
        x = x * x + 1.0;
        y = y * y + 1.0;
    }
    return x + y;
}

/* 4 链 */
double __attribute__((noinline,optimize("no-fast-math")))
dep_chain_4(double x, int n) {
    double a = x, b = x+1, c = x+2, d = x+3;
    for (int i = 0; i < n; i++) {
        a = a*a + 1.0;
        b = b*b + 1.0;
        c = c*c + 1.0;
        d = d*d + 1.0;
    }
    return a+b+c+d;
}

/* 8 链 */
double __attribute__((noinline,optimize("no-fast-math")))
dep_chain_8(double x, int n) {
    double v[8];
    for (int i = 0; i < 8; i++) v[i] = x + i;
    for (int i = 0; i < n; i++) {
        v[0]=v[0]*v[0]+1; v[1]=v[1]*v[1]+1; v[2]=v[2]*v[2]+1; v[3]=v[3]*v[3]+1;
        v[4]=v[4]*v[4]+1; v[5]=v[5]*v[5]+1; v[6]=v[6]*v[6]+1; v[7]=v[7]*v[7]+1;
    }
    double s=0; for (int i = 0; i < 8; i++) s += v[i];
    return s;
}

/* 通用测量：调用 fn(x, N) 一次，返回耗时 ns（取 REPS 次中位数） */
static double time_fn(double (*fn)(double, int), double x) {
    uint64_t ts[REPS];
    for (int r = 0; r < REPS; r++) {
        uint64_t t0 = now_ns();
        double result = fn(x, N);
        uint64_t t1 = now_ns();
        sink((uint64_t)result);  /* 关键：防优化，且让 result 有外部副作用 */
        ts[r] = t1 - t0;
    }
    /* 插入排序求中位数 */
    for (int i = 1; i < REPS; i++) {
        uint64_t k = ts[i]; int j = i;
        while (j > 0 && ts[j-1] > k) { ts[j] = ts[j-1]; j--; }
        ts[j] = k;
    }
    return (double)ts[REPS/2];
}

int main(void) {
    pin_to_cpu(0);

    printf("== Lab02.1: 数据相关与 ILP ==\n\n");
    printf("  N = %d (iterations per chain)\n", N);
    printf("  2.5 GHz 飞腾，所以 1 ns = 2.5 cycles\n\n");

    struct { const char *name; double (*fn)(double, int); int n_chains; } tests[] = {
        { "dep_chain_1", dep_chain_1, 1 },
        { "dep_chain_2", dep_chain_2, 2 },
        { "dep_chain_4", dep_chain_4, 4 },
        { "dep_chain_8", dep_chain_8, 8 },
    };

    printf("%-15s %12s %15s %15s\n", "variant", "T(ms)", "ns/op", "cyc/op");
    printf("%-15s %12s %15s %15s\n", "------------", "------", "------", "------");

    for (size_t i = 0; i < sizeof(tests)/sizeof(tests[0]); i++) {
        double t = time_fn(tests[i].fn, 1.5);
        /* 每 op = 一条链的一次更新；总 op 数 = n_chains × N */
        double ns_per_op = t / (double)(tests[i].n_chains * N);
        double cyc_per_op = ns_per_op * 2.5;  /* 2.5 GHz */
        printf("%-15s %12.2f %15.3f %15.3f\n",
               tests[i].name, t/1e6, ns_per_op, cyc_per_op);
    }

    printf("\n  == 解读 ==\n");
    printf("  * dep_chain_1 的 cyc/op ≈ fmul_lat + fadd_lat (理论 ≈ 8 cyc)\n");
    printf("  * dep_chain_4 应该 cyc/op 明显下降（4-wide 充分并行）\n");
    printf("  * dep_chain_8 若和 _4 接近 → 重命名容量至少 8+32=40 个 PRF\n");
    return 0;
}
