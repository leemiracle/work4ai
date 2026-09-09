/*
 * Lab05/src/auto_vectorize.c — GCC 自动向量化 vs 标量
 *
 * 同一段 dot 代码，用 __attribute__ 控制 GCC 是否自动向量化：
 *   - no-tree-vectorize: 标量，每元素一条 fmul+fadd
 *   - tree-vectorize (默认 -O3): 编译器识别可向量化，生成 fmla + ld1
 *
 * 对比性能 + objdump 看是否生成 NEON 指令。
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdint.h>
#include "bench.h"

#define N_VEC (4 * 1024 * 1024)
#define REPS  11

static float g_a[N_VEC] __attribute__((aligned(64)));
static float g_b[N_VEC] __attribute__((aligned(64)));

/* 标量版（禁止向量化）*/
static float __attribute__((noinline,optimize("no-tree-vectorize")))
dot_novec(const float *a, const float *b, int n) {
    float s = 0;
    for (int i = 0; i < n; i++) s += a[i] * b[i];
    return s;
}

/* 让编译器自动向量化（-O2 默认不开，-O3 或 optimize("tree-vectorize") 开）*/
static float __attribute__((noinline,optimize("tree-vectorize","fast-math")))
dot_autovec(const float *a, const float *b, int n) {
    float s = 0;
    for (int i = 0; i < n; i++) s += a[i] * b[i];
    return s;
}

static double time_dot(float (*fn)(const float*, const float*, int)) {
    uint64_t ts[REPS];
    for (int r = 0; r < REPS; r++) {
        uint64_t t0 = now_ns();
        volatile float s = fn(g_a, g_b, N_VEC);
        sink((uint64_t)s);
        uint64_t t1 = now_ns();
        ts[r] = t1 - t0;
    }
    for (int i = 1; i < REPS; i++) {
        uint64_t k = ts[i]; int j = i;
        while (j > 0 && ts[j-1] > k) { ts[j] = ts[j-1]; j--; }
        ts[j] = k;
    }
    return (double)ts[REPS/2];
}

int main(void) {
    pin_to_cpu(0);
    for (int i = 0; i < N_VEC; i++) { g_a[i] = (float)i*0.001f; g_b[i] = (float)(i+1)*0.001f; }

    printf("== Lab05.2: 自动向量化 vs 标量 (N=%d) ==\n\n", N_VEC);

    float s1 = dot_novec(g_a, g_b, N_VEC);
    float s2 = dot_autovec(g_a, g_b, N_VEC);
    /* 累加顺序不同致浮点精度差异（同 neon_intrinsics.c），用相对误差判定 */
    float diff = s1 - s2; if (diff < 0) diff = -diff;
    float mag  = s1 < 0 ? -s1 : s1;
    float rel  = mag > 0 ? diff / mag : 0;
    printf("  correctness: novec=%.2f  autovec=%.2f  rel_err=%.2e  %s\n\n",
           s1, s2, rel, (rel < 1e-3f) ? "✓" : "✗ (fast-math 重排差异)");

    double t_nv = time_dot(dot_novec);
    double t_av = time_dot(dot_autovec);
    double flops = 2.0 * N_VEC;

    printf("%-26s %12s %12s %10s\n", "method", "T(ms)", "GFLOPS", "speedup");
    printf("%-26s %12s %12s %10s\n", "-----", "------", "------", "-------");
    printf("%-26s %12.2f %12.2f %10s\n", "no-tree-vectorize", t_nv/1e6, flops/t_nv, "1.00x");
    printf("%-26s %12.2f %12.2f %9.2fx\n", "auto-vectorize (-O3)", t_av/1e6, flops/t_av, t_nv/t_av);

    printf("\n  == 解读 ==\n");
    printf("  * 自动向量化: GCC -O3 -ftree-vectorize 识别可并行循环，生成 NEON\n");
    printf("  * 关键: 循环必须'无依赖'（s += a[i]*b[i] 的归约可向量化，需 fast-math）\n");
    printf("  * fast-math 允许浮点重排（结合律），否则编译器不敢向量化归约\n");
    printf("  * 验证是否真向量化:\n");
    printf("    objdump -d auto_vectorize | sed -n '/<dot_autovec>:/,/ret/p' | grep -E 'fmla|ld1|fadd'\n");
    printf("    有 fmla/ld1 → 已向量化；只有 fmul/fadd → 没向量化\n");
    printf("  * 现代建议: 优先用 NEON intrinsic (neon_intrinsics.c)，不依赖编译器判断\n");
    return 0;
}
