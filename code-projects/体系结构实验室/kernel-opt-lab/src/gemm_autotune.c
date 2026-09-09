/* ============================================================================
 * gemm_autotune.c — GEMM 运行时自动调优器（v0.9 新增）
 *
 * 扩展 gemm_tune.c：从"编译期固定 MR"升级到"运行时按尺寸 dispatch"
 *
 * 核心思想：
 *   - 矩阵尺寸不同，最优 MR 也不同（小矩阵 MR=2 够，大矩阵 MR=8 才填满 FVU）
 *   - 启动时跑一次微 benchmark（每候选跑 K=64 小块），选最佳 MR
 *   - 结果缓存到静态表（key = M/N/K 的桶），后续命中直接 dispatch
 *
 * vs gemm_tune.c：
 *   gemm_tune.c 只 sweep 出表（离线分析）
 *   本文件提供 runtime API：gemm_dispatch(A, B, C, M, N, K) 自动选 MR
 *
 * 性能：dispatch 开销 < 1us（hash + 函数指针），相对 GEMM 几十 ms 可忽略
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

static double now_ns() {
    struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t);
    return t.tv_sec * 1e9 + t.tv_nsec;
}

static void pack_B_blk(const float *B, float *B_blk, int N, int K) {
    for (int jb = 0; jb < N / 4; jb++)
        for (int k = 0; k < K; k++)
            for (int ji = 0; ji < 4; ji++)
                B_blk[jb * K * 4 + k * 4 + ji] = B[(jb * 4 + ji) * K + k];
}

/* === 候选实现：MR=1/2/4/8（同 gemm_tune.c，参数化 M/N/K）=== */

static void gemm_mr1(const float *A, const float *B_blk, float *C, int M, int N, int K) {
    for (int i = 0; i < M; i++)
        for (int jb = 0; jb < N/4; jb++) {
            const float *b = &B_blk[jb * K * 4];
            float32x4_t c0 = vdupq_n_f32(0);
            for (int k = 0; k < K; k += 4) {
                float32x4_t a0 = vld1q_f32(&A[i*K + k]);
                c0 = vfmaq_laneq_f32(c0, vld1q_f32(&b[(k+0)*4]), a0, 0);
                c0 = vfmaq_laneq_f32(c0, vld1q_f32(&b[(k+1)*4]), a0, 1);
                c0 = vfmaq_laneq_f32(c0, vld1q_f32(&b[(k+2)*4]), a0, 2);
                c0 = vfmaq_laneq_f32(c0, vld1q_f32(&b[(k+3)*4]), a0, 3);
            }
            vst1q_f32(&C[i*N + jb*4], c0);
        }
}

static void gemm_mr2(const float *A, const float *B_blk, float *C, int M, int N, int K) {
    int M2 = M & ~1;
    for (int i = 0; i < M2; i += 2)
        for (int jb = 0; jb < N/4; jb++) {
            const float *b = &B_blk[jb * K * 4];
            float32x4_t c0 = vdupq_n_f32(0), c1 = vdupq_n_f32(0);
            for (int k = 0; k < K; k += 4) {
                float32x4_t a0 = vld1q_f32(&A[(i+0)*K + k]);
                float32x4_t a1 = vld1q_f32(&A[(i+1)*K + k]);
                float32x4_t b0=vld1q_f32(&b[(k+0)*4]), b1=vld1q_f32(&b[(k+1)*4]);
                float32x4_t b2=vld1q_f32(&b[(k+2)*4]), b3=vld1q_f32(&b[(k+3)*4]);
                c0=vfmaq_laneq_f32(c0,b0,a0,0); c1=vfmaq_laneq_f32(c1,b0,a1,0);
                c0=vfmaq_laneq_f32(c0,b1,a0,1); c1=vfmaq_laneq_f32(c1,b1,a1,1);
                c0=vfmaq_laneq_f32(c0,b2,a0,2); c1=vfmaq_laneq_f32(c1,b2,a1,2);
                c0=vfmaq_laneq_f32(c0,b3,a0,3); c1=vfmaq_laneq_f32(c1,b3,a1,3);
            }
            vst1q_f32(&C[(i+0)*N + jb*4], c0);
            vst1q_f32(&C[(i+1)*N + jb*4], c1);
        }
    /* 尾部 M%2 */
    if (M2 < M) gemm_mr1(&A[M2*K], B_blk, &C[M2*N], M-M2, N, K);
}

static void gemm_mr4(const float *A, const float *B_blk, float *C, int M, int N, int K) {
    int M4 = M & ~3;
    for (int i = 0; i < M4; i += 4)
        for (int jb = 0; jb < N/4; jb++) {
            const float *b = &B_blk[jb * K * 4];
            float32x4_t c0=vdupq_n_f32(0), c1=vdupq_n_f32(0);
            float32x4_t c2=vdupq_n_f32(0), c3=vdupq_n_f32(0);
            for (int k = 0; k < K; k += 4) {
                float32x4_t a0=vld1q_f32(&A[(i+0)*K+k]), a1=vld1q_f32(&A[(i+1)*K+k]);
                float32x4_t a2=vld1q_f32(&A[(i+2)*K+k]), a3=vld1q_f32(&A[(i+3)*K+k]);
                float32x4_t b0=vld1q_f32(&b[(k+0)*4]), b1=vld1q_f32(&b[(k+1)*4]);
                float32x4_t b2=vld1q_f32(&b[(k+2)*4]), b3=vld1q_f32(&b[(k+3)*4]);
                c0=vfmaq_laneq_f32(c0,b0,a0,0); c1=vfmaq_laneq_f32(c1,b0,a1,0);
                c2=vfmaq_laneq_f32(c2,b0,a2,0); c3=vfmaq_laneq_f32(c3,b0,a3,0);
                c0=vfmaq_laneq_f32(c0,b1,a0,1); c1=vfmaq_laneq_f32(c1,b1,a1,1);
                c2=vfmaq_laneq_f32(c2,b1,a2,1); c3=vfmaq_laneq_f32(c3,b1,a3,1);
                c0=vfmaq_laneq_f32(c0,b2,a0,2); c1=vfmaq_laneq_f32(c1,b2,a1,2);
                c2=vfmaq_laneq_f32(c2,b2,a2,2); c3=vfmaq_laneq_f32(c3,b2,a3,2);
                c0=vfmaq_laneq_f32(c0,b3,a0,3); c1=vfmaq_laneq_f32(c1,b3,a1,3);
                c2=vfmaq_laneq_f32(c2,b3,a2,3); c3=vfmaq_laneq_f32(c3,b3,a3,3);
            }
            vst1q_f32(&C[(i+0)*N+jb*4],c0); vst1q_f32(&C[(i+1)*N+jb*4],c1);
            vst1q_f32(&C[(i+2)*N+jb*4],c2); vst1q_f32(&C[(i+3)*N+jb*4],c3);
        }
    if (M4 < M) gemm_mr2(&A[M4*K], B_blk, &C[M4*N], M-M4, N, K);
}

static void gemm_mr8(const float *A, const float *B_blk, float *C, int M, int N, int K) {
    int M8 = M & ~7;
    for (int i = 0; i < M8; i += 8)
        for (int jb = 0; jb < N/4; jb++) {
            const float *b = &B_blk[jb * K * 4];
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
    if (M8 < M) gemm_mr4(&A[M8*K], B_blk, &C[M8*N], M-M8, N, K);
}

typedef void (*gemm_fn)(const float*, const float*, float*, int, int, int);

static gemm_fn candidates[] = { gemm_mr1, gemm_mr2, gemm_mr4, gemm_mr8 };
static const char *cand_names[] = { "MR=1", "MR=2", "MR=4", "MR=8" };
#define NCAND (int)(sizeof(candidates)/sizeof(candidates[0]))

/* === Autotuner：尺寸分桶 + 缓存 === */

/* 桶：把 M 维按 log2 分桶（M=8/16/32/.../2048），N/K 类似
 * 简化：只按 M 桶（M 维主导寄存器选择），N/K 用启发式 */
#define M_BUCKETS 12  /* M ∈ {1,2,4,...,2048} */

typedef struct {
    int      m_bucket;   /* M 维桶 ID（log2(M)）*/
    int      best_idx;   /* 最佳候选索引（0..NCAND-1）*/
    double   best_gflops;
    int      valid;
} tune_entry_t;

static tune_entry_t cache[M_BUCKETS];

static int m_to_bucket(int M) {
    int b = 0;
    while ((1 << b) < M && b < M_BUCKETS - 1) b++;
    return b;
}

/* 对给定 (M, N, K) 跑微 benchmark 选最优候选
 * 微 bench：缩小 K 到 ≤128 跑 5 次，看哪个 MR 最快
 * （K 越小越能反映 startup overhead / 寄存器压力差异）*/
static int autotune_pick(int M, int N, int K) {
    int mb = m_to_bucket(M);
    if (cache[mb].valid) return cache[mb].best_idx;

    /* 构造测试矩阵：N 缩到 64，K 缩到 min(K, 128) */
    int Nt = (N < 64) ? N : 64;
    int Kt = (K < 128) ? K : 128;
    /* M 缩到桶代表值 */
    int Mt = 1 << mb;
    if (Mt > M) Mt = M;

    float *A = (float*)kl_xmalloc((size_t)Mt*Kt*sizeof(float));
    float *B = (float*)kl_xmalloc((size_t)Nt*Kt*sizeof(float));
    float *Bb = (float*)kl_xmalloc((size_t)Nt*Kt*sizeof(float));
    float *C = (float*)kl_xmalloc((size_t)Mt*Nt*sizeof(float));
    for (int i=0;i<Mt*Kt;i++) A[i] = (float)(i%17)/17.0f;
    for (int i=0;i<Nt*Kt;i++) B[i] = (float)(i%19)/19.0f;
    pack_B_blk(B, Bb, Nt, Kt);

    double best_gf = 0;
    int best_idx = NCAND - 1;  /* 默认 MR=8 */
    for (int c = 0; c < NCAND; c++) {
        /* warmup */
        candidates[c](A, Bb, C, Mt, Nt, Kt);
        candidates[c](A, Bb, C, Mt, Nt, Kt);
        double t0 = now_ns();
        int iter = 20;
        for (int it=0; it<iter; it++) candidates[c](A, Bb, C, Mt, Nt, Kt);
        double t1 = now_ns();
        double gf = 2.0*Mt*Nt*Kt*iter/(t1-t0);
        if (gf > best_gf) { best_gf = gf; best_idx = c; }
    }
    free(A); free(B); free(Bb); free(C);

    cache[mb].m_bucket = mb;
    cache[mb].best_idx = best_idx;
    cache[mb].best_gflops = best_gf;
    cache[mb].valid = 1;
    return best_idx;
}

/* 公共 API：自动选 MR 并执行 */
static void gemm_dispatch(const float *A, const float *B_blk, float *C,
                          int M, int N, int K) {
    int idx = autotune_pick(M, N, K);
    candidates[idx](A, B_blk, C, M, N, K);
}

/* === 验证正确性 === */
static void gemm_scalar(const float *A, const float *B, float *C, int M, int N, int K) {
    for (int i = 0; i < M; i++)
        for (int j = 0; j < N; j++) {
            float s = 0;
            for (int k = 0; k < K; k++) s += A[i*K+k] * B[j*K+k];
            C[i*N+j] = s;
        }
}

int main() {
    int failures = 0;
    printf("=== GEMM 运行时自动调优器（v0.9）===\n\n");
    printf("策略：按 M 维 log2 分桶，每桶跑微 bench 选最优 MR，结果缓存\n\n");

    /* 演示：多种尺寸下 dispatch 选什么 MR */
    struct { int M, N, K; } cases[] = {
        {16,   1024, 1024},  /* 极小 M：MR=1 可能够 */
        {64,   1024, 1024},
        {256,  1024, 1024},
        {1024, 1024, 1024},  /* 经典大矩阵：MR=8 最优 */
        {2048, 512,  512},
    };
    int n_cases = sizeof(cases)/sizeof(cases[0]);

    printf("  尺寸(M×N×K)     | 自动选择 | 桶 | 实测 GFLOPS | vs 强制 MR=8\n");
    printf("  ----------------+----------+----+-------------+-------------\n");

    for (int ci = 0; ci < n_cases; ci++) {
        int M = cases[ci].M, N = cases[ci].N, K = cases[ci].K;
        /* 量化 N/K 到 4 的倍数（NEON 要求）*/
        N = (N + 3) & ~3;

        /* dispatch 选 MR */
        int idx = autotune_pick(M, N, K);
        int mb = m_to_bucket(M);

        /* 真实大矩阵 benchmark */
        float *A = kl_xmalloc((size_t)M*K*sizeof(float));
        float *B = kl_xmalloc((size_t)N*K*sizeof(float));
        float *Bb = kl_xmalloc((size_t)N*K*sizeof(float));
        float *C = kl_xmalloc((size_t)M*N*sizeof(float));
        for (int i=0;i<M*K;i++) A[i] = (float)(i%17)/17.0f;
        for (int i=0;i<N*K;i++) B[i] = (float)(i%19)/19.0f;
        pack_B_blk(B, Bb, N, K);

        /* 自动 dispatch */
        gemm_dispatch(A, Bb, C, M, N, K);  /* warmup + 触发 tune */
        gemm_dispatch(A, Bb, C, M, N, K);
        double t0 = now_ns();
        int iter = (M*N*K > 100e6) ? 3 : 10;
        for (int i=0;i<iter;i++) gemm_dispatch(A, Bb, C, M, N, K);
        double t1 = now_ns();
        double gf_auto = 2.0*M*N*K*iter/(t1-t0);

        /* 强制 MR=8 对比 */
        gemm_mr8(A, Bb, C, M, N, K); gemm_mr8(A, Bb, C, M, N, K);
        t0 = now_ns();
        for (int i=0;i<iter;i++) gemm_mr8(A, Bb, C, M, N, K);
        t1 = now_ns();
        double gf_mr8 = 2.0*M*N*K*iter/(t1-t0);

        printf("  %4d×%4d×%4d | %-7s  | %2d | %10.2f | %5.2f× (%.2f)\n",
               M, N, K, cand_names[idx], mb, gf_auto,
               gf_auto/gf_mr8, gf_mr8);

        free(A); free(B); free(Bb); free(C);
    }

    /* 正确性：dispatch vs scalar */
    printf("\n=== Correctness (8×8 vs scalar) ===\n");
    int M=8, N=8, K=64;
    float A[8*64], B[8*64], Bb[8*64], Cv[8*8], Cs[8*8];
    for (int i=0;i<M*K;i++) A[i]=(float)(i%17)/17.0f;
    for (int i=0;i<N*K;i++) B[i]=(float)(i%19)/19.0f;
    pack_B_blk(B, Bb, N, K);
    gemm_scalar(A, B, Cs, M, N, K);
    gemm_dispatch(A, Bb, Cv, M, N, K);
    float md=0; int errs=0;
    for (int i=0;i<M*N;i++) {
        float d = fabsf(Cv[i]-Cs[i]);
        if (d>md) md=d;
        if (d>1e-4) errs++;
    }
    if (errs > 0) failures++;
    printf("  %s (errs=%d max_diff=%.2e)\n", errs==0?"✅ PASS":"❌ FAIL", errs, md);

    return failures > 0;
}
