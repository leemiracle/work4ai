/*
 * Lab01/src/isa_features.c — 飞腾 D3000 ISA 特性实测
 *
 * 主要靠 HWCAP（内核已经做了 CPUID 探测）。
 * 对 HWCAP 已确认的特性，跑一次"业务功能"验证（用编译器支持的指令）。
 *
 * 注: GCC 9.3.1 aarch64 assembler 对 v8.3+ 的 .arch_extension 修饰符
 * 支持不全（如 'fcma', 'dotprod'）。因此 fcmla/udot 的实际执行验证
 * 在 dot_product.c / fcmla_complex.c 中用 .inst 字节码绕过 assembler。
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <sys/auxv.h>
#include <signal.h>
#include <setjmp.h>

#include <arm_neon.h>
#include <arm_acle.h>

/* HWCAP 标志位（手写，避免 glibc 版本问题） */
#ifndef HWCAP_ASIMDHP
#define HWCAP_ASIMDHP  (1 << 10)
#endif
#ifndef HWCAP_FPHP
#define HWCAP_FPHP     (1 << 9)
#endif
#ifndef HWCAP_ATOMICS
#define HWCAP_ATOMICS  (1 << 8)
#endif
#ifndef HWCAP_ASIMDRDM
#define HWCAP_ASIMDRDM (1 << 12)
#endif
#ifndef HWCAP_ASIMDDP
#define HWCAP_ASIMDDP  (1 << 20)
#endif
#ifndef HWCAP_LRCPC
#define HWCAP_LRCPC    (1 << 15)
#endif
#ifndef HWCAP_FCMA
#define HWCAP_FCMA     (1 << 11)
#endif
#ifndef HWCAP_SHA3
#define HWCAP_SHA3     (1 << 17)
#endif
#ifndef HWCAP_SHA512
#define HWCAP_SHA512   (1 << 21)
#endif
#ifndef HWCAP_SM3
#define HWCAP_SM3      (1 << 18)
#endif
#ifndef HWCAP_SM4
#define HWCAP_SM4      (1 << 19)
#endif
#ifndef HWCAP_SVE
#define HWCAP_SVE      (1 << 22)
#endif
#ifndef HWCAP_I8MM
#define HWCAP_I8MM     (1 << 27)
#endif
#ifndef HWCAP_BF16
#define HWCAP_BF16     (1 << 30)
#endif

/* SIGILL 安全执行 */
static sigjmp_buf jbuf;
static void sigill_handler(int sig) { siglongjmp(jbuf, 1); }

#define TRY_RUN(CODE) ({                                                \
    int _ok = 1;                                                        \
    struct sigaction _old, _sa;                                         \
    _sa.sa_handler = sigill_handler;                                    \
    sigemptyset(&_sa.sa_mask);                                          \
    _sa.sa_flags = 0;                                                   \
    sigaction(SIGILL, &_sa, &_old);                                     \
    if (sigsetjmp(jbuf, 1) == 0) {                                      \
        CODE;                                                           \
    } else {                                                            \
        _ok = 0;                                                        \
    }                                                                   \
    sigaction(SIGILL, &_old, NULL);                                     \
    _ok;                                                                \
})

/* ----- 在编译时已知支持的指令上跑业务功能验证 ----- */

/* FP16: 编译时启用了 +fp16 修饰符 */
#if defined(__ARM_FEATURE_FP16) && (__ARM_FEATURE_FP16 == 1)
#define HAVE_FP16_BUILT 1
static int test_fp16_run(void) {
    float16x8_t a = vdupq_n_f16(1.5f16);
    float16x8_t b = vdupq_n_f16(2.0f16);
    float16x8_t c = vaddq_f16(a, b);
    return c[0] > 3.0f16 && c[0] < 4.0f16;
}
#else
#define HAVE_FP16_BUILT 0
static int test_fp16_run(void) { return -1; }
#endif

/* AES: 编译时 +crypto 启用 */
#if defined(__ARM_FEATURE_CRYPTO)
#define HAVE_CRYPTO_BUILT 1
static int test_aes_run(void) {
    uint8x16_t a = vdupq_n_u8(1);
    uint8x16_t k = vdupq_n_u8(2);
    uint8x16_t r = vaeseq_u8(a, k);
    return vgetq_lane_u8(r, 0) != 1;
}
static int test_sha256_run(void) {
    uint32x4_t a = vdupq_n_u32(0);
    uint32x4_t b = vdupq_n_u32(0);
    uint32x4_t c = vdupq_n_u32(0);
    uint32x4_t r = vsha256hq_u32(a, b, c);
    return r[0] != 0 || r[1] != 0;
}
#else
#define HAVE_CRYPTO_BUILT 0
static int test_aes_run(void)    { return -1; }
static int test_sha256_run(void) { return -1; }
#endif

/* CRC32: 通常 +crc 启用 */
#if defined(__ARM_FEATURE_CRC32)
#define HAVE_CRC_BUILT 1
static int test_crc32_run(void) {
    uint32_t r = __crc32cw(0xFFFFFFFFu, 0x12345678u);
    return r != 0 && r != 0xFFFFFFFFu;
}
#else
#define HAVE_CRC_BUILT 0
static int test_crc32_run(void) { return -1; }
#endif

/* ----- 主程序：HWCAP + 运行时验证 ----- */

static void print_row(const char *name, const char *ver,
                      int hwcap, int actual) {
    printf("  %-30s  v%-5s  hwcap=%s  exec=%s\n",
           name, ver,
           hwcap ? "✓" : "✗",
           actual == -1 ? "n/a" : (actual ? "✓" : "✗ SIGILL"));
    if (actual != -1 && hwcap != actual) {
        printf("  ⚠️  HWCAP 与执行不一致\n");
    }
}

int main(void) {
    unsigned long hw  = getauxval(AT_HWCAP);
    unsigned long hw2 = getauxval(AT_HWCAP2);

    printf("================================\n");
    printf("  isa_features — 飞腾 D3000 ISA 实测\n");
    printf("================================\n\n");
    printf("AT_HWCAP  = 0x%lx\n", hw);
    printf("AT_HWCAP2 = 0x%lx\n", hw2);
    printf("编译时 flags: " __VERSION__ "\n");
#if HAVE_FP16_BUILT
    printf("  __ARM_FEATURE_FP16 = 1 (编译启用)\n");
#endif
#if HAVE_CRYPTO_BUILT
    printf("  __ARM_FEATURE_CRYPTO = 1 (编译启用)\n");
#endif
#if HAVE_CRC_BUILT
    printf("  __ARM_FEATURE_CRC32 = 1 (编译启用)\n");
#endif
    printf("\n");

    printf("== 支持的特性矩阵 ==\n");
    print_row("ASIMD (NEON base)",   "8.0", !!(hw & HWCAP_ASIMD),    -1);
    print_row("AES",                 "8.0", !!(hw & HWCAP_AES),      HAVE_CRYPTO_BUILT ? TRY_RUN(test_aes_run()) : -1);
    print_row("SHA1",                "8.0", !!(hw & HWCAP_SHA1),     -1);
    print_row("SHA256",              "8.0", !!(hw & HWCAP_SHA2),     HAVE_CRYPTO_BUILT ? TRY_RUN(test_sha256_run()) : -1);
    print_row("PMULL",               "8.0", !!(hw & HWCAP_PMULL),    -1);
    print_row("CRC32",               "8.0", !!(hw & HWCAP_CRC32),    HAVE_CRC_BUILT ? TRY_RUN(test_crc32_run()) : -1);
    print_row("LSE ATOMICS",         "8.1", !!(hw & HWCAP_ATOMICS),  -1);
    print_row("ASIMDRDM (SQRDMLAH)", "8.1", !!(hw & HWCAP_ASIMDRDM), -1);
    print_row("LRCPC",               "8.1", !!(hw & HWCAP_LRCPC),    -1);
    print_row("FP16 标量 (FHP)",     "8.2", !!(hw & HWCAP_FPHP),     -1);
    print_row("FP16 NEON (ASIMDHP)", "8.2", !!(hw & HWCAP_ASIMDHP),  HAVE_FP16_BUILT ? TRY_RUN(test_fp16_run()) : -1);
    print_row("FCMA (复数)",         "8.3", !!(hw & HWCAP_FCMA),     -1);
    print_row("SHA3",                "8.4", !!(hw & HWCAP_SHA3),     -1);
    print_row("SHA512",              "8.4", !!(hw & HWCAP_SHA512),   -1);
    print_row("SM3 (国密)",          "8.4", !!(hw & HWCAP_SM3),      -1);
    print_row("SM4 (国密)",          "8.4", !!(hw & HWCAP_SM4),      -1);
    print_row("Dot Product (UDOT)",  "8.4", !!(hw & HWCAP_ASIMDDP),  -1);
    printf("\n");

    printf("== 不支持的特性（确认）==\n");
    print_row("SVE",   "8.4+", !!(hw & HWCAP_SVE),  -1);
    print_row("I8MM",  "8.6",  !!(hw2 & HWCAP_I8MM), -1);
    print_row("BF16",  "8.6",  !!(hw2 & HWCAP_BF16), -1);

    printf("\n== 结论 ==\n");
    int v84_count = 0;
    if (hw & HWCAP_ASIMDDP) v84_count++;
    if (hw & HWCAP_SHA3)    v84_count++;
    if (hw & HWCAP_SHA512)  v84_count++;
    if (hw & HWCAP_SM3)     v84_count++;
    if (hw & HWCAP_SM4)     v84_count++;
    if (v84_count >= 3) {
        printf("  ✅ 飞腾 D3000 实测支持到 ARMv8.4 级别特性\n");
        printf("     可做: fp16 GEMM (Lab05.6), int8 UDOT CNN (Lab05.7),\n");
        printf("           SM3/SM4 国密 (Lab07.3), FCMLA FFT (Lab01.7)\n");
    }
    if (!(hw & HWCAP_SVE)) {
        printf("  ⚠️  SVE 不支持（SIMD 仅 128-bit 固定宽度）\n");
    }
    if (!(hw2 & HWCAP_BF16)) {
        printf("  ⚠️  BF16 不支持（fp16 路径要注意累积精度）\n");
    }

    return 0;
}
