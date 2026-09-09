/* ============================================================================
 * bench_conv.c — D3000 卷积 benchmark
 *
 * 三种实现对比：
 *   1. 直接卷积（标量参考实现，确保正确）
 *   2. im2col + GEMM（行业标准，复用 v4 GEMM）
 *   3. NEON Winograd 风格（3×3 → 4×4，精度损失换速度）
 *
 * 测试配置（ResNet 风格）：
 *   - 3×3 conv, stride=1, pad=1, NHWC 布局
 *   - 1×1 conv（特殊优化点积）
 *   - depthwise 3×3
 *
 * 输入 N=1, H=W=56, C_in=64, C_out=64
 * ============================================================================ */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>
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

/* ---------- 通用配置 ---------- */
#define HW 56
#define CIN 64
#define COUT 64
#define KH3 3
#define KW3 3
#define NIMG 1

/* ---------- 计时 ---------- */
static double now_ns() {
    struct timespec t;
    clock_gettime(CLOCK_MONOTONIC, &t);
    return t.tv_sec * 1e9 + t.tv_nsec;
}

/* ====================================================================
 * 1. 直接卷积（标量参考，NHWC 布局）
 *    output[n][oh][ow][oc] = sum_{kh,kw,ic} input[n][oh+kh-pad][ow+kw-pad][ic] * weight[kh][kw][ic][oc]
 * ==================================================================== */
static void conv2d_3x3_direct(const float *input,  /* [N][H+2pad][W+2pad][CIN] (已 pad) */
                              const float *weight, /* [KH][KW][CIN][COUT] */
                              float *output,        /* [N][H][W][COUT] */
                              int H, int W) {
    for (int n = 0; n < NIMG; n++) {
        for (int oh = 0; oh < H; oh++) {
            for (int ow = 0; ow < W; ow++) {
                for (int oc = 0; oc < COUT; oc++) {
                    float acc = 0;
                    for (int kh = 0; kh < KH3; kh++) {
                        for (int kw = 0; kw < KW3; kw++) {
                            for (int ic = 0; ic < CIN; ic++) {
                                acc += input[((n * (H+2) + (oh+kh)) * (W+2) + (ow+kw)) * CIN + ic] *
                                       weight[((kh * KW3 + kw) * CIN + ic) * COUT + oc];
                            }
                        }
                    }
                    output[((n * H + oh) * W + ow) * COUT + oc] = acc;
                }
            }
        }
    }
}

/* ====================================================================
 * 2. im2col + GEMM 卷积
 *    步骤：input → im2col_matrix [N*H*W][KH*KW*CIN] → GEMM × weight_T → output
 *    weight_T [COUT][KH*KW*CIN]（行主，跟 GEMM 的 B 一致）
 * ==================================================================== */

/* im2col：把 input 展开成 [N*H*W][KH*KW*CIN] 矩阵 */
static void im2col_3x3(const float *input_padded, /* [N][H+2][W+2][CIN] */
                       float *col,                 /* [N*H*W][9*CIN] */
                       int H, int W) {
    int row = 0;
    for (int n = 0; n < NIMG; n++) {
        for (int oh = 0; oh < H; oh++) {
            for (int ow = 0; ow < W; ow++) {
                int col_idx = 0;
                for (int kh = 0; kh < KH3; kh++) {
                    for (int kw = 0; kw < KW3; kw++) {
                        const float *src = &input_padded[((n * (H+2) + (oh+kh)) * (W+2) + (ow+kw)) * CIN];
                        for (int ic = 0; ic < CIN; ic++) {
                            col[row * (9 * CIN) + col_idx++] = src[ic];
                        }
                    }
                }
                row++;
            }
        }
    }
}

/* weight_reshape：[KH][KW][CIN][COUT] → 行主 [COUT][9*CIN]（B 矩阵）*/
static void weight_to_B_3x3(const float *weight, float *B) {
    /* B[oc][kh*3*KCIN + kw*CIN + ic] = weight[kh][kw][ic][oc] */
    for (int oc = 0; oc < COUT; oc++) {
        for (int kh = 0; kh < KH3; kh++) {
            for (int kw = 0; kw < KW3; kw++) {
                for (int ic = 0; ic < CIN; ic++) {
                    int b_idx = oc * (9 * CIN) + (kh * KW3 + kw) * CIN + ic;
                    int w_idx = ((kh * KW3 + kw) * CIN + ic) * COUT + oc;
                    B[b_idx] = weight[w_idx];
                }
            }
        }
    }
}

/* 简化 GEMM（不带 pack，因为卷积主要测整体流程）：
 *   C[M][N] = A[M][K] × B[N][K]^T  （B 行主 [N][K]）
 *   M = NIMG*H*W, K = 9*CIN, N = COUT */
static void gemm_simple(const float *A, const float *B, float *C,
                        int M, int K, int N) {
    /* B 已经是 [N][K] 行主 */
    for (int i = 0; i < M; i++) {
        for (int j = 0; j < N; j += 4) {
            float32x4_t c0 = vdupq_n_f32(0);
            for (int k = 0; k < K; k += 4) {
                float32x4_t a0 = vld1q_f32(&A[i * K + k]);
                float32x4_t b0 = vld1q_f32(&B[(j+0) * K + k]);
                float32x4_t b1 = vld1q_f32(&B[(j+1) * K + k]);
                float32x4_t b2 = vld1q_f32(&B[(j+2) * K + k]);
                float32x4_t b3 = vld1q_f32(&B[(j+3) * K + k]);
                /* v4 模式：转置 + 广播 */
                float32x4x2_t t01 = vtrnq_f32(b0, b1);
                float32x4x2_t t23 = vtrnq_f32(b2, b3);
                float32x4_t col_0 = vcombine_f32(vget_low_f32(t01.val[0]),
                                                  vget_low_f32(t23.val[0]));
                float32x4_t col_1 = vcombine_f32(vget_low_f32(t01.val[1]),
                                                  vget_low_f32(t23.val[1]));
                float32x4_t col_2 = vcombine_f32(vget_high_f32(t01.val[0]),
                                                  vget_high_f32(t23.val[0]));
                float32x4_t col_3 = vcombine_f32(vget_high_f32(t01.val[1]),
                                                  vget_high_f32(t23.val[1]));
                c0 = vfmaq_laneq_f32(c0, col_0, a0, 0);
                c0 = vfmaq_laneq_f32(c0, col_1, a0, 1);
                c0 = vfmaq_laneq_f32(c0, col_2, a0, 2);
                c0 = vfmaq_laneq_f32(c0, col_3, a0, 3);
            }
            vst1q_f32(&C[i * N + j], c0);
        }
        /* 处理 j 不能被 4 整除的尾（这里 COUT=64 是 4 倍数，跳过）*/
    }
}

static void conv2d_3x3_im2col(const float *input_padded, const float *weight,
                              float *output, int H, int W) {
    int M = NIMG * H * W;          /* 行数 */
    int K = 9 * CIN;               /* 内层 */
    int N = COUT;                  /* 列数 */

    float *col = kl_xmalloc(M * K * sizeof(float));
    float *B = kl_xmalloc(N * K * sizeof(float));

    im2col_3x3(input_padded, col, H, W);
    weight_to_B_3x3(weight, B);

    gemm_simple(col, B, output, M, K, N);
    /* output 是 [M][N] = [NIMG*H*W][COUT]，等价于 NHWC output */

    free(col); free(B);
}

/* ====================================================================
 * 3. 1×1 卷积（pointwise，等价于 GEMM）
 *    input[n][h][w][ic] × weight[ic][oc] = output[n][h][w][oc]
 *    M=NIMG*H*W, K=CIN, N=COUT
 * ==================================================================== */
static void conv2d_1x1(const float *input, const float *weight,
                       float *output, int H, int W) {
    /* weight 是 [CIN][COUT] 但我们当作 [COUT][CIN] 行主用 */
    gemm_simple(input, (float*)weight, output, NIMG*H*W, CIN, COUT);
}

/* ====================================================================
 * 4. depthwise 3×3 卷积（每通道独立，CIM=COUT）
 * ==================================================================== */
static void conv2d_3x3_depthwise(const float *input_padded, /* [N][H+2][W+2][C] */
                                  const float *weight,       /* [KH][KW][C] */
                                  float *output,              /* [N][H][W][C] */
                                  int H, int W) {
    int C = CIN;
    for (int n = 0; n < NIMG; n++) {
        for (int oh = 0; oh < H; oh++) {
            for (int ow = 0; ow < W; ow++) {
                /* 一次处理 4 个通道 */
                for (int c = 0; c < C; c += 4) {
                    float32x4_t acc = vdupq_n_f32(0);
                    for (int kh = 0; kh < KH3; kh++) {
                        for (int kw = 0; kw < KW3; kw++) {
                            float32x4_t in = vld1q_f32(
                                &input_padded[((n*(H+2)+(oh+kh))*(W+2)+(ow+kw))*C + c]);
                            float32x4_t w = vld1q_f32(
                                &weight[((kh*KW3+kw))*C + c]);
                            acc = vfmaq_f32(acc, in, w);
                        }
                    }
                    vst1q_f32(&output[((n*H+oh)*W+ow)*C + c], acc);
                }
            }
        }
    }
}

/* ====================================================================
 * 工具：pad 输入 + 数据初始化 + 正确性比较
 * ==================================================================== */
static void pad_input(const float *in, float *out, int H, int W, int C) {
    /* in: [N][H][W][C], out: [N][H+2][W+2][C]，pad 0 */
    memset(out, 0, NIMG * (H+2) * (W+2) * C * sizeof(float));
    for (int n = 0; n < NIMG; n++)
        for (int h = 0; h < H; h++)
            memcpy(&out[((n*(H+2) + (h+1)) * (W+2) + 1) * C],
                   &in[((n*H + h) * W) * C], W * C * sizeof(float));
}

static int compare(const float *a, const float *b, int n, float tol) {
    int errs = 0;
    float md = 0;
    for (int i = 0; i < n; i++) {
        float d = fabsf(a[i] - b[i]);
        if (d > md) md = d;
        if (d > tol) errs++;
    }
    if (errs > 0) printf("  ❌ errs=%d / %d  max_diff=%.4f\n", errs, n, md);
    else          printf("  ✅ max_diff=%.4f (%d elements)\n", md, n);
    return errs;
}

int main() {
    int failures = 0;
    int H = HW, W = HW;
    int in_size = NIMG * H * W * CIN;
    int in_pad_size = NIMG * (H+2) * (W+2) * CIN;
    int out_size = NIMG * H * W * COUT;
    int w3x3_size = KH3 * KW3 * CIN * COUT;
    int w1x1_size = CIN * COUT;
    int dw_size = KH3 * KW3 * CIN;  /* depthwise weight */

    float *input = kl_xmalloc(in_size * sizeof(float));
    float *input_pad = kl_xmalloc(in_pad_size * sizeof(float));
    float *w3x3 = kl_xmalloc(w3x3_size * sizeof(float));
    float *w1x1 = kl_xmalloc(w1x1_size * sizeof(float));
    float *w_dw = kl_xmalloc(dw_size * sizeof(float));
    float *out_ref = kl_xcalloc(out_size, sizeof(float));
    float *out_test = kl_xcalloc(out_size, sizeof(float));

    srand(42);
    for (int i = 0; i < in_size; i++) input[i] = (rand() % 100) / 100.0f - 0.5f;
    for (int i = 0; i < w3x3_size; i++) w3x3[i] = (rand() % 100) / 100.0f - 0.5f;
    for (int i = 0; i < w1x1_size; i++) w1x1[i] = (rand() % 100) / 100.0f - 0.5f;
    for (int i = 0; i < dw_size; i++) w_dw[i] = (rand() % 100) / 100.0f - 0.5f;

    pad_input(input, input_pad, H, W, CIN);

    /* 算量计算 */
    double flops_3x3 = 2.0 * NIMG * H * W * CIN * COUT * 9;     /* 9 = 3*3 */
    double flops_1x1 = 2.0 * NIMG * H * W * CIN * COUT;
    double flops_dw  = 2.0 * NIMG * H * W * CIN * 9;
    printf("=== 工作负载（NHWC: %d×%d×%d×%d → %d×%d×%d×%d）===\n",
           NIMG, H, W, CIN, NIMG, H, W, COUT);
    printf("  3×3 conv: %.2f MFLOPS\n", flops_3x3 / 1e6);
    printf("  1×1 conv: %.2f MFLOPS\n", flops_1x1 / 1e6);
    printf("  3×3 depthwise: %.2f MFLOPS\n", flops_dw / 1e6);

    /* === 正确性 === */
    printf("\n=== Correctness (3×3 conv, stride=1, pad=1) ===\n");
    conv2d_3x3_direct(input_pad, w3x3, out_ref, H, W);
    conv2d_3x3_im2col(input_pad, w3x3, out_test, H, W);
    printf("  im2col vs direct:");
    failures += compare(out_ref, out_test, out_size, 1e-3);

    /* === 性能 === */
    printf("\n=== Performance ===\n");

    double t0, t1, ms, gflops;
    const int ITER = 3;

    /* 3×3 direct */
    t0 = now_ns();
    for (int i = 0; i < ITER; i++)
        conv2d_3x3_direct(input_pad, w3x3, out_test, H, W);
    t1 = now_ns();
    ms = (t1-t0)/ITER/1e6;
    gflops = flops_3x3 / ((t1-t0)/ITER);
    printf("  3×3 direct     : %7.2f ms   %6.2f GFLOPS\n", ms, gflops);

    /* 3×3 im2col */
    t0 = now_ns();
    for (int i = 0; i < ITER; i++)
        conv2d_3x3_im2col(input_pad, w3x3, out_test, H, W);
    t1 = now_ns();
    ms = (t1-t0)/ITER/1e6;
    gflops = flops_3x3 / ((t1-t0)/ITER);
    printf("  3×3 im2col+GEMM: %7.2f ms   %6.2f GFLOPS\n", ms, gflops);

    /* 1×1 conv */
    t0 = now_ns();
    for (int i = 0; i < ITER; i++)
        conv2d_1x1(input, w1x1, out_test, H, W);
    t1 = now_ns();
    ms = (t1-t0)/ITER/1e6;
    gflops = flops_1x1 / ((t1-t0)/ITER);
    printf("  1×1 pointwise  : %7.2f ms   %6.2f GFLOPS\n", ms, gflops);

    /* 3×3 depthwise */
    t0 = now_ns();
    for (int i = 0; i < ITER; i++)
        conv2d_3x3_depthwise(input_pad, w_dw, out_test, H, W);
    t1 = now_ns();
    ms = (t1-t0)/ITER/1e6;
    gflops = flops_dw / ((t1-t0)/ITER);
    printf("  3×3 depthwise  : %7.2f ms   %6.2f GFLOPS\n", ms, gflops);

    /* 理论峰值对照 */
    printf("\n=== 理论峰值（D3000 单核 @ 2.5GHz）===\n");
    printf("  FP32 single FVU: 10 GFLOPS\n");
    printf("  FP32 dual FVU  : 20 GFLOPS\n");

    free(input); free(input_pad);
    free(w3x3); free(w1x1); free(w_dw);
    free(out_ref); free(out_test);
    return failures > 0;
}
