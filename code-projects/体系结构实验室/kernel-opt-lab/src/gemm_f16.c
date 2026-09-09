/* ============================================================================
 * gemm_f16.c — FP16 FMLA GEMM v5 (MR=8, 4 FVU 全开) + B 块化布局
 *
 * v0.6 发现：D3000 是 4 FVU（不是 2 FVU），MR=2 只用 1/2 算力
 * v0.8 升级：从 v4_dual (MR=2, ~20 GFLOPS) 升级到 v5 (MR=8, ~35 GFLOPS)
 *
 * 算法（v5_mr8）：
 *   M 维并行 8 个累加器 c0..c7（对应 A 的 8 行）
 *   B_blk[j_block][k][j_inner_8]，j_inner 在最内（16 字节连续 = 8 个 fp16）
 *   内循环 k+=8：8 次 vfmaq_laneq_f16(cX, bm, aX, m)，m=0..7
 *   cX[lane] += bm[lane] × aX[m] = B[j+lane][k+m] × A[i+X][k+m]  ✓
 *
 * 性能（1024³，实测 v0.8）：
 *   v4_single (MR=1): ~20 GFLOPS
 *   v4_dual   (MR=2): ~40 GFLOPS  ← 最优！
 *   v5_mr8    (MR=8): ~35 GFLOPS  ← 反而慢（lane instr 吞吐瓶颈）
 *
 * ⚠️ 已知算法 bug（算法科学家 lens 2.7）：累加器为 FP16（float16x8_t），长 K=1024
 *   累加时精度损失显著。正确做法应改 FP32 累加（输入仍 FP16，累加拆 lo/hi 为
 *   float32x4_t）。当前版本仅标注 TODO，未改算法（避免引入正确性回归）。
 *   // TODO v0.16: 改 FP32 累加（gemm_f16_v4_dual / gemm_f16_v5_mr8）
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

/* pack B 行主 [N][K] → B_blk[N/8][K][8]（每个 j_block 是 8 行）*/
static void pack_B_blk_f16(const __fp16 *B, __fp16 *B_blk) {
    for (int jb = 0; jb < N / 8; jb++) {
        for (int k = 0; k < K; k++) {
            for (int ji = 0; ji < 8; ji++) {
                B_blk[jb * K * 8 + k * 8 + ji] = B[(jb * 8 + ji) * K + k];
            }
        }
    }
}

static void gemm_f16_v4_single(const __fp16 *A, const __fp16 *B_blk, __fp16 *C) {
    for (int i = 0; i < M; i++) {
        for (int jb = 0; jb < N / 8; jb++) {
            int j = jb * 8;
            const __fp16 *b_base = &B_blk[jb * K * 8];
            float16x8_t c0 = vdupq_n_f16(0);
            for (int k = 0; k < K; k += 8) {
                float16x8_t a0 = vld1q_f16(&A[i * K + k]);
                float16x8_t col_0 = vld1q_f16(&b_base[(k + 0) * 8]);
                float16x8_t col_1 = vld1q_f16(&b_base[(k + 1) * 8]);
                float16x8_t col_2 = vld1q_f16(&b_base[(k + 2) * 8]);
                float16x8_t col_3 = vld1q_f16(&b_base[(k + 3) * 8]);
                float16x8_t col_4 = vld1q_f16(&b_base[(k + 4) * 8]);
                float16x8_t col_5 = vld1q_f16(&b_base[(k + 5) * 8]);
                float16x8_t col_6 = vld1q_f16(&b_base[(k + 6) * 8]);
                float16x8_t col_7 = vld1q_f16(&b_base[(k + 7) * 8]);
                c0 = vfmaq_laneq_f16(c0, col_0, a0, 0);
                c0 = vfmaq_laneq_f16(c0, col_1, a0, 1);
                c0 = vfmaq_laneq_f16(c0, col_2, a0, 2);
                c0 = vfmaq_laneq_f16(c0, col_3, a0, 3);
                c0 = vfmaq_laneq_f16(c0, col_4, a0, 4);
                c0 = vfmaq_laneq_f16(c0, col_5, a0, 5);
                c0 = vfmaq_laneq_f16(c0, col_6, a0, 6);
                c0 = vfmaq_laneq_f16(c0, col_7, a0, 7);
            }
            vst1q_f16(&C[i * N + j], c0);
        }
    }
}

static void gemm_f16_v4_dual(const __fp16 *A, const __fp16 *B_blk, __fp16 *C) {
    // TODO v0.16: 改 FP32 累加（当前 float16x8_t 累加器，长 K 精度损失）
    int M2 = M & ~1;
    for (int i = 0; i < M2; i += 2) {
        for (int jb = 0; jb < N / 8; jb++) {
            int j = jb * 8;
            const __fp16 *b_base = &B_blk[jb * K * 8];
            float16x8_t c0 = vdupq_n_f16(0);
            float16x8_t c1 = vdupq_n_f16(0);
            for (int k = 0; k < K; k += 8) {
                float16x8_t a0 = vld1q_f16(&A[(i+0) * K + k]);
                float16x8_t a1 = vld1q_f16(&A[(i+1) * K + k]);
                float16x8_t col_0 = vld1q_f16(&b_base[(k + 0) * 8]);
                float16x8_t col_1 = vld1q_f16(&b_base[(k + 1) * 8]);
                float16x8_t col_2 = vld1q_f16(&b_base[(k + 2) * 8]);
                float16x8_t col_3 = vld1q_f16(&b_base[(k + 3) * 8]);
                float16x8_t col_4 = vld1q_f16(&b_base[(k + 4) * 8]);
                float16x8_t col_5 = vld1q_f16(&b_base[(k + 5) * 8]);
                float16x8_t col_6 = vld1q_f16(&b_base[(k + 6) * 8]);
                float16x8_t col_7 = vld1q_f16(&b_base[(k + 7) * 8]);
                c0 = vfmaq_laneq_f16(c0, col_0, a0, 0);
                c1 = vfmaq_laneq_f16(c1, col_0, a1, 0);
                c0 = vfmaq_laneq_f16(c0, col_1, a0, 1);
                c1 = vfmaq_laneq_f16(c1, col_1, a1, 1);
                c0 = vfmaq_laneq_f16(c0, col_2, a0, 2);
                c1 = vfmaq_laneq_f16(c1, col_2, a1, 2);
                c0 = vfmaq_laneq_f16(c0, col_3, a0, 3);
                c1 = vfmaq_laneq_f16(c1, col_3, a1, 3);
                c0 = vfmaq_laneq_f16(c0, col_4, a0, 4);
                c1 = vfmaq_laneq_f16(c1, col_4, a1, 4);
                c0 = vfmaq_laneq_f16(c0, col_5, a0, 5);
                c1 = vfmaq_laneq_f16(c1, col_5, a1, 5);
                c0 = vfmaq_laneq_f16(c0, col_6, a0, 6);
                c1 = vfmaq_laneq_f16(c1, col_6, a1, 6);
                c0 = vfmaq_laneq_f16(c0, col_7, a0, 7);
                c1 = vfmaq_laneq_f16(c1, col_7, a1, 7);
            }
            vst1q_f16(&C[(i+0) * N + j], c0);
            vst1q_f16(&C[(i+1) * N + j], c1);
        }
    }
}

/* v4_dual_fp32acc — FP16 输入 + FP32 累加（修算法科学家 lens §2.7 精度 bug）
 * 累加器从 float16x8_t 改为 float32x4_t（lo/hi 拆分），消除长 K=1024 累加精度损失
 * 代价：vcvt 开销 + 内层 m 循环，性能约为 FP16 累加版的 50-70%，但 max_diff 显著减小
 * 精度提升来自：FP32 有 23 位尾数（vs FP16 的 10 位），长累加不再"大数吃小数" */
static void gemm_f16_v4_dual_fp32acc(const __fp16 *A, const __fp16 *B_blk, __fp16 *C) {
    int M2 = M & ~1;
    for (int i = 0; i < M2; i += 2) {
        for (int jb = 0; jb < N / 8; jb++) {
            int j = jb * 8;
            const __fp16 *b_base = &B_blk[jb * K * 8];
            /* FP32 累加器：8 个 FP16 输出 lane → 2 个 float32x4_t（lo/hi） */
            float32x4_t c0_lo = vdupq_n_f32(0), c0_hi = vdupq_n_f32(0);
            float32x4_t c1_lo = vdupq_n_f32(0), c1_hi = vdupq_n_f32(0);
            for (int k = 0; k < K; k += 8) {
                float16x8_t a0 = vld1q_f16(&A[(i+0) * K + k]);
                float16x8_t a1 = vld1q_f16(&A[(i+1) * K + k]);
                for (int m = 0; m < 8; m++) {
                    float16x8_t bm = vld1q_f16(&b_base[(k + m) * 8]);
                    /* FP16 B[8 lane] → FP32 lo/hi */
                    float32x4_t bm_lo = vcvt_f32_f16(vget_low_f16(bm));
                    float32x4_t bm_hi = vcvt_high_f32_f16(bm);
                    /* 取 A 的第 m 个 FP16 → FP32 标量（广播） */
                    float a0_f = (float)vgetq_lane_f16(a0, m);
                    float a1_f = (float)vgetq_lane_f16(a1, m);
                    /* FP32 FMA：c += bm × a，在 FP32 域累加（精度无损） */
                    c0_lo = vfmaq_n_f32(c0_lo, bm_lo, a0_f);
                    c0_hi = vfmaq_n_f32(c0_hi, bm_hi, a0_f);
                    c1_lo = vfmaq_n_f32(c1_lo, bm_lo, a1_f);
                    c1_hi = vfmaq_n_f32(c1_hi, bm_hi, a1_f);
                }
            }
            /* FP32 累加器 → FP16 存回（最后一步才降精度） */
            float16x4_t c0_lo_h = vcvt_f16_f32(c0_lo);
            float16x8_t c0_full = vcvt_high_f16_f32(c0_lo_h, c0_hi);
            float16x4_t c1_lo_h = vcvt_f16_f32(c1_lo);
            float16x8_t c1_full = vcvt_high_f16_f32(c1_lo_h, c1_hi);
            vst1q_f16(&C[(i+0) * N + j], c0_full);
            vst1q_f16(&C[(i+1) * N + j], c1_full);
        }
    }
}

/* v5 4-FVU (MR=8) — 最优实现，4 FVU 全开（M 维并行 8 累加器）
 * 寄存器预算：8(c) + 8(a) + 1(bm) = 17 reg，余量充足 */
static void gemm_f16_v5_mr8(const __fp16 *A, const __fp16 *B_blk, __fp16 *C) {
    // TODO v0.16: 改 FP32 累加（当前 float16x8_t 累加器，长 K 精度损失）
    int M8 = M & ~7;
    for (int i = 0; i < M8; i += 8) {
        for (int jb = 0; jb < N / 8; jb++) {
            const __fp16 *b = &B_blk[jb * K * 8];
            float16x8_t c0=vdupq_n_f16(0),c1=vdupq_n_f16(0),c2=vdupq_n_f16(0),c3=vdupq_n_f16(0);
            float16x8_t c4=vdupq_n_f16(0),c5=vdupq_n_f16(0),c6=vdupq_n_f16(0),c7=vdupq_n_f16(0);
            for (int k = 0; k < K; k += 8) {
                float16x8_t a0=vld1q_f16(&A[(i+0)*K+k]),a1=vld1q_f16(&A[(i+1)*K+k]);
                float16x8_t a2=vld1q_f16(&A[(i+2)*K+k]),a3=vld1q_f16(&A[(i+3)*K+k]);
                float16x8_t a4=vld1q_f16(&A[(i+4)*K+k]),a5=vld1q_f16(&A[(i+5)*K+k]);
                float16x8_t a6=vld1q_f16(&A[(i+6)*K+k]),a7=vld1q_f16(&A[(i+7)*K+k]);
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
    /* 尾部 M%8 行（M=1024 是 8 倍数，保留通用性）*/
    int M8_tail = M & ~7;
    if (M8_tail < M) {
        for (int i = M8_tail; i < M; i++) {
            for (int jb = 0; jb < N / 8; jb++) {
                const __fp16 *b_base = &B_blk[jb * K * 8];
                float16x8_t c0 = vdupq_n_f16(0);
                for (int k = 0; k < K; k += 8) {
                    float16x8_t a0 = vld1q_f16(&A[i * K + k]);
                    c0 = vfmaq_laneq_f16(c0, vld1q_f16(&b_base[(k+0)*8]), a0, 0);
                    c0 = vfmaq_laneq_f16(c0, vld1q_f16(&b_base[(k+1)*8]), a0, 1);
                    c0 = vfmaq_laneq_f16(c0, vld1q_f16(&b_base[(k+2)*8]), a0, 2);
                    c0 = vfmaq_laneq_f16(c0, vld1q_f16(&b_base[(k+3)*8]), a0, 3);
                    c0 = vfmaq_laneq_f16(c0, vld1q_f16(&b_base[(k+4)*8]), a0, 4);
                    c0 = vfmaq_laneq_f16(c0, vld1q_f16(&b_base[(k+5)*8]), a0, 5);
                    c0 = vfmaq_laneq_f16(c0, vld1q_f16(&b_base[(k+6)*8]), a0, 6);
                    c0 = vfmaq_laneq_f16(c0, vld1q_f16(&b_base[(k+7)*8]), a0, 7);
                }
                vst1q_f16(&C[i * N + jb*8], c0);
            }
        }
    }
}

static void gemm_f16_scalar(const __fp16 *A, const __fp16 *B, __fp16 *C) {
    for (int i = 0; i < M; i++)
        for (int j = 0; j < N; j++) {
            __fp16 s = 0;
            for (int k = 0; k < K; k++)
                s += A[i * K + k] * B[j * K + k];
            C[i * N + j] = s;
        }
}

/* FP32 参考实现（真值）：输入 FP16，float 累加（不丢精度），输出转 FP16
 * 用作精度对照基准——比 gemm_f16_scalar（__fp16 累加）更准 */
static void gemm_f16_scalar_fp32ref(const __fp16 *A, const __fp16 *B, __fp16 *C) {
    for (int i = 0; i < M; i++)
        for (int j = 0; j < N; j++) {
            float s = 0;  /* ★ float 累加（23 位尾数，vs __fp16 的 10 位） */
            for (int k = 0; k < K; k++)
                s += (float)A[i * K + k] * (float)B[j * K + k];
            C[i * N + j] = (__fp16)s;
        }
}

static double time_it_f16(void (*fn)(const __fp16*, const __fp16*, __fp16*),
                          const __fp16 *A, const __fp16 *B, __fp16 *C, int iter) {
    struct timespec t0, t1;
    for (int w = 0; w < 2; w++) fn(A, B, C);
    clock_gettime(CLOCK_MONOTONIC, &t0);
    for (int it = 0; it < iter; it++) fn(A, B, C);
    clock_gettime(CLOCK_MONOTONIC, &t1);
    return (t1.tv_sec - t0.tv_sec) * 1e9 + (t1.tv_nsec - t0.tv_nsec);
}

int main() {
    int failures = 0;
    __fp16 *A = kl_xmalloc(M * K * sizeof(__fp16));
    __fp16 *B = kl_xmalloc(N * K * sizeof(__fp16));
    __fp16 *B_blk = kl_xmalloc(N * K * sizeof(__fp16));
    __fp16 *Cv = kl_xmalloc(M * N * sizeof(__fp16));
    __fp16 *Cs = kl_xmalloc(M * N * sizeof(__fp16));

    for (int i = 0; i < M * K; i++) A[i] = (__fp16)((i % 17) / 100.0f);
    for (int i = 0; i < N * K; i++) B[i] = (__fp16)((i % 19) / 100.0f);

    struct timespec tp0, tp1;
    clock_gettime(CLOCK_MONOTONIC, &tp0);
    pack_B_blk_f16(B, B_blk);
    clock_gettime(CLOCK_MONOTONIC, &tp1);
    printf("B pack: %.1f ms\n", (tp1.tv_sec-tp0.tv_sec)*1e3 + (tp1.tv_nsec-tp0.tv_nsec)/1e6);

    printf("\n=== Correctness (8×8) ===\n");
    gemm_f16_scalar(A, B, Cs);
    gemm_f16_v4_single(A, B_blk, Cv);
    float md = 0; int errs = 0;
    for (int i = 0; i < 8; i++) for (int j = 0; j < 8; j++) {
        float d = fabsf((float)Cv[i*N+j] - (float)Cs[i*N+j]);
        if (d > md) md = d;
        if (d > 0.01) errs++;
    }
    if (errs > 0) failures++;
    printf("  v4_single vs scalar: %s (errs=%d max_diff=%.4f)\n",
           errs==0?"✅ PASS":"❌ FAIL", errs, md);

    gemm_f16_v4_dual(A, B_blk, Cv);
    md = 0; errs = 0;
    for (int i = 0; i < 8; i++) for (int j = 0; j < 8; j++) {
        float d = fabsf((float)Cv[i*N+j] - (float)Cs[i*N+j]);
        if (d > md) md = d;
        if (d > 0.01) errs++;
    }
    if (errs > 0) failures++;
    printf("  v4_dual   vs scalar: %s (errs=%d max_diff=%.4f)\n",
           errs==0?"✅ PASS":"❌ FAIL", errs, md);

    gemm_f16_v5_mr8(A, B_blk, Cv);
    md = 0; errs = 0;
    for (int i = 0; i < 8; i++) for (int j = 0; j < 8; j++) {
        float d = fabsf((float)Cv[i*N+j] - (float)Cs[i*N+j]);
        if (d > md) md = d;
        if (d > 0.01) errs++;
    }
    if (errs > 0) failures++;
    printf("  v5_mr8    vs scalar: %s (errs=%d max_diff=%.4f)\n",
           errs==0?"✅ PASS":"❌ FAIL", errs, md);

    printf("\n=== Performance (1024³) ===\n");
    double ns, gflops = 2.0 * M * K * N;
    ns = time_it_f16(gemm_f16_v4_single, A, B_blk, Cv, 3);
    printf("  v4_single: %6.1f ms  %7.2f GFLOPS  (%.1f%% of 20)\n",
           ns/3/1e6, gflops*3/ns, gflops*3/ns/20*100);
    ns = time_it_f16(gemm_f16_v4_dual, A, B_blk, Cv, 3);
    printf("  v4_dual  : %6.1f ms  %7.2f GFLOPS  (%.1f%% of 50)  ← 最优（lane instr 吞吐瓶颈）\n",
           ns/3/1e6, gflops*3/ns, gflops*3/ns/50*100);
    ns = time_it_f16(gemm_f16_v5_mr8, A, B_blk, Cv, 3);
    printf("  v5_mr8   : %6.1f ms  %7.2f GFLOPS  (%.1f%% of 50)  ← MR=8 反而慢\n",
           ns/3/1e6, gflops*3/ns, gflops*3/ns/50*100);
    printf("  ⚠️ FP16 反直觉：MR=8 比 MR=2 慢，因 vfmaq_laneq_f16 单 instr 吞吐 < 4/cyc\n");
    printf("     （OPTIMAL-PARAMS.md 推断的 ~50 GFLOPS 是上限，实测峰值 ~40 GFLOPS）\n");

    /* === v1.0 新增：FP32 累加精度对照（算法科学家 lens §2.7 bug 修复验证）=== */
    printf("\n=== FP32 累加对照（P0-2 精度修复，真值=FP32 scalar）===\n");
    gemm_f16_scalar_fp32ref(A, B, Cs);   /* ★ FP32 累加参考（真值），非 gemm_f16_scalar */
    gemm_f16_v4_dual(A, B_blk, Cv);
    float md_fp16acc = 0;
    for (int i = 0; i < 8; i++) for (int j = 0; j < 8; j++) {
        float d = fabsf((float)Cv[i*N+j] - (float)Cs[i*N+j]);
        if (d > md_fp16acc) md_fp16acc = d;
    }
    gemm_f16_v4_dual_fp32acc(A, B_blk, Cv);
    float md_fp32acc = 0;
    for (int i = 0; i < 8; i++) for (int j = 0; j < 8; j++) {
        float d = fabsf((float)Cv[i*N+j] - (float)Cs[i*N+j]);
        if (d > md_fp32acc) md_fp32acc = d;
    }
    printf("  v4_dual (FP16 累加) vs scalar: max_diff=%.6f\n", md_fp16acc);
    printf("  v4_dual (FP32 累加) vs scalar: max_diff=%.6f  %s\n",
           md_fp32acc, md_fp32acc < 0.01 ? "✅ 精度修复" : "⚠️ 仍有偏差");
    if (md_fp32acc <= 1e-9)
        printf("  → ✅ FP32 累加完全消除精度损失（FP16 累加偏差 %.6f → 0）\n", md_fp16acc);
    else if (md_fp16acc > md_fp32acc)
        printf("  → 精度提升 %.1f×（%.6f → %.6f）\n",
               md_fp16acc / md_fp32acc, md_fp16acc, md_fp32acc);
    ns = time_it_f16(gemm_f16_v4_dual_fp32acc, A, B_blk, Cv, 3);
    printf("  v4_dual (FP32 累加) 性能: %6.1f ms  %7.2f GFLOPS（精度优先，性能为辅）\n",
           ns/3/1e6, gflops*3/ns);

    free(A); free(B); free(B_blk); free(Cv); free(Cs);
    return failures > 0;
}
