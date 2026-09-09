/* ============================================================================
 * gemm_f32.c — FP32 GEMM v5 (MR=8, B-blocked, 4 FVU 全开)
 *
 * v0.6 重大发现：D3000 是 4 FVU（不是 2 FVU），MR=2 只用 1/2 算力
 * v0.7 升级：从 v4_dual (MR=2, 19.59 GFLOPS) 升级到 v5 (MR=8, ~39 GFLOPS)
 *
 * 性能（1024³）：
 *   v5 single FVU (MR=1): 10.15 GFLOPS
 *   v4 dual FVU    (MR=2): 19.59 GFLOPS
 *   v5 4-FVU       (MR=8): 39.20 GFLOPS  ← 本文件
 *
 * 理论：4 FMLA/cyc × 4 lane × 2.5 GHz = 40 GFLOPS（实测 98%）
 * ============================================================================ */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>
#include <arm_neon.h>

#define M 1024
#define K 1024
#define N 1024

/* pack B 行主 [N][K] → B_blk[N/4][K][4] */
static void pack_B_blk(const float *B, float *B_blk) {
    for (int jb = 0; jb < N / 4; jb++)
        for (int k = 0; k < K; k++)
            for (int ji = 0; ji < 4; ji++)
                B_blk[jb * K * 4 + k * 4 + ji] = B[(jb * 4 + ji) * K + k];
}

/* v5 single FVU (MR=1) — 保留作为对照 */
static void gemm_f32_v5_single(const float *A, const float *B_blk, float *C) {
    for (int i = 0; i < M; i++) {
        for (int jb = 0; jb < N / 4; jb++) {
            const float *b_base = &B_blk[jb * K * 4];
            float32x4_t c0 = vdupq_n_f32(0);
            for (int k = 0; k < K; k += 4) {
                float32x4_t a0 = vld1q_f32(&A[i * K + k]);
                float32x4_t col_0 = vld1q_f32(&b_base[(k+0)*4]);
                float32x4_t col_1 = vld1q_f32(&b_base[(k+1)*4]);
                float32x4_t col_2 = vld1q_f32(&b_base[(k+2)*4]);
                float32x4_t col_3 = vld1q_f32(&b_base[(k+3)*4]);
                c0 = vfmaq_laneq_f32(c0, col_0, a0, 0);
                c0 = vfmaq_laneq_f32(c0, col_1, a0, 1);
                c0 = vfmaq_laneq_f32(c0, col_2, a0, 2);
                c0 = vfmaq_laneq_f32(c0, col_3, a0, 3);
            }
            vst1q_f32(&C[i * N + jb*4], c0);
        }
    }
}

/* v4 dual FVU (MR=2) — 保留作为对照 */
static void gemm_f32_v4_dual(const float *A, const float *B_blk, float *C) {
    int M2 = M & ~1;
    for (int i = 0; i < M2; i += 2) {
        for (int jb = 0; jb < N / 4; jb++) {
            const float *b_base = &B_blk[jb * K * 4];
            float32x4_t c0 = vdupq_n_f32(0), c1 = vdupq_n_f32(0);
            for (int k = 0; k < K; k += 4) {
                float32x4_t a0 = vld1q_f32(&A[(i+0)*K + k]);
                float32x4_t a1 = vld1q_f32(&A[(i+1)*K + k]);
                float32x4_t col_0 = vld1q_f32(&b_base[(k+0)*4]);
                float32x4_t col_1 = vld1q_f32(&b_base[(k+1)*4]);
                float32x4_t col_2 = vld1q_f32(&b_base[(k+2)*4]);
                float32x4_t col_3 = vld1q_f32(&b_base[(k+3)*4]);
                c0 = vfmaq_laneq_f32(c0, col_0, a0, 0);
                c1 = vfmaq_laneq_f32(c1, col_0, a1, 0);
                c0 = vfmaq_laneq_f32(c0, col_1, a0, 1);
                c1 = vfmaq_laneq_f32(c1, col_1, a1, 1);
                c0 = vfmaq_laneq_f32(c0, col_2, a0, 2);
                c1 = vfmaq_laneq_f32(c1, col_2, a1, 2);
                c0 = vfmaq_laneq_f32(c0, col_3, a0, 3);
                c1 = vfmaq_laneq_f32(c1, col_3, a1, 3);
            }
            vst1q_f32(&C[(i+0)*N + jb*4], c0);
            vst1q_f32(&C[(i+1)*N + jb*4], c1);
        }
    }
}

/* v5 4-FVU (MR=8) — 最优实现，4 FVU 全开 */
static void gemm_f32_v5_mr8(const float *A, const float *B_blk, float *C) {
    int M8 = M & ~7;
    for (int i = 0; i < M8; i += 8) {
        for (int jb = 0; jb < N / 4; jb++) {
            const float *b_base = &B_blk[jb * K * 4];
            float32x4_t c0=vdupq_n_f32(0), c1=vdupq_n_f32(0),
                        c2=vdupq_n_f32(0), c3=vdupq_n_f32(0),
                        c4=vdupq_n_f32(0), c5=vdupq_n_f32(0),
                        c6=vdupq_n_f32(0), c7=vdupq_n_f32(0);
            for (int k = 0; k < K; k += 4) {
                /* v1.0 software prefetch：A 按行跨步访问(K=1024 float/行,跨cache line)，
                 * 硬件预取器跟不上，提前 32 float(8次迭代)预取盖住 L2 延迟。
                 * 仅 prefetch 行 0/4 降低指令开销(其余行在同 cache line 附近) */
                __builtin_prefetch(&A[(i+0)*K + k + 32], 0, 1);
                __builtin_prefetch(&A[(i+4)*K + k + 32], 0, 1);
                float32x4_t a0=vld1q_f32(&A[(i+0)*K+k]),a1=vld1q_f32(&A[(i+1)*K+k]);
                float32x4_t a2=vld1q_f32(&A[(i+2)*K+k]),a3=vld1q_f32(&A[(i+3)*K+k]);
                float32x4_t a4=vld1q_f32(&A[(i+4)*K+k]),a5=vld1q_f32(&A[(i+5)*K+k]);
                float32x4_t a6=vld1q_f32(&A[(i+6)*K+k]),a7=vld1q_f32(&A[(i+7)*K+k]);
                float32x4_t b0=vld1q_f32(&b_base[(k+0)*4]),b1=vld1q_f32(&b_base[(k+1)*4]);
                float32x4_t b2=vld1q_f32(&b_base[(k+2)*4]),b3=vld1q_f32(&b_base[(k+3)*4]);
                c0=vfmaq_laneq_f32(c0,b0,a0,0);c1=vfmaq_laneq_f32(c1,b0,a1,0);
                c2=vfmaq_laneq_f32(c2,b0,a2,0);c3=vfmaq_laneq_f32(c3,b0,a3,0);
                c4=vfmaq_laneq_f32(c4,b0,a4,0);c5=vfmaq_laneq_f32(c5,b0,a5,0);
                c6=vfmaq_laneq_f32(c6,b0,a6,0);c7=vfmaq_laneq_f32(c7,b0,a7,0);
                c0=vfmaq_laneq_f32(c0,b1,a0,1);c1=vfmaq_laneq_f32(c1,b1,a1,1);
                c2=vfmaq_laneq_f32(c2,b1,a2,1);c3=vfmaq_laneq_f32(c3,b1,a3,1);
                c4=vfmaq_laneq_f32(c4,b1,a4,1);c5=vfmaq_laneq_f32(c5,b1,a5,1);
                c6=vfmaq_laneq_f32(c6,b1,a6,1);c7=vfmaq_laneq_f32(c7,b1,a7,1);
                c0=vfmaq_laneq_f32(c0,b2,a0,2);c1=vfmaq_laneq_f32(c1,b2,a1,2);
                c2=vfmaq_laneq_f32(c2,b2,a2,2);c3=vfmaq_laneq_f32(c3,b2,a3,2);
                c4=vfmaq_laneq_f32(c4,b2,a4,2);c5=vfmaq_laneq_f32(c5,b2,a5,2);
                c6=vfmaq_laneq_f32(c6,b2,a6,2);c7=vfmaq_laneq_f32(c7,b2,a7,2);
                c0=vfmaq_laneq_f32(c0,b3,a0,3);c1=vfmaq_laneq_f32(c1,b3,a1,3);
                c2=vfmaq_laneq_f32(c2,b3,a2,3);c3=vfmaq_laneq_f32(c3,b3,a3,3);
                c4=vfmaq_laneq_f32(c4,b3,a4,3);c5=vfmaq_laneq_f32(c5,b3,a5,3);
                c6=vfmaq_laneq_f32(c6,b3,a6,3);c7=vfmaq_laneq_f32(c7,b3,a7,3);
            }
            vst1q_f32(&C[(i+0)*N+jb*4],c0);vst1q_f32(&C[(i+1)*N+jb*4],c1);
            vst1q_f32(&C[(i+2)*N+jb*4],c2);vst1q_f32(&C[(i+3)*N+jb*4],c3);
            vst1q_f32(&C[(i+4)*N+jb*4],c4);vst1q_f32(&C[(i+5)*N+jb*4],c5);
            vst1q_f32(&C[(i+6)*N+jb*4],c6);vst1q_f32(&C[(i+7)*N+jb*4],c7);
        }
    }
    /* 尾部 M%8 行（M=1024 是 8 倍数，但通用性保留）*/
    int M8_tail = M & ~7;
    if (M8_tail < M) {
        for (int i = M8_tail; i < M; i++) {
            for (int jb = 0; jb < N / 4; jb++) {
                const float *b_base = &B_blk[jb * K * 4];
                float32x4_t c0 = vdupq_n_f32(0);
                for (int k = 0; k < K; k += 4) {
                    float32x4_t a0 = vld1q_f32(&A[i*K + k]);
                    c0 = vfmaq_laneq_f32(c0, vld1q_f32(&b_base[(k+0)*4]), a0, 0);
                    c0 = vfmaq_laneq_f32(c0, vld1q_f32(&b_base[(k+1)*4]), a0, 1);
                    c0 = vfmaq_laneq_f32(c0, vld1q_f32(&b_base[(k+2)*4]), a0, 2);
                    c0 = vfmaq_laneq_f32(c0, vld1q_f32(&b_base[(k+3)*4]), a0, 3);
                }
                vst1q_f32(&C[i*N + jb*4], c0);
            }
        }
    }
}

static void gemm_f32_scalar(const float *A, const float *B, float *C) {
    for (int i = 0; i < M; i++)
        for (int j = 0; j < N; j++) {
            float s = 0;
            for (int k = 0; k < K; k++) s += A[i*K+k] * B[j*K+k];
            C[i*N+j] = s;
        }
}

static double now_ns() {
    struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t);
    return t.tv_sec * 1e9 + t.tv_nsec;
}

int main() {
    /* v0.9：posix_memalign 替换 malloc（性能架构师 P0.3 + OS 专家 P0.3 共识）
     * 消除 alignment penalty，D3000 NEON vld1q 对齐到 64B cache line */
    float *A=NULL,*B=NULL,*Bb=NULL,*Cv=NULL,*Cs=NULL;
    posix_memalign((void**)&A,  64, M*K*4);
    posix_memalign((void**)&B,  64, N*K*4);
    posix_memalign((void**)&Bb, 64, N*K*4);
    posix_memalign((void**)&Cv, 64, M*N*4);
    posix_memalign((void**)&Cs, 64, M*N*4);

    for (int i=0;i<M*K;i++) A[i]=(float)(i%17)/17.0f;
    for (int i=0;i<N*K;i++) B[i]=(float)(i%19)/19.0f;
    pack_B_blk(B, Bb);

    printf("=== FP32 GEMM v5 (MR=8, 4 FVU) ===\n\n");
    printf("Correctness (8x8):\n");
    gemm_f32_scalar(A, B, Cs);

    gemm_f32_v5_single(A, Bb, Cv);
    float md=0; for (int i=0;i<8;i++) for(int j=0;j<8;j++){
        float d=fabsf(Cv[i*N+j]-Cs[i*N+j]); if(d>md)md=d;}
    printf("  v5_single (MR=1)  vs scalar: %s (max_diff=%.2e)\n", md<1e-4?"✅":"❌", md);

    gemm_f32_v4_dual(A, Bb, Cv);
    md=0; for (int i=0;i<8;i++) for(int j=0;j<8;j++){
        float d=fabsf(Cv[i*N+j]-Cs[i*N+j]); if(d>md)md=d;}
    printf("  v4_dual   (MR=2)  vs scalar: %s (max_diff=%.2e)\n", md<1e-4?"✅":"❌", md);

    gemm_f32_v5_mr8(A, Bb, Cv);
    md=0; for (int i=0;i<8;i++) for(int j=0;j<8;j++){
        float d=fabsf(Cv[i*N+j]-Cs[i*N+j]); if(d>md)md=d;}
    printf("  v5_mr8    (MR=8)  vs scalar: %s (max_diff=%.2e)\n", md<1e-4?"✅":"❌", md);

    printf("\nPerformance (1024^3, 3 iter):\n");
    double gf=2.0*M*K*N, t0,t1;

    gemm_f32_v5_single(A,Bb,Cv); gemm_f32_v5_single(A,Bb,Cv);
    t0=now_ns(); for(int i=0;i<3;i++) gemm_f32_v5_single(A,Bb,Cv); t1=now_ns();
    printf("  v5_single (MR=1): %6.1f ms  %6.2f GFLOPS  (%.1f%% of 10)\n",
           (t1-t0)/3/1e6, gf*3/(t1-t0), gf*3/(t1-t0)/10*100);

    gemm_f32_v4_dual(A,Bb,Cv); gemm_f32_v4_dual(A,Bb,Cv);
    t0=now_ns(); for(int i=0;i<3;i++) gemm_f32_v4_dual(A,Bb,Cv); t1=now_ns();
    printf("  v4_dual   (MR=2): %6.1f ms  %6.2f GFLOPS  (%.1f%% of 20)\n",
           (t1-t0)/3/1e6, gf*3/(t1-t0), gf*3/(t1-t0)/20*100);

    gemm_f32_v5_mr8(A,Bb,Cv); gemm_f32_v5_mr8(A,Bb,Cv);
    t0=now_ns(); for(int i=0;i<3;i++) gemm_f32_v5_mr8(A,Bb,Cv); t1=now_ns();
    printf("  v5_mr8    (MR=8): %6.1f ms  %6.2f GFLOPS  (%.1f%% of 40)  ← 最优\n",
           (t1-t0)/3/1e6, gf*3/(t1-t0), gf*3/(t1-t0)/40*100);

    free(A);free(B);free(Bb);free(Cv);free(Cs);
    return 0;
}
