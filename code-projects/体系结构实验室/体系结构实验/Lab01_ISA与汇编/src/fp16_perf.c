/*
 * Lab01/src/fp16_perf.c — ARMv8.2 FP16 性能对比（用 .inst 绕过 GCC 9 限制）
 *
 * 飞腾 GCC 9.3.1 不支持 .arch_extension fp16 修饰符，
 * 所以 fadd/fmul/fmla 用 .inst 直接编码（4 字节机器码）。
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <arm_neon.h>
#include "bench.h"

#define N (4 * 1024 * 1024)
#define REPS 21

/* A64 指令编码（参考 ARMv8 ARM DDI0487）
 *  FADD Vd.8H, Vn.8H, Vm.8H    : 0x6E20 0C40 <<16 | (Rm<<16) | (Rn<<5) | Rd
 *  FMUL Vd.8H, Vn.8H, Vm.8H    : 0x6E20 0D40
 *  FMLA Vd.8H, Vn.8H, Vm.8H    : 0x6E20 0C00
 *  FADD Vd.4S, Vn.4S, Vm.4S    : 0x4E20 0D40
 *  FMLA Vd.4S, Vn.4S, Vm.4S    : 0x4E20 0C00
 *  FMLA Vd.2D, Vn.2D, Vm.2D    : 0x6E20 0C00
 *
 * 简化: 用通用格式, 把 Rm/Rn/Rd 填进去
 * 8H (fp16):  size=11 (bits 23:22), bit 30=1 → 0x6E2X XXXX
 * 4S (fp32):  size=00, bit 30=1 → 0x4E2X
 * 2D (fp64):  size=01, bit 30=1 → 0x6E2X (实际有更多差异)
 *
 * 下面用宏简化指令编码
 */
#define ENC_VEC3(op_high, Rd, Rn, Rm) \
    (((uint32_t)(op_high) << 16) | ((uint32_t)(Rm) << 16) | \
     ((uint32_t)(Rn) << 5)  | (uint32_t)(Rd))

/* FADD V0.8H, V0.8H, V1.8H → 0x6E218C40 (size=11, Rm=1)
 *   high bits: 0110 1110 0010 0000 1000 1100 0100 0000
 *   = 0x6E208C40 + (Rm<<16) + (Rn<<5) + Rd
 */
#define FADD_FP16(Rd, Rn, Rm) (0x6E208C40u | ((Rm) << 16) | ((Rn) << 5) | (Rd))
#define FMUL_FP16(Rd, Rn, Rm) (0x6E208D40u | ((Rm) << 16) | ((Rn) << 5) | (Rd))
#define FMLA_FP16(Rd, Rn, Rm) (0x6E208C00u | ((Rm) << 16) | ((Rn) << 5) | (Rd))
#define FMLA_FP32(Rd, Rn, Rm) (0x4E20 0C00u | ((Rm) << 16) | ((Rn) << 5) | (Rd))
#define FMLA_FP64(Rd, Rn, Rm) (0x6E20 0C00u | ((Rm) << 16) | ((Rn) << 5) | (Rd))

static inline void fmla_fp16x8(float16x8_t *acc, const float16x8_t *a, const float16x8_t *b) {
    __asm__ __volatile__(
        ".inst 0x%[inst0] + 0\n"  /* 占位，下面用 .word 替代 */
        :: [inst0] "i"(0u)
    );
    /* 上面 GCC 不支持，改用直接的 .word + 编码 */
}

/* 实际可行方案：用 asm volatile + .word */
#define EMIT_INST(INST) \
    __asm__ __volatile__(".inst " #INST "\n" ::: "memory")

/* 8-wide fp16 fmla 用 .inst 写法 */
static void fmla_fp16_loop(const float16x8_t *a, const float16x8_t *b, float16x8_t *c, int n) {
    for (int i = 0; i < n; i++) {
        /* v0 = a[i], v1 = b[i], v2 = c[i] */
        __asm__ __volatile__(
            "ldr q0, [%[a], #%[off], lsl #4]\n"
            "ldr q1, [%[b], #%[off], lsl #4]\n"
            "ldr q2, [%[c], #%[off], lsl #4]\n"
            ".inst 0x6E218C00 + (0 << 16) + (2 << 5) + 2\n"  /* fmla v2.8h, v2.8h, v0.8h */
            ".inst 0x6E118C00 + (1 << 16) + (2 << 5) + 2\n"  /* fmla v2.8h, v2.8h, v1.8h */
            "str q2, [%[c], #%[off], lsl #4]\n"
            :: [a] "r"(a), [b] "r"(b), [c] "r"(c), [off] "r"(i)
            : "v0", "v1", "v2", "memory"
        );
    }
}

/* 由于上面指令编码复杂，直接退化到用 intrinsics 但加 fp16 编译参数 */
/* 这个文件应当用 -march=armv8.2-a+fp16 编译 */

#if defined(__ARM_FEATURE_FP16_SCALAR_ARITHMETIC) || defined(__ARM_FEATURE_FP16_VECTOR_ARITHMETIC) || defined(__ARM_FEATURE_FP16)

static float16x8_t *a16, *b16, *c16;
static float32x4_t *a32, *b32, *c32;
static float64x2_t *a64, *b64, *c64;

static void fmla_fp16(void) {
    for (int i = 0; i < N/8; i++)
        c16[i] = vfmaq_f16(c16[i], a16[i], b16[i]);
}
static void fmla_fp32(void) {
    for (int i = 0; i < N/4; i++)
        c32[i] = vfmaq_f32(c32[i], a32[i], b32[i]);
}
static void fmla_fp64(void) {
    for (int i = 0; i < N/2; i++)
        c64[i] = vfmaq_f64(c64[i], a64[i], b64[i]);
}

static double time_it(void (*fn)(void)) {
    uint64_t ts[REPS];
    for (int r = 0; r < REPS; r++) {
        uint64_t t0 = now_ns();
        fn();
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
    pin_to_cpu(0);
    posix_memalign((void**)&a16, 64, (N/8) * sizeof(float16x8_t));
    posix_memalign((void**)&b16, 64, (N/8) * sizeof(float16x8_t));
    posix_memalign((void**)&c16, 64, (N/8) * sizeof(float16x8_t));
    posix_memalign((void**)&a32, 64, (N/4) * sizeof(float32x4_t));
    posix_memalign((void**)&b32, 64, (N/4) * sizeof(float32x4_t));
    posix_memalign((void**)&c32, 64, (N/4) * sizeof(float32x4_t));
    posix_memalign((void**)&a64, 64, (N/2) * sizeof(float64x2_t));
    posix_memalign((void**)&b64, 64, (N/2) * sizeof(float64x2_t));
    posix_memalign((void**)&c64, 64, (N/2) * sizeof(float64x2_t));

    for (int i = 0; i < N/8; i++) { a16[i] = vdupq_n_f16(1.5f16); b16[i] = vdupq_n_f16(2.0f16); c16[i] = vdupq_n_f16(0); }
    for (int i = 0; i < N/4; i++) { a32[i] = vdupq_n_f32(1.5f);   b32[i] = vdupq_n_f32(2.0f);   c32[i] = vdupq_n_f32(0); }
    for (int i = 0; i < N/2; i++) { a64[i] = vdupq_n_f64(1.5);    b64[i] = vdupq_n_f64(2.0);    c64[i] = vdupq_n_f64(0); }

    printf("== Lab01.5: FP16 vs FP32 vs FP64 SIMD (N=%d) ==\n\n", N);

    fmla_fp16(); fmla_fp32(); fmla_fp64();  /* warmup */

    double t16 = time_it(fmla_fp16);
    double t32 = time_it(fmla_fp32);
    double t64 = time_it(fmla_fp64);

    double flops = 2.0 * N;  /* 1 mul + 1 add per element */
    printf("%-15s %12s %12s %12s\n", "type", "T_med(us)", "GFLOPS", "speedup");
    printf("%-15s %12s %12s %12s\n", "-------------", "----------", "------", "-------");
    printf("%-15s %12.1f %12.2f %12s\n",    "FP64 (2-wide)", t64/1000, flops/t64, "1.00x");
    printf("%-15s %12.1f %12.2f %12.2fx\n", "FP32 (4-wide)", t32/1000, flops/t32, t64/t32);
    printf("%-15s %12.1f %12.2f %12.2fx\n", "FP16 (8-wide)", t16/1000, flops/t16, t64/t16);

    printf("\n  == 解读 ==\n");
    printf("  * 理论: fp16 比 fp32 快 2x，比 fp64 快 4x\n");
    printf("  * 实测: 看 SIMD 单元是否充分并行\n");
    printf("  * 注意: fp16 仅 11 位尾数（~3-4 位十进制），累积精度差\n");

    free(a16); free(b16); free(c16);
    free(a32); free(b32); free(c32);
    free(a64); free(b64); free(c64);
    return 0;
}

#else /* !__ARM_FEATURE_FP16 */
int main(void) {
    printf("[fp16_perf] 跳过：编译时未启用 __ARM_FEATURE_FP16\n");
    printf("请用 -march=armv8.2-a+simd+crypto+fp16 编译\n");
    printf("或用 kpgcc -mcpu=ftc86x\n");
    return 0;
}
#endif
