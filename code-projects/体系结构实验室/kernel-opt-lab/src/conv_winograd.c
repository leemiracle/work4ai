/* ============================================================================
 * bench_winograd.c — Winograd F(2×2, 3×3) 卷积实现
 *
 * 数学（F(m, r) 表示 m 输出，r kernel）：
 *   F(2, 3) 1D 矩阵：
 *     B^T (4×4) = [[1, 0, -1, 0],
 *                  [0, 1, 1, 0],
 *                  [0, -1, 1, 0],
 *                  [0, 1, 0, -1]]
 *     G (4×3) = [[1, 0, 0],
 *                [1/2, 1/2, 1/2],
 *                [1/2, -1/2, 1/2],
 *                [0, 0, 1]]
 *     A^T (2×4) = [[1, 1, 1, 0],
 *                  [0, 1, -1, -1]]
 *
 * 2D F(2×2, 3×3)：每 tile 处理 4×4 输入 → 2×2 输出（中心 2×2）
 *   1. U = G g G^T  (4×4，权重变换，预计算)
 *   2. V = B^T d B  (4×4，输入变换，每 tile 一次)
 *   3. M = U ⊙ V   (4×4 element-wise mul)
 *   4. Y = A^T M A (2×2，输出变换)
 *
 * 加速比：原来每输出 9 MAC，现在每 4 输出 16 mul + 变换开销
 *        理论 9×4/16 = 2.25×，实际 1.5-2×
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

#define HW 56
#define CIN 64
#define COUT 64
#define KH3 3
#define KW3 3
#define NIMG 1

static double now_ns() {
    struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t);
    return t.tv_sec * 1e9 + t.tv_nsec;
}

/* Winograd F(2,3) 1D 变换矩阵 */
static const float Bt[4][4] = {
    { 1, 0, -1, 0},
    { 0, 1, 1, 0},
    { 0,-1, 1, 0},
    { 0, 1, 0,-1}
};
static const float G[4][3] = {
    {1,    0,    0},
    {0.5,  0.5,  0.5},
    {0.5, -0.5,  0.5},
    {0,    0,    1}
};
static const float At[2][4] = {
    {1, 1, 1, 0},
    {0, 1,-1,-1}
};

/* === 标量参考：直接卷积（已 pad 输入）=== */
static void conv2d_direct(const float *input, const float *weight, float *output, int H, int W) {
    for (int n = 0; n < NIMG; n++)
        for (int oh = 0; oh < H; oh++)
            for (int ow = 0; ow < W; ow++)
                for (int oc = 0; oc < COUT; oc++) {
                    float acc = 0;
                    for (int kh = 0; kh < KH3; kh++)
                        for (int kw = 0; kw < KW3; kw++)
                            for (int ic = 0; ic < CIN; ic++)
                                acc += input[((n*(H+2)+(oh+kh))*(W+2)+(ow+kw))*CIN+ic] *
                                       weight[((kh*KW3+kw)*CIN+ic)*COUT+oc];
                    output[((n*H+oh)*W+ow)*COUT+oc] = acc;
                }
}

/* === Winograd F(2x2, 3x3) === */

/* 权重变换：g[3][3] → U[4][4]，每个输出通道独立 */
static void winograd_transform_weight(const float *weight, /* [KH][KW][CIN][COUT] */
                                      float *U) {          /* [COUT][CIN][4][4] */
    for (int oc = 0; oc < COUT; oc++) {
        for (int ic = 0; ic < CIN; ic++) {
            /* g: 3×3 */
            float g[3][3];
            for (int kh = 0; kh < 3; kh++)
                for (int kw = 0; kw < 3; kw++)
                    g[kh][kw] = weight[((kh*3+kw)*CIN+ic)*COUT+oc];

            /* temp = G g (4×3)，结果 4×3 */
            float tmp[4][3];
            for (int i = 0; i < 4; i++)
                for (int j = 0; j < 3; j++) {
                    float s = 0;
                    for (int k = 0; k < 3; k++) s += G[i][k] * g[k][j];
                    tmp[i][j] = s;
                }
            /* U = tmp × G^T = (G g) × G^T (4×3 × 3×4 = 4×4) */
            for (int i = 0; i < 4; i++)
                for (int j = 0; j < 4; j++) {
                    float s = 0;
                    for (int k = 0; k < 3; k++) s += tmp[i][k] * G[j][k];
                    U[((oc*CIN+ic)*4+i)*4+j] = s;
                }
        }
    }
}

/* 输入变换：d[4][4] → V[4][4]，V = B^T d B */
static inline void winograd_transform_input_tile(const float d[4][4], float V[4][4]) {
    /* tmp = B^T d (4×4 × 4×4 = 4×4) */
    float tmp[4][4];
    for (int i = 0; i < 4; i++)
        for (int j = 0; j < 4; j++) {
            float s = 0;
            for (int k = 0; k < 4; k++) s += Bt[i][k] * d[k][j];
            tmp[i][j] = s;
        }
    /* V = tmp × B (4×4 × 4×4)，注意 B^T d B = (B^T d) B，B 是 B^T 的转置 */
    for (int i = 0; i < 4; i++)
        for (int j = 0; j < 4; j++) {
            float s = 0;
            for (int k = 0; k < 4; k++) s += tmp[i][k] * Bt[j][k];
            V[i][j] = s;
        }
}

/* 输出变换：M[4][4] → Y[2][2]，Y = A^T M A */
static inline void winograd_transform_output_tile(const float M[4][4], float Y[2][2]) {
    /* tmp = A^T M (2×4 × 4×4 = 2×4) */
    float tmp[2][4];
    for (int i = 0; i < 2; i++)
        for (int j = 0; j < 4; j++) {
            float s = 0;
            for (int k = 0; k < 4; k++) s += At[i][k] * M[k][j];
            tmp[i][j] = s;
        }
    /* Y = tmp × A (2×4 × 4×2)，A 是 A^T 的转置 */
    for (int i = 0; i < 2; i++)
        for (int j = 0; j < 2; j++) {
            float s = 0;
            for (int k = 0; k < 4; k++) s += tmp[i][k] * At[j][k];
            Y[i][j] = s;
        }
}

/* Winograd 卷积主函数 */
static void conv2d_winograd(const float *input, /* [N][H+2][W+2][CIN] 已 pad */
                            const float *U,      /* [COUT][CIN][4][4] 预变换权重 */
                            float *output,        /* [N][H][W][COUT] */
                            int H, int W) {
    /* H, W 必须是偶数（每 tile 输出 2×2）*/
    if (H % 2 || W % 2) {
        printf("Winograd 要求 H, W 偶数，当前 H=%d W=%d\n", H, W);
        return;
    }

    for (int n = 0; n < NIMG; n++) {
        for (int th = 0; th < H; th += 2) {
            for (int tw = 0; tw < W; tw += 2) {
                /* 对每个 tile，按 channel 聚合 M，然后做输出变换 */
                float M_sum[COUT][4][4];
                memset(M_sum, 0, sizeof(M_sum));

                for (int ic = 0; ic < CIN; ic++) {
                    /* 抽取 4×4 输入 tile（中心 2×2 对应输出 oh=th, ow=tw）*/
                    float d[4][4];
                    for (int i = 0; i < 4; i++)
                        for (int j = 0; j < 4; j++)
                            d[i][j] = input[((n*(H+2)+(th+i))*(W+2)+(tw+j))*CIN+ic];

                    /* V = B^T d B */
                    float V[4][4];
                    winograd_transform_input_tile(d, V);

                    /* M[oc] += U[oc][ic] ⊙ V */
                    for (int oc = 0; oc < COUT; oc++) {
                        const float *U_oc_ic = &U[((oc*CIN+ic)*16)];  /* 4×4 块 = 16 floats */
                        for (int i = 0; i < 4; i++)
                            for (int j = 0; j < 4; j++)
                                M_sum[oc][i][j] += U_oc_ic[i*4+j] * V[i][j];
                    }
                }

                /* 每个 oc 做输出变换，写到 output[th..th+1][tw..tw+1][oc] */
                for (int oc = 0; oc < COUT; oc++) {
                    float Y[2][2];
                    winograd_transform_output_tile(M_sum[oc], Y);
                    output[((n*H+th+0)*W+(tw+0))*COUT+oc] = Y[0][0];
                    output[((n*H+th+0)*W+(tw+1))*COUT+oc] = Y[0][1];
                    output[((n*H+th+1)*W+(tw+0))*COUT+oc] = Y[1][0];
                    output[((n*H+th+1)*W+(tw+1))*COUT+oc] = Y[1][1];
                }
            }
        }
    }
}

static void pad_input(const float *in, float *out, int H, int W, int C) {
    memset(out, 0, NIMG * (H+2) * (W+2) * C * sizeof(float));
    for (int n = 0; n < NIMG; n++)
        for (int h = 0; h < H; h++)
            memcpy(&out[((n*(H+2) + (h+1)) * (W+2) + 1) * C],
                   &in[((n*H + h) * W) * C], W * C * sizeof(float));
}

static int compare(const float *a, const float *b, int n, float tol, const char *name) {
    int errs = 0;
    float md = 0;
    for (int i = 0; i < n; i++) {
        float d = fabsf(a[i] - b[i]);
        if (d > md) md = d;
        if (d > tol) errs++;
    }
    printf("  %-25s %s (errs=%d max_diff=%.4f)\n",
           name, errs==0?"✅ PASS":"❌ FAIL", errs, md);
    return errs;
}

int main() {
    int failures = 0;
    int H = HW, W = HW;
    int in_size = NIMG * H * W * CIN;
    int in_pad_size = NIMG * (H+2) * (W+2) * CIN;
    int out_size = NIMG * H * W * COUT;
    int w_size = KH3 * KW3 * CIN * COUT;
    int U_size = COUT * CIN * 16;

    float *input = kl_xmalloc(in_size * sizeof(float));
    float *input_pad = kl_xmalloc(in_pad_size * sizeof(float));
    float *weight = kl_xmalloc(w_size * sizeof(float));
    float *U = kl_xmalloc(U_size * sizeof(float));
    float *out_ref = kl_xcalloc(out_size, sizeof(float));
    float *out_test = kl_xcalloc(out_size, sizeof(float));

    srand(42);
    for (int i = 0; i < in_size; i++) input[i] = (rand() % 100) / 100.0f - 0.5f;
    for (int i = 0; i < w_size; i++) weight[i] = (rand() % 100) / 100.0f - 0.5f;

    pad_input(input, input_pad, H, W, CIN);

    /* 预变换权重 */
    double t0 = now_ns();
    winograd_transform_weight(weight, U);
    double t1 = now_ns();
    printf("权重 Winograd 变换: %.2f ms\n", (t1-t0)/1e6);

    /* 正确性 */
    printf("\n=== Correctness (3×3 conv 56×56×64→56×56×64) ===\n");
    conv2d_direct(input_pad, weight, out_ref, H, W);
    conv2d_winograd(input_pad, U, out_test, H, W);
    failures += compare(out_ref, out_test, out_size, 1e-3, "Winograd vs Direct");

    /* 性能 */
    double flops_3x3 = 2.0 * NIMG * H * W * CIN * COUT * 9;
    const int ITER = 3;

    printf("\n=== Performance ===\n");

    t0 = now_ns();
    for (int i = 0; i < ITER; i++) conv2d_direct(input_pad, weight, out_test, H, W);
    t1 = now_ns();
    printf("  Direct (scalar)  : %7.2f ms  %6.2f GFLOPS\n",
           (t1-t0)/ITER/1e6, flops_3x3*ITER/(t1-t0));

    t0 = now_ns();
    for (int i = 0; i < ITER; i++) conv2d_winograd(input_pad, U, out_test, H, W);
    t1 = now_ns();
    double ms_w = (t1-t0)/ITER/1e6;
    double gf_w = flops_3x3*ITER/(t1-t0);
    printf("  Winograd F(2,3)  : %7.2f ms  %6.2f GFLOPS (等效)\n", ms_w, gf_w);

    /* Winograd 实际 mul 数：每 tile 16 mul + 变换开销 ≈ 4×4×CIN per tile
       代替 9 MAC × 4 outputs = 36 MAC，理论加速比 36/16 = 2.25× */
    /* 用 Winograd 自己的 GFLOPS 衡量（按实际 mul 数）*/
    double real_flops = 2.0 * NIMG * (H/2) * (W/2) * CIN * COUT * 16;
    printf("  Winograd 真实算量: %.2f MFLOPS (vs direct %.2f MFLOPS)\n",
           real_flops/1e6, flops_3x3/1e6);
    printf("  Winograd 实际 GFLOPS（按真实 mul）: %.2f\n", real_flops*ITER/(t1-t0));

    free(input); free(input_pad); free(weight); free(U);
    free(out_ref); free(out_test);
    return failures > 0;
}
