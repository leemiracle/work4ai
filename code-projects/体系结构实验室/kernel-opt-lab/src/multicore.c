/* ============================================================================
 * bench_multicore.c — 多核 OpenMP 扩展性测试
 *
 * 在 v4 GEMM 和卷积上加 #pragma omp parallel for
 * 测 1/2/4/8 核扩展性（D3000 8 核）
 * ============================================================================ */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
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

#define M 1024
#define K 1024
#define N 1024

static void pack_B_blk(const float *B, float *B_blk) {
    #pragma omp parallel for
    for (int jb = 0; jb < N / 4; jb++) {
        for (int k = 0; k < K; k++)
            for (int ji = 0; ji < 4; ji++)
                B_blk[jb * K * 4 + k * 4 + ji] = B[(jb * 4 + ji) * K + k];
    }
}

/* 单核 v4 dual FVU（参考实现）*/
static void gemm_v4_dual(const float *A, const float *B_blk, float *C) {
    int M2 = M & ~1;
    for (int i = 0; i < M2; i += 2) {
        for (int jb = 0; jb < N / 4; jb++) {
            int j = jb * 4;
            const float *b_base = &B_blk[jb * K * 4];
            float32x4_t c0 = vdupq_n_f32(0);
            float32x4_t c1 = vdupq_n_f32(0);
            for (int k = 0; k < K; k += 4) {
                float32x4_t a0 = vld1q_f32(&A[(i+0) * K + k]);
                float32x4_t a1 = vld1q_f32(&A[(i+1) * K + k]);
                float32x4_t col_0 = vld1q_f32(&b_base[(k+0)*4]);
                float32x4_t col_1 = vld1q_f32(&b_base[(k+1)*4]);
                float32x4_t col_2 = vld1q_f32(&b_base[(k+2)*4]);
                float32x4_t col_3 = vld1q_f32(&b_base[(k+3)*4]);
                c0 = vfmaq_laneq_f32(c0, col_0, a0, 0);
                c1 = vfmaq_laneq_f32(c1, col_0, a1, 0);
                c0 = vfmaq_laneq_f32(c0, col_1, a0, 1);
                c1 = vfmaq_laneq_f32(c1, col_1, a1, 1);
                c0 = vfmaq_laneq_f32(c0, col_2, a0, 2);
                c1 = vfmaq_laneq_f32(c1, col_2, a1, 2);
                c0 = vfmaq_laneq_f32(c0, col_3, a0, 3);
                c1 = vfmaq_laneq_f32(c1, col_3, a1, 3);
            }
            vst1q_f32(&C[(i+0)*N + j], c0);
            vst1q_f32(&C[(i+1)*N + j], c1);
        }
    }
}

/* 多核版：外层 i 循环并行 */
static void gemm_v4_dual_omp(const float *A, const float *B_blk, float *C, int nthreads) {
    int M2 = M & ~1;
    #pragma omp parallel for num_threads(nthreads) schedule(static)
    for (int i = 0; i < M2; i += 2) {
        for (int jb = 0; jb < N / 4; jb++) {
            int j = jb * 4;
            const float *b_base = &B_blk[jb * K * 4];
            float32x4_t c0 = vdupq_n_f32(0);
            float32x4_t c1 = vdupq_n_f32(0);
            for (int k = 0; k < K; k += 4) {
                float32x4_t a0 = vld1q_f32(&A[(i+0) * K + k]);
                float32x4_t a1 = vld1q_f32(&A[(i+1) * K + k]);
                float32x4_t col_0 = vld1q_f32(&b_base[(k+0)*4]);
                float32x4_t col_1 = vld1q_f32(&b_base[(k+1)*4]);
                float32x4_t col_2 = vld1q_f32(&b_base[(k+2)*4]);
                float32x4_t col_3 = vld1q_f32(&b_base[(k+3)*4]);
                c0 = vfmaq_laneq_f32(c0, col_0, a0, 0);
                c1 = vfmaq_laneq_f32(c1, col_0, a1, 0);
                c0 = vfmaq_laneq_f32(c0, col_1, a0, 1);
                c1 = vfmaq_laneq_f32(c1, col_1, a1, 1);
                c0 = vfmaq_laneq_f32(c0, col_2, a0, 2);
                c1 = vfmaq_laneq_f32(c1, col_2, a1, 2);
                c0 = vfmaq_laneq_f32(c0, col_3, a0, 3);
                c1 = vfmaq_laneq_f32(c1, col_3, a1, 3);
            }
            vst1q_f32(&C[(i+0)*N + j], c0);
            vst1q_f32(&C[(i+1)*N + j], c1);
        }
    }
}

static double now_ns() {
    struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t);
    return t.tv_sec * 1e9 + t.tv_nsec;
}

int main() {
    int failures = 0;
    float *A = kl_xmalloc(M * K * sizeof(float));
    float *B = kl_xmalloc(N * K * sizeof(float));
    float *B_blk = kl_xmalloc(N * K * sizeof(float));
    float *C = kl_xmalloc(M * N * sizeof(float));

    for (int i = 0; i < M * K; i++) A[i] = (float)(i % 17) / 17.0f;
    for (int i = 0; i < N * K; i++) B[i] = (float)(i % 19) / 19.0f;
    pack_B_blk(B, B_blk);

#ifdef _OPENMP
    int max_threads = omp_get_max_threads();
    printf("OpenMP 可用，最大线程数: %d\n\n", max_threads);
#else
    printf("OpenMP 未启用！\n");
    return 1;
#endif

    double gflops = 2.0 * M * K * N;
    printf("=== FP32 GEMM 1024³ 多核扩展性 ===\n");
    printf("  线程数 |  时间(ms) | GFLOPS | 加速比 | 效率\n");
    printf("  ------+-----------+--------+--------+------\n");

    /* 先单核 */
    double t0 = now_ns();
    for (int it = 0; it < 3; it++) gemm_v4_dual(A, B_blk, C);
    double t1 = now_ns();
    double ms1 = (t1-t0)/3/1e6;
    double gf1 = gflops * 3 / (t1-t0);
    printf("  1     | %9.1f | %6.2f |  1.00x | 100%%\n", ms1, gf1);

    /* 多核 */
    int thread_list[] = {2, 4, 8, max_threads};
    int n_list = sizeof(thread_list) / sizeof(thread_list[0]);
    for (int idx = 0; idx < n_list; idx++) {
        int nt = thread_list[idx];
        double t0 = now_ns();
        for (int it = 0; it < 3; it++) gemm_v4_dual_omp(A, B_blk, C, nt);
        double t1 = now_ns();
        double ms = (t1-t0)/3/1e6;
        double gf = gflops * 3 / (t1-t0);
        double speedup = ms1 / ms;
        double eff = speedup / nt * 100;
        printf("  %d     | %9.1f | %6.2f | %5.2fx | %4.1f%%\n",
               nt, ms, gf, speedup, eff);
    }

    free(A); free(B); free(B_blk); free(C);
    return failures > 0;
}
