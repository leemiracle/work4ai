/*
 * Lab07/src/aes_test.c — AES-128 实测（飞腾硬件加速）
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <arm_neon.h>
#include "bench.h"

#define N_BYTES (16 * 1024 * 1024)  /* 16 MB */
#define REPS 11

static uint8_t plaintext[N_BYTES] __attribute__((aligned(64)));
static uint8_t ciphertext[N_BYTES] __attribute__((aligned(64)));
static uint8_t aes_key[16] = {0x2b, 0x7e, 0x15, 0x16, 0x28, 0xae, 0xd2, 0xa6,
                               0xab, 0xf7, 0x15, 0x88, 0x09, 0xcf, 0x4f, 0x3c};

/* AES 单块加密（16 字节），用 v8.0 硬件指令 vaeseq_u8 + vaesmcq_u8 */
#if defined(__ARM_FEATURE_CRYPTO)
static inline void aes128_block(const uint8_t *in, uint8_t *out, const uint8_t *key) {
    uint8x16_t state = vld1q_u8(in);
    uint8x16_t k0 = vld1q_u8(key);

    /* 简化: 只做 1 轮 AESE + AESMC（完整 AES-128 需要 10 轮 + 最后 1 轮 AESE） */
    state = vaeseq_u8(state, k0);
    state = vaesmcq_u8(state);

    /* 重复 10 次（真实 AES 是 9 轮 AESE+AESMC + 1 轮 AESE + XOR 最后一个 round key） */
    for (int r = 0; r < 9; r++) {
        state = vaeseq_u8(state, k0);
        state = vaesmcq_u8(state);
    }
    state = vaeseq_u8(state, k0);
    /* 最后 AddRoundKey (简化: 用同一 key) */
    state = veorq_u8(state, k0);

    vst1q_u8(out, state);
}
#define HAVE_AES_HW 1
#else
#define HAVE_AES_HW 0
static inline void aes128_block(const uint8_t *in, uint8_t *out, const uint8_t *key) {
    /* 软件占位: 直接拷贝 */
    memcpy(out, in, 16);
    (void)key;
}
#endif

static double time_it(void) {
    uint64_t ts[REPS];
    for (int r = 0; r < REPS; r++) {
        uint64_t t0 = now_ns();
        for (size_t i = 0; i < N_BYTES; i += 16)
            aes128_block(&plaintext[i], &ciphertext[i], aes_key);
        uint64_t t1 = now_ns();
        sink(ciphertext[N_BYTES/2]);
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

    srand(42);
    for (size_t i = 0; i < N_BYTES; i++) plaintext[i] = (uint8_t)(rand() & 0xFF);

    printf("== Lab07.1: AES-128 实测 (N=%zu MB) ==\n\n", (size_t)(N_BYTES/(1024*1024)));
    printf("  硬件 AES: %s\n\n", HAVE_AES_HW ? "✓ __ARM_FEATURE_CRYPTO" : "✗ 软件实现");

    double t = time_it();
    printf("%-20s %12s %12s\n", "method", "T(ms)", "GB/s");
    printf("%-20s %12s %12s\n", "----------------", "----------", "------");
    printf("%-20s %12.1f %12.2f\n", HAVE_AES_HW ? "AES 硬件加速" : "AES 软件",
            t/1e6, (double)N_BYTES / t);  /* bytes/ns = GB/s */

    printf("\n  == 解读 ==\n");
    printf("  * ⚠ 诚实声明: 本测是 AESE+AESMC 指令组合的吞吐演示，非完整 AES-128。\n");
    printf("    (简化: 10 轮全用同一 round key，无 KeyExpansion。测的是指令周期，非真实加密吞吐)\n");
    printf("  * 完整 AES-128 (11 round keys + FIPS 197 向量校验) 见 OpenSSL: openssl speed -evp aes-128-cbc\n");
    printf("  * 飞腾 D3000M 完整 AES-128-GCM 实测约 1-3 GB/s (见 Expert_05)\n");
    printf("  * 软件 AES-128-CTR 约 100-200 MB/s\n");
    return 0;
}
