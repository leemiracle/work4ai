/* ============================================================================
 * bench_asm_kernel.c — 手写 NEON 汇编微内核 vs 编译器自动向量化
 *
 * 目标：用一个最小化 4×4 微内核展示：
 *   1. 内联汇编怎么写（约束、寄存器分配）
 *   2. 跟 PhyGCC -O3 自动生成的代码对比
 *   3. 教学价值 > 实际性能（v4_dual 已 97.9%，手写难再突破）
 *
 * 微内核：计算 C[4×4] += A[4] × B[4×4]
 *   A 是 4 个 float（K 维一次）
 *   B 是 4×4 块（4 个 j × 4 个 k），16 个 float 连续
 *   C 是 4 个累加器（c0..c3），每个 float32x4_t
 *
 * 每次内迭代：
 *   a0 = vld1q_f32(A + k)        // 1 ld
 *   b = vld1q_f32(B + k*16)      // 1 ld（一次拿 4×4 块）
 *   c_i += b_lane_i × a_lane_i   // 4 次 fmla
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

static void pack_B_blk(const float *B, float *B_blk) {
    for (int jb = 0; jb < N / 4; jb++)
        for (int k = 0; k < K; k++)
            for (int ji = 0; ji < 4; ji++)
                B_blk[jb * K * 4 + k * 4 + ji] = B[(jb * 4 + ji) * K + k];
}

/* ---------- C 内联版（基准）：编译器自动调度 ---------- */
static void micro_kernel_c(const float *A, const float *B_blk, float *C,
                            int M2, int N2, int K_) {
    for (int i = 0; i < M2; i++) {
        for (int jb = 0; jb < N2 / 4; jb++) {
            const float *b_base = &B_blk[jb * K_ * 4];
            float32x4_t c0 = vdupq_n_f32(0);
            for (int k = 0; k < K_; k += 4) {
                float32x4_t a0 = vld1q_f32(&A[i * K_ + k]);
                float32x4_t col_0 = vld1q_f32(&b_base[(k+0)*4]);
                float32x4_t col_1 = vld1q_f32(&b_base[(k+1)*4]);
                float32x4_t col_2 = vld1q_f32(&b_base[(k+2)*4]);
                float32x4_t col_3 = vld1q_f32(&b_base[(k+3)*4]);
                c0 = vfmaq_laneq_f32(c0, col_0, a0, 0);
                c0 = vfmaq_laneq_f32(c0, col_1, a0, 1);
                c0 = vfmaq_laneq_f32(c0, col_2, a0, 2);
                c0 = vfmaq_laneq_f32(c0, col_3, a0, 3);
            }
            vst1q_f32(&C[i * N2 + jb*4], c0);
        }
    }
}

/* ---------- 内联汇编版：手写一个 K 内迭代 ----------
 * 计算 c0 += col_m × a0[m] for m=0..3
 * 等价于 c0 = vfmaq_laneq_f32(c0, col_m, a0, m)
 *
 * 关键 ARMv8 NEON 指令：
 *   ld1 {vN.4s}, [X]        // 加载 4 个 float
 *   fmla vD.4s, vN.4s, vM.s[idx]   // vD += vN × vM[idx]（标量广播）
 *
 * 用 "v" 约束让 GCC 自由分配 NEON 寄存器，"r" 分配 GPR
 */
static inline float32x4_t fma_lane_4(float32x4_t c, float32x4_t a0,
                                      float32x4_t col0, float32x4_t col1,
                                      float32x4_t col2, float32x4_t col3) {
    float32x4_t result = c;
    __asm__ (
        "fmla %[res].4s, %[c0].4s, %[a].s[0]\n\t"
        "fmla %[res].4s, %[c1].4s, %[a].s[1]\n\t"
        "fmla %[res].4s, %[c2].4s, %[a].s[2]\n\t"
        "fmla %[res].4s, %[c3].4s, %[a].s[3]\n\t"
        : [res] "=w" (result)
        : "[res]" (result),
          [a] "w" (a0),
          [c0] "w" (col0), [c1] "w" (col1),
          [c2] "w" (col2), [c3] "w" (col3)
    );
    return result;
}

static void micro_kernel_asm(const float *A, const float *B_blk, float *C,
                              int M2, int N2, int K_) {
    for (int i = 0; i < M2; i++) {
        for (int jb = 0; jb < N2 / 4; jb++) {
            const float *b_base = &B_blk[jb * K_ * 4];
            float32x4_t c0 = vdupq_n_f32(0);
            for (int k = 0; k < K_; k += 4) {
                float32x4_t a0 = vld1q_f32(&A[i * K_ + k]);
                float32x4_t col_0 = vld1q_f32(&b_base[(k+0)*4]);
                float32x4_t col_1 = vld1q_f32(&b_base[(k+1)*4]);
                float32x4_t col_2 = vld1q_f32(&b_base[(k+2)*4]);
                float32x4_t col_3 = vld1q_f32(&b_base[(k+3)*4]);
                c0 = fma_lane_4(c0, a0, col_0, col_1, col_2, col_3);
            }
            vst1q_f32(&C[i * N2 + jb*4], c0);
        }
    }
}

static double now_ns() {
    struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t);
    return t.tv_sec * 1e9 + t.tv_nsec;
}

static void gemm_f32_scalar_ref(const float *A, const float *B, float *C) {
    for (int i = 0; i < M; i++)
        for (int j = 0; j < N; j++) {
            float s = 0;
            for (int k = 0; k < K; k++) s += A[i*K+k] * B[j*K+k];
            C[i*N+j] = s;
        }
}

int main() {
    int failures = 0;
    float *A = kl_xmalloc(M * K * sizeof(float));
    float *B = kl_xmalloc(N * K * sizeof(float));
    float *B_blk = kl_xmalloc(N * K * sizeof(float));
    float *Cc = kl_xmalloc(M * N * sizeof(float));
    float *Ca = kl_xmalloc(M * N * sizeof(float));
    float *Cs = kl_xmalloc(M * N * sizeof(float));

    for (int i = 0; i < M * K; i++) A[i] = (float)(i % 17) / 17.0f;
    for (int i = 0; i < N * K; i++) B[i] = (float)(i % 19) / 19.0f;
    pack_B_blk(B, B_blk);

    printf("=== Correctness (8×8) ===\n");
    /* 注意：传 N2=1024 让 micro_kernel 输出布局跟 Cs 一致 */
    micro_kernel_c(A, B_blk, Cc, 8, N, K);   /* M=8, N=1024 → 写 Cc[0..8][0..1024] */
    micro_kernel_asm(A, B_blk, Ca, 8, N, K);
    gemm_f32_scalar_ref(A, B, Cs);            /* 写 Cs[0..1024][0..1024] */
    float md_c = 0, md_a = 0;
    for (int i = 0; i < 8; i++) for (int j = 0; j < 8; j++) {
        float dc = fabsf(Cc[i*N+j] - Cs[i*N+j]);
        float da = fabsf(Ca[i*N+j] - Cs[i*N+j]);
        if (dc > md_c) md_c = dc;
        if (da > md_a) md_a = da;
    }
    if (md_c >= 1e-4) failures++;
    printf("  C version vs scalar:    %s (max_diff=%.2e)\n", md_c<1e-4?"✅":"❌", md_c);
    if (md_a >= 1e-4) failures++;
    printf("  ASM version vs scalar:  %s (max_diff=%.2e)\n", md_a<1e-4?"✅":"❌", md_a);

    printf("\n=== Performance (1024³, single FVU 对照) ===\n");
    printf("  ⚠️  注：这两个都是 single FVU 实现，对比的是\n");
    printf("     编译器调度 vs 手写 ASM 在 single FVU 下的差异\n\n");

    double gf = 2.0 * M * K * N;
    double t0, t1;
    int ITER = 3;

    t0 = now_ns();
    for (int it = 0; it < ITER; it++) micro_kernel_c(A, B_blk, Cc, M, N, K);
    t1 = now_ns();
    printf("  C 内联 (PhyGCC -O3 调度)  : %7.2f ms  %6.2f GFLOPS\n",
           (t1-t0)/ITER/1e6, gf*ITER/(t1-t0));

    t0 = now_ns();
    for (int it = 0; it < ITER; it++) micro_kernel_asm(A, B_blk, Ca, M, N, K);
    t1 = now_ns();
    printf("  内联 ASM (手写 fmla 调度)  : %7.2f ms  %6.2f GFLOPS\n",
           (t1-t0)/ITER/1e6, gf*ITER/(t1-t0));

    printf("\n  理论峰值 single FVU: 10 GFLOPS\n");
    printf("  → 看 PhyGCC 自动调度 vs 手写 ASM 的差距\n");

    free(A); free(B); free(B_blk); free(Cc); free(Ca); free(Cs);
    return failures > 0;
}
