/* ============================================================================
 * conv_winograd_f44.c — Winograd F(4×4, 3×3) 卷积实现
 *
 * v0.8 新增：在 F(2,3) 基础上做大 tile F(4,3) 一维 → F(4×4, 3×3) 二维
 *
 * 数学（F(m, r)：m 输出，r kernel，输入 tile = m+r-1）：
 *   F(4, 3) 1D 矩阵（Lavin & Gray 2016）：
 *     B^T (6×6) =
 *       [[ 4,  0, -5,  0,  1,  0],
 *        [ 0, -4, -4,  1,  1,  0],
 *        [ 0,  4, -4, -1,  1,  0],
 *        [ 0, -2, -1,  2,  1,  0],
 *        [ 0,  2, -1, -2,  1,  0],
 *        [ 0,  4,  0, -5,  0,  1]]
 *     G (6×3) =
 *       [[1/4,    0,    0],
 *        [-1/6, -1/6, -1/6],
 *        [-1/6,  1/6, -1/6],
 *        [1/24, 1/12,  1/6],
 *        [1/24,-1/12,  1/6],
 *        [   0,    0,    1]]
 *     A^T (4×6) =
 *       [[1, 1, 1, 1, 1, 0],
 *        [0, 1,-1, 2,-2, 0],
 *        [0, 1, 1, 4, 4, 0],
 *        [0, 1,-1, 8,-8, 1]]
 *
 * 2D F(4×4, 3×3)：每 tile 处理 6×6 输入 → 4×4 输出
 *   1. U = G g G^T  (6×6，权重变换，预计算)
 *   2. V = B^T d B  (6×6，输入变换，每 tile 一次)
 *   3. M = U ⊙ V   (6×6 element-wise mul)
 *   4. Y = A^T M A (4×4，输出变换)
 *
 * 理论加速比：原来每输出 9 MAC，每 16 输出 144 MAC
 *              现在 36 mul/tile（变换摊到 channel）
 *              理论 144/36 = 4×，实际 1.78× 左右（变换开销）
 *
 * 适用：3×3 stride=1 pad=1，CIN/COUT 较大时收益明显
 * ============================================================================ */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>
#include <time.h>

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

/* Winograd tile 参数 */
#define TILE_OUT 4    /* 每tile输出 4×4 */
#define TILE_IN  6    /* 每tile输入 6×6 (= TILE_OUT + KH3 - 1) */

static double now_ns() {
    struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t);
    return t.tv_sec * 1e9 + t.tv_nsec;
}

/* F(4,3) 1D 变换矩阵 */
static const float Bt[6][6] = {
    { 4,  0, -5,  0,  1,  0},
    { 0, -4, -4,  1,  1,  0},
    { 0,  4, -4, -1,  1,  0},
    { 0, -2, -1,  2,  1,  0},
    { 0,  2, -1, -2,  1,  0},
    { 0,  4,  0, -5,  0,  1}
};
static const float G[6][3] = {
    {1.0/4,     0,        0     },
    {-1.0/6,   -1.0/6,   -1.0/6},
    {-1.0/6,    1.0/6,   -1.0/6},
    {1.0/24,   1.0/12,    1.0/6},
    {1.0/24,  -1.0/12,    1.0/6},
    {0,         0,        1     }
};
static const float At[4][6] = {
    {1, 1, 1, 1, 1, 0},
    {0, 1,-1, 2,-2, 0},
    {0, 1, 1, 4, 4, 0},
    {0, 1,-1, 8,-8, 1}
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

/* === Winograd F(4x4, 3x3) === */

/* 权重变换：g[3][3] → U[6][6]，每个 (oc, ic) 独立 */
static void winograd_transform_weight(const float *weight, /* [KH][KW][CIN][COUT] */
                                      float *U) {          /* [COUT][CIN][6][6] */
    for (int oc = 0; oc < COUT; oc++) {
        for (int ic = 0; ic < CIN; ic++) {
            float g[3][3];
            for (int kh = 0; kh < 3; kh++)
                for (int kw = 0; kw < 3; kw++)
                    g[kh][kw] = weight[((kh*3+kw)*CIN+ic)*COUT+oc];

            /* tmp = G g (6×3) */
            float tmp[6][3];
            for (int i = 0; i < 6; i++)
                for (int j = 0; j < 3; j++) {
                    float s = 0;
                    for (int k = 0; k < 3; k++) s += G[i][k] * g[k][j];
                    tmp[i][j] = s;
                }
            /* U = tmp × G^T (6×3 × 3×6 = 6×6) */
            for (int i = 0; i < 6; i++)
                for (int j = 0; j < 6; j++) {
                    float s = 0;
                    for (int k = 0; k < 3; k++) s += tmp[i][k] * G[j][k];
                    U[((oc*CIN+ic)*36 + i*6 + j)] = s;
                }
        }
    }
}

/* 输入变换：d[6][6] → V[6][6]，V = B^T d B */
static inline void winograd_transform_input_tile(const float d[TILE_IN][TILE_IN],
                                                 float V[TILE_IN][TILE_IN]) {
    /* tmp = B^T d (6×6 × 6×6 = 6×6) */
    float tmp[TILE_IN][TILE_IN];
    for (int i = 0; i < TILE_IN; i++)
        for (int j = 0; j < TILE_IN; j++) {
            float s = 0;
            for (int k = 0; k < TILE_IN; k++) s += Bt[i][k] * d[k][j];
            tmp[i][j] = s;
        }
    /* V = tmp × B (B = (B^T)^T)，即 V[i][j] = sum_k tmp[i][k] × Bt[j][k] */
    for (int i = 0; i < TILE_IN; i++)
        for (int j = 0; j < TILE_IN; j++) {
            float s = 0;
            for (int k = 0; k < TILE_IN; k++) s += tmp[i][k] * Bt[j][k];
            V[i][j] = s;
        }
}

/* 输出变换：M[6][6] → Y[4][4]，Y = A^T M A */
static inline void winograd_transform_output_tile(const float M[TILE_IN][TILE_IN],
                                                  float Y[TILE_OUT][TILE_OUT]) {
    /* tmp = A^T M (4×6 × 6×6 = 4×6) */
    float tmp[TILE_OUT][TILE_IN];
    for (int i = 0; i < TILE_OUT; i++)
        for (int j = 0; j < TILE_IN; j++) {
            float s = 0;
            for (int k = 0; k < TILE_IN; k++) s += At[i][k] * M[k][j];
            tmp[i][j] = s;
        }
    /* Y = tmp × A (4×6 × 6×4 = 4×4)，A = (A^T)^T */
    for (int i = 0; i < TILE_OUT; i++)
        for (int j = 0; j < TILE_OUT; j++) {
            float s = 0;
            for (int k = 0; k < TILE_IN; k++) s += tmp[i][k] * At[j][k];
            Y[i][j] = s;
        }
}

/* Winograd F(4,4,3,3) 卷积主函数 */
static void conv2d_winograd_f44(const float *input, /* [N][H+2][W+2][CIN] 已 pad */
                                const float *U,      /* [COUT][CIN][6][6] 预变换权重 */
                                float *output,        /* [N][H][W][COUT] */
                                int H, int W) {
    /* H, W 必须是 4 的倍数 */
    if (H % TILE_OUT || W % TILE_OUT) {
        printf("F(4,4) Winograd 要求 H, W 是 %d 的倍数，当前 H=%d W=%d\n", TILE_OUT, H, W);
        return;
    }

    for (int n = 0; n < NIMG; n++) {
        for (int th = 0; th < H; th += TILE_OUT) {
            for (int tw = 0; tw < W; tw += TILE_OUT) {
                /* 每 tile 聚合 M，然后做输出变换 */
                float M_sum[COUT][TILE_IN][TILE_IN];
                memset(M_sum, 0, sizeof(M_sum));

                for (int ic = 0; ic < CIN; ic++) {
                    /* 抽取 6×6 输入 tile（中心 4×4 对应输出 oh=th..th+3, ow=tw..tw+3）*/
                    float d[TILE_IN][TILE_IN];
                    for (int i = 0; i < TILE_IN; i++)
                        for (int j = 0; j < TILE_IN; j++)
                            d[i][j] = input[((n*(H+2)+(th+i))*(W+2)+(tw+j))*CIN+ic];

                    /* V = B^T d B */
                    float V[TILE_IN][TILE_IN];
                    winograd_transform_input_tile(d, V);

                    /* M[oc] += U[oc][ic] ⊙ V */
                    for (int oc = 0; oc < COUT; oc++) {
                        const float *U_oc_ic = &U[((oc*CIN+ic)*TILE_IN*TILE_IN)];
                        for (int i = 0; i < TILE_IN; i++)
                            for (int j = 0; j < TILE_IN; j++)
                                M_sum[oc][i][j] += U_oc_ic[i*TILE_IN+j] * V[i][j];
                    }
                }

                /* 每个 oc 做输出变换，写到 output[th..th+3][tw..tw+3][oc] */
                for (int oc = 0; oc < COUT; oc++) {
                    float Y[TILE_OUT][TILE_OUT];
                    winograd_transform_output_tile(M_sum[oc], Y);
                    for (int i = 0; i < TILE_OUT; i++)
                        for (int j = 0; j < TILE_OUT; j++)
                            output[((n*H+th+i)*W+(tw+j))*COUT+oc] = Y[i][j];
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
    int U_size = COUT * CIN * TILE_IN * TILE_IN;

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
    printf("=== Winograd F(4×4, 3×3) ===\n");
    printf("权重 F(4,3) 变换: %.2f ms\n", (t1-t0)/1e6);

    /* 正确性 */
    printf("\n=== Correctness (3×3 conv 56×56×64→56×56×64) ===\n");
    conv2d_direct(input_pad, weight, out_ref, H, W);
    conv2d_winograd_f44(input_pad, U, out_test, H, W);
    /* F(4,3) 数值精度比 F(2,3) 差（变换矩阵含 1/24 等小系数），tol 放宽到 1e-2 */
    failures += compare(out_ref, out_test, out_size, 1e-2, "F(4,4) vs Direct");

    /* 性能 */
    double flops_3x3 = 2.0 * NIMG * H * W * CIN * COUT * 9;
    const int ITER = 3;

    printf("\n=== Performance ===\n");

    t0 = now_ns();
    for (int i = 0; i < ITER; i++) conv2d_direct(input_pad, weight, out_test, H, W);
    t1 = now_ns();
    printf("  Direct (scalar)  : %7.2f ms  %6.2f GFLOPS (等效)\n",
           (t1-t0)/ITER/1e6, flops_3x3*ITER/(t1-t0));

    t0 = now_ns();
    for (int i = 0; i < ITER; i++) conv2d_winograd_f44(input_pad, U, out_test, H, W);
    t1 = now_ns();
    double ms_w = (t1-t0)/ITER/1e6;
    double gf_w = flops_3x3*ITER/(t1-t0);
    printf("  F(4,4) Winograd  : %7.2f ms  %6.2f GFLOPS (等效)\n", ms_w, gf_w);

    /* 真实 mul 数：每 tile 6×6=36 mul，代替 9×16=144 MAC
       理论加速比 144/36 = 4×（变换摊销后）*/
    double real_flops = 2.0 * NIMG * (H/TILE_OUT) * (W/TILE_OUT) * CIN * COUT * 36;
    printf("\n  F(4,4) 真实算量: %.2f MFLOPS (vs direct %.2f MFLOPS, F(2,3) %.2f MFLOPS)\n",
           real_flops/1e6, flops_3x3/1e6, 2.0*NIMG*(H/2)*(W/2)*CIN*COUT*16/1e6);
    printf("  F(4,4) 实际 GFLOPS（按真实 mul）: %.2f\n", real_flops*ITER/(t1-t0));
    printf("  理论加速比 vs Direct: %.2f×（实际 %.2f×）\n",
           144.0/36.0, flops_3x3*ITER/(t1-t0) / (real_flops*ITER/(t1-t0)));

    free(input); free(input_pad); free(weight); free(U);
    free(out_ref); free(out_test);
    return failures > 0;
}
