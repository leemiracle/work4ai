/*
 * FTC862 GEMM Performance Benchmark
 * Tests: INT8 SDOT, FP16 FMLA, FP32 FMLA
 * Measures actual GFLOPS/GOPS on Phytium D3000 (FTC862)
 *
 * Compile:
 *   gcc -O3 -march=armv8.2-a+fp16+dotprod -o bench_gemm bench_gemm.c -lm
 *   /opt/kpgcc_release/bin/gcc -O3 -mcpu=ftc663+fp16+dotprod+crypto+crc+lse+rcpc -o bench_gemm bench_gemm.c -lm
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>
#include <math.h>

#ifdef __ARM_NEON
#include <arm_neon.h>
#endif

#define WARMUP_ITER 3
#define BENCH_ITER  20

static double get_time_ns(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec * 1e9 + (double)ts.tv_nsec;
}

/* ========== INT8 SDOT GEMM (MxK * KxN -> MxN, accumulate in int32) ========== */
static void gemm_s8_sdot(const int8_t *A, const int8_t *B, int32_t *C,
                          int M, int K, int N) {
#ifdef __ARM_FEATURE_DOTPROD
    for (int i = 0; i < M; i++) {
        for (int j = 0; j < N; j += 4) {
            int32x4_t c0 = vdupq_n_s32(0);
            for (int k = 0; k < K; k += 4) {
                int8x16_t a0 = vld1q_s8(&A[i * K + k]);
                int8x16_t b0 = vld1q_s8(&B[(j + 0) * K + k]);
                int8x16_t b1 = vld1q_s8(&B[(j + 1) * K + k]);
                int8x16_t b2 = vld1q_s8(&B[(j + 2) * K + k]);
                int8x16_t b3 = vld1q_s8(&B[(j + 3) * K + k]);
                c0 = vdotq_laneq_s32(c0, a0, b0, 0);
                c0 = vdotq_laneq_s32(c0, a0, b1, 1);
                c0 = vdotq_laneq_s32(c0, a0, b2, 2);
                c0 = vdotq_laneq_s32(c0, a0, b3, 3);
            }
            vst1q_s32(&C[i * N + j], c0);
        }
    }
#else
    for (int i = 0; i < M; i++)
        for (int j = 0; j < N; j++) {
            int32_t s = 0;
            for (int k = 0; k < K; k++)
                s += (int32_t)A[i * K + k] * (int32_t)B[j * K + k];
            C[i * N + j] = s;
        }
#endif
}

/* ========== INT8 SDOT GEMM with 2x interleaving (dual FVU test) ========== */
static void gemm_s8_sdot_dual(const int8_t *A, const int8_t *B, int32_t *C,
                               int M, int K, int N) {
#ifdef __ARM_FEATURE_DOTPROD
    for (int i = 0; i < M; i += 2) {
        for (int j = 0; j < N; j += 4) {
            int32x4_t c0 = vdupq_n_s32(0);
            int32x4_t c1 = vdupq_n_s32(0);
            for (int k = 0; k < K; k += 4) {
                int8x16_t a0 = vld1q_s8(&A[(i + 0) * K + k]);
                int8x16_t a1 = vld1q_s8(&A[(i + 1) * K + k]);
                int8x16_t b0 = vld1q_s8(&B[(j + 0) * K + k]);
                int8x16_t b1 = vld1q_s8(&B[(j + 1) * K + k]);
                int8x16_t b2 = vld1q_s8(&B[(j + 2) * K + k]);
                int8x16_t b3 = vld1q_s8(&B[(j + 3) * K + k]);
                c0 = vdotq_laneq_s32(c0, a0, b0, 0);
                c1 = vdotq_laneq_s32(c1, a1, b0, 0);
                c0 = vdotq_laneq_s32(c0, a0, b1, 1);
                c1 = vdotq_laneq_s32(c1, a1, b1, 1);
                c0 = vdotq_laneq_s32(c0, a0, b2, 2);
                c1 = vdotq_laneq_s32(c1, a1, b2, 2);
                c0 = vdotq_laneq_s32(c0, a0, b3, 3);
                c1 = vdotq_laneq_s32(c1, a1, b3, 3);
            }
            vst1q_s32(&C[(i + 0) * N + j], c0);
            vst1q_s32(&C[(i + 1) * N + j], c1);
        }
    }
#else
    gemm_s8_sdot(A, B, C, M, K, N);
#endif
}

/* ========== FP16 FMLA GEMM ========== */
static void gemm_f16(const __fp16 *A, const __fp16 *B, __fp16 *C,
                      int M, int K, int N) {
#ifdef __ARM_FEATURE_FP16_VECTOR_ARITHMETIC
    for (int i = 0; i < M; i++) {
        for (int j = 0; j < N; j += 8) {
            float16x8_t c0 = vdupq_n_f16(0);
            for (int k = 0; k < K; k += 8) {
                float16x8_t a0 = vld1q_f16(&A[i * K + k]);
                float16x8_t b0 = vld1q_f16(&B[(j + 0) * K + k]);
                float16x8_t b1 = vld1q_f16(&B[(j + 1) * K + k]);
                float16x8_t b2 = vld1q_f16(&B[(j + 2) * K + k]);
                float16x8_t b3 = vld1q_f16(&B[(j + 3) * K + k]);
                float16x8_t b4 = vld1q_f16(&B[(j + 4) * K + k]);
                float16x8_t b5 = vld1q_f16(&B[(j + 5) * K + k]);
                float16x8_t b6 = vld1q_f16(&B[(j + 6) * K + k]);
                float16x8_t b7 = vld1q_f16(&B[(j + 7) * K + k]);
                c0 = vfmaq_laneq_f16(c0, a0, b0, 0);
                c0 = vfmaq_laneq_f16(c0, a0, b1, 1);
                c0 = vfmaq_laneq_f16(c0, a0, b2, 2);
                c0 = vfmaq_laneq_f16(c0, a0, b3, 3);
                c0 = vfmaq_laneq_f16(c0, a0, b4, 4);
                c0 = vfmaq_laneq_f16(c0, a0, b5, 5);
                c0 = vfmaq_laneq_f16(c0, a0, b6, 6);
                c0 = vfmaq_laneq_f16(c0, a0, b7, 7);
            }
            vst1q_f16(&C[i * N + j], c0);
        }
    }
#else
    for (int i = 0; i < M; i++)
        for (int j = 0; j < N; j++) {
            float s = 0;
            for (int k = 0; k < K; k++)
                s += (float)A[i * K + k] * (float)B[j * K + k];
            C[i * N + j] = (__fp16)s;
        }
#endif
}

/* ========== FP32 FMLA GEMM ========== */
static void gemm_f32(const float *A, const float *B, float *C,
                      int M, int K, int N) {
#ifdef __ARM_NEON
    for (int i = 0; i < M; i++) {
        for (int j = 0; j < N; j += 4) {
            float32x4_t c0 = vdupq_n_f32(0);
            for (int k = 0; k < K; k += 4) {
                float32x4_t a0 = vld1q_f32(&A[i * K + k]);
                float32x4_t b0 = vld1q_f32(&B[(j + 0) * K + k]);
                float32x4_t b1 = vld1q_f32(&B[(j + 1) * K + k]);
                float32x4_t b2 = vld1q_f32(&B[(j + 2) * K + k]);
                float32x4_t b3 = vld1q_f32(&B[(j + 3) * K + k]);
                c0 = vfmaq_laneq_f32(c0, a0, b0, 0);
                c0 = vfmaq_laneq_f32(c0, a0, b1, 1);
                c0 = vfmaq_laneq_f32(c0, a0, b2, 2);
                c0 = vfmaq_laneq_f32(c0, a0, b3, 3);
            }
            vst1q_f32(&C[i * N + j], c0);
        }
    }
#else
    for (int i = 0; i < M; i++)
        for (int j = 0; j < N; j++) {
            float s = 0;
            for (int k = 0; k < K; k++)
                s += A[i * K + k] * B[j * K + k];
            C[i * N + j] = s;
        }
#endif
}

/* ========== FP32 FMLA GEMM with 2x M-row interleave (dual FVU) ==========
 * D3000 (FTC862) has dual FP32 FMLA throughput when 2 independent
 * accumulators are kept alive. Same memory traffic → 2x compute.
 * Pattern matches gemm_s8_sdot_dual above.
 * ===================================================================== */
static void gemm_f32_dual(const float *A, const float *B, float *C,
                           int M, int K, int N) {
#ifdef __ARM_NEON
    /* M must be even for 2-row interleave; fall back if odd */
    int M2 = M & ~1;
    for (int i = 0; i < M2; i += 2) {
        for (int j = 0; j < N; j += 4) {
            float32x4_t c0 = vdupq_n_f32(0);
            float32x4_t c1 = vdupq_n_f32(0);
            for (int k = 0; k < K; k += 4) {
                float32x4_t a0 = vld1q_f32(&A[(i + 0) * K + k]);
                float32x4_t a1 = vld1q_f32(&A[(i + 1) * K + k]);
                float32x4_t b0 = vld1q_f32(&B[(j + 0) * K + k]);
                float32x4_t b1 = vld1q_f32(&B[(j + 1) * K + k]);
                float32x4_t b2 = vld1q_f32(&B[(j + 2) * K + k]);
                float32x4_t b3 = vld1q_f32(&B[(j + 3) * K + k]);
                c0 = vfmaq_laneq_f32(c0, a0, b0, 0);
                c1 = vfmaq_laneq_f32(c1, a1, b0, 0);
                c0 = vfmaq_laneq_f32(c0, a0, b1, 1);
                c1 = vfmaq_laneq_f32(c1, a1, b1, 1);
                c0 = vfmaq_laneq_f32(c0, a0, b2, 2);
                c1 = vfmaq_laneq_f32(c1, a1, b2, 2);
                c0 = vfmaq_laneq_f32(c0, a0, b3, 3);
                c1 = vfmaq_laneq_f32(c1, a1, b3, 3);
            }
            vst1q_f32(&C[(i + 0) * N + j], c0);
            vst1q_f32(&C[(i + 1) * N + j], c1);
        }
    }
    /* Tail row if M was odd */
    if (M & 1) {
        int i = M - 1;
        for (int j = 0; j < N; j += 4) {
            float32x4_t c0 = vdupq_n_f32(0);
            for (int k = 0; k < K; k += 4) {
                float32x4_t a0 = vld1q_f32(&A[i * K + k]);
                float32x4_t b0 = vld1q_f32(&B[(j + 0) * K + k]);
                float32x4_t b1 = vld1q_f32(&B[(j + 1) * K + k]);
                float32x4_t b2 = vld1q_f32(&B[(j + 2) * K + k]);
                float32x4_t b3 = vld1q_f32(&B[(j + 3) * K + k]);
                c0 = vfmaq_laneq_f32(c0, a0, b0, 0);
                c0 = vfmaq_laneq_f32(c0, a0, b1, 1);
                c0 = vfmaq_laneq_f32(c0, a0, b2, 2);
                c0 = vfmaq_laneq_f32(c0, a0, b3, 3);
            }
            vst1q_f32(&C[i * N + j], c0);
        }
    }
#else
    gemm_f32(A, B, C, M, K, N);
#endif
}

/* ========== Scalar naive GEMM for correctness check ========== */
static void gemm_f32_scalar(const float *A, const float *B, float *C,
                             int M, int K, int N) {
    for (int i = 0; i < M; i++)
        for (int j = 0; j < N; j++) {
            float s = 0;
            for (int k = 0; k < K; k++)
                s += A[i * K + k] * B[j * K + k];
            C[i * N + j] = s;
        }
}

static void fill_random_f32(float *p, int n) {
    for (int i = 0; i < n; i++) p[i] = (float)(rand() % 1000) / 500.0f - 1.0f;
}
static void fill_random_f16(__fp16 *p, int n) {
    for (int i = 0; i < n; i++) p[i] = (__fp16)((float)(rand() % 1000) / 500.0f - 1.0f);
}
static void fill_random_s8(int8_t *p, int n) {
    for (int i = 0; i < n; i++) p[i] = (int8_t)(rand() % 256 - 128);
}

/* ========== Micro-kernel standalone throughput test ========== */
/* Pure SDOT throughput: no load/store, just MACs on registers */
static void bench_sdot_raw(int iters) {
#ifdef __ARM_FEATURE_DOTPROD
    int32x4_t acc0 = vdupq_n_s32(0);
    int32x4_t acc1 = vdupq_n_s32(0);
    int8x16_t va = vdupq_n_s8(1);
    int8x16_t vb = vdupq_n_s8(2);
    double t0 = get_time_ns();
    for (int i = 0; i < iters; i++) {
        acc0 = vdotq_s32(acc0, va, vb);
        acc1 = vdotq_s32(acc1, va, vb);
        acc0 = vdotq_s32(acc0, va, vb);
        acc1 = vdotq_s32(acc1, va, vb);
        acc0 = vdotq_s32(acc0, va, vb);
        acc1 = vdotq_s32(acc1, va, vb);
        acc0 = vdotq_s32(acc0, va, vb);
        acc1 = vdotq_s32(acc1, va, vb);
    }
    double t1 = get_time_ns();
    double ops = (double)iters * 8 * 4 * 4;
    double sec = (t1 - t0) / 1e9;
    printf("  SDOT raw throughput (dual acc):  %8.2f GOPS (%.0f ns / %d iter)\n",
           ops / sec / 1e9, t1 - t0, iters);
    volatile int32_t sink = vgetq_lane_s32(acc0, 0) + vgetq_lane_s32(acc1, 0);
    (void)sink;
#endif
}

/* Pure FMLA FP16 throughput */
static void bench_fmla_f16_raw(int iters) {
#ifdef __ARM_FEATURE_FP16_VECTOR_ARITHMETIC
    float16x8_t acc0 = vdupq_n_f16(0);
    float16x8_t acc1 = vdupq_n_f16(0);
    float16x8_t va = vdupq_n_f16(1.0f);
    float16x8_t vb = vdupq_n_f16(1.0f);
    double t0 = get_time_ns();
    for (int i = 0; i < iters; i++) {
        acc0 = vfmaq_f16(acc0, va, vb);
        acc1 = vfmaq_f16(acc1, va, vb);
        acc0 = vfmaq_f16(acc0, va, vb);
        acc1 = vfmaq_f16(acc1, va, vb);
        acc0 = vfmaq_f16(acc0, va, vb);
        acc1 = vfmaq_f16(acc1, va, vb);
        acc0 = vfmaq_f16(acc0, va, vb);
        acc1 = vfmaq_f16(acc1, va, vb);
    }
    double t1 = get_time_ns();
    double ops = (double)iters * 8 * 2 * 8;
    double sec = (t1 - t0) / 1e9;
    printf("  FMLA F16 raw throughput (dual acc): %8.2f GFLOPS (%.0f ns / %d iter)\n",
           ops / sec / 1e9, t1 - t0, iters);
    volatile float16_t sink = vgetq_lane_f16(acc0, 0) + vgetq_lane_f16(acc1, 0);
    (void)sink;
#endif
}

/* Pure FMLA FP32 throughput */
static void bench_fmla_f32_raw(int iters) {
#ifdef __ARM_NEON
    float32x4_t acc0 = vdupq_n_f32(0);
    float32x4_t acc1 = vdupq_n_f32(0);
    float32x4_t va = vdupq_n_f32(1.0f);
    float32x4_t vb = vdupq_n_f32(1.0f);
    double t0 = get_time_ns();
    for (int i = 0; i < iters; i++) {
        acc0 = vfmaq_f32(acc0, va, vb);
        acc1 = vfmaq_f32(acc1, va, vb);
        acc0 = vfmaq_f32(acc0, va, vb);
        acc1 = vfmaq_f32(acc1, va, vb);
        acc0 = vfmaq_f32(acc0, va, vb);
        acc1 = vfmaq_f32(acc1, va, vb);
        acc0 = vfmaq_f32(acc0, va, vb);
        acc1 = vfmaq_f32(acc1, va, vb);
    }
    double t1 = get_time_ns();
    double ops = (double)iters * 8 * 2 * 4;
    double sec = (t1 - t0) / 1e9;
    printf("  FMLA F32 raw throughput (dual acc): %8.2f GFLOPS (%.0f ns / %d iter)\n",
           ops / sec / 1e9, t1 - t0, iters);
    volatile float sink = vgetq_lane_f32(acc0, 0) + vgetq_lane_f32(acc1, 0);
    (void)sink;
#endif
}

int main(int argc, char *argv[]) {
    printf("=== FTC862 (Phytium D3000) GEMM Performance Benchmark ===\n");
    printf("Compiler: GCC %d.%d.%d\n", __GNUC__, __GNUC_MINOR__, __GNUC_PATCHLEVEL__);
#ifdef __ARM_FEATURE_DOTPROD
    printf("DOTPROD:  ENABLED\n");
#else
    printf("DOTPROD:  DISABLED\n");
#endif
#ifdef __ARM_FEATURE_FP16_VECTOR_ARITHMETIC
    printf("FP16VEC:  ENABLED\n");
#else
    printf("FP16VEC:  DISABLED\n");
#endif
#ifdef __ARM_NEON
    printf("NEON:     ENABLED\n");
#endif
    printf("\n");

    int M_sizes[] = {64, 128, 256, 512};
    int K_sizes[] = {64, 128, 256, 512};
    int N_sizes[] = {64, 128, 256, 512};
    int nsizes = 4;

    srand(42);

    /* ---- Raw throughput tests ---- */
    printf("--- Raw Instruction Throughput (single core, register-only) ---\n");
    bench_sdot_raw(10000000);
    bench_fmla_f16_raw(10000000);
    bench_fmla_f32_raw(10000000);
    printf("\n");

    /* ---- INT8 SDOT GEMM ---- */
    printf("--- INT8 SDOT GEMM (single core) ---\n");
    printf("  %6s %6s %6s | %10s | %10s | %5s\n", "M", "K", "N", "Time(ms)", "GOPS", "Eff%");
    printf("  ------+------+------+------------+-----------+------\n");
    for (int si = 0; si < nsizes; si++) {
        int M = M_sizes[si], K = K_sizes[si], N = N_sizes[si];
        int8_t *A = malloc(M * K); fill_random_s8(A, M * K);
        int8_t *B = malloc(N * K); fill_random_s8(B, N * K);
        int32_t *C = malloc(M * N * sizeof(int32_t));
        double peak_gops = 16.0 * 2.5;  /* single FVU: 16 MAC/cyc */

        for (int w = 0; w < WARMUP_ITER; w++)
            gemm_s8_sdot(A, B, C, M, K, N);
        double t0 = get_time_ns();
        for (int b = 0; b < BENCH_ITER; b++)
            gemm_s8_sdot(A, B, C, M, K, N);
        double t1 = get_time_ns();
        double ms = (t1 - t0) / BENCH_ITER / 1e6;
        double gops = 2.0 * M * K * N / ((t1 - t0) / BENCH_ITER);
        printf("  %6d %6d %6d | %10.3f | %10.2f | %4.1f%%\n",
               M, K, N, ms, gops, gops / peak_gops * 100);
        free(A); free(B); free(C);
    }

    /* ---- INT8 SDOT GEMM dual-FVU ---- */
    printf("\n--- INT8 SDOT GEMM 2-row interleave (dual FVU test) ---\n");
    printf("  %6s %6s %6s | %10s | %10s | %5s\n", "M", "K", "N", "Time(ms)", "GOPS", "Eff%");
    printf("  ------+------+------+------------+-----------+------\n");
    for (int si = 0; si < nsizes; si++) {
        int M = M_sizes[si] * 2, K = K_sizes[si], N = N_sizes[si];
        if (M % 2) M++;
        int8_t *A = malloc(M * K); fill_random_s8(A, M * K);
        int8_t *B = malloc(N * K); fill_random_s8(B, N * K);
        int32_t *C = malloc(M * N * sizeof(int32_t));
        double peak_gops = 32.0 * 2.5;

        for (int w = 0; w < WARMUP_ITER; w++)
            gemm_s8_sdot_dual(A, B, C, M, K, N);
        double t0 = get_time_ns();
        for (int b = 0; b < BENCH_ITER; b++)
            gemm_s8_sdot_dual(A, B, C, M, K, N);
        double t1 = get_time_ns();
        double ms = (t1 - t0) / BENCH_ITER / 1e6;
        double gops = 2.0 * M * K * N / ((t1 - t0) / BENCH_ITER);
        printf("  %6d %6d %6d | %10.3f | %10.2f | %4.1f%%\n",
               M, K, N, ms, gops, gops / peak_gops * 100);
        free(A); free(B); free(C);
    }

    /* ---- FP16 FMLA GEMM ---- */
    printf("\n--- FP16 FMLA GEMM (single core) ---\n");
    printf("  %6s %6s %6s | %10s | %10s | %5s\n", "M", "K", "N", "Time(ms)", "GFLOPS", "Eff%");
    printf("  ------+------+------+------------+-----------+------\n");
    for (int si = 0; si < nsizes; si++) {
        int M = M_sizes[si], K = K_sizes[si], N = N_sizes[si];
        __fp16 *A = malloc(M * K * sizeof(__fp16)); fill_random_f16(A, M * K);
        __fp16 *B = malloc(N * K * sizeof(__fp16)); fill_random_f16(B, N * K);
        __fp16 *C = malloc(M * N * sizeof(__fp16));
        double peak_gflops = 8.0 * 2.5;  /* single FVU: 8 MAC/cyc */

        for (int w = 0; w < WARMUP_ITER; w++)
            gemm_f16(A, B, C, M, K, N);
        double t0 = get_time_ns();
        for (int b = 0; b < BENCH_ITER; b++)
            gemm_f16(A, B, C, M, K, N);
        double t1 = get_time_ns();
        double ms = (t1 - t0) / BENCH_ITER / 1e6;
        double gflops = 2.0 * M * K * N / ((t1 - t0) / BENCH_ITER);
        printf("  %6d %6d %6d | %10.3f | %10.2f | %4.1f%%\n",
               M, K, N, ms, gflops, gflops / peak_gflops * 100);
        free(A); free(B); free(C);
    }

    /* ---- FP32 FMLA GEMM ---- */
    printf("\n--- FP32 FMLA GEMM (single core) ---\n");
    printf("  %6s %6s %6s | %10s | %10s | %5s\n", "M", "K", "N", "Time(ms)", "GFLOPS", "Eff%");
    printf("  ------+------+------+------------+-----------+------\n");
    for (int si = 0; si < nsizes; si++) {
        int M = M_sizes[si], K = K_sizes[si], N = N_sizes[si];
        float *A = malloc(M * K * sizeof(float)); fill_random_f32(A, M * K);
        float *B = malloc(N * K * sizeof(float)); fill_random_f32(B, N * K);
        float *C = malloc(M * N * sizeof(float));
        double peak_gflops = 4.0 * 2.5;  /* single FVU: 4 MAC/cyc */

        for (int w = 0; w < WARMUP_ITER; w++)
            gemm_f32(A, B, C, M, K, N);
        double t0 = get_time_ns();
        for (int b = 0; b < BENCH_ITER; b++)
            gemm_f32(A, B, C, M, K, N);
        double t1 = get_time_ns();
        double ms = (t1 - t0) / BENCH_ITER / 1e6;
        double gflops = 2.0 * M * K * N / ((t1 - t0) / BENCH_ITER);
        printf("  %6d %6d %6d | %10.3f | %10.2f | %4.1f%%\n",
               M, K, N, ms, gflops, gflops / peak_gflops * 100);
        free(A); free(B); free(C);
    }

    /* ---- Large-scale GEMM (near-cache-boundary sizes) ---- */
    printf("\n--- Large GEMM (cache boundary analysis, single core) ---\n");
    int lg_sizes[][3] = {
        {128, 1024, 128},
        {256, 1024, 256},
        {512, 1024, 512},
        {256, 4096, 256},
        {512, 4096, 512},
        {1024, 1024, 1024},
    };
    int nlg = sizeof(lg_sizes) / sizeof(lg_sizes[0]);
    printf("  %6s %6s %6s | %10s | %10s | %5s | %s\n",
           "M", "K", "N", "Time(ms)", "GFLOPS", "Eff%", "Note");
    printf("  ------+------+------+------------+-----------+------+--------\n");
    for (int si = 0; si < nlg; si++) {
        int M = lg_sizes[si][0], K = lg_sizes[si][1], N = lg_sizes[si][2];
        float *A = malloc(M * K * sizeof(float)); fill_random_f32(A, M * K);
        float *B = malloc(N * K * sizeof(float)); fill_random_f32(B, N * K);
        float *C = malloc(M * N * sizeof(float));
        double peak_gflops = 4.0 * 2.5;  /* single FVU: 4 MAC/cyc */

        int bench_iter = (M * K * N > 64*1024*1024) ? 5 : BENCH_ITER;
        for (int w = 0; w < 2; w++)
            gemm_f32(A, B, C, M, K, N);
        double t0 = get_time_ns();
        for (int b = 0; b < bench_iter; b++)
            gemm_f32(A, B, C, M, K, N);
        double t1 = get_time_ns();
        double ms = (t1 - t0) / bench_iter / 1e6;
        double gflops = 2.0 * M * K * N / ((t1 - t0) / bench_iter);

        const char *note = "";
        long long data_bytes = (long long)M * K + (long long)N * K + (long long)M * N;
        data_bytes *= sizeof(float);
        if (data_bytes < 32 * 1024) note = "< L1D";
        else if (data_bytes < 512 * 1024) note = "< L2";
        else if (data_bytes < 4 * 1024 * 1024) note = "< L3(cluster)";
        else if (data_bytes < 8 * 1024 * 1024) note = "L3+SLC";
        else note = "> all cache";

        printf("  %6d %6d %6d | %10.3f | %10.2f | %4.1f%% | %s\n",
               M, K, N, ms, gflops, gflops / peak_gflops * 100, note);
        free(A); free(B); free(C);
    }

    /* ---- Large-scale GEMM: single vs dual FVU head-to-head ----
     * Same matrices, same data layout. Only difference is the kernel.
     * Reveals whether the data path can feed dual FVU (peak = 2x). */
    printf("\n--- Large GEMM: single vs dual FVU (single core) ---\n");
    printf("  %6s %6s %6s | %10s | %10s | %10s | %10s | %s\n",
           "M", "K", "N", "single ms", "single GF", "dual ms", "dual GF", "speedup");
    printf("  ------+------+------+------------+-----------+------------+-----------+---------\n");
    {
        int dual_sizes[][3] = {
            {128, 1024, 128},
            {256, 1024, 256},
            {512, 1024, 512},
            {1024, 1024, 1024},
        };
        int ndual = sizeof(dual_sizes) / sizeof(dual_sizes[0]);
        for (int si = 0; si < ndual; si++) {
            int M = dual_sizes[si][0], K = dual_sizes[si][1], N = dual_sizes[si][2];
            if (M & 1) M++;  /* ensure even for dual FVU */
            float *A = malloc(M * K * sizeof(float)); fill_random_f32(A, M * K);
            float *B = malloc(N * K * sizeof(float)); fill_random_f32(B, N * K);
            float *C = malloc(M * N * sizeof(float));

            int iter = (M * K * N > 64*1024*1024) ? 5 : BENCH_ITER;

            /* warmup both */
            for (int w = 0; w < 2; w++) { gemm_f32(A, B, C, M, K, N); gemm_f32_dual(A, B, C, M, K, N); }

            double t0 = get_time_ns();
            for (int b = 0; b < iter; b++) gemm_f32(A, B, C, M, K, N);
            double t1 = get_time_ns();
            double ms_s = (t1 - t0) / iter / 1e6;
            double gf_s = 2.0 * M * K * N / ((t1 - t0) / iter);

            t0 = get_time_ns();
            for (int b = 0; b < iter; b++) gemm_f32_dual(A, B, C, M, K, N);
            t1 = get_time_ns();
            double ms_d = (t1 - t0) / iter / 1e6;
            double gf_d = 2.0 * M * K * N / ((t1 - t0) / iter);

            printf("  %6d %6d %6d | %10.3f | %10.2f | %10.3f | %10.2f | %5.2fx\n",
                   M, K, N, ms_s, gf_s, ms_d, gf_d, gf_d / gf_s);
            free(A); free(B); free(C);
        }
    }

    printf("\n--- Peak Theoretical (single core @ 2.5GHz) ---\n");
    printf("  INT8 SDOT: 32 MAC/cyc * 2.5 GHz = 80.0 GOPS (dual FVU)\n");
    printf("  FP16 FMLA: 16 MAC/cyc * 2.5 GHz = 40.0 GFLOPS (dual FVU)\n");
    printf("  FP32 FMLA:  8 MAC/cyc * 2.5 GHz = 20.0 GFLOPS (dual FVU)\n");
    printf("  FP32 FMLA:  4 MAC/cyc * 2.5 GHz = 10.0 GFLOPS (single FVU)\n");

    return 0;
}
