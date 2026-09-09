/* ============================================================================
 * multicore_winograd.c — 多核 Winograd F(2×2, 3×3)
 *
 * 关键洞察：Winograd 的 tile 计算完全独立（th/tw 不重叠）
 * → 在 th 循环加 #pragma omp parallel for 完美并行
 *
 * 预期：8 核能达到 100+ GFLOPS 等效
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

#define HW 56
#define CIN 64
#define COUT 64
#define KH3 3
#define KW3 3

static const float Bt[4][4] = {
    { 1, 0, -1, 0}, {0, 1, 1, 0}, {0,-1, 1, 0}, {0, 1, 0,-1}
};
static const float Gm[4][3] = {
    {1,0,0}, {0.5,0.5,0.5}, {0.5,-0.5,0.5}, {0,0,1}
};
static const float At[2][4] = {{1,1,1,0}, {0,1,-1,-1}};

static double now_ns() {
    struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t);
    return t.tv_sec * 1e9 + t.tv_nsec;
}

static void winograd_transform_weight(const float *weight, float *U) {
    for (int oc = 0; oc < COUT; oc++) {
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
}

static inline void transform_input_tile(const float d[4][4], float V[4][4]) {
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

static inline void transform_output_tile(const float M[4][4], float Y[2][2]) {
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

/* 单核 Winograd */
static void winograd_single(const float *input, const float *U, float *output, int H, int W) {
    for (int th = 0; th < H; th += 2) {
        for (int tw = 0; tw < W; tw += 2) {
            float M_sum[COUT][4][4];
            memset(M_sum, 0, sizeof(M_sum));
            for (int ic = 0; ic < CIN; ic++) {
                float d[4][4], V[4][4];
                for (int i = 0; i < 4; i++)
                    for (int j = 0; j < 4; j++)
                        d[i][j] = input[((th+i)*(W+2)+(tw+j))*CIN+ic];
                transform_input_tile(d, V);
                for (int oc = 0; oc < COUT; oc++) {
                    const float *U_oc_ic = &U[((oc*CIN+ic)*16)];
                    for (int i = 0; i < 4; i++)
                        for (int j = 0; j < 4; j++)
                            M_sum[oc][i][j] += U_oc_ic[i*4+j] * V[i][j];
                }
            }
            for (int oc = 0; oc < COUT; oc++) {
                float Y[2][2];
                transform_output_tile(M_sum[oc], Y);
                output[((th+0)*W+(tw+0))*COUT+oc] = Y[0][0];
                output[((th+0)*W+(tw+1))*COUT+oc] = Y[0][1];
                output[((th+1)*W+(tw+0))*COUT+oc] = Y[1][0];
                output[((th+1)*W+(tw+1))*COUT+oc] = Y[1][1];
            }
        }
    }
}

/* 多核 Winograd：th 循环并行 */
static void winograd_omp(const float *input, const float *U, float *output,
                          int H, int W, int nthreads) {
    #pragma omp parallel for num_threads(nthreads) schedule(static)
    for (int th = 0; th < H; th += 2) {
        /* 每个 tile 独立累加器（避免共享写冲突）*/
        for (int tw = 0; tw < W; tw += 2) {
            float M_sum[COUT][4][4];
            memset(M_sum, 0, sizeof(M_sum));
            for (int ic = 0; ic < CIN; ic++) {
                float d[4][4], V[4][4];
                for (int i = 0; i < 4; i++)
                    for (int j = 0; j < 4; j++)
                        d[i][j] = input[((th+i)*(W+2)+(tw+j))*CIN+ic];
                transform_input_tile(d, V);
                for (int oc = 0; oc < COUT; oc++) {
                    const float *U_oc_ic = &U[((oc*CIN+ic)*16)];
                    for (int i = 0; i < 4; i++)
                        for (int j = 0; j < 4; j++)
                            M_sum[oc][i][j] += U_oc_ic[i*4+j] * V[i][j];
                }
            }
            for (int oc = 0; oc < COUT; oc++) {
                float Y[2][2];
                transform_output_tile(M_sum[oc], Y);
                output[((th+0)*W+(tw+0))*COUT+oc] = Y[0][0];
                output[((th+0)*W+(tw+1))*COUT+oc] = Y[0][1];
                output[((th+1)*W+(tw+0))*COUT+oc] = Y[1][0];
                output[((th+1)*W+(tw+1))*COUT+oc] = Y[1][1];
            }
        }
    }
}

int main() {
    int failures = 0;
    int H = HW, W = HW;
    int in_size = (H+2) * (W+2) * CIN;
    int out_size = H * W * COUT;
    int w_size = 9 * CIN * COUT;
    int U_size = COUT * CIN * 16;

    float *input = kl_xcalloc(in_size, sizeof(float));
    float *weight = kl_xmalloc(w_size * sizeof(float));
    float *U = kl_xmalloc(U_size * sizeof(float));
    float *out_s = kl_xcalloc(out_size, sizeof(float));
    float *out_m = kl_xcalloc(out_size, sizeof(float));

    srand(42);
    /* 简化：input 已 pad，给中间 H×W 区域随机值，padding 区域保持 0 */
    for (int h = 0; h < H; h++)
        for (int w = 0; w < W; w++)
            for (int c = 0; c < CIN; c++)
                input[((h+1)*(W+2)+(w+1))*CIN+c] = (rand() % 100) / 100.0f - 0.5f;
    for (int i = 0; i < w_size; i++) weight[i] = (rand() % 100) / 100.0f - 0.5f;

    winograd_transform_weight(weight, U);

#ifdef _OPENMP
    int max_thr = omp_get_max_threads();
    printf("OpenMP 可用，最大线程: %d\n\n", max_thr);
#else
    printf("需 -fopenmp\n"); return 1;
#endif

    /* 正确性 */
    winograd_single(input, U, out_s, H, W);
    winograd_omp(input, U, out_m, H, W, 4);
    int errs = 0; float md = 0;
    for (int i = 0; i < out_size; i++) {
        float d = fabsf(out_s[i] - out_m[i]);
        if (d > md) md = d;
        if (d > 1e-4) errs++;
    }
    if (errs > 0) failures++;
    printf("=== Correctness (single vs 4-thread) ===\n");
    printf("  %s (errs=%d max_diff=%.2e)\n\n", errs==0?"✅ PASS":"❌ FAIL", errs, md);

    double flops = 2.0 * H * W * CIN * COUT * 9;
    printf("=== Winograd 多核扩展性（等效 GFLOPS，56×56×64）===\n");
    printf("  线程 | 时间(ms) | 等效 GFLOPS | 加速比 | 效率\n");
    printf("  -----+----------+--------------+--------+------\n");

    double t0 = now_ns();
    for (int i = 0; i < 3; i++) winograd_single(input, U, out_s, H, W);
    double t1 = now_ns();
    double ms1 = (t1-t0)/3/1e6;
    double gf1 = flops*3/(t1-t0);
    printf("  1    | %8.1f | %12.2f |  1.00x | 100%%\n", ms1, gf1);

    int thread_list[] = {2, 4, 8};
    for (int idx = 0; idx < 3; idx++) {
        int nt = thread_list[idx];
        double t0 = now_ns();
        for (int i = 0; i < 3; i++) winograd_omp(input, U, out_m, H, W, nt);
        double t1 = now_ns();
        double ms = (t1-t0)/3/1e6;
        double gf = flops*3/(t1-t0);
        printf("  %d    | %8.1f | %12.2f | %5.2fx | %4.1f%%\n",
               nt, ms, gf, ms1/ms, ms1/ms/nt*100);
    }

    free(input); free(weight); free(U); free(out_s); free(out_m);
    return failures > 0;
}
