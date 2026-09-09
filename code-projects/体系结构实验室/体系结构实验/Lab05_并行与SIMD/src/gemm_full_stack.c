/*
 * Lab05/src/gemm_full_stack.c — GEMM 优化全栈
 *
 * 五步走：
 *   Step 0: 朴素 O(n^3)
 *   Step 1: 循环交换 (i,j,k -> i,k,j) - cache 友好
 *   Step 2: 分块 (32x32 tile)
 *   Step 3: NEON 自动向量化 (-O3 -ftree-vectorize)
 *   Step 4: NEON intrinsic 手写
 *   Step 5: OpenMP 多核
 *
 * 测量 GFLOPS（双精度 GEMM: N^3 次 mul + N^3 次 add = 2*N^3 FLOP）
 *
 * 飞腾 D3000 理论峰值:
 *   2.5 GHz × 4-wide × 1 fmla/cyc × 2 (mul+add) = 20 GFLOPS/core
 *   8 cores = 160 GFLOPS
 *
 * 用法: ./gemm_full_stack [N]
 *   N = 矩阵维度，默认 512
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <math.h>
#include <arm_neon.h>
#include "bench.h"

#define REPS 7

/* ----- Step 0: 朴素 O(n^3)，i,j,k 顺序 ----- */
static void gemm_naive(const double *A, const double *B, double *C, int n) {
    for (int i = 0; i < n; i++)
        for (int j = 0; j < n; j++)
            for (int k = 0; k < n; k++)
                C[i*n + j] += A[i*n + k] * B[k*n + j];
}

/* ----- Step 1: 循环交换 j,k ----- */
static void gemm_ikj(const double *A, const double *B, double *C, int n) {
    for (int i = 0; i < n; i++)
        for (int k = 0; k < n; k++) {
            double a = A[i*n + k];
            for (int j = 0; j < n; j++)
                C[i*n + j] += a * B[k*n + j];
        }
}

/* ----- Step 2: 分块（32x32 tile） ----- */
static void gemm_blocked(const double *A, const double *B, double *C, int n) {
    const int BS = 32;
    for (int ii = 0; ii < n; ii += BS)
        for (int jj = 0; jj < n; jj += BS)
            for (int kk = 0; kk < n; kk += BS)
                for (int i = ii; i < ii + BS && i < n; i++)
                    for (int k = kk; k < kk + BS && k < n; k++) {
                        double a = A[i*n + k];
                        for (int j = jj; j < jj + BS && j < n; j++)
                            C[i*n + j] += a * B[k*n + j];
                    }
}

/* ----- Step 4: NEON 手写（fp32，因为飞腾 NEON 双精度只有 2-wide） ----- */
static void gemm_neon_fp32(const float *A, const float *B, float *C, int n) {
    /* 每次处理 C 的 4 行（用 4 个 v 寄存器累积） */
    for (int i = 0; i < n; i++) {
        for (int k = 0; k < n; k++) {
            float32x4_t a_v = vdupq_n_f32(A[i*n + k]);
            for (int j = 0; j + 3 < n; j += 4) {
                float32x4_t b_v = vld1q_f32(&B[k*n + j]);
                float32x4_t c_v = vld1q_f32(&C[i*n + j]);
                c_v = vfmaq_f32(c_v, a_v, b_v);  /* fmla */
                vst1q_f32(&C[i*n + j], c_v);
            }
        }
    }
}

/* ----- Step 5: OpenMP 多核 ----- */
static void gemm_ikj_omp(const double *A, const double *B, double *C, int n) {
    #pragma omp parallel for
    for (int i = 0; i < n; i++)
        for (int k = 0; k < n; k++) {
            double a = A[i*n + k];
            for (int j = 0; j < n; j++)
                C[i*n + j] += a * B[k*n + j];
        }
}

/* ----- 计时工具 ----- */
static double time_ms(void (*fn)(const double*, const double*, double*, int),
                     const double *A, const double *B, double *C, int n) {
    /* warmup */
    memset(C, 0, n*n*sizeof(double));
    fn(A, B, C, n);

    uint64_t ts[REPS];
    for (int r = 0; r < REPS; r++) {
        memset(C, 0, n*n*sizeof(double));
        uint64_t t0 = now_ns();
        fn(A, B, C, n);
        uint64_t t1 = now_ns();
        ts[r] = t1 - t0;
    }
    for (int i = 1; i < REPS; i++) {
        uint64_t k = ts[i]; int j = i;
        while (j > 0 && ts[j-1] > k) { ts[j] = ts[j-1]; j--; }
        ts[j] = k;
    }
    return (double)ts[REPS/2] / 1e6;
}

int main(int argc, char **argv) {
    int n = argc > 1 ? atoi(argv[1]) : 512;
    /* ⚠ 不 pin_to_cpu(0)：Step5 OpenMP 需要多核，旧版 pin 核0 让 8 线程全挤单核，
     * "bandwidth-bound 无加速"结论部分是绑核 bug 假象。单核步骤由 taskset 控制。*/

    double *A, *B, *C;
    posix_memalign((void**)&A, 64, n*n*sizeof(double));
    posix_memalign((void**)&B, 64, n*n*sizeof(double));
    posix_memalign((void**)&C, 64, n*n*sizeof(double));
    for (int i = 0; i < n*n; i++) {
        A[i] = (double)(i) * 0.001;
        B[i] = (double)(i + 1) * 0.001;
    }

    /* 正确性校验：在小矩阵(8×8)上对比所有版本结果一致性 */
    {
        const int vn = 8;
        double vA[64], vB[64], vC0[64], vC1[64], vC2[64], vC5[64];
        for (int i = 0; i < vn*vn; i++) { vA[i] = (double)i*0.1; vB[i] = (double)(i+1)*0.1; }
        memset(vC0,0,sizeof vC0); gemm_naive(vA,vB,vC0,vn);
        memset(vC1,0,sizeof vC1); gemm_ikj(vA,vB,vC1,vn);
        memset(vC2,0,sizeof vC2); gemm_blocked(vA,vB,vC2,vn);
        memset(vC5,0,sizeof vC5); gemm_ikj_omp(vA,vB,vC5,vn);
        int ok = 1;
        for (int i = 0; i < vn*vn; i++) {
            if (fabs(vC0[i]-vC1[i])>1e-9 || fabs(vC0[i]-vC2[i])>1e-9 || fabs(vC0[i]-vC5[i])>1e-9) { ok=0; break; }
        }
        printf("== Lab05.3: GEMM 优化全栈 (N=%d, 2.5 GHz) ==\n", n);
        printf("  正确性校验(8×8, naive=ikj=blocked=omp): %s\n\n",
               ok ? "✓ 一致" : "✗ 不一致！版本间结果不同");
    }

    printf("%-25s %12s %12s %10s\n", "method", "T(ms)", "GFLOPS", "%peak");
    printf("%-25s %12s %12s %10s\n", "-----------------------", "----------", "----------", "------");

    /* ⚠ peak 计算修正：双精度 NEON 仅 2-wide，fp32 才 4-wide。
     * 旧版 fp64 行误用 fp32 peak(20) 做分母 → %peak 高估 2×。*/
    double peak_fp64 = 2.5 * 2.0 * 2.0;  /* fp64 NEON 2-wide × fmla × 2op = 10 GFLOPS/core */
    double peak_fp32 = 2.5 * 4.0 * 2.0;  /* fp32 NEON 4-wide × fmla × 2op = 20 GFLOPS/core */
    double flops = 2.0 * (double)n * (double)n * (double)n;

    double t0 = time_ms(gemm_naive, A, B, C, n);
    printf("%-25s %12.1f %12.2f %9.1f%%\n", "0. 朴素 (i,j,k)", t0, flops/(t0*1e6), flops/(t0*1e6)/peak_fp64*100);

    double t1 = time_ms(gemm_ikj, A, B, C, n);
    printf("%-25s %12.1f %12.2f %9.1f%%\n", "1. 循环交换 (i,k,j)", t1, flops/(t1*1e6), flops/(t1*1e6)/peak_fp64*100);

    double t2 = time_ms(gemm_blocked, A, B, C, n);
    printf("%-25s %12.1f %12.2f %9.1f%%\n", "2. 分块 (32x32)", t2, flops/(t2*1e6), flops/(t2*1e6)/peak_fp64*100);

    /* NEON fp32 版本 */
    float *Af32, *Bf32, *Cf32;
    posix_memalign((void**)&Af32, 64, n*n*sizeof(float));
    posix_memalign((void**)&Bf32, 64, n*n*sizeof(float));
    posix_memalign((void**)&Cf32, 64, n*n*sizeof(float));
    for (int i = 0; i < n*n; i++) { Af32[i] = (float)A[i]; Bf32[i] = (float)B[i]; }

    {
        /* warmup */
        memset(Cf32, 0, n*n*sizeof(float));
        gemm_neon_fp32(Af32, Bf32, Cf32, n);

        uint64_t ts[REPS];
        for (int r = 0; r < REPS; r++) {
            memset(Cf32, 0, n*n*sizeof(float));
            uint64_t t0n = now_ns();
            gemm_neon_fp32(Af32, Bf32, Cf32, n);
            uint64_t t1n = now_ns();
            ts[r] = t1n - t0n;
        }
        for (int i = 1; i < REPS; i++) {
            uint64_t k = ts[i]; int j = i;
            while (j > 0 && ts[j-1] > k) { ts[j] = ts[j-1]; j--; }
            ts[j] = k;
        }
        double t3 = (double)ts[REPS/2] / 1e6;
        /* peak_fp32 已修正为 20（旧版误为 40，多乘一个 2）*/
        printf("%-25s %12.1f %12.2f %9.1f%%\n", "4. NEON 手写 (fp32)", t3, flops/(t3*1e6), flops/(t3*1e6)/peak_fp32*100);
    }

    /* OpenMP 版本 */
    double t5 = time_ms(gemm_ikj_omp, A, B, C, n);
    double peak_8c = peak_fp64 * 8.0;  /* 8 核 fp64 peak = 80 GFLOPS */
    printf("%-25s %12.1f %12.2f %9.1f%%\n", "5. OpenMP 8核 (i,k,j)", t5, flops/(t5*1e6), flops/(t5*1e6)/peak_8c*100);

    printf("\n  == 解读 ==\n");
    printf("  * peak/core: fp64=%.0f GFLOPS(2-wide), fp32=%.0f GFLOPS(4-wide)\n", peak_fp64, peak_fp32);
    printf("  * peak/8cores: fp64=%.0f GFLOPS\n", peak_8c);
    printf("  * 朴素 → 循环交换: cache miss 大幅减少\n");
    printf("  * 循环交换 → 分块: L1/L2 利用率最大化\n");
    printf("  * 分块 → NEON: SIMD 4-wide fp32 加速 ~4x\n");
    printf("  * ⚠ 单核 → 8核(双精度 ikj): 实测加速比取决于算术强度\n");
    printf("    双精度 ikj 算术强度 0.083 FLOP/byte, 偏 bandwidth-bound,\n");
    printf("    小 N 时多核有加速(本测 N=%d), 大 N(1024) 时 DDR 带宽成墙.\n", n);
    printf("    要多核高效扩展须先提高算术强度 (NEON fp32 + 寄存器分块).\n");
    printf("  * Step3(自动向量化) 见 auto_vectorize.c 单独对比.\n");

    free(A); free(B); free(C); free(Af32); free(Bf32); free(Cf32);
    return 0;
}
