/* ============================================================================
 * gemm_s8.c — INT8 SDOT GEMM v5 (MR=8, 4 FVU 全开) + B 块化布局
 *
 * v0.6 发现：D3000 是 4 FVU（不是 2 FVU），MR=2 只用 1/2 算力
 * v0.8 升级：从 v4_dual (MR=2) 升级到 v5 (MR=8, ~78 GOPS)
 *
 * 正确算法（关键洞察）：
 *   vdotq_s32(c, a, b) 是 4 个独立 dot product：
 *     c[i] += sum_m a[i*4+m] × b[i*4+m]  for i=0..3
 *
 *   把 a 4 字节复制 4 次成 16 字节，b 取 4×4 块（4 个 j × 4 个 k）：
 *     c[i] += sum_m A[i_row][k+m] × B[j+i][k+m]  ✓
 *
 * v5_mr8：M 维并行 8 累加器 c0..c7，单条 vdotq 单 instr 16 MAC
 *
 * B 块布局：B_blk[j_block][k][j_inner_4]，j_inner 在最内（16 字节连续）
 * ============================================================================ */
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

/* pack B 行主 [N][K] → B_blk[N/4][K][4]（每个 j_block 是 4 行）*/
static void pack_B_blk_s8(const int8_t *B, int8_t *B_blk) {
    for (int jb = 0; jb < N / 4; jb++) {
        for (int k = 0; k < K; k++) {
            for (int ji = 0; ji < 4; ji++) {
                B_blk[jb * K * 4 + k * 4 + ji] = B[(jb * 4 + ji) * K + k];
            }
        }
    }
}

/* INT8 v4 single FVU：B 块化 + vdotq_s32 */
static void gemm_s8_v4_single(const int8_t *A, const int8_t *B_blk, int32_t *C) {
    for (int i = 0; i < M; i++) {
        for (int jb = 0; jb < N / 4; jb++) {
            int j = jb * 4;
            const int8_t *b_base = &B_blk[jb * K * 4];
            int32x4_t c0 = vdupq_n_s32(0);
            for (int k = 0; k < K; k += 4) {
                /* A[i][k..k+3] 复制成 16 字节 */
                int32x2_t a2 = vld1_s32((const int32_t*)&A[i * K + k]);
                int32x4_t a4 = vdupq_lane_s32(a2, 0);
                int8x16_t a16 = vreinterpretq_s8_s32(a4);
                /* B_blk 的 4×4 块：4 个 j × 4 个 k */
                int8x16_t b_blk = vld1q_s8(&b_base[k * 4]);
                /* c0[i] += sum_m A[i][k+m] × B[j+i][k+m] */
                c0 = vdotq_s32(c0, a16, b_blk);
            }
            vst1q_s32(&C[i * N + j], c0);
        }
    }
}

/* INT8 v4 dual FVU：M 维并行 2 累加器 */
static void gemm_s8_v4_dual(const int8_t *A, const int8_t *B_blk, int32_t *C) {
    int M2 = M & ~1;
    for (int i = 0; i < M2; i += 2) {
        for (int jb = 0; jb < N / 4; jb++) {
            int j = jb * 4;
            const int8_t *b_base = &B_blk[jb * K * 4];
            int32x4_t c0 = vdupq_n_s32(0);
            int32x4_t c1 = vdupq_n_s32(0);
            for (int k = 0; k < K; k += 4) {
                int32x2_t a2_0 = vld1_s32((const int32_t*)&A[(i+0) * K + k]);
                int32x2_t a2_1 = vld1_s32((const int32_t*)&A[(i+1) * K + k]);
                int8x16_t a16_0 = vreinterpretq_s8_s32(vdupq_lane_s32(a2_0, 0));
                int8x16_t a16_1 = vreinterpretq_s8_s32(vdupq_lane_s32(a2_1, 0));
                int8x16_t b_blk = vld1q_s8(&b_base[k * 4]);
                c0 = vdotq_s32(c0, a16_0, b_blk);
                c1 = vdotq_s32(c1, a16_1, b_blk);
            }
            vst1q_s32(&C[(i+0) * N + j], c0);
            vst1q_s32(&C[(i+1) * N + j], c1);
        }
    }
}

/* v5 4-FVU (MR=8) — 最优实现，M 维并行 8 累加器
 * 寄存器：8(c s32) + 8(a16 s8) + 1(b_blk) = 17 reg */
static void gemm_s8_v5_mr8(const int8_t *A, const int8_t *B_blk, int32_t *C) {
    int M8 = M & ~7;
    for (int i = 0; i < M8; i += 8) {
        for (int jb = 0; jb < N / 4; jb++) {
            const int8_t *b = &B_blk[jb * K * 4];
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
    /* 尾部 M%8 行 */
    int M8_tail = M & ~7;
    if (M8_tail < M) {
        for (int i = M8_tail; i < M; i++) {
            for (int jb = 0; jb < N / 4; jb++) {
                const int8_t *b_base = &B_blk[jb * K * 4];
                int32x4_t c0 = vdupq_n_s32(0);
                for (int k = 0; k < K; k += 4) {
                    int32x2_t a2 = vld1_s32((const int32_t*)&A[i * K + k]);
                    int8x16_t a16 = vreinterpretq_s8_s32(vdupq_lane_s32(a2, 0));
                    int8x16_t b_blk = vld1q_s8(&b_base[k * 4]);
                    c0 = vdotq_s32(c0, a16, b_blk);
                }
                vst1q_s32(&C[i * N + jb*4], c0);
            }
        }
    }
}

static void gemm_s8_scalar(const int8_t *A, const int8_t *B, int32_t *C) {
    for (int i = 0; i < M; i++)
        for (int j = 0; j < N; j++) {
            int32_t s = 0;
            for (int k = 0; k < K; k++)
                s += (int32_t)A[i * K + k] * (int32_t)B[j * K + k];
            C[i * N + j] = s;
        }
}

static double time_it_s8(void (*fn)(const int8_t*, const int8_t*, int32_t*),
                         const int8_t *A, const int8_t *B, int32_t *C, int iter) {
    struct timespec t0, t1;
    for (int w = 0; w < 2; w++) fn(A, B, C);
    clock_gettime(CLOCK_MONOTONIC, &t0);
    for (int it = 0; it < iter; it++) fn(A, B, C);
    clock_gettime(CLOCK_MONOTONIC, &t1);
    return (t1.tv_sec - t0.tv_sec) * 1e9 + (t1.tv_nsec - t0.tv_nsec);
}

int main() {
    int failures = 0;
    int8_t *A = kl_xmalloc(M * K);
    int8_t *B = kl_xmalloc(N * K);
    int8_t *B_blk = kl_xmalloc(N * K);
    int32_t *Cv = kl_xmalloc(M * N * sizeof(int32_t));
    int32_t *Cs = kl_xmalloc(M * N * sizeof(int32_t));

    for (int i = 0; i < M * K; i++) A[i] = (int8_t)(i % 17);
    for (int i = 0; i < N * K; i++) B[i] = (int8_t)(i % 11);

    struct timespec tp0, tp1;
    clock_gettime(CLOCK_MONOTONIC, &tp0);
    pack_B_blk_s8(B, B_blk);
    clock_gettime(CLOCK_MONOTONIC, &tp1);
    printf("B pack: %.1f ms\n", (tp1.tv_sec-tp0.tv_sec)*1e3 + (tp1.tv_nsec-tp0.tv_nsec)/1e6);

    printf("\n=== Correctness (8×8) ===\n");
    gemm_s8_scalar(A, B, Cs);
    gemm_s8_v4_single(A, B_blk, Cv);
    int md = 0, errs = 0;
    for (int i = 0; i < 8; i++) for (int j = 0; j < 8; j++) {
        int d = abs(Cv[i*N+j] - Cs[i*N+j]);
        if (d > md) md = d;
        if (d > 0) errs++;
    }
    if (errs > 0) failures++;
    printf("  v4_single vs scalar: %s (errs=%d max_diff=%d)\n",
           errs==0?"✅ PASS":"❌ FAIL", errs, md);

    gemm_s8_v4_dual(A, B_blk, Cv);
    md = 0; errs = 0;
    for (int i = 0; i < 8; i++) for (int j = 0; j < 8; j++) {
        int d = abs(Cv[i*N+j] - Cs[i*N+j]);
        if (d > md) md = d;
        if (d > 0) errs++;
    }
    if (errs > 0) failures++;
    printf("  v4_dual   vs scalar: %s (errs=%d max_diff=%d)\n",
           errs==0?"✅ PASS":"❌ FAIL", errs, md);

    gemm_s8_v5_mr8(A, B_blk, Cv);
    md = 0; errs = 0;
    for (int i = 0; i < 8; i++) for (int j = 0; j < 8; j++) {
        int d = abs(Cv[i*N+j] - Cs[i*N+j]);
        if (d > md) md = d;
        if (d > 0) errs++;
    }
    if (errs > 0) failures++;
    printf("  v5_mr8    vs scalar: %s (errs=%d max_diff=%d)\n",
           errs==0?"✅ PASS":"❌ FAIL", errs, md);

    printf("\n=== Performance (1024³) ===\n");
    double ns, gops = 2.0 * M * K * N;
    ns = time_it_s8(gemm_s8_v4_single, A, B_blk, Cv, 3);
    printf("  v4_single: %6.1f ms  %7.2f GOPS  (%.1f%% of 40)\n",
           ns/3/1e6, gops*3/ns, gops*3/ns/40*100);
    ns = time_it_s8(gemm_s8_v4_dual, A, B_blk, Cv, 3);
    printf("  v4_dual  : %6.1f ms  %7.2f GOPS  (%.1f%% of 80)\n",
           ns/3/1e6, gops*3/ns, gops*3/ns/80*100);
    ns = time_it_s8(gemm_s8_v5_mr8, A, B_blk, Cv, 3);
    printf("  v5_mr8   : %6.1f ms  %7.2f GOPS  (%.1f%% of 80)  ← 最优（实测峰值~80）\n",
           ns/3/1e6, gops*3/ns, gops*3/ns/80*100);

    free(A); free(B); free(B_blk); free(Cv); free(Cs);
    return failures > 0;
}
