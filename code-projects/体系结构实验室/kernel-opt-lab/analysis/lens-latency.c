/* ============================================================================
 * lens-latency.c — 视角 5：延迟分布 p50/p90/p99（长尾分析）
 *
 * 当前 baseline.md 只报"平均 GFLOPS"，掩盖了：
 *   - OS 调度抢占导致的 tail latency
 *   - 单次 cold start vs warm 差异
 *   - 是否有稳定的实时性（关键应用：自动驾驶、语音助手）
 *
 * 本 lens 跑 N 次单次 GEMM 调用，记录每次延迟，输出分布
 * ============================================================================ */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>
#include <arm_neon.h>

static double now_ns() {
    struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t);
    return t.tv_sec * 1e9 + t.tv_nsec;
}

#define N 1024
#define SAMPLES 1000

static void pack_B(const float *B, float *Bb) {
    for (int jb=0;jb<N/4;jb++) for (int k=0;k<N;k++) for (int j=0;j<4;j++)
        Bb[jb*N*4+k*4+j] = B[(jb*4+j)*N+k];
}

/* GEMM MR=8（同 baseline）*/
static void gemm_mr8(const float *A, const float *Bb, float *C) {
    for (int i=0;i<N;i+=8) for (int jb=0;jb<N/4;jb++) {
        const float *b=&Bb[jb*N*4];
        float32x4_t c0=vdupq_n_f32(0),c1=vdupq_n_f32(0),c2=vdupq_n_f32(0),c3=vdupq_n_f32(0);
        float32x4_t c4=vdupq_n_f32(0),c5=vdupq_n_f32(0),c6=vdupq_n_f32(0),c7=vdupq_n_f32(0);
        for (int k=0;k<N;k+=4) {
            float32x4_t a0=vld1q_f32(&A[(i+0)*N+k]),a1=vld1q_f32(&A[(i+1)*N+k]);
            float32x4_t a2=vld1q_f32(&A[(i+2)*N+k]),a3=vld1q_f32(&A[(i+3)*N+k]);
            float32x4_t a4=vld1q_f32(&A[(i+4)*N+k]),a5=vld1q_f32(&A[(i+5)*N+k]);
            float32x4_t a6=vld1q_f32(&A[(i+6)*N+k]),a7=vld1q_f32(&A[(i+7)*N+k]);
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
}

/* 小算子：Element-wise add（看小算子的 OS 噪声占比）*/
static int g_n_add = 16*1024;  /* 64KB / 4B，全局变量避免函数指针 cast */
static void elem_add_wrap(float *A, float *B, float *C) {
    for (int i=0;i<g_n_add;i+=4) {
        float32x4_t a=vld1q_f32(&A[i]),b=vld1q_f32(&B[i]);
        vst1q_f32(&C[i], vaddq_f32(a,b));
    }
}

static int cmp_double(const void *a, const void *b) {
    double d = *(const double*)a - *(const double*)b;
    return d < 0 ? -1 : (d > 0 ? 1 : 0);
}
static double percentile(double *sorted, int n, double p) {
    int idx = (int)(p * n);
    if (idx >= n) idx = n - 1;
    return sorted[idx];
}

static void measure_dist(const char *name, void (*run)(float*, float*, float*),
                         float *A, float *B, float *C, int warmup_iter) {
    static double latencies[SAMPLES];
    /* warmup */
    for (int i = 0; i < warmup_iter; i++) run(A, B, C);

    /* 采样 */
    for (int i = 0; i < SAMPLES; i++) {
        double t0 = now_ns();
        run(A, B, C);
        latencies[i] = now_ns() - t0;
    }
    qsort(latencies, SAMPLES, sizeof(double), cmp_double);

    double p50 = percentile(latencies, SAMPLES, 0.50);
    double p90 = percentile(latencies, SAMPLES, 0.90);
    double p99 = percentile(latencies, SAMPLES, 0.99);
    double p999 = percentile(latencies, SAMPLES, 0.999);
    double min = latencies[0];
    double max = latencies[SAMPLES-1];
    double mean = 0; for (int i=0;i<SAMPLES;i++) mean += latencies[i];
    mean /= SAMPLES;

    double tail_ratio = p99 / p50;

    printf("| %s | %.2f | %.2f | %.2f | %.2f | %.2f | %.2f | %.2f× | %s |\n",
           name, min/1e6, p50/1e6, p90/1e6, p99/1e6, p999/1e6, max/1e6,
           tail_ratio,
           tail_ratio > 1.5 ? "⚠️ 长尾" : (tail_ratio > 1.2 ? "轻微抖动" : "✓ 稳定"));
}

int main() {
    printf("# Lens 5: 延迟分布 p50/p90/p99（长尾分析）\n\n");
    printf("采样 %d 次单次调用，看 OS 调度/中断导致的 tail latency\n\n", SAMPLES);

    static float A[N*N], B[N*N], Bb[N*N], C[N*N];
    for (int i = 0; i < N*N; i++) { A[i] = (float)(i%17)/17.0f; B[i] = (float)(i%19)/19.0f; }
    pack_B(B, Bb);

    printf("| 算子 | min | p50 | p90 | p99 | p99.9 | max | p99/p50 | 评价 |\n");
    printf("|---|---|---|---|---|---|---|---|---|\n");

    /* GEMM（~55ms/次，1000 次 ≈ 55 秒）*/
    measure_dist("GEMM MR=8 1024³",
                 (void(*)(float*,float*,float*))gemm_mr8, A, Bb, C, 5);

    /* 小算子 elem_add on 64KB（~0.01ms/次） */
    measure_dist("Elem-add 64KB", elem_add_wrap, A, B, C, 100);

    printf("\n## 关键洞察\n\n");
    printf("- **p99/p50 > 1.5** 表示有明显长尾（OS 抢占 / 中断 / cache 污染）\n");
    printf("- **大算子（GEMM）** p99/p50 应接近 1（计算时间 >> OS 噪声）\n");
    printf("- **小算子（elem-add）** p99/p50 可能很大（OS 噪声占比高）\n");
    printf("- **max vs p99**：若 max 远超 p99，是偶发大抢占（context switch）\n");
    printf("\n**实时性结论**：\n");
    printf("- D3000 + 麒麟 V10 不是 RTOS，**不适合硬实时**（p99/p50 不可控）\n");
    printf("- 对**软实时**（语音/视频 30ms deadline）：算子选小一点 + 留 50%% 余量\n");
    printf("- 对**.batch 推理**：tail 不重要，关注平均吞吐\n");
    printf("\n**优化方向**：\n");
    printf("- `taskset` 绑核 / `chrt` 提优先级 / `isolcpus` 隔离核 → 减小长尾\n");
    printf("- `mlockall` 锁内存 → 避免 page fault\n");
    printf("- 关闭 IRQ 路由到目标核 → 减少 context switch\n");
    return 0;
}
