/* 验证 D3000 真实算力：MR=8 重测 FP32/FP16/INT8 */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>
#include <arm_neon.h>

/* P0-3 安全包装：malloc/calloc/posix_memalign 失败即 perror+exit（OOM 不静默 NULL 解引用） */
static inline void* kl_xmalloc(size_t n) {
    void *p = NULL;
    if (posix_memalign(&p, 64, n)) { perror("kl_xmalloc OOM"); exit(12); }
    return p;
}
static inline void* kl_xcalloc(size_t n, size_t sz) {
    void *p = calloc(n, sz);
    if (!p) { perror("kl_xcalloc OOM"); exit(12); }
    return p;
}
static inline int kl_xposix_memalign(void **p, size_t align, size_t n) {
    int r = posix_memalign(p, align, n);
    if (r || !*p) { perror("kl_xposix_memalign OOM"); exit(12); }
    return r;
}

#define M 1024
#define K 1024
#define N 1024

static double now_ns() {
    struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t);
    return t.tv_sec * 1e9 + t.tv_nsec;
}

/* === FP32 MR=8 === */
static void pack_B_f32(const float *B, float *B_blk) {
    for (int jb = 0; jb < N/4; jb++)
        for (int k = 0; k < K; k++)
            for (int ji = 0; ji < 4; ji++)
                B_blk[jb*K*4 + k*4 + ji] = B[(jb*4+ji)*K + k];
}
static void gemm_f32_mr8(const float *A, const float *B_blk, float *C) {
    int M8 = M & ~7;
    for (int i = 0; i < M8; i += 8)
        for (int jb = 0; jb < N/4; jb++) {
            const float *b = &B_blk[jb*K*4];
            float32x4_t c0=vdupq_n_f32(0),c1=vdupq_n_f32(0),c2=vdupq_n_f32(0),c3=vdupq_n_f32(0);
            float32x4_t c4=vdupq_n_f32(0),c5=vdupq_n_f32(0),c6=vdupq_n_f32(0),c7=vdupq_n_f32(0);
            for (int k = 0; k < K; k += 4) {
                float32x4_t a0=vld1q_f32(&A[(i+0)*K+k]),a1=vld1q_f32(&A[(i+1)*K+k]);
                float32x4_t a2=vld1q_f32(&A[(i+2)*K+k]),a3=vld1q_f32(&A[(i+3)*K+k]);
                float32x4_t a4=vld1q_f32(&A[(i+4)*K+k]),a5=vld1q_f32(&A[(i+5)*K+k]);
                float32x4_t a6=vld1q_f32(&A[(i+6)*K+k]),a7=vld1q_f32(&A[(i+7)*K+k]);
                float32x4_t b0=vld1q_f32(&b[(k+0)*4]),b1=vld1q_f32(&b[(k+1)*4]);
                float32x4_t b2=vld1q_f32(&b[(k+2)*4]),b3=vld1q_f32(&b[(k+3)*4]);
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

/* === FP16 MR=8（每寄存器 8 lane）=== */
static void pack_B_f16(const __fp16 *B, __fp16 *B_blk) {
    for (int jb = 0; jb < N/8; jb++)
        for (int k = 0; k < K; k++)
            for (int ji = 0; ji < 8; ji++)
                B_blk[jb*K*8 + k*8 + ji] = B[(jb*8+ji)*K + k];
}
static void gemm_f16_mr8(const __fp16 *A, const __fp16 *B_blk, __fp16 *C) {
    int M8 = M & ~7;
    for (int i = 0; i < M8; i += 8)
        for (int jb = 0; jb < N/8; jb++) {
            const __fp16 *b = &B_blk[jb*K*8];
            float16x8_t c0=vdupq_n_f16(0),c1=vdupq_n_f16(0),c2=vdupq_n_f16(0),c3=vdupq_n_f16(0);
            float16x8_t c4=vdupq_n_f16(0),c5=vdupq_n_f16(0),c6=vdupq_n_f16(0),c7=vdupq_n_f16(0);
            for (int k = 0; k < K; k += 8) {
                float16x8_t a0=vld1q_f16(&A[(i+0)*K+k]),a1=vld1q_f16(&A[(i+1)*K+k]);
                float16x8_t a2=vld1q_f16(&A[(i+2)*K+k]),a3=vld1q_f16(&A[(i+3)*K+k]);
                float16x8_t a4=vld1q_f16(&A[(i+4)*K+k]),a5=vld1q_f16(&A[(i+5)*K+k]);
                float16x8_t a6=vld1q_f16(&A[(i+6)*K+k]),a7=vld1q_f16(&A[(i+7)*K+k]);
                for (int m = 0; m < 8; m++) { (void)m; }
                float16x8_t bm;
                bm=vld1q_f16(&b[(k+0)*8]);
                c0=vfmaq_laneq_f16(c0,bm,a0,0);c1=vfmaq_laneq_f16(c1,bm,a1,0);
                c2=vfmaq_laneq_f16(c2,bm,a2,0);c3=vfmaq_laneq_f16(c3,bm,a3,0);
                c4=vfmaq_laneq_f16(c4,bm,a4,0);c5=vfmaq_laneq_f16(c5,bm,a5,0);
                c6=vfmaq_laneq_f16(c6,bm,a6,0);c7=vfmaq_laneq_f16(c7,bm,a7,0);
                bm=vld1q_f16(&b[(k+1)*8]);
                c0=vfmaq_laneq_f16(c0,bm,a0,1);c1=vfmaq_laneq_f16(c1,bm,a1,1);
                c2=vfmaq_laneq_f16(c2,bm,a2,1);c3=vfmaq_laneq_f16(c3,bm,a3,1);
                c4=vfmaq_laneq_f16(c4,bm,a4,1);c5=vfmaq_laneq_f16(c5,bm,a5,1);
                c6=vfmaq_laneq_f16(c6,bm,a6,1);c7=vfmaq_laneq_f16(c7,bm,a7,1);
                bm=vld1q_f16(&b[(k+2)*8]);
                c0=vfmaq_laneq_f16(c0,bm,a0,2);c1=vfmaq_laneq_f16(c1,bm,a1,2);
                c2=vfmaq_laneq_f16(c2,bm,a2,2);c3=vfmaq_laneq_f16(c3,bm,a3,2);
                c4=vfmaq_laneq_f16(c4,bm,a4,2);c5=vfmaq_laneq_f16(c5,bm,a5,2);
                c6=vfmaq_laneq_f16(c6,bm,a6,2);c7=vfmaq_laneq_f16(c7,bm,a7,2);
                bm=vld1q_f16(&b[(k+3)*8]);
                c0=vfmaq_laneq_f16(c0,bm,a0,3);c1=vfmaq_laneq_f16(c1,bm,a1,3);
                c2=vfmaq_laneq_f16(c2,bm,a2,3);c3=vfmaq_laneq_f16(c3,bm,a3,3);
                c4=vfmaq_laneq_f16(c4,bm,a4,3);c5=vfmaq_laneq_f16(c5,bm,a5,3);
                c6=vfmaq_laneq_f16(c6,bm,a6,3);c7=vfmaq_laneq_f16(c7,bm,a7,3);
                bm=vld1q_f16(&b[(k+4)*8]);
                c0=vfmaq_laneq_f16(c0,bm,a0,4);c1=vfmaq_laneq_f16(c1,bm,a1,4);
                c2=vfmaq_laneq_f16(c2,bm,a2,4);c3=vfmaq_laneq_f16(c3,bm,a3,4);
                c4=vfmaq_laneq_f16(c4,bm,a4,4);c5=vfmaq_laneq_f16(c5,bm,a5,4);
                c6=vfmaq_laneq_f16(c6,bm,a6,4);c7=vfmaq_laneq_f16(c7,bm,a7,4);
                bm=vld1q_f16(&b[(k+5)*8]);
                c0=vfmaq_laneq_f16(c0,bm,a0,5);c1=vfmaq_laneq_f16(c1,bm,a1,5);
                c2=vfmaq_laneq_f16(c2,bm,a2,5);c3=vfmaq_laneq_f16(c3,bm,a3,5);
                c4=vfmaq_laneq_f16(c4,bm,a4,5);c5=vfmaq_laneq_f16(c5,bm,a5,5);
                c6=vfmaq_laneq_f16(c6,bm,a6,5);c7=vfmaq_laneq_f16(c7,bm,a7,5);
                bm=vld1q_f16(&b[(k+6)*8]);
                c0=vfmaq_laneq_f16(c0,bm,a0,6);c1=vfmaq_laneq_f16(c1,bm,a1,6);
                c2=vfmaq_laneq_f16(c2,bm,a2,6);c3=vfmaq_laneq_f16(c3,bm,a3,6);
                c4=vfmaq_laneq_f16(c4,bm,a4,6);c5=vfmaq_laneq_f16(c5,bm,a5,6);
                c6=vfmaq_laneq_f16(c6,bm,a6,6);c7=vfmaq_laneq_f16(c7,bm,a7,6);
                bm=vld1q_f16(&b[(k+7)*8]);
                c0=vfmaq_laneq_f16(c0,bm,a0,7);c1=vfmaq_laneq_f16(c1,bm,a1,7);
                c2=vfmaq_laneq_f16(c2,bm,a2,7);c3=vfmaq_laneq_f16(c3,bm,a3,7);
                c4=vfmaq_laneq_f16(c4,bm,a4,7);c5=vfmaq_laneq_f16(c5,bm,a5,7);
                c6=vfmaq_laneq_f16(c6,bm,a6,7);c7=vfmaq_laneq_f16(c7,bm,a7,7);
            }
            vst1q_f16(&C[(i+0)*N+jb*8],c0);vst1q_f16(&C[(i+1)*N+jb*8],c1);
            vst1q_f16(&C[(i+2)*N+jb*8],c2);vst1q_f16(&C[(i+3)*N+jb*8],c3);
            vst1q_f16(&C[(i+4)*N+jb*8],c4);vst1q_f16(&C[(i+5)*N+jb*8],c5);
            vst1q_f16(&C[(i+6)*N+jb*8],c6);vst1q_f16(&C[(i+7)*N+jb*8],c7);
        }
}

/* === INT8 MR=8（vdotq_s32 单 instr 16 MAC）=== */
static void pack_B_s8(const int8_t *B, int8_t *B_blk) {
    for (int jb = 0; jb < N/4; jb++)
        for (int k = 0; k < K; k++)
            for (int ji = 0; ji < 4; ji++)
                B_blk[jb*K*4 + k*4 + ji] = B[(jb*4+ji)*K + k];
}
static void gemm_s8_mr8(const int8_t *A, const int8_t *B_blk, int32_t *C) {
    int M8 = M & ~7;
    for (int i = 0; i < M8; i += 8)
        for (int jb = 0; jb < N/4; jb++) {
            const int8_t *b = &B_blk[jb*K*4];
            int32x4_t c0=vdupq_n_s32(0),c1=vdupq_n_s32(0),c2=vdupq_n_s32(0),c3=vdupq_n_s32(0);
            int32x4_t c4=vdupq_n_s32(0),c5=vdupq_n_s32(0),c6=vdupq_n_s32(0),c7=vdupq_n_s32(0);
            for (int k = 0; k < K; k += 4) {
                int32x2_t a2_0=vld1_s32((int32_t*)&A[(i+0)*K+k]);
                int32x2_t a2_1=vld1_s32((int32_t*)&A[(i+1)*K+k]);
                int32x2_t a2_2=vld1_s32((int32_t*)&A[(i+2)*K+k]);
                int32x2_t a2_3=vld1_s32((int32_t*)&A[(i+3)*K+k]);
                int32x2_t a2_4=vld1_s32((int32_t*)&A[(i+4)*K+k]);
                int32x2_t a2_5=vld1_s32((int32_t*)&A[(i+5)*K+k]);
                int32x2_t a2_6=vld1_s32((int32_t*)&A[(i+6)*K+k]);
                int32x2_t a2_7=vld1_s32((int32_t*)&A[(i+7)*K+k]);
                int8x16_t a16_0=vreinterpretq_s8_s32(vdupq_lane_s32(a2_0,0));
                int8x16_t a16_1=vreinterpretq_s8_s32(vdupq_lane_s32(a2_1,0));
                int8x16_t a16_2=vreinterpretq_s8_s32(vdupq_lane_s32(a2_2,0));
                int8x16_t a16_3=vreinterpretq_s8_s32(vdupq_lane_s32(a2_3,0));
                int8x16_t a16_4=vreinterpretq_s8_s32(vdupq_lane_s32(a2_4,0));
                int8x16_t a16_5=vreinterpretq_s8_s32(vdupq_lane_s32(a2_5,0));
                int8x16_t a16_6=vreinterpretq_s8_s32(vdupq_lane_s32(a2_6,0));
                int8x16_t a16_7=vreinterpretq_s8_s32(vdupq_lane_s32(a2_7,0));
                int8x16_t b_blk=vld1q_s8(&b[k*4]);
                c0=vdotq_s32(c0,a16_0,b_blk);c1=vdotq_s32(c1,a16_1,b_blk);
                c2=vdotq_s32(c2,a16_2,b_blk);c3=vdotq_s32(c3,a16_3,b_blk);
                c4=vdotq_s32(c4,a16_4,b_blk);c5=vdotq_s32(c5,a16_5,b_blk);
                c6=vdotq_s32(c6,a16_6,b_blk);c7=vdotq_s32(c7,a16_7,b_blk);
            }
            vst1q_s32(&C[(i+0)*N+jb*4],c0);vst1q_s32(&C[(i+1)*N+jb*4],c1);
            vst1q_s32(&C[(i+2)*N+jb*4],c2);vst1q_s32(&C[(i+3)*N+jb*4],c3);
            vst1q_s32(&C[(i+4)*N+jb*4],c4);vst1q_s32(&C[(i+5)*N+jb*4],c5);
            vst1q_s32(&C[(i+6)*N+jb*4],c6);vst1q_s32(&C[(i+7)*N+jb*4],c7);
        }
}

int main() {
    int failures = 0;
    /* FP32 */
    float *A=kl_xmalloc(M*K*4),*B=kl_xmalloc(N*K*4),*Bb=kl_xmalloc(N*K*4),*C=kl_xmalloc(M*N*4);
    for (int i=0;i<M*K;i++) A[i]=(float)(i%17)/17.0f;
    for (int i=0;i<N*K;i++) B[i]=(float)(i%19)/19.0f;
    pack_B_f32(B,Bb);
    gemm_f32_mr8(A,Bb,C); gemm_f32_mr8(A,Bb,C);
    double t0=now_ns();
    for (int it=0;it<3;it++) gemm_f32_mr8(A,Bb,C);
    double t1=now_ns();
    double gf=2.0*M*K*N*3/(t1-t0);
    printf("=== MR=8 重测（D3000 真实峰值）===\n");
    printf("  FP32 MR=8: %6.2f GFLOPS  (%.1f%% of 40)\n", gf, gf/40*100);

    /* FP16 */
    __fp16 *A16=kl_xmalloc(M*K*2),*B16=kl_xmalloc(N*K*2),*Bb16=kl_xmalloc(N*K*2),*C16=kl_xmalloc(M*N*2);
    for (int i=0;i<M*K;i++) A16[i]=(__fp16)((i%17)/100.0f);
    for (int i=0;i<N*K;i++) B16[i]=(__fp16)((i%19)/100.0f);
    pack_B_f16(B16,Bb16);
    gemm_f16_mr8(A16,Bb16,C16); gemm_f16_mr8(A16,Bb16,C16);
    t0=now_ns();
    for (int it=0;it<3;it++) gemm_f16_mr8(A16,Bb16,C16);
    t1=now_ns();
    gf=2.0*M*K*N*3/(t1-t0);
    printf("  FP16 MR=8: %6.2f GFLOPS  (%.1f%% of 80)\n", gf, gf/80*100);

    /* INT8 */
    int8_t *A8=kl_xmalloc(M*K),*B8=kl_xmalloc(N*K),*Bb8=kl_xmalloc(N*K);
    int32_t *C8=kl_xmalloc(M*N*4);
    for (int i=0;i<M*K;i++) A8[i]=(int8_t)(i%17);
    for (int i=0;i<N*K;i++) B8[i]=(int8_t)(i%11);
    pack_B_s8(B8,Bb8);
    gemm_s8_mr8(A8,Bb8,C8); gemm_s8_mr8(A8,Bb8,C8);
    t0=now_ns();
    for (int it=0;it<3;it++) gemm_s8_mr8(A8,Bb8,C8);
    t1=now_ns();
    gf=2.0*M*K*N*3/(t1-t0);
    printf("  INT8 MR=8: %6.2f GOPS   (%.1f%% of 160)\n", gf, gf/160*100);

    printf("\n  D3000 真实算力峰值（4 FVU）：\n");
    printf("    FP32 = 4 FMLA/cyc × 4 lane × 2.5 GHz = 40 GFLOPS\n");
    printf("    FP16 = 4 FMLA/cyc × 8 lane × 2.5 GHz = 80 GFLOPS\n");
    printf("    INT8 = 4 SDOT/cyc × 16 MAC × 2.5 GHz = 160 GOPS\n");
    return failures > 0;
}
