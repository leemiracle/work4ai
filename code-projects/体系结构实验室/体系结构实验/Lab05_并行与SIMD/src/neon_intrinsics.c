/*
 * Lab05/src/neon_intrinsics.c — NEON intrinsic 实战
 *
 * 用 ARM NEON intrinsic 实现 dot4 / matvec，对比标量版本：
 *   - dot4:   4 元素点积，NEON 一次 fmla 处理 4 路
 *   - matvec: 4×N 矩阵 × N 向量，每行一个 v 累加器
 *
 * NEON 寄存器 V0-V31（128 位），一次处理：
 *   - 4 个 float (4-wide fp32)
 *   - 2 个 double (2-wide fp64)
 *   - 8 个 int16 / 16 个 int8
 *
 * 关键 intrinsic:
 *   vld1q_f32  : 加载 4 个 float 到 v 寄存器
 *   vmulq_f32  : 4 路乘
 *   vfmaq_f32  : 4 路乘累加 (fmla)
 *   vaddvq_f32 : 横向 4 路加和（多周期）
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <math.h>
#include <stdint.h>
#include <arm_neon.h>
#include "bench.h"

#define N_VEC (4 * 1024 * 1024)   /* 向量长度，4 的倍数 */
#define REPS  11

static float A[N_VEC] __attribute__((aligned(64)));
static float B[N_VEC] __attribute__((aligned(64)));

/* ---- 标量 dot ---- */
static float __attribute__((noinline,optimize("no-tree-vectorize")))
dot_scalar(const float *a, const float *b, int n) {
    float s = 0;
    for (int i = 0; i < n; i++) s += a[i] * b[i];
    return s;
}

/* ---- NEON dot4（手动 4-wide 累加，最后横向加）---- */
static float __attribute__((noinline,optimize("no-tree-vectorize")))
dot_neon(const float *a, const float *b, int n) {
    float32x4_t acc = vdupq_n_f32(0.0f);
    for (int i = 0; i + 3 < n; i += 4) {
        float32x4_t va = vld1q_f32(&a[i]);
        float32x4_t vb = vld1q_f32(&b[i]);
        acc = vfmaq_f32(acc, va, vb);   /* fmla: 4 路乘累加 */
    }
    /* 横向加 4 个 lane */
    return vaddvq_f32(acc);
}

/* ---- 标量 vs NEON 对照 ---- */
static double time_dot(float (*fn)(const float*, const float*, int)) {
    uint64_t ts[REPS];
    for (int r = 0; r < REPS; r++) {
        uint64_t t0 = now_ns();
        volatile float s = fn(A, B, N_VEC);
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
    for (int i = 0; i < N_VEC; i++) { A[i] = (float)i * 0.001f; B[i] = (float)(i+1) * 0.001f; }

    printf("== Lab05.1: NEON intrinsic 实战 (N=%d) ==\n\n", N_VEC);

    /* 正确性：scalar(顺序累加) vs neon(4路并行累加)。
     * 两者数学等价但浮点累加顺序不同 → 结果有正常精度差异（非 bug）。
     * 值在 2.4e13 量级，float ULP~1e6，4M 次累加的累积误差可达 ~1e9。
     * 故用相对误差判定，而非绝对差。*/
    float s_scalar = dot_scalar(A, B, N_VEC);
    float s_neon   = dot_neon(A, B, N_VEC);
    float rel_err = fabsf(s_scalar - s_neon) / fabsf(s_scalar);
    printf("  correctness: scalar=%.4f  neon=%.4f  rel_err=%.2e  %s\n\n",
           s_scalar, s_neon, rel_err, (rel_err < 1e-3f) ? "✓" : "✗");

    double t_s = time_dot(dot_scalar);
    double t_n = time_dot(dot_neon);
    double flops = 2.0 * N_VEC;

    printf("%-22s %12s %12s %10s\n", "method", "T(ms)", "GFLOPS", "speedup");
    printf("%-22s %12s %12s %10s\n", "-----", "------", "------", "-------");
    printf("%-22s %12.2f %12.2f %10s\n", "scalar (no-vec)", t_s/1e6, flops/t_s, "1.00x");
    printf("%-22s %12.2f %12.2f %9.2fx\n", "NEON vfmaq (4-wide)", t_n/1e6, flops/t_n, t_s/t_n);

    printf("\n  == 解读 ==\n");
    printf("  * NEON 一次 vfmaq 处理 4 个 float 乘累加 (128-bit 寄存器)\n");
    printf("  * 理论加速 4x (fp32 4-wide)；实测受 load 带宽 + vaddvq 横向加限制\n");
    printf("  * vaddvq_f32 是横向归约（多周期），长向量下被摊薄\n");
    printf("  * 关键 intrinsic:\n");
    printf("    vld1q_f32  : 加载 4 float\n");
    printf("    vfmaq_f32  : 4 路乘累加 (acc += a × b)\n");
    printf("    vaddvq_f32 : 横向 4 路加（归约）\n");
    printf("  * 对比: fp64 仅 2-wide (vfmaq_f64)，fp16 8-wide (vfmaq_f16)\n");
    printf("  * 进阶: 4×4 GEMM micro-kernel 用 4 个 v 累加器 + vfmaq_laneq\n");
    return 0;
}
