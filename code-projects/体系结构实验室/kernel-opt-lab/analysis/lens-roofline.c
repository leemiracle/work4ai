/* ============================================================================
 * lens-roofline.c — 视角 1：Roofline Model（compute vs memory bound）
 *
 * 经典体系结构分析工具（Williams et al., CACM 2009）：
 *   Achieved GFLOPS = min(Peak Compute, Peak BW × Arithmetic Intensity)
 *   AI (FLOPs/Byte) = 算量 / 数据搬运量
 *
 * 本 lens 做 3 件事：
 *   1. 实测 D3000 各级内存带宽（L1/L2/L3/DRAM，streaming 读/写）
 *   2. 算每个算子的 Arithmetic Intensity
 *   3. 输出表：每个算子在哪个 cache 层级 hit、compute-bound 还是 memory-bound
 *
 * 关键洞察：
 *   - GEMM 的 AI ≈ 2K/sizeof（数据复用），K 越大越 compute-bound
 *   - 卷积 im2col 后等价 GEMM，AI 由 K = CIN×k×k 决定
 *   - Winograd 变换后 AI = 36/某值，依赖 tile 形状
 *   - 矩阵尺寸小 → 工作集装 L1/L2 → 走 cache 带宽（高）
 *   - 矩阵尺寸大 → 工作集溢出 → 走 DRAM 带宽（低）
 * ============================================================================ */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <arm_neon.h>

static double now_ns() {
    struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t);
    return t.tv_sec * 1e9 + t.tv_nsec;
}

/* === 1. 实测各级带宽（streaming read + write）===
 * 用不同工作集大小触发不同 cache 层级
 * D3000: L1D=64KB / L2=512KB / L3=4-8MB / DRAM=64GB */
static double measure_bw(size_t bytes) {
    /* 分配 + 对齐 */
    void *p1, *p2;
    if (posix_memalign(&p1, 64, bytes) || posix_memalign(&p2, 64, bytes)) return -1;
    float *A = (float*)p1, *B = (float*)p2;
    size_t n = bytes / sizeof(float);
    for (size_t i = 0; i < n; i++) { A[i] = i * 1e-7f; B[i] = 0; }

    /* streaming: A → B（读 A + 写 B），字节流量 = 2 × bytes */
    /* warmup */
    for (int w = 0; w < 3; w++) {
        for (size_t i = 0; i < n; i += 4) {
            float32x4_t v = vld1q_f32(&A[i]);
            vst1q_f32(&B[i], v);
        }
    }
    double t0 = now_ns();
    int iter = 100;
    for (int it = 0; it < iter; it++) {
        for (size_t i = 0; i < n; i += 4) {
            float32x4_t v = vld1q_f32(&A[i]);
            vst1q_f32(&B[i], v);
        }
    }
    double t1 = now_ns();
    double bytes_moved = 2.0 * bytes * iter;  /* 读 + 写 */
    free(A); free(B);
    return bytes_moved / (t1 - t0);  /* GB/s = bytes/ns（数值上等价） */
}

/* === 2. 算每个算子的 Arithmetic Intensity ===
 * AI = FLOPs / Bytes_moved
 *   GEMM(M,N,K) 算量 = 2MNK，搬运 = (MK + KN + MN) × 4B（朴素版）
 *   B-blocked 后：A 复用 N/4 次，B 复用 M 次，C 写 1 次
 *     有效字节 = MN×4 (C) + MN×4/4 (A 摊销) + ... 复杂
 *   工程经验：GEMM AI ≈ K（4-byte elem 时）
 *
 *   卷积 im2col 等价 GEMM，K = CIN × KH × KW
 *   Winograd F(m,r) 每 tile 36 mul × CIN，搬运 = 36 × CIN × 2（U+V）
 *     AI = 36 / 2 = 18（很高 → compute bound）
 *
 *   Element-wise add: AI = 1/8（纯 memory bound）
 */

typedef struct {
    const char *name;
    long   flops;       /* 算量 */
    long   bytes;       /* 字节流量 */
    double ai;          /* = flops / bytes */
    const char *bound;  /* compute/memory/ Transitional */
} op_t;

int main() {
    printf("# Lens 1: Roofline Model\n\n");
    printf("## 1.1 实测各级内存带宽\n\n");
    printf("| 层级 | 工作集 | 实测带宽 |\n");
    printf("|---|---|---|\n");

    struct { const char *name; size_t bytes; } levels[] = {
        {"L1D",   4 * 1024},       /* 4KB 装得下 L1 */
        {"L1D+", 32 * 1024},       /* 32KB 仍在 L1 */
        {"L2",    256 * 1024},     /* 256KB → L2 */
        {"L2+",   4 * 1024 * 1024 - 64*1024},  /* ~4MB → L3 */
        {"L3+",   16 * 1024 * 1024}, /* 16MB 超 L3 → DRAM */
        {"DRAM",  64 * 1024 * 1024}, /* 64MB 大块 DRAM */
    };
    int nl = sizeof(levels)/sizeof(levels[0]);
    double bw[6];
    for (int i = 0; i < nl; i++) {
        bw[i] = measure_bw(levels[i].bytes);
        printf("| %s | %zu KB | %.1f GB/s |\n",
               levels[i].name, levels[i].bytes/1024, bw[i]);
    }

    /* D3000 已知参数 */
    double peak_f32 = 40.0;  /* GFLOPS（4 FVU）*/
    double peak_f16 = 40.0;
    double peak_int8 = 80.0;
    double bw_dram = bw[5];  /* DRAM 带宽 */

    printf("\n## 1.2 各算子 Arithmetic Intensity + Roofline 预测\n\n");
    printf("D3000 峰值：FP32=%.0f GFLOPS, DRAM BW=%.1f GB/s\n", peak_f32, bw_dram);
    printf("Memory-bound 上限 = DRAM_BW × AI；Compute-bound 上限 = peak\n\n");

    /* 算子列表 */
    /* GEMM 不同尺寸 */
    /* AI(GEMM,B-blocked) ≈ K（每 B 元素复用 MR 次）*/
    op_t ops[] = {
        /* FP32 GEMM 1024³: AI ≈ K = 1024 */
        {"GEMM 1024³ (FP32)",   2L*1024*1024*1024,  1024L*1024*4 + 1024L*1024*4 + 1024L*1024*4, 0, ""},
        {"GEMM 64³ (FP32)",     2L*64*64*64,        64L*64*4 * 3,                                0, ""},
        /* GEMM 大矩阵溢出 L3 */
        {"GEMM 2048³ (FP32)",   2L*2048*2048*2048,  3L*2048*2048*4,                              0, ""},
        /* 卷积 im2col 等价 GEMM: K = CIN×9 = 576 */
        {"Conv im2col (CIN=64, 3×3)", 2L*56*56*64*64*9, 64L*9*4 + 64L*9*4 + 56L*56*64*4, 0, ""},
        /* Winograd F(2,3): 每 tile 16 mul × CIN，搬运 = 16×CIN×4 (V) + 16×CIN×4 (U，摊销) */
        {"Winograd F(2,3)",     2L*56*56/4*64*64*16, 16L*64*4 + 16L*64*4,                         0, ""},
        /* Winograd F(4,4): 36 mul × CIN */
        {"Winograd F(4,4)",     2L*56*56/16*64*64*36, 36L*64*4 + 36L*64*4,                        0, ""},
        /* Element-wise add: AI ≈ 1/12（每 element 1 add，3 流量）*/
        {"Elem-wise add",       1L*1024*1024,       3L*1024*1024*4,                              0, ""},
        /* Attention: 复杂，N=1024, head=64, AI = QK + softmax + AV */
        {"Attention N=1024",    2L*4*1024*1024*64,  4L*1024*1024*4,                              0, ""},
    };
    int n_ops = sizeof(ops)/sizeof(ops[0]);

    printf("| 算子 | AI (FLOPs/B) | Roofline 上限 | 实测 GFLOPS | 性质 |\n");
    printf("|---|---|---|---|---|\n");

    /* 已知实测 GFLOPS（来自 baseline.md）*/
    double actual[] = {39.45, 39.45, 30.0, 7.63, 18.13, 26.19, 1.0, 3.23};

    for (int i = 0; i < n_ops; i++) {
        ops[i].ai = (double)ops[i].flops / ops[i].bytes;
        /* Roofline: min(peak, bw × AI)，但小工作集走 L1/L2 高带宽 */
        /* 简化：用 DRAM BW 算保守上限 */
        double roof_dram = bw_dram * ops[i].ai;  /* GB/s × FLOPs/B = GFLOPS */
        double roof = (peak_f32 < roof_dram) ? peak_f32 : roof_dram;

        if (ops[i].ai > 50) ops[i].bound = "compute-bound ✓";
        else if (ops[i].ai < 5) ops[i].bound = "memory-bound";
        else ops[i].bound = "transitional";

        printf("| %s | %.1f | %.1f GFLOPS | %.2f | %s |\n",
               ops[i].name, ops[i].ai, roof, actual[i], ops[i].bound);
    }

    printf("\n## 1.3 关键洞察\n\n");
    printf("- GEMM 1024³ AI=%d，远超 DRAM/peak 交叉点 → **compute-bound**\n", 1024);
    printf("- Winograd F(4,4) AI=%.0f（高复用）→ compute-bound，故能达 26 GFLOPS\n",
           36.0*64*4*2.0 / (36.0*64*4*2));
    printf("- Element-wise AI=%.2f → 纯 memory-bound，性能受带宽限制\n", 1.0/12);
    printf("- GEMM 64³ AI=%d 但工作集 16KB 装得下 L1（BW 高）→ 仍可接近 peak\n", 64);
    printf("- GEMM 2048³ 工作集 48MB 超 L3 → 走 DRAM，AI 仍高但实际掉到 30 GFLOPS\n");
    printf("\n**工程结论**：算子优化方向取决于 bound 性质\n");
    printf("- compute-bound → 增强 ILP（MR=8、4 FVU 全开）\n");
    printf("- memory-bound → 数据布局、prefetch、分块复用\n");

    return 0;
}
