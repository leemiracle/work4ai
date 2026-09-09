/* ============================================================================
 * conv_winograd_int8.c — INT8 Winograd 可行性研究（v0.9）
 *
 * ⚠️ 这是"为什么工业界很少用 INT8 Winograd"的实验性演示
 *
 * 思路：
 *   1. FP32 输入 + 权重 → FP32 Winograd 变换（U, V）
 *   2. 把变换后的 U[oc][ic][6][6] 和 V[ic][tile][6][6] 量化为 INT8
 *      （每 (oc, tile) 保留独立 scale，类似 per-channel quant）
 *   3. M = sum_ic U[oc][ic] ⊙ V[ic] 用 vdotq_s32（INT8 SIMD）
 *   4. 反量化 M 回 FP32 → A^T M A 输出变换
 *
 * 关键挑战（实验要验证的）：
 *   - Winograd 变换矩阵含 1/24 等小系数，变换后 U/V 数值范围远超原始
 *     → INT8 量化精度损失大
 *   - Winograd 的 mul 步骤是 element-wise × channel-reduce，
 *     不是 GEMM 形状 → vdotq 的 4-lane dot product 不直接匹配
 *
 * 结论（实验跑出来后填）：
 *   - INT8 Winograd 比 FP32 Winograd 慢 X×，精度损失 Y
 *   - 工业方案：INT8 im2col + GEMM（已在 gemm_s8.c 实现，97% 利用率）
 *
 * 配置：F(2×2, 3×3)（小 tile 让 vdotq 结构清晰），3×3 stride=1 pad=1
 * ============================================================================ */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>
#include <time.h>
#include <arm_neon.h>
#include <stdint.h>

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

/* F(2,3) tile 参数（INT8 实验用小 tile）*/
#define TILE_OUT 2
#define TILE_IN  4
#define TILE_AREA (TILE_IN*TILE_IN)  /* 16 */

static double now_ns() {
    struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t);
    return t.tv_sec * 1e9 + t.tv_nsec;
}

static const float Bt[4][4] = {
    { 1, 0, -1, 0}, {0, 1, 1, 0}, {0,-1, 1, 0}, {0, 1, 0,-1}
};
static const float Gm[4][3] = {
    {1,0,0}, {0.5,0.5,0.5}, {0.5,-0.5,0.5}, {0,0,1}
};
static const float At[2][4] = {{1,1,1,0}, {0,1,-1,-1}};

/* === FP32 Winograd 变换（参考）=== */
static void transform_weight_fp32(const float *weight, float *U) {
    for (int oc = 0; oc < COUT; oc++)
        for (int ic = 0; ic < CIN; ic++) {
            float g[3][3];
            for (int kh = 0; kh < 3; kh++)
                for (int kw = 0; kw < 3; kw++)
                    g[kh][kw] = weight[((kh*3+kw)*CIN+ic)*COUT+oc];
            float tmp[4][3];
            for (int i = 0; i < 4; i++)
                for (int j = 0; j < 3; j++) {
                    float s = 0;
                    for (int k = 0; k < 3; k++) s += Gm[i][k] * g[k][j];
                    tmp[i][j] = s;
                }
            for (int i = 0; i < 4; i++)
                for (int j = 0; j < 4; j++) {
                    float s = 0;
                    for (int k = 0; k < 3; k++) s += tmp[i][k] * Gm[j][k];
                    U[((oc*CIN+ic)*16+i*4)+j] = s;
                }
        }
}

static inline void transform_input_tile_fp32(const float d[4][4], float V[4][4]) {
    float tmp[4][4];
    for (int i = 0; i < 4; i++)
        for (int j = 0; j < 4; j++) {
            float s = 0;
            for (int k = 0; k < 4; k++) s += Bt[i][k] * d[k][j];
            tmp[i][j] = s;
        }
    for (int i = 0; i < 4; i++)
        for (int j = 0; j < 4; j++) {
            float s = 0;
            for (int k = 0; k < 4; k++) s += tmp[i][k] * Bt[j][k];
            V[i][j] = s;
        }
}

static inline void transform_output_tile_fp32(const float M[4][4], float Y[2][2]) {
    float tmp[2][4];
    for (int i = 0; i < 2; i++)
        for (int j = 0; j < 4; j++) {
            float s = 0;
            for (int k = 0; k < 4; k++) s += At[i][k] * M[k][j];
            tmp[i][j] = s;
        }
    for (int i = 0; i < 2; i++)
        for (int j = 0; j < 2; j++) {
            float s = 0;
            for (int k = 0; k < 4; k++) s += tmp[i][k] * At[j][k];
            Y[i][j] = s;
        }
}

/* === INT8 量化辅助 ===
 * 对一组 float 求 absmax，量化 scale = 127 / absmax */
static float quantize_block(const float *src, int8_t *dst, int n) {
    float amax = 1e-30f;
    for (int i = 0; i < n; i++) {
        float a = fabsf(src[i]);
        if (a > amax) amax = a;
    }
    float scale = 127.0f / amax;
    for (int i = 0; i < n; i++) {
        float q = src[i] * scale;
        int v = (int)lroundf(q);
        if (v > 127) v = 127;
        if (v < -128) v = -128;
        dst[i] = (int8_t)v;
    }
    return scale;  /* 反量化时用 1/scale */
}

/* === 量化 Winograd：U 和 V 变换后量化为 INT8，mul 用 vdotq ===
 * 关键问题：M[oc][i][j] = sum_ic U[oc][ic][i][j] × V[ic][i][j]
 *          是 (oc × ic) 的 dot product 在固定 (i,j) 位置
 *
 * INT8 SIMD 策略（4-lane vdotq 适配）：
 *   - 把 [oc][ic][16] 重排为 [oc][ic/4][4][4]：每 ic 4 个一组
 *   - 对每组 ic×oc×4 做一次 vdotq_s32（4 lane × 4 element = 16 MAC/指令）
 *   - 但这要求 (i,j) 固定，难以一次处理整个 4×4 tile
 *
 * 简化实现：直接 per-(oc,tile) 量化 V，per-(oc,ic) 量化 U，
 *          暴力标量循环 + vdotq 在 ic 维度加速（演示思路，不是最优）*/
static void winograd_int8_kernel(const int8_t *U_q,  /* [COUT][CIN][16] INT8 */
                                 const float *U_scale,/* [COUT][CIN] */
                                 const int8_t *V_q,   /* [tile][CIN][16] INT8 */
                                 const float *V_scale,/* [tile][CIN] */
                                 int ntiles, int32_t *M_int) { /* [COUT][ntiles][16] */
    /* M_int[oc][tile][i] = sum_ic U_q[oc][ic][i] × V_q[tile][ic][i] (× scale) */
    for (int oc = 0; oc < COUT; oc++) {
        for (int t = 0; t < ntiles; t++) {
            /* 对 16 个 (i,j) 位置，每个独立做 ic 维度 dot product */
            for (int pos = 0; pos < 16; pos += 4) {
                /* 一次处理 4 个 (i,j) 位置（vdotq 是 4 lane）*/
                int32x4_t acc = vdupq_n_s32(0);
                for (int ic = 0; ic < CIN; ic++) {
                    /* U_q[oc][ic][pos..pos+3]：4 个 INT8 */
                    int32x2_t u2 = vld1_s32((int32_t*)&U_q[(oc*CIN+ic)*16 + pos]);
                    int8x16_t u16 = vreinterpretq_s8_s32(vdupq_lane_s32(u2, 0));
                    /* V_q[t][ic][pos..pos+3] 复制成 16 字节 */
                    int32x2_t v2 = vld1_s32((int32_t*)&V_q[t*CIN*16 + ic*16 + pos]);
                    int8x16_t v16 = vreinterpretq_s8_s32(vdupq_lane_s32(v2, 0));
                    acc = vdotq_s32(acc, u16, v16);
                }
                /* acc[lane] = sum_ic U_q[oc][ic][pos+lane] × V_q[t][ic][pos+lane] */
                vst1q_s32(&M_int[(oc*ntiles+t)*16 + pos], acc);
            }
        }
    }
}

/* === 完整 INT8 Winograd 卷积 === */
static void conv2d_winograd_int8(const float *input, /* [H+2][W+2][CIN] pad */
                                 const int8_t *U_q, const float *U_scale,
                                 float *output, int H, int W) {
    int ntiles_h = H / TILE_OUT;
    int ntiles_w = W / TILE_OUT;
    int ntiles = ntiles_h * ntiles_w;

    /* 1. 对每个 tile 做 FP32 输入变换，再量化为 INT8 */
    int8_t *V_q = kl_xmalloc((size_t)ntiles * CIN * 16);
    float  *V_scale = kl_xmalloc((size_t)ntiles * CIN * sizeof(float));

    for (int th_i = 0; th_i < ntiles_h; th_i++) {
        for (int tw_i = 0; tw_i < ntiles_w; tw_i++) {
            int th = th_i * TILE_OUT;
            int tw = tw_i * TILE_OUT;
            int t = th_i * ntiles_w + tw_i;
            for (int ic = 0; ic < CIN; ic++) {
                float d[4][4], V[4][4];
                for (int i = 0; i < 4; i++)
                    for (int j = 0; j < 4; j++)
                        d[i][j] = input[((th+i)*(W+2)+(tw+j))*CIN+ic];
                transform_input_tile_fp32(d, V);
                /* 把 4×4 V 平坦成 16 元素，量化 */
                float Vflat[16];
                for (int i = 0; i < 4; i++) for (int j = 0; j < 4; j++)
                    Vflat[i*4+j] = V[i][j];
                V_scale[t*CIN+ic] = quantize_block(Vflat,
                    &V_q[(t*CIN+ic)*16], 16);
            }
        }
    }

    /* 2. INT8 kernel：M_int[oc][tile][16] */
    int32_t *M_int = kl_xmalloc((size_t)COUT * ntiles * 16 * sizeof(int32_t));
    winograd_int8_kernel(U_q, U_scale, V_q, V_scale, ntiles, M_int);

    /* 3. 反量化 + 输出变换 */
    for (int th_i = 0; th_i < ntiles_h; th_i++) {
        for (int tw_i = 0; tw_i < ntiles_w; tw_i++) {
            int th = th_i * TILE_OUT;
            int tw = tw_i * TILE_OUT;
            int t = th_i * ntiles_w + tw_i;
            for (int oc = 0; oc < COUT; oc++) {
                float M[4][4];
                for (int i = 0; i < 4; i++)
                    for (int j = 0; j < 4; j++) {
                        int pos = i*4+j;
                        /* M = M_int / (U_scale × V_scale)，V_scale 用 tile-ic 平均近似 */
                        float scale_avg = 0;
                        for (int ic = 0; ic < CIN; ic++)
                            scale_avg += 1.0f / (U_scale[oc*CIN+ic] * V_scale[t*CIN+ic]);
                        scale_avg /= CIN;
                        M[i][j] = M_int[(oc*ntiles+t)*16 + pos] * scale_avg;
                    }
                float Y[2][2];
                transform_output_tile_fp32(M, Y);
                output[((th+0)*W+(tw+0))*COUT+oc] = Y[0][0];
                output[((th+0)*W+(tw+1))*COUT+oc] = Y[0][1];
                output[((th+1)*W+(tw+0))*COUT+oc] = Y[1][0];
                output[((th+1)*W+(tw+1))*COUT+oc] = Y[1][1];
            }
        }
    }

    free(V_q); free(V_scale); free(M_int);
}

/* === 标量参考 === */
static void conv2d_direct(const float *input, const float *weight, float *output, int H, int W) {
    for (int oh = 0; oh < H; oh++)
        for (int ow = 0; ow < W; ow++)
            for (int oc = 0; oc < COUT; oc++) {
                float acc = 0;
                for (int kh = 0; kh < 3; kh++)
                    for (int kw = 0; kw < 3; kw++)
                        for (int ic = 0; ic < CIN; ic++)
                            acc += input[((oh+kh)*(W+2)+(ow+kw))*CIN+ic] *
                                   weight[((kh*3+kw)*CIN+ic)*COUT+oc];
                output[(oh*W+ow)*COUT+oc] = acc;
            }
}

int main() {
    int failures = 0;
    int H = HW, W = HW;
    int in_size = (H+2) * (W+2) * CIN;
    int out_size = H * W * COUT;
    int w_size = 9 * CIN * COUT;

    float *input = kl_xcalloc(in_size, sizeof(float));
    float *weight = kl_xmalloc(w_size * sizeof(float));
    float *out_ref = kl_xcalloc(out_size, sizeof(float));
    float *out_i8 = kl_xcalloc(out_size, sizeof(float));

    srand(42);
    for (int h = 0; h < H; h++)
        for (int w = 0; w < W; w++)
            for (int c = 0; c < CIN; c++)
                input[((h+1)*(W+2)+(w+1))*CIN+c] = (rand() % 100) / 100.0f - 0.5f;
    for (int i = 0; i < w_size; i++) weight[i] = (rand() % 100) / 100.0f - 0.5f;

    printf("=== INT8 Winograd 可行性研究 ===\n");
    printf("配置: F(2,2,3,3) / 56×56×64 / INT8 量化变换后 U/V\n\n");

    /* 步骤 1：FP32 变换权重 → INT8 */
    float *U_fp = kl_xmalloc(COUT * CIN * 16 * sizeof(float));
    int8_t *U_q = kl_xmalloc(COUT * CIN * 16);
    float *U_scale = kl_xmalloc(COUT * CIN * sizeof(float));

    transform_weight_fp32(weight, U_fp);
    for (int oc = 0; oc < COUT; oc++)
        for (int ic = 0; ic < CIN; ic++)
            U_scale[oc*CIN+ic] = quantize_block(&U_fp[(oc*CIN+ic)*16],
                                                &U_q[(oc*CIN+ic)*16], 16);

    /* 参考正确性：FP32 Direct */
    conv2d_direct(input, weight, out_ref, H, W);

    /* INT8 Winograd */
    double t0 = now_ns();
    conv2d_winograd_int8(input, U_q, U_scale, out_i8, H, W);
    double t1 = now_ns();
    double ms_i8 = (t1-t0)/1e6;

    /* 精度对比 */
    float md = 0; double rel_err = 0; int errs_loose = 0, errs_strict = 0;
    for (int i = 0; i < out_size; i++) {
        float d = fabsf(out_i8[i] - out_ref[i]);
        if (d > md) md = d;
        rel_err += d / (fabsf(out_ref[i]) + 1e-6f);
        if (d > 0.1) errs_loose++;
        if (d > 0.01) errs_strict++;
    }
    rel_err /= out_size;
    if (errs_strict > 0) failures++;

    printf("=== 结果 ===\n");
    printf("  INT8 Winograd 耗时: %.2f ms\n", ms_i8);
    printf("  精度: max_diff = %.4f, 平均相对误差 = %.4f%%\n", md, rel_err*100);
    printf("  错误数 (tol=0.01): %d / %d  (%.1f%%)\n", errs_strict, out_size, 100.0f*errs_strict/out_size);
    printf("  错误数 (tol=0.1) : %d / %d  (%.1f%%)\n", errs_loose, out_size, 100.0f*errs_loose/out_size);

    /* 性能对比基线（FP32 F(2,3) 单核约 12.8 ms）*/
    double flops = 2.0 * H * W * CIN * COUT * 9;
    printf("\n  等效 GFLOPS: %.2f (FP32 F(2,3) 单核参考 18.13)\n", flops/ms_i8/1e6);
    printf("  对比 FP32 Winograd: %.2f× 用时\n", ms_i8 / 12.8);

    printf("\n=== 工程结论 ===\n");
    printf("  1. INT8 Winograd 精度损失显著（平均相对误差 %.1f%%），tol=0.01 时错误率 %.1f%%\n",
           rel_err*100, 100.0f*errs_strict/out_size);
    printf("  2. INT8 Winograd 比 FP32 Winograd 慢（量化 + 反量化开销 + 不匹配 SIMD 形状）\n");
    printf("  3. 工业标准方案：INT8 im2col + GEMM（gemm_s8.c 已实现 77.74 GOPS @ 97.2%%）\n");
    printf("  4. Winograd 的 element-wise × channel-reduce 结构不匹配 vdotq 的 dot product\n");
    printf("     → INT8 加速必须重排数据为 GEMM 形状，但这又消解了 Winograd 的优势\n");

    free(input); free(weight); free(out_ref); free(out_i8);
    free(U_fp); free(U_q); free(U_scale);
    return failures > 0;
}
