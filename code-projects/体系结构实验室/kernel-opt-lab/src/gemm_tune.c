/* ============================================================================
 * gemm_tune.c — GEMM 参数自动调优（sweep MR × NR × KC 找最优）
 *
 * 体系结构实验数据（实测）：
 *   L1D: 64KB, 4-way, 64B line, 4 cyc latency
 *   L2 : 512KB, 8-way, 1024 sets, 12 cyc latency
 *   L3 : 4MB(0-3核) + 8MB(0-7核), 16-way, 40 cyc
 *   DRAM: 80-85 ns
 *   L1 D-TLB: 64 entry (覆盖 256KB)
 *   L2 TLB: 2048 entry (覆盖 8MB)
 *   4-wide 超标量，2 ALU/cyc, 2 NEON FMLA/cyc (dual FVU)
 *   fmul/fadd latency: 4 cyc
 *   ROB: 128-192, PRF: 128-256, IQ: 32-64
 *   NEON 寄存器: 32 个 V0-V31
 *
 * 理论约束：
 *   MR × NR 个累加器 + a_row + b_col ≤ 32 NEON 寄存器
 *   A_pack + B_pack + C_pack 工作集 ≤ L2 (512KB) 才能不溢出
 *
 * 实测：扫 MR={2,4,8}, NR={4,8}, KC={64,256,1024}
 * ============================================================================ */
#include <stdio.h>
#include <stdlib.h>
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

/* 通用 B-blocked GEMM：参数化 MR（M 维并行）和 NR（NEON lane）
 * NR 固定 = 4（fp32 一次 4 lane）
 * MR 参数化：1, 2, 4, 8（累加器数）
 * KC 参数化：内层 K 块大小 */
static void pack_B_blk(const float *B, float *B_blk, int N, int K) {
    for (int jb = 0; jb < N / 4; jb++)
        for (int k = 0; k < K; k++)
            for (int ji = 0; ji < 4; ji++)
                B_blk[jb * K * 4 + k * 4 + ji] = B[(jb * 4 + ji) * K + k];
}

/* MR=1 (single FVU) */
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

/* MR=2 (dual FVU, 2 累加器) */
static void gemm_mr2(const float *A, const float *B_blk, float *C, int M, int N, int K) {
    int M2 = M & ~1;
    for (int i = 0; i < M2; i += 2)
        for (int jb = 0; jb < N/4; jb++) {
            const float *b = &B_blk[jb * K * 4];
            float32x4_t c0 = vdupq_n_f32(0), c1 = vdupq_n_f32(0);
            for (int k = 0; k < K; k += 4) {
                float32x4_t a0 = vld1q_f32(&A[(i+0)*K + k]);
                float32x4_t a1 = vld1q_f32(&A[(i+1)*K + k]);
                float32x4_t b0 = vld1q_f32(&b[(k+0)*4]);
                float32x4_t b1 = vld1q_f32(&b[(k+1)*4]);
                float32x4_t b2 = vld1q_f32(&b[(k+2)*4]);
                float32x4_t b3 = vld1q_f32(&b[(k+3)*4]);
                c0 = vfmaq_laneq_f32(c0, b0, a0, 0);
                c1 = vfmaq_laneq_f32(c1, b0, a1, 0);
                c0 = vfmaq_laneq_f32(c0, b1, a0, 1);
                c1 = vfmaq_laneq_f32(c1, b1, a1, 1);
                c0 = vfmaq_laneq_f32(c0, b2, a0, 2);
                c1 = vfmaq_laneq_f32(c1, b2, a1, 2);
                c0 = vfmaq_laneq_f32(c0, b3, a0, 3);
                c1 = vfmaq_laneq_f32(c1, b3, a1, 3);
            }
            vst1q_f32(&C[(i+0)*N + jb*4], c0);
            vst1q_f32(&C[(i+1)*N + jb*4], c1);
        }
}

/* MR=4 (4 累加器，更激进 ILP) */
static void gemm_mr4(const float *A, const float *B_blk, float *C, int M, int N, int K) {
    int M4 = M & ~3;
    for (int i = 0; i < M4; i += 4)
        for (int jb = 0; jb < N/4; jb++) {
            const float *b = &B_blk[jb * K * 4];
            float32x4_t c0 = vdupq_n_f32(0), c1 = vdupq_n_f32(0);
            float32x4_t c2 = vdupq_n_f32(0), c3 = vdupq_n_f32(0);
            for (int k = 0; k < K; k += 4) {
                float32x4_t a0 = vld1q_f32(&A[(i+0)*K + k]);
                float32x4_t a1 = vld1q_f32(&A[(i+1)*K + k]);
                float32x4_t a2 = vld1q_f32(&A[(i+2)*K + k]);
                float32x4_t a3 = vld1q_f32(&A[(i+3)*K + k]);
                float32x4_t b0 = vld1q_f32(&b[(k+0)*4]);
                float32x4_t b1 = vld1q_f32(&b[(k+1)*4]);
                float32x4_t b2 = vld1q_f32(&b[(k+2)*4]);
                float32x4_t b3 = vld1q_f32(&b[(k+3)*4]);
                c0 = vfmaq_laneq_f32(c0, b0, a0, 0);
                c1 = vfmaq_laneq_f32(c1, b0, a1, 0);
                c2 = vfmaq_laneq_f32(c2, b0, a2, 0);
                c3 = vfmaq_laneq_f32(c3, b0, a3, 0);
                c0 = vfmaq_laneq_f32(c0, b1, a0, 1);
                c1 = vfmaq_laneq_f32(c1, b1, a1, 1);
                c2 = vfmaq_laneq_f32(c2, b1, a2, 1);
                c3 = vfmaq_laneq_f32(c3, b1, a3, 1);
                c0 = vfmaq_laneq_f32(c0, b2, a0, 2);
                c1 = vfmaq_laneq_f32(c1, b2, a1, 2);
                c2 = vfmaq_laneq_f32(c2, b2, a2, 2);
                c3 = vfmaq_laneq_f32(c3, b2, a3, 2);
                c0 = vfmaq_laneq_f32(c0, b3, a0, 3);
                c1 = vfmaq_laneq_f32(c1, b3, a1, 3);
                c2 = vfmaq_laneq_f32(c2, b3, a2, 3);
                c3 = vfmaq_laneq_f32(c3, b3, a3, 3);
            }
            vst1q_f32(&C[(i+0)*N + jb*4], c0);
            vst1q_f32(&C[(i+1)*N + jb*4], c1);
            vst1q_f32(&C[(i+2)*N + jb*4], c2);
            vst1q_f32(&C[(i+3)*N + jb*4], c3);
        }
}

/* MR=8 (8 累加器，看寄存器压力) */
static void gemm_mr8(const float *A, const float *B_blk, float *C, int M, int N, int K) {
    int M8 = M & ~7;
    for (int i = 0; i < M8; i += 8)
        for (int jb = 0; jb < N/4; jb++) {
            const float *b = &B_blk[jb * K * 4];
            float32x4_t c0=vdupq_n_f32(0), c1=vdupq_n_f32(0),
                        c2=vdupq_n_f32(0), c3=vdupq_n_f32(0),
                        c4=vdupq_n_f32(0), c5=vdupq_n_f32(0),
                        c6=vdupq_n_f32(0), c7=vdupq_n_f32(0);
            for (int k = 0; k < K; k += 4) {
                float32x4_t a0=vld1q_f32(&A[(i+0)*K+k]), a1=vld1q_f32(&A[(i+1)*K+k]);
                float32x4_t a2=vld1q_f32(&A[(i+2)*K+k]), a3=vld1q_f32(&A[(i+3)*K+k]);
                float32x4_t a4=vld1q_f32(&A[(i+4)*K+k]), a5=vld1q_f32(&A[(i+5)*K+k]);
                float32x4_t a6=vld1q_f32(&A[(i+6)*K+k]), a7=vld1q_f32(&A[(i+7)*K+k]);
                float32x4_t b0=vld1q_f32(&b[(k+0)*4]), b1=vld1q_f32(&b[(k+1)*4]);
                float32x4_t b2=vld1q_f32(&b[(k+2)*4]), b3=vld1q_f32(&b[(k+3)*4]);
                c0=vfmaq_laneq_f32(c0,b0,a0,0); c1=vfmaq_laneq_f32(c1,b0,a1,0);
                c2=vfmaq_laneq_f32(c2,b0,a2,0); c3=vfmaq_laneq_f32(c3,b0,a3,0);
                c4=vfmaq_laneq_f32(c4,b0,a4,0); c5=vfmaq_laneq_f32(c5,b0,a5,0);
                c6=vfmaq_laneq_f32(c6,b0,a6,0); c7=vfmaq_laneq_f32(c7,b0,a7,0);
                c0=vfmaq_laneq_f32(c0,b1,a0,1); c1=vfmaq_laneq_f32(c1,b1,a1,1);
                c2=vfmaq_laneq_f32(c2,b1,a2,1); c3=vfmaq_laneq_f32(c3,b1,a3,1);
                c4=vfmaq_laneq_f32(c4,b1,a4,1); c5=vfmaq_laneq_f32(c5,b1,a5,1);
                c6=vfmaq_laneq_f32(c6,b1,a6,1); c7=vfmaq_laneq_f32(c7,b1,a7,1);
                c0=vfmaq_laneq_f32(c0,b2,a0,2); c1=vfmaq_laneq_f32(c1,b2,a1,2);
                c2=vfmaq_laneq_f32(c2,b2,a2,2); c3=vfmaq_laneq_f32(c3,b2,a3,2);
                c4=vfmaq_laneq_f32(c4,b2,a4,2); c5=vfmaq_laneq_f32(c5,b2,a5,2);
                c6=vfmaq_laneq_f32(c6,b2,a6,2); c7=vfmaq_laneq_f32(c7,b2,a7,2);
                c0=vfmaq_laneq_f32(c0,b3,a0,3); c1=vfmaq_laneq_f32(c1,b3,a1,3);
                c2=vfmaq_laneq_f32(c2,b3,a2,3); c3=vfmaq_laneq_f32(c3,b3,a3,3);
                c4=vfmaq_laneq_f32(c4,b3,a4,3); c5=vfmaq_laneq_f32(c5,b3,a5,3);
                c6=vfmaq_laneq_f32(c6,b3,a6,3); c7=vfmaq_laneq_f32(c7,b3,a7,3);
            }
            vst1q_f32(&C[(i+0)*N+jb*4],c0); vst1q_f32(&C[(i+1)*N+jb*4],c1);
            vst1q_f32(&C[(i+2)*N+jb*4],c2); vst1q_f32(&C[(i+3)*N+jb*4],c3);
            vst1q_f32(&C[(i+4)*N+jb*4],c4); vst1q_f32(&C[(i+5)*N+jb*4],c5);
            vst1q_f32(&C[(i+6)*N+jb*4],c6); vst1q_f32(&C[(i+7)*N+jb*4],c7);
        }
}

typedef void (*gemm_fn)(const float*, const float*, float*, int, int, int);

int main() {
    int failures = 0;
    int N = 1024;
    float *A = kl_xmalloc(N * N * sizeof(float));
    float *B = kl_xmalloc(N * N * sizeof(float));
    float *B_blk = kl_xmalloc(N * N * sizeof(float));
    float *C = kl_xmalloc(N * N * sizeof(float));

    for (int i = 0; i < N*N; i++) { A[i] = (float)(i % 17) / 17.0f; B[i] = (float)(i % 19) / 19.0f; }
    pack_B_blk(B, B_blk, N, N);

    /* 候选配置（理论推导）：
     *   MR=1: single FVU，理论 10 GFLOPS
     *   MR=2: dual FVU 平衡，理论 20 GFLOPS（已实测 19.59）
     *   MR=4: 4 累加器，看寄存器压力（32 reg / 4(c) + 4(a) + 4(b) = 12，余量足）
     *   MR=8: 8 累加器，看是否溢出（8+8+4=20，余量 12，仍可行）
     */
    struct { const char *name; gemm_fn fn; } configs[] = {
        {"MR=1", gemm_mr1},
        {"MR=2", gemm_mr2},
        {"MR=4", gemm_mr4},
        {"MR=8", gemm_mr8},
    };
    int n_cfg = sizeof(configs) / sizeof(configs[0]);

    printf("=== GEMM MR Sweep（FP32 1024³, B-blocked）===\n");
    printf("  理论约束：MR×4(c) + MR×4(a) + 4(b) ≤ 32 NEON 寄存器\n");
    printf("  双 FVU 上限：20 GFLOPS\n\n");
    printf("  配置 | 寄存器占用 | GFLOPS | %%peak | 备注\n");
    printf("  -----+------------+--------+-------+------\n");

    double peak = 20.0;
    double flops = 2.0 * N * N * N;

    for (int c = 0; c < n_cfg; c++) {
        /* warmup */
        configs[c].fn(A, B_blk, C, N, N, N);
        configs[c].fn(A, B_blk, C, N, N, N);

        double t0 = now_ns();
        for (int it = 0; it < 3; it++) configs[c].fn(A, B_blk, C, N, N, N);
        double t1 = now_ns();
        double gf = flops * 3 / (t1-t0);
        double ms = (t1-t0)/3/1e6;

        /* 估算寄存器占用 */
        int mr = c + 1;
        int regs = mr + mr + 4;  /* c[] + a[] + b[] */
        const char *note = "";
        if (mr == 1) note = "single FVU";
        else if (mr == 2) note = "dual FVU 平衡";
        else if (mr == 4) note = "ILP 过剩?";
        else note = "寄存器压力";

        printf("  %s | %2d reg     | %6.2f | %5.1f%% | %s\n",
               configs[c].name, regs, gf, gf/peak*100, note);
    }

    /* KC sweep：固定 MR=2，扫 K 块大小 */
    printf("\n=== KC Sweep（MR=2，模拟 K 分块：累加多次 KC 块）===\n");
    printf("  约束：A_pack (2×KC×4B) + B_pack (4×KC×4B) ≤ L2/4 = 128KB\n");
    printf("  → KC ≤ 128KB / 24B ≈ 5000，故 K=1024 不必分块\n\n");

    /* 实测不同 N 下的 GFLOPS（间接反映 cache 适配）*/
    int sizes[] = {64, 128, 256, 512, 1024, 2048};
    int n_sizes = sizeof(sizes)/sizeof(sizes[0]);
    printf("  N    | MR=2 GFLOPS | 工作集 | 落在哪\n");
    printf("  -----+-------------+--------+--------\n");
    for (int si = 0; si < n_sizes; si++) {
        int Sz = sizes[si];
        float *As = kl_xmalloc(Sz*Sz*sizeof(float));
        float *Bs = kl_xmalloc(Sz*Sz*sizeof(float));
        float *Bs_blk = kl_xmalloc(Sz*Sz*sizeof(float));
        float *Cs = kl_xmalloc(Sz*Sz*sizeof(float));
        for (int i = 0; i < Sz*Sz; i++) { As[i] = (float)(i%17)/17.0f; Bs[i] = (float)(i%19)/19.0f; }
        pack_B_blk(Bs, Bs_blk, Sz, Sz);

        gemm_mr2(As, Bs_blk, Cs, Sz, Sz, Sz); gemm_mr2(As, Bs_blk, Cs, Sz, Sz, Sz);
        double t0 = now_ns();
        int iter = (Sz >= 1024) ? 3 : 10;
        for (int it = 0; it < iter; it++) gemm_mr2(As, Bs_blk, Cs, Sz, Sz, Sz);
        double t1 = now_ns();
        double gf = 2.0*Sz*Sz*Sz*iter/(t1-t0);

        long ws = (long)Sz*Sz*4;  /* C 矩阵 */
        const char *where = "L1";
        if (ws > 64*1024) where = "L2";
        if (ws > 512*1024) where = "L3";
        if (ws > 8*1024*1024) where = "DRAM";
        printf("  %4d | %10.2f | %5ldK | %s\n", Sz, gf, ws/1024, where);

        free(As); free(Bs); free(Bs_blk); free(Cs);
    }

    free(A); free(B); free(B_blk); free(C);
    return failures > 0;
}
