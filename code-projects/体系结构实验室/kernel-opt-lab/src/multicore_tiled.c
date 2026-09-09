/* ============================================================================
 * multicore_tiled.c — MC×NC 分块多核 GEMM（验证 OS 专家盲区⑥）
 *
 * OS 专家论断：multicore.c flat 并行导致 8 核 16MB C 超 L3，应做 MC×NC=512
 * 本文件验证：flat vs MC×NC 分块的实际差异
 *
 * 简化版：用 v5_mr8 内核 + 外层 MC×NC 分块（每块 1MB 装进 L3）
 * ============================================================================ */
#include <stdio.h>
#include <stdlib.h>
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

#define N 1024

static double now_ns() {
    struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t);
    return t.tv_sec * 1e9 + t.tv_nsec;
}

/* pack B 子块：B[JC..JC+NC][K] → B_blk[NC/4][K][4] */
static void pack_B_sub(const float *B, float *B_blk, int JC, int NC, int K) {
    for (int jb = 0; jb < NC/4; jb++)
        for (int k = 0; k < K; k++)
            for (int ji = 0; ji < 4; ji++)
                B_blk[jb * K * 4 + k * 4 + ji] = B[(JC + jb*4 + ji) * K + k];
}

/* v5_mr8 微内核：M_sub×NC×K GEMM（M_sub ≤ 当前 MC）*/
static void gemm_mr8_sub(const float *A, const float *B_blk, float *C,
                         int M_sub, int NC, int K, int N_full) {
    int M8 = M_sub & ~7;
    for (int i = 0; i < M8; i += 8)
        for (int jb = 0; jb < NC/4; jb++) {
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
            vst1q_f32(&C[(i+0)*N_full+jb*4],c0);vst1q_f32(&C[(i+1)*N_full+jb*4],c1);
            vst1q_f32(&C[(i+2)*N_full+jb*4],c2);vst1q_f32(&C[(i+3)*N_full+jb*4],c3);
            vst1q_f32(&C[(i+4)*N_full+jb*4],c4);vst1q_f32(&C[(i+5)*N_full+jb*4],c5);
            vst1q_f32(&C[(i+6)*N_full+jb*4],c6);vst1q_f32(&C[(i+7)*N_full+jb*4],c7);
        }
}

/* flat 并行（基线，同 multicore.c 思路）：i 维并行 */
static void gemm_flat(const float *A, const float *B_blk, float *C, int nthreads) {
    #pragma omp parallel for num_threads(nthreads) schedule(static)
    for (int i = 0; i < N; i += 8)
        gemm_mr8_sub(&A[i*N], B_blk, &C[i*N], 8, N, N, N);
}

/* MC×NC 分块并行：外层串行 (ic, jc)，内层 OMP 并行 ic 内部 i 行
 * MC=256（每块 C: 256×256×4=256KB，装 L2）, NC=512（B_blk 子块: 512×N×4=2MB，装 L3）*/
static void gemm_tiled(const float *A, const float *B, float *C, int nthreads,
                       int MC, int NC) {
    /* 预 pack 全部 B（按 NC 分块）*/
    float *Bb = kl_xmalloc(N * N * sizeof(float));
    pack_B_sub(B, Bb, 0, N, N);

    for (int ic = 0; ic < N; ic += MC) {
        int MC_now = (ic + MC <= N) ? MC : N - ic;
        #pragma omp parallel for num_threads(nthreads) schedule(static)
        for (int ii = 0; ii < MC_now; ii += 8) {
            int M_sub = (ii + 8 <= MC_now) ? 8 : (MC_now - ii);
            /* v0.9 安全修复（安全专家盲区③）：原代码 if (M_sub==8) 跳过 tail，
             * 导致奇数 MC_now 时尾部行静默错误。改为：tail 也走 mr8（M=1024
             * 是 8 倍数不会触发，但通用性必须保留）。*/
            if (M_sub == 8)
                gemm_mr8_sub(&A[(ic+ii)*N], Bb, &C[(ic+ii)*N], M_sub, N, N, N);
            else {
                /* tail：标量兜底，避免静默错误 */
                const float *a_row = &A[(ic+ii)*N];
                float *c_row = &C[(ic+ii)*N];
                for (int i = 0; i < M_sub; i++)
                    for (int jb = 0; jb < N/4; jb++) {
                        const float *b = &Bb[jb*N*4];
                        float32x4_t c = vld1q_f32(&c_row[i*N+jb*4]);
                        for (int k = 0; k < N; k += 4) {
                            float32x4_t a = vld1q_f32(&a_row[i*N+k]);
                            c = vfmaq_laneq_f32(c, vld1q_f32(&b[(k+0)*4]), a, 0);
                            c = vfmaq_laneq_f32(c, vld1q_f32(&b[(k+1)*4]), a, 1);
                            c = vfmaq_laneq_f32(c, vld1q_f32(&b[(k+2)*4]), a, 2);
                            c = vfmaq_laneq_f32(c, vld1q_f32(&b[(k+3)*4]), a, 3);
                        }
                        vst1q_f32(&c_row[i*N+jb*4], c);
                    }
            }
        }
    }
    free(Bb);
}

int main() {
    int failures = 0;
    float *A = kl_xmalloc(N*N*sizeof(float));
    float *B = kl_xmalloc(N*N*sizeof(float));
    float *Bb = kl_xmalloc(N*N*sizeof(float));
    float *C = kl_xcalloc(N*N, sizeof(float));

    for (int i=0;i<N*N;i++){A[i]=(float)(i%17)/17.0f;B[i]=(float)(i%19)/19.0f;}
    pack_B_sub(B, Bb, 0, N, N);

    printf("# MC×NC 分块 vs flat 多核 GEMM 对比\n\n");
    printf("矩阵: 1024³ FP32, MR=8 微内核\n\n");

    double flops = 2.0*N*N*N;

    /* flat 基线 */
    printf("## 1. flat 并行（同 multicore.c）\n\n");
    printf("| 线程 | 时间 ms | GFLOPS | 效率 |\n|---|---|---|---|\n");
    double t0_single = now_ns();
    for (int it=0; it<3; it++) gemm_mr8_sub(A, Bb, C, N, N, N, N);
    double t1_single = now_ns();
    double gf_single = flops*3/(t1_single-t0_single);
    printf("| 1 | %.1f | %.2f | 100%% |\n", (t1_single-t0_single)/3/1e6, gf_single);

    for (int nt = 2; nt <= 8; nt *= 2) {
        double t0 = now_ns();
        for (int it=0; it<3; it++) gemm_flat(A, Bb, C, nt);
        double t1 = now_ns();
        double ms = (t1-t0)/3/1e6;
        double gf = flops*3/(t1-t0);
        printf("| %d | %.1f | %.2f | %.1f%% |\n", nt, ms, gf, gf/gf_single/nt*100);
    }

    /* tiled（MC=256）*/
    printf("\n## 2. MC×NC 分块（MC=256, 内层 OMP）\n\n");
    printf("| 线程 | 时间 ms | GFLOPS | 效率 |\n|---|---|---|---|\n");
    for (int nt = 2; nt <= 8; nt *= 2) {
        double t0 = now_ns();
        for (int it=0; it<3; it++) gemm_tiled(A, B, C, nt, 256, N);
        double t1 = now_ns();
        double ms = (t1-t0)/3/1e6;
        double gf = flops*3/(t1-t0);
        printf("| %d | %.1f | %.2f | %.1f%% |\n", nt, ms, gf, gf/gf_single/nt*100);
    }

    printf("\n## 关键洞察\n\n");
    printf("- 如果 tiled 比 flat 快 → OS 专家盲区⑥成立（L3 容量是真瓶颈）\n");
    printf("- 如果 tiled 没快 → 真因不是 L3 容量，可能是 DRAM 带宽 / TLB / 线程同步\n");
    printf("- 麒麟 V10 + libgomp 12.3.2 的实际行为可能与理论预测不同\n");

    free(A); free(B); free(Bb); free(C);
    return failures > 0;
}
