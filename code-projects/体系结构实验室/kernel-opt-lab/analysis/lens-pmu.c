/* ============================================================================
 * lens-pmu.c — 视角 2：PMU 微架构计数器（IPC / cache / branch）
 *
 * 通过 perf_event_open(2) 系统调用拿硬件计数器：
 *   - CPU_CYCLES / INSTRUCTIONS → IPC（IPC<1 表示 stall 多）
 *   - CACHE_REFERENCES / MISSES → L1D 命中率
 *   - BRANCH_INSTRUCTIONS / MISSES → 分支预测准确率
 *
 * 体系结构解读：
 *   - 高 IPC（>2）+ 低 cache miss → 微架构效率高，瓶颈在 FPU 算力
 *   - 低 IPC（<1）+ 高 cache miss → 数据搬运是瓶颈
 *   - 高 branch miss → 分支密集型，需要循环展开/无分支
 *
 * 用 perf_event_paranoid=1 即可（当前 D3000 满足）
 * ============================================================================ */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <sys/syscall.h>
#include <linux/perf_event.h>
#include <arm_neon.h>

static double now_ns() {
    struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t);
    return t.tv_sec * 1e9 + t.tv_nsec;
}

/* === perf_event 封装 === */
typedef struct {
    int cycles, inst, cache_ref, cache_miss, br, br_miss;
} pmu_t;

static int perf_open_cpu(int hw_type) {
    struct perf_event_attr pe;
    memset(&pe, 0, sizeof(pe));
    pe.type = PERF_TYPE_HARDWARE;
    pe.size = sizeof(pe);
    pe.config = hw_type;
    pe.disabled = 1;
    pe.exclude_kernel = 1;
    pe.exclude_hv = 1;
    int fd = syscall(__NR_perf_event_open, &pe, 0, -1, -1, 0);
    return fd;
}

static pmu_t pmu_start() {
    pmu_t p;
    p.cycles     = perf_open_cpu(PERF_COUNT_HW_CPU_CYCLES);
    p.inst       = perf_open_cpu(PERF_COUNT_HW_INSTRUCTIONS);
    p.cache_ref  = perf_open_cpu(PERF_COUNT_HW_CACHE_REFERENCES);
    p.cache_miss = perf_open_cpu(PERF_COUNT_HW_CACHE_MISSES);
    p.br         = perf_open_cpu(PERF_COUNT_HW_BRANCH_INSTRUCTIONS);
    p.br_miss    = perf_open_cpu(PERF_COUNT_HW_BRANCH_MISSES);
    int fds[] = {p.cycles, p.inst, p.cache_ref, p.cache_miss, p.br, p.br_miss};
    for (int i = 0; i < 6; i++) if (fds[i] > 0) ioctl(fds[i], PERF_EVENT_IOC_ENABLE, 0);
    return p;
}

static void pmu_stop_read(pmu_t *p, long *out) {
    int fds[] = {p->cycles, p->inst, p->cache_ref, p->cache_miss, p->br, p->br_miss};
    for (int i = 0; i < 6; i++) {
        if (fds[i] > 0) {
            ioctl(fds[i], PERF_EVENT_IOC_DISABLE, 0);
            read(fds[i], &out[i], sizeof(long));
            close(fds[i]);
        } else out[i] = -1;
    }
}

/* === 测试算子（不同 bound 性质）=== */

/* 1. GEMM MR=8（compute-bound）*/
static void pack_B(const float *B, float *Bb, int N, int K) {
    for (int jb=0;jb<N/4;jb++) for (int k=0;k<K;k++) for (int j=0;j<4;j++)
        Bb[jb*K*4+k*4+j] = B[(jb*4+j)*K+k];
}
static void gemm_mr8(const float *A, const float *Bb, float *C, int M, int N, int K) {
    for (int i=0;i<M;i+=8) for (int jb=0;jb<N/4;jb++) {
        const float *b=&Bb[jb*K*4];
        float32x4_t c0=vdupq_n_f32(0),c1=vdupq_n_f32(0),c2=vdupq_n_f32(0),c3=vdupq_n_f32(0);
        float32x4_t c4=vdupq_n_f32(0),c5=vdupq_n_f32(0),c6=vdupq_n_f32(0),c7=vdupq_n_f32(0);
        for (int k=0;k<K;k+=4) {
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
}

/* 2. Element-wise add（memory-bound）*/
static void elem_add(const float *A, const float *B, float *C, int N) {
    for (int i=0;i<N;i+=4) {
        float32x4_t a=vld1q_f32(&A[i]), b=vld1q_f32(&B[i]);
        vst1q_f32(&C[i], vaddq_f32(a,b));
    }
}

/* 3. Stream copy（纯 memory）*/
static void stream_copy(const float *A, float *B, int N) {
    for (int i=0;i<N;i+=4) vst1q_f32(&B[i], vld1q_f32(&A[i]));
}

/* 4. Reduction（branch + 依赖链）*/
static float reduce(const float *A, int N) {
    float32x4_t acc = vdupq_n_f32(0);
    for (int i=0;i<N;i+=4) acc = vaddq_f32(acc, vld1q_f32(&A[i]));
    float buf[4]; vst1q_f32(buf, acc);
    return buf[0]+buf[1]+buf[2]+buf[3];
}

/* 跑某算子 + 抓 PMU */
#define RUN_PMU(name, code, flops) do { \
    int N=1024; \
    float *A=malloc(N*N*4),*B=malloc(N*N*4),*Bb=malloc(N*N*4),*C=malloc(N*N*4); \
    for(int i=0;i<N*N;i++){A[i]=(float)(i%17)/17.0f;B[i]=(float)(i%19)/19.0f;} \
    pack_B(B,Bb,N,N); \
    /* warmup */ code; \
    pmu_t p = pmu_start(); \
    double t0=now_ns(); \
    for(int it=0;it<3;it++) code; \
    double t1=now_ns(); \
    long out[6]; pmu_stop_read(&p, out); \
    double gf = (flops)*3/(t1-t0); \
    printf("| %s | %.2f | %.2f | %.1f%% | %.1f%% | %.2f |\n", \
        name, gf, (double)out[1]/out[0], \
        100.0*(1.0-(double)out[3]/out[2]), \
        100.0*(1.0-(double)out[5]/out[4]), \
        (t1-t0)/3/1e6); \
    free(A);free(B);free(Bb);free(C); \
} while(0)

int main() {
    printf("# Lens 2: PMU 微架构计数器\n\n");
    printf("解读：IPC 高 → 单位 cycle 完成指令多（FPU 算力主导）\n");
    printf("      cache 命中率高 → 数据复用好\n");
    printf("      branch 准确率高 → 控制流可预测\n\n");

    printf("| 算子 | GFLOPS | IPC | Cache 命中 | Branch 准确 | 单次 ms |\n");
    printf("|---|---|---|---|---|---|\n");

    RUN_PMU("GEMM MR=8 (compute)", gemm_mr8(A,Bb,C,N,N,N), 2.0*N*N*N);
    RUN_PMU("Elem-wise add (mem)", elem_add(A,B,C,N*N), 1.0*N*N);
    RUN_PMU("Stream copy (pure mem)", stream_copy(A,C,N*N), 0.0 /* 报 0 GFLOPS */);
    RUN_PMU("Reduction (dep chain)", { volatile float r = reduce(A, N*N); (void)r; }, 1.0*N*N);

    printf("\n## 关键洞察\n\n");
    printf("- **GEMM MR=8** IPC 应该接近峰值（4-wide issue），cache 命中 >95%%\n");
    printf("- **Elem-wise** IPC 低（数据依赖 stall），cache 仍然命中（流式访问）\n");
    printf("- **Reduction** branch 准确率影响最大（循环 + 末尾 reduction 依赖链）\n");
    printf("- IPC 与 GFLOPS 的关系：IPC 高 ≠ 算力高（要看 instr 类型，FMLA vs LD/ST）\n");
    printf("\n**工程启示**：\n");
    printf("- 想 push 算力 → 关注 FMLA/SDOT instr 占比（compute density）\n");
    printf("- 想 push 带宽 → 关注 cache 命中（数据布局 + prefetch）\n");
    printf("- 想 push 单 thread → 关注 IPC + branch（指令调度 + 循环展开）\n");

    return 0;
}
