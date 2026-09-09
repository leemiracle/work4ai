/*
 * Lab01/src/dot_product.c — ARMv8.4 UDOT 探测
 *
 * 飞腾 GCC 9.3.1 不支持 +dotprod 修饰符，无法直接 emit udot 指令。
 * 这个程序做:
 *   1. HWCAP 确认 ASIMDDP
 *   2. 用纯 NEON（v8.0）实现等效的 4-way int8 点积
 *   3. 给出在新 GCC 上用 vdotq_s32 intrinsic 的代码模板
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <sys/auxv.h>
#include <arm_neon.h>
#include "bench.h"

#ifndef HWCAP_ASIMDDP
#define HWCAP_ASIMDDP (1 << 20)
#endif

#define N (4 * 1024 * 1024)
#define REPS 21

static int8_t A[N] __attribute__((aligned(64)));
static int8_t B[N] __attribute__((aligned(64)));

/* 标量 int8 点积 */
static int64_t dot_scalar(void) {
    int64_t s = 0;
    for (int i = 0; i < N; i++) s += (int64_t)A[i] * B[i];
    return s;
}

/* 用 v8.0 NEON 实现 int8 × int8 → int32 4 路点积
 * 流程: 4 个 int8 widen 到 int16 → 乘 → widen 到 int32 → 加
 * 注意: 每 N/16 次外循环累加 int32，可能溢出！
 * 实测中 N=4M 时会溢出（学习点），实际应用要 periodic dump 到 int64。
 */
static int64_t dot_neon_v80(void) {
    int64_t acc64 = 0;
    /* 每 1024 个 int8 一组，组内 int32 累加再 widen 到 int64 */
    for (int outer = 0; outer < N; outer += 1024) {
        int32x4_t acc = vdupq_n_s32(0);
        int end = outer + 1024;
        if (end > N) end = N;
        for (int i = outer; i < end; i += 16) {
            int8x16_t a = vld1q_s8(&A[i]);
            int8x16_t b = vld1q_s8(&B[i]);
            int16x8_t a_lo = vmovl_s8(vget_low_s8(a));
            int16x8_t b_lo = vmovl_s8(vget_low_s8(b));
            int16x8_t a_hi = vmovl_s8(vget_high_s8(a));
            int16x8_t b_hi = vmovl_s8(vget_high_s8(b));
            int16x8_t p_lo = vmulq_s16(a_lo, b_lo);
            int16x8_t p_hi = vmulq_s16(a_hi, b_hi);
            int32x4_t p0 = vmovl_s16(vget_low_s16(p_lo));
            int32x4_t p1 = vmovl_s16(vget_high_s16(p_lo));
            int32x4_t p2 = vmovl_s16(vget_low_s16(p_hi));
            int32x4_t p3 = vmovl_s16(vget_high_s16(p_hi));
            acc = vaddq_s32(acc, vaddq_s32(vaddq_s32(p0, p1), vaddq_s32(p2, p3)));
        }
        /* widen 4 个 int32 到 int64 */
        acc64 += (int64_t)vaddvq_s32(acc);
    }
    return acc64;
}

#if defined(__ARM_FEATURE_DOTPROD)
/* 如果编译时启用了 +dotprod，用原生 intrinsic */
static int64_t dot_udot_native(void) {
    int32x4_t acc = vdupq_n_s32(0);
    for (int i = 0; i < N; i += 16) {
        int8x16_t a = vld1q_s8(&A[i]);
        int8x16_t b = vld1q_s8(&B[i]);
        acc = vdotq_s32(acc, a, b);  /* 一条指令完成上面所有工作 */
    }
    return (int64_t)vaddvq_s32(acc);
}
#define HAVE_UDOT_NATIVE 1
#else
#define HAVE_UDOT_NATIVE 0
/* stub：未启用 dotprod 时返回 0 */
static int64_t dot_udot_native(void) { return 0; }
#endif

static double time_it(int64_t (*fn)(void)) {
    uint64_t ts[REPS];
    for (int r = 0; r < REPS; r++) {
        uint64_t t0 = now_ns();
        int64_t s = fn();
        sink((uint64_t)s);
        uint64_t t1 = now_ns();
        ts[r] = t1 - t0;
    }
    for (int i = 1; i < REPS; i++) {
        uint64_t k = ts[i]; int j = i;
        while (j > 0 && ts[j-1] > k) { ts[j] = ts[j-1]; j--; }
        ts[j] = k;
    }
    return (double)ts[REPS/2];
}

int main(void) {
    unsigned long hw = getauxval(AT_HWCAP);
    pin_to_cpu(0);

    for (int i = 0; i < N; i++) {
        A[i] = (int8_t)(i & 0x7F);
        B[i] = (int8_t)((i * 7) & 0x7F);
    }

    printf("== Lab01.6: UDOT 探测 (v8.4 ASIMDDP) ==\n\n");
    printf("  HWCAP.ASIMDDP = %s\n", (hw & HWCAP_ASIMDDP) ? "✓ 支持" : "✗ 不支持");
    printf("  编译时 __ARM_FEATURE_DOTPROD = %s\n\n", HAVE_UDOT_NATIVE ? "✓" : "✗ (需 GCC 10+ 或 +dotprod)");

    int64_t s1 = dot_scalar();
    int64_t s2 = dot_neon_v80();
    printf("  correctness: scalar=%lld  neon_v80=%lld  %s\n\n",
           (long long)s1, (long long)s2,
           (s1 == s2) ? "✓" : "✗ MISMATCH");

    double t_s = time_it(dot_scalar);
    double t_n = time_it(dot_neon_v80);

    printf("%-30s %12s %12s\n", "method", "T_med(us)", "GMACS");
    printf("%-30s %12s %12s\n", "------------------------------", "----------", "------");
    /* GMACS = N MAC / t_s / 1e9，t 是 ns 时 = N / t_ns */
    printf("%-30s %12.1f %12.2f\n", "int8 scalar", t_s/1000, (double)N/(t_s));
    printf("%-30s %12.1f %12.2f\n", "int8 NEON v8.0 (widen+mul)", t_n/1000, (double)N/(t_n));

    if (HAVE_UDOT_NATIVE) {
        double t_u = time_it(dot_udot_native);
        printf("%-30s %12.1f %12.2f\n", "int8 UDOT (v8.4 单指令)", t_u/1000, (double)N/(t_u));
        printf("\n  * UDOT vs NEON v8.0: %.2fx 加速\n", t_n/t_u);
    } else {
        printf("\n  * 预期: v8.4 UDOT 比 v8.0 NEON 快 ~3-4x (1 条指令 vs 6+ 条)\n");
    }

    printf("\n  == 解读 ==\n");
    printf("  * HWCAP 报告 ASIMDDP = %s\n", (hw & HWCAP_ASIMDDP) ? "硬件支持" : "硬件不支持");
    printf("  * 实测 UDOT intrinsic 需要重编译:\n");
    printf("      gcc -march=armv8.2-a+simd+crypto+fp16+dotprod ...\n");
    printf("      或 kpgcc -mcpu=ftc86x （kpgcc 12+ 支持）\n");
    printf("  * 应用: 量化 CNN (TFLite/ONNX Runtime int8 推理)\n");
    return 0;
}
