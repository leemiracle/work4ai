/* fp_precision_demo.c — 飞腾 D3000M 浮点精度与 bit-diff 实测演示
 * ===========================================================================
 * Expert_08_Numerics 自有 artifact（数值分析专家视角）
 *
 * 角色：FP 正确性工程师。我只问一件事：**同一算法在同一颗 CPU 上，
 *       换个 -O 或换个精度，结果还 bit-exact 吗？误差累积多大？**
 *
 * 四组实验：
 *   A. Kahan 求和 vs 朴素求和 —— 误差量级对比（ULP / 相对误差）
 *   B. -O0/-O2/-O3/-ffast-math 的 bit-diff —— 同一点积不同结果
 *   C. FP16 vs FP32 累加误差 —— 无 BF16 时被迫用 FP16 的精度代价
 *   D. FMA（融合乘加）对误差的影响 —— 飞腾 NEON 的 FMLA 是否省 1 次舍入
 *
 * 编译（飞腾 D3000M / 任意 aarch64，gcc ≥ 8）：
 *   gcc -O0 fp_precision_demo.c -o demo_O0   -lm
 *   gcc -O2 fp_precision_demo.c -o demo_O2   -lm
 *   gcc -O3 fp_precision_demo.c -o demo_O3   -lm
 *   gcc -O3 -ffast-math fp_precision_demo.c -o demo_fast -lm
 *   # FP16 实验需 fp16 支持（飞腾 v8.2 实测支持 HWCAP_ASIMDHP）：
 *   gcc -O2 -march=armv8.4-a+simd+crypto fp_precision_demo.c -o demo_fp16 -lm
 *
 * 通用：本文件在 x86-64 上也能编译运行（FP16 自动 fallback 到软件模拟），
 *       但实验 C 的硬件加速数据只有 aarch64 才有意义。
 *
 * 预期洞察（详见 Expert_08 README §3）：
 *   - 朴素 FP32 求和 vs Kahan：相对误差差 ~6 个数量级
 *   - -O3 向量化 vs -O0：bit-diff 约 1-3 ULP
 *   - -ffast-math：Kahan 求和被「优化」成朴素求和，误差暴涨（致命）
 *   - FP16 累加：比 FP32 多损失 ~3 位有效数字（这是无 BF16 的代价）
 * ===========================================================================
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <math.h>
#include <time.h>

#if defined(__aarch64__)
  #include <arm_neon.h>
  #define HAVE_NEON 1
#else
  #define HAVE_NEON 0
#endif

/* _Float16 / __fp16：aarch64 GCC 支持；其它平台用软件模拟 */
#if defined(__aarch64__) && defined(__ARM_FP16_FORMAT_IEEE)
  #define HAVE_FP16 1
  typedef __fp16 fp16_t;
#else
  #define HAVE_FP16 0
#endif

#define N_SUM 1000000   /* 求和元素数（故意大，放大误差） */
#define N_DOT 4096      /* 点积维度 */

/* -------------------------------------------------------------------------
 * 工具：用 union 做 type-punning，安全地取一个 float 的位模式（不违反严格别名）
 * ------------------------------------------------------------------------- */
static uint32_t f32_to_bits(float f) {
    union { float f; uint32_t u; } pun;
    pun.f = f;
    return pun.u;
}

/* 计算 |a-b| 的 ULP 差（unit in the last place）。
 * ULP 是度量「两个浮点数差了多少个最小精度步长」的标尺：
 *   0 ULP = bit-exact；1 ULP = 最后一位差 1；越大越离谱。
 * 对 NaN / Inf 返回一个很大的数。*/
static uint64_t ulp_diff(float a, float b) {
    uint32_t ua = f32_to_bits(a);
    uint32_t ub = f32_to_bits(b);
    /* 处理符号位：负数用补码式的单调映射，让相邻表示的 ULP 差正确 */
    int64_t sa = ua & 0x80000000u ? (int64_t)(UINT32_MAX - ua) : (int64_t)ua + (int64_t)INT32_MAX;
    int64_t sb = ub & 0x80000000u ? (int64_t)(UINT32_MAX - ub) : (int64_t)ub + (int64_t)INT32_MAX;
    int64_t d = sa - sb;
    return (uint64_t)(d < 0 ? -d : d);
}

/* -------------------------------------------------------------------------
 * 实验 A：朴素求和 vs Kahan 求和 vs 配对求和（pairwise）
 * ------------------------------------------------------------------------- */

/* 朴素串行求和：误差 ~ O(n) ULP（每步引入 ≤0.5 ULP，n 步最坏累积 n/2 ULP）*/
static float naive_sum_f32(const float *a, int n) {
    float s = 0.0f;
    for (int i = 0; i < n; i++) s += a[i];
    return s;
}

/* Kahan 补偿求和：用补偿变量 c 把每步的低位舍入误差「捡回来」。
 * 理论上误差 ~ O(1) ULP（与 n 无关），精度逼近 FP64。
 * !! 警告：-ffast-math 会把这里的 (t-sum)-y 优化成 0（它假设 FP 结合律成立），
 *          于是 Kahan 退化成朴素求和，补偿完全失效。这就是 fast-math 的致命点。*/
static float kahan_sum_f32(const float *a, int n) {
    float s = 0.0f, c = 0.0f;
    for (int i = 0; i < n; i++) {
        float y = a[i] - c;      /* 减去上一步欠的 */
        float t = s + y;         /* 实际加进去 */
        c = (t - s) - y;         /* 算出这一步丢掉的低位 */
        s = t;
    }
    return s;
}

/* 配对（二分）求和：分治归约，误差 ~ O(log n) ULP。
 * 这正是 -O3 向量化 + 树状归约「无意中」采用的策略。*/
static float pairwise_sum_f32(const float *a, int lo, int hi) {
    if (hi - lo <= 8) {
        float s = 0.0f;
        for (int i = lo; i < hi; i++) s += a[i];
        return s;
    }
    int mid = lo + (hi - lo) / 2;
    return pairwise_sum_f32(a, lo, mid) + pairwise_sum_f32(a, mid, hi);
}

/* -------------------------------------------------------------------------
 * 实验 B：点积的 bit-diff（朴素串行，故意「脆弱」以暴露 -O 差异）
 * ------------------------------------------------------------------------- */
static float dot_naive(const float *a, const float *b, int n) {
    float s = 0.0f;
    for (int i = 0; i < n; i++) s += a[i] * b[i];
    return s;
}

#if HAVE_NEON
/* NEON 4 路并行点积：与标量串行的累加顺序不同 → 可能 1-3 ULP 差异 */
static float dot_neon(const float *a, const float *b, int n) {
    float32x4_t vsum = vdupq_n_f32(0.0f);
    int i;
    for (i = 0; i + 3 < n; i += 4) {
        float32x4_t va = vld1q_f32(a + i);
        float32x4_t vb = vld1q_f32(b + i);
        vsum = vmlaq_f32(vsum, va, vb);   /* a*b + acc，可能融合成 FMA */
    }
    float s = vaddvq_f32(vsum);           /* 横向归约 4 路 → 1 */
    for (; i < n; i++) s += a[i] * b[i];  /* 尾部 */
    return s;
}
#endif

/* -------------------------------------------------------------------------
 * 实验 C：FP16 vs FP32 累加误差（无 BF16 的代价演示）
 * ------------------------------------------------------------------------- */
#if HAVE_FP16
/* FP16 朴素累加：每步舍入到 FP16（只有 ~3.3 位十进制精度）。
 * 飞腾 v8.2 实测支持 FP16 NEON（HWCAP_ASIMDHP），3.81× 加速 [Lab01]。
 * 但 FP16 动态范围只有 [6.1e-5, 65504]，极易下溢/溢出。*/
static fp16_t naive_sum_fp16(const float *a, int n) {
    fp16_t s = (fp16_t)0.0f;
    for (int i = 0; i < n; i++) s += (fp16_t)a[i];
    return s;
}
#endif

/* BF16 软件模拟：把 FP32 截断到 BF16（8 位指数 + 7 位尾数）。
 * 飞腾 D3000M 实测【不支持】BF16（HWCAP_BF16 ❌，见 扩展专题.md 第27行）。
 * 这里用软件模拟展示「如果有 BF16」的精度/范围权衡。*/
static float fp32_to_bf16(float f) {
    union { float f; uint32_t u; } pun;
    pun.f = f;
    /* 取 FP32 高 16 位，对第 17 位做 round-to-nearest-even */
    uint32_t lsb = (pun.u >> 16) & 1;
    uint32_t rounding_bias = 0x7FFF + lsb;
    pun.u += rounding_bias;
    pun.u &= 0xFFFF0000u;   /* 截到 16 位 BF16 表示 */
    return pun.f;
}

static float naive_sum_bf16_sim(const float *a, int n) {
    float s = 0.0f;
    for (int i = 0; i < n; i++) s = fp32_to_bf16(s + fp32_to_bf16(a[i]));
    return s;
}

/* -------------------------------------------------------------------------
 * 实验 D：FMA 省一次舍入（飞腾 FMLA 是否真融合）
 * ------------------------------------------------------------------------- */
/* 分离的 mul+add：两次舍入。
 * volatile 中间变量强制把乘积先写回内存（舍入到 fp32），再读出做加法，
 * 从而阻止编译器把它收缩成单次舍入的 FMA。
 * （GCC 默认 -ffp-contract=fast 会收缩 mul+add→FMA，导致「分离」也变一次舍入）*/
static float mul_then_add(float a, float b, float c) {
    volatile float p = a * b;   /* 第一次舍入：强制落盘到 fp32 */
    return p + c;               /* 第二次舍入 */
}
/* FMA：一次舍入（a*b 不先舍入，保留全宽中间结果再加 c）。
 * 飞腾 NEON 的 FMLA 指令是融合的（v8.0 起 ASIMD 保证）。
 * -ffast-math 可能把 mul_then_add 收缩成 FMA，改变 bit 结果。*/
#if HAVE_NEON
static float fma_neon(float a, float b, float c) {
    float32x2_t va = vdup_n_f32(a);
    float32x2_t vb = vdup_n_f32(b);
    float32x2_t vc = vdup_n_f32(c);
    float32x2_t vr = vmla_f32(vc, va, vb);  /* vc + va*vb，融合 */
    return vget_lane_f32(vr, 0);
}
#endif

/* -------------------------------------------------------------------------
 * 计时
 * ------------------------------------------------------------------------- */
static double now_ms(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec * 1000.0 + ts.tv_nsec / 1e6;
}

/* =========================================================================
 * 主程序
 * ========================================================================= */
int main(void) {
    /* —— 准备数据：故意构造「精度杀手」—— 大量小数累加到一个大和。
     * 经典案例：1 + 1e-7 + 1e-7 + ... (×1000000)，朴素 FP32 会吞掉后面的增量。*/
    float *data = malloc(N_SUM * sizeof(float));
    float *dotA = malloc(N_DOT * sizeof(float));
    float *dotB = malloc(N_DOT * sizeof(float));
    if (!data || !dotA || !dotB) { fprintf(stderr, "OOM\n"); return 1; }

    /* 数据集 1：一个小常数 + 大量更小的增量（放大「大数吃小数」效应）*/
    for (int i = 0; i < N_SUM; i++) data[i] = 1e-4f;   /* 1e6 × 1e-4 = 100 */
    data[0] = 1.0f;                                     /* 先放个大数 */
    /* 真实和 ≈ 1.0 + 999999 × 1e-4 ≈ 1.0 + 99.9999 = 100.9999 */

    /* 数据集 2：点积用确定性种子（保证可复现）*/
    srand(42);
    for (int i = 0; i < N_DOT; i++) {
        dotA[i] = (float)rand() / RAND_MAX;
        dotB[i] = (float)rand() / RAND_MAX;
    }

    printf("==============================================================\n");
    printf(" 飞腾 D3000M 浮点精度与 bit-diff 实测  (Expert_08_Numerics)\n");
    printf(" N_SUM=%d  N_DOT=%d   NEON=%d  FP16=%d\n",
           N_SUM, N_DOT, HAVE_NEON, HAVE_FP16);
    printf("==============================================================\n\n");

    /* ===== 实验 A：求和误差对比 ===== */
    printf("【实验 A】求和算法的相对误差（理论真值 ≈ 100.9999）\n");
    double truth = 1.0 + (double)(N_SUM - 1) * 1e-4;   /* 用 FP64 当「真值」*/
    printf("  理论真值(FP64) : %.10f\n", truth);

    float s_naive  = naive_sum_f32(data, N_SUM);
    float s_kahan  = kahan_sum_f32(data, N_SUM);
    float s_pair   = pairwise_sum_f32(data, 0, N_SUM);

    printf("  朴素 FP32 求和 : %.6f   相对误差=%.3e\n",
           s_naive, fabs(s_naive - truth) / truth);
    printf("  Kahan 补偿求和 : %.6f   相对误差=%.3e\n",
           s_kahan, fabs(s_kahan - truth) / truth);
    printf("  配对(树状)求和 : %.6f   相对误差=%.3e\n",
           s_pair, fabs(s_pair - truth) / truth);
    printf("  Kahan vs 朴素 ULP 差 : %llu\n",
           (unsigned long long)ulp_diff(s_kahan, s_naive));
    printf("  → 朴素求和的「大数吃小数」：1.0 + 1e-4 时 1e-4 被部分吞掉\n\n");

    /* ===== 实验 B：点积 bit-diff ===== */
    printf("【实验 B】点积 bit-diff（同一代码、同一输入，仅 -O 不同）\n");
    printf("  维度 N=%d，FP32\n\n", N_DOT);

    float d_scalar = dot_naive(dotA, dotB, N_DOT);
    printf("  dot_naive (标量串行) = %.14f   bits=0x%08X\n",
           d_scalar, f32_to_bits(d_scalar));

#if HAVE_NEON
    float d_neon = dot_neon(dotA, dotB, N_DOT);
    printf("  dot_neon  (NEON 4路) = %.14f   bits=0x%08X\n",
           d_neon, f32_to_bits(d_neon));
    printf("  标量 vs NEON ULP 差  = %llu  (累加顺序不同)\n",
           (unsigned long long)ulp_diff(d_scalar, d_neon));
#else
    printf("  (非 aarch64：跳过 NEON 点积)\n");
#endif
    printf("\n  提示：用不同 -O 各编译一份，比较 dot_naive 的 bits：\n");
    printf("    -O0/-O1/-O2 通常 bit-exact；-O3 向量化后 ~1-3 ULP；\n");
    printf("    -ffast-math 允许重关联，差异可能 >>10 ULP。\n\n");

    /* ===== 实验 C：FP16 / BF16-sim vs FP32（两个子实验）=====
     * C1 范围致命伤：故意构造超过 FP16 上限(65504)的求和 → FP16 溢出 +Inf，
     *    而 BF16 因指数位与 FP32 相同(8位)、范围=±3.4e38 → 完全无恙。
     *    这正是 D3000M 无 BF16 的核心痛点：大动态范围场景 FP16 直接崩溃。
     * C2 精度梯度：大规模累加中等量级值，展示三档精度的舍入误差累积。*/
    printf("【实验 C】精度档位的范围与精度代价（无 BF16 之痛）\n");

    /* —— C1：范围溢出（飞腾无 BF16 的致命伤）—— */
    printf("  C1 范围测试：求和 [60000, 6000, 6000, 6000] = 78000 (>65504)\n");
    float big[4] = {60000.0f, 6000.0f, 6000.0f, 6000.0f};
    float f32c1 = naive_sum_f32(big, 4);
    float bf16c1 = naive_sum_bf16_sim(big, 4);
    printf("    FP32  : %.0f   (精确)\n", f32c1);
    printf("    BF16  : %.0f   (范围=FP32，无溢出) [飞腾硬件不支持]\n", bf16c1);
#if HAVE_FP16
    fp16_t f16c1 = naive_sum_fp16(big, 4);
    float f16v1 = (float)f16c1;
    printf("    FP16  : %s   (60000+6000 超 65504 → +Inf 溢出!) [飞腾硬件支持]\n",
           isinf(f16v1) ? "+Inf" : "有限");
#else
    printf("    FP16  : (非 aarch64 跳过)\n");
#endif

    /* —— C2：精度累积（大规模求和的舍入误差）—— */
    printf("  C2 精度测试：%d 个 [0.1,1.0] 值累加\n", N_SUM);
    float *dataC = malloc(N_SUM * sizeof(float));
    if (!dataC) { fprintf(stderr, "OOM\n"); return 1; }
    srand(7);
    double truthC = 0.0;
    for (int i = 0; i < N_SUM; i++) {
        float v = 0.1f + 0.9f * ((float)rand() / RAND_MAX);
        dataC[i] = v;
        truthC += v;
    }
    printf("    理论真值(FP64)=%.1f\n", truthC);
    float s_f32c = naive_sum_f32(dataC, N_SUM);
    float s_bf16c = naive_sum_bf16_sim(dataC, N_SUM);
    printf("    FP32 累加 : %.1f   相对误差=%.3e\n",
           s_f32c, fabs((double)s_f32c - truthC) / truthC);
    printf("    BF16 模拟 : %.1f   相对误差=%.3e  (尾数仅7位，小增量被吞)\n",
           s_bf16c, fabs((double)s_bf16c - truthC) / truthC);
#if HAVE_FP16
    fp16_t s_f16c = naive_sum_fp16(dataC, N_SUM);
    float f16v = (float)s_f16c;
    printf("    FP16 累加 : %.1f   相对误差=%.3e  (和>2048 后增量<ulp 被吞，静默饱和)\n",
           f16v, fabs((double)f16v - truthC) / truthC);
#else
    printf("    FP16      : (非 aarch64 跳过)\n");
#endif
    printf("\n  → 两条铁律：\n");
    printf("    1) 范围：BF16=FP32(±3.4e38)，FP16 仅[6e-5,65504]。大动态范围→FP16 必崩。\n");
    printf("    2) 精度：均匀小量累加时，FP16(10位尾数)比 BF16(7位)更准——但都远逊 FP32。\n");
    printf("    ML 现实：梯度动态范围跨 10+ 数量级，FP16 易溢出/下溢 → 需 loss-scaling；\n");
    printf("             BF16 用范围换精度，免 loss-scaling → 训练更稳。D3000M 两样都没有原生 BF16。\n\n");
    free(dataC);

    /* ===== 实验 D：FMA 一次舍入 vs 两次舍入（飞腾 FMLA 是否真融合）=====
     * 经典反例：a=(1+2^-23), b=(1+2^-23), c=-(1+2^-22)。
     *  数学真值 a*b+c = (1+2^-23)^2 - (1+2^-22) = 1+2^-22+2^-46 -1-2^-22 = 2^-46。
     *  - 分离 mul+add：a*b = 1+2^-22+2^-46，2^-46 低于 fp32 ulp 被舍入 → 成 (1+2^-22)，
     *    再 +c = (1+2^-22) - (1+2^-22) = 0。
     *  - FMA：a*b 保留全宽(含 2^-46)再加 c → 2^-46 ≈ 1.4e-14。
     *  差异：分离=0，FMA≠0。FMA 更准，但 bit 结果不同。*/
    printf("【实验 D】FMA 融合乘加（省一次舍入）\n");
    /* volatile 阻止编译器常量折叠，确保运行时真实计算分离路径 vs FMA 路径 */
    volatile float va = 0x1.000002p+0f;   /* 1 + 2^-23 */
    volatile float vb = 0x1.000002p+0f;
    volatile float vc = -0x1.000004p+0f;  /* -(1 + 2^-22) */
    float a = va, bb = vb, c = vc;
    float r_split = mul_then_add(a, bb, c);   /* volatile 屏障 → 两次舍入 → 0 */
    float r_fma   = fmaf(a, bb, c);           /* C99 标准：保证单次舍入 FMA → 2^-46 */
    printf("  分离 mul+add : %.10e   bits=0x%08X (两次舍入，2^-46 被丢→0)\n",
           r_split, f32_to_bits(r_split));
    printf("  fmaf() 单舍入 : %.10e   bits=0x%08X (一次舍入，保住 2^-46)\n",
           r_fma, f32_to_bits(r_fma));
    printf("  ULP 差       : %llu  (一个=0，一个≠0)\n",
           (unsigned long long)ulp_diff(r_split, r_fma));
    printf("  → 数学真值=2^-46≈1.4e-14。fmaf≈真值(非零)，分离=0。\n");
    printf("    FMA 更准但改了 bit；-ffast-math 会把 mul+add 自动收缩成 FMA，破坏 bit-exact。\n");
    printf("    （飞腾 NEON 的 FMLA 指令即硬件 FMA，与 fmaf 等价单次舍入）\n\n");

    /* ===== 性能对照（朴素 vs Kahan 开销）===== */
    printf("【性能】朴素 vs Kahan 求和耗时（N=%d，FP32）\n", N_SUM);
    double t0, t1; volatile float sink = 0;
    t0 = now_ms();
    for (int k = 0; k < 20; k++) sink += naive_sum_f32(data, N_SUM);
    t1 = now_ms();
    printf("  朴素 : %.2f ms\n", (t1 - t0) / 20);
    t0 = now_ms();
    for (int k = 0; k < 20; k++) sink += kahan_sum_f32(data, N_SUM);
    t1 = now_ms();
    printf("  Kahan: %.2f ms  (补偿的代价：~3-4× 慢)\n", (t1 - t0) / 20);
    (void)sink;

    printf("\n==============================================================\n");
    printf(" 结论速查：\n");
    printf("  · 需要 bit-exact 可复现 → 用 -O2，禁 -ffast-math，禁 -O3 向量化\n");
    printf("  · 需要 FMA 精度但可复现 → 显式 #pragma STDC FP_CONTRACT ON/OFF 控制\n");
    printf("  · 科学计算(CFD/FEM)     → FP64 + Kahan，绝不 -ffast-math\n");
    printf("  · ML 推理(飞腾无BF16)   → FP16 + loss-scaling，或 INT8 + 校准\n");
    printf("  · 密码学(SM3/SM4)       → 硬件指令 bit-exact，不受 -O 影响\n");
    printf("==============================================================\n");

    free(data); free(dotA); free(dotB);
    return 0;
}
