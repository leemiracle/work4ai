/* ============================================================================
 * bench_conv_sizes.c — 卷积尺寸扩展性 (32→224)
 *
 * 测试不同空间尺寸下，im2col+GEMM / Winograd / 多核 的相对优势
 * ============================================================================ */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>
#include <time.h>
#include <arm_neon.h>
#ifdef _OPENMP
#include <omp.h>
#endif

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

#define CIN 64
#define COUT 64

static double now_ns() {
    struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t);
    return t.tv_sec * 1e9 + t.tv_nsec;
}

/* 简化 im2col + GEMM 卷积，参数化 H/W，单核 */
static void conv_im2col(const float *in_pad, const float *wt, float *out,
                        int H, int W) {
    int M = H * W;
    int K = 9 * CIN;
    /* 临时分配（性能测试用，实际工程应预分配）*/
    float *col = kl_xmalloc(M * K * sizeof(float));
    float *B = kl_xmalloc(COUT * K * sizeof(float));

    /* im2col */
    for (int oh = 0; oh < H; oh++)
        for (int ow = 0; ow < W; ow++) {
            int row = oh * W + ow;
            int ci = 0;
            for (int kh = 0; kh < 3; kh++)
                for (int kw = 0; kw < 3; kw++)
                    for (int c = 0; c < CIN; c++)
                        col[row*K + ci++] = in_pad[((oh+kh)*(W+2)+(ow+kw))*CIN + c];
        }
    /* weight reshape [3][3][CIN][COUT] → [COUT][9*CIN] */
    for (int oc = 0; oc < COUT; oc++)
        for (int kh = 0; kh < 3; kh++)
            for (int kw = 0; kw < 3; kw++)
                for (int c = 0; c < CIN; c++)
                    B[oc*K + (kh*3+kw)*CIN + c] = wt[((kh*3+kw)*CIN+c)*COUT + oc];

    /* 简单 GEMM (v4 风格 + vtrn) */
    for (int i = 0; i < M; i++)
        for (int j = 0; j < COUT; j += 4) {
            float32x4_t c0 = vdupq_n_f32(0);
            for (int k = 0; k < K; k += 4) {
                float32x4_t a0 = vld1q_f32(&col[i*K + k]);
                float32x4_t b0 = vld1q_f32(&B[(j+0)*K + k]);
                float32x4_t b1 = vld1q_f32(&B[(j+1)*K + k]);
                float32x4_t b2 = vld1q_f32(&B[(j+2)*K + k]);
                float32x4_t b3 = vld1q_f32(&B[(j+3)*K + k]);
                float32x4x2_t t01 = vtrnq_f32(b0, b1);
                float32x4x2_t t23 = vtrnq_f32(b2, b3);
                float32x4_t col_0 = vcombine_f32(vget_low_f32(t01.val[0]), vget_low_f32(t23.val[0]));
                float32x4_t col_1 = vcombine_f32(vget_low_f32(t01.val[1]), vget_low_f32(t23.val[1]));
                float32x4_t col_2 = vcombine_f32(vget_high_f32(t01.val[0]), vget_high_f32(t23.val[0]));
                float32x4_t col_3 = vcombine_f32(vget_high_f32(t01.val[1]), vget_high_f32(t23.val[1]));
                c0 = vfmaq_laneq_f32(c0, col_0, a0, 0);
                c0 = vfmaq_laneq_f32(c0, col_1, a0, 1);
                c0 = vfmaq_laneq_f32(c0, col_2, a0, 2);
                c0 = vfmaq_laneq_f32(c0, col_3, a0, 3);
            }
            vst1q_f32(&out[i*COUT + j], c0);
        }
    free(col); free(B);
}

static void pad_input(const float *in, float *out, int H, int W) {
    memset(out, 0, (H+2) * (W+2) * CIN * sizeof(float));
    for (int h = 0; h < H; h++)
        memcpy(&out[((h+1) * (W+2) + 1) * CIN],
               &in[(h * W) * CIN], W * CIN * sizeof(float));
}

int main() {
    int failures = 0;
    int sizes[] = {32, 56, 112, 160, 224};
    int n_sizes = sizeof(sizes) / sizeof(sizes[0]);

    printf("=== 卷积尺寸扩展性（CIN=COUT=64, 3×3 stride=1 pad=1）===\n\n");
    printf("  H×W  | M=N=H*W | 算量(MFLOPS) | im2col 时间(ms) | GFLOPS\n");
    printf("  -----+----------+--------------+----------------+--------\n");

    for (int si = 0; si < n_sizes; si++) {
        int H = sizes[si], W = sizes[si];
        int in_size = H * W * CIN;
        int in_pad_size = (H+2) * (W+2) * CIN;
        int out_size = H * W * COUT;
        int w_size = 9 * CIN * COUT;

        float *in = kl_xmalloc(in_size * sizeof(float));
        float *in_pad = kl_xmalloc(in_pad_size * sizeof(float));
        float *wt = kl_xmalloc(w_size * sizeof(float));
        float *out = kl_xcalloc(out_size, sizeof(float));

        srand(42);
        for (int i = 0; i < in_size; i++) in[i] = (rand() % 100) / 100.0f - 0.5f;
        for (int i = 0; i < w_size; i++) wt[i] = (rand() % 100) / 100.0f - 0.5f;
        pad_input(in, in_pad, H, W);

        double flops = 2.0 * H * W * CIN * COUT * 9;
        int iter = (H >= 112) ? 1 : 3;

        /* warmup */
        conv_im2col(in_pad, wt, out, H, W);

        double t0 = now_ns();
        for (int it = 0; it < iter; it++)
            conv_im2col(in_pad, wt, out, H, W);
        double t1 = now_ns();
        double ms = (t1-t0)/iter/1e6;
        double gf = flops * iter / (t1-t0);

        printf("  %3dx%-3d | %6d   | %10.2f   | %12.1f ms | %6.2f\n",
               H, W, H*W, flops/1e6, ms, gf);

        free(in); free(in_pad); free(wt); free(out);
    }

    /* ImageNet 第一层（224×224×3 → 224×224×64）特别测试 */
    printf("\n=== ImageNet 第一层（224×224×3 → 224×224×64）===\n");
    int H = 224, W = 224, Cin = 3;
    int in_size = H * W * Cin;
    int in_pad_size = (H+2) * (W+2) * Cin;
    int out_size = H * W * COUT;
    int w_size = 9 * Cin * COUT;
    float *in = kl_xmalloc(in_size * sizeof(float));
    float *in_pad = kl_xmalloc(in_pad_size * sizeof(float));
    float *wt = kl_xmalloc(w_size * sizeof(float));
    float *out = kl_xcalloc(out_size, sizeof(float));
    srand(42);
    for (int i = 0; i < in_size; i++) in[i] = (rand() % 100) / 100.0f - 0.5f;
    for (int i = 0; i < w_size; i++) wt[i] = (rand() % 100) / 100.0f - 0.5f;

    /* 注意 CIN=3 跟前面 im2col 不兼容（要求 CIN=64），跳过实际计算 */
    double flops = 2.0 * H * W * Cin * COUT * 9;
    printf("  算量: %.2f MFLOPS（理论 FP32 dual FVU 20 GFLOPS 跑满需 %.2f ms）\n",
           flops/1e6, flops / 20e9 * 1e3);
    printf("  注：CIN=3 太小，每 pixel 算量 27 MAC，访存主导，估计 GFLOPS 不会超过 5\n");

    free(in); free(in_pad); free(wt); free(out);
    return failures > 0;
}
