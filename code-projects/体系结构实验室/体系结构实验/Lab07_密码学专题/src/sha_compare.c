/*
 * Lab07/src/sha_compare.c — SHA 哈希硬件加速对比
 *
 * 飞腾 D3000 支持 SHA1/256 (v8.0) + SHA3/SHA512 (v8.4)。
 * 本实验测硬件 SHA256 压缩函数的吞吐，对比软件查表实现。
 *
 * ⚠ 简化版：只测硬件压缩指令 (vsha256hq) 的吞吐，不做完整消息调度。
 *    完整 SHA256 实现（消息调度 + padding）见 OpenSSL/mbedTLS。
 *    教学目标：展示硬件指令 vs 软件的吞吐差。
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <arm_neon.h>
#include "bench.h"

#define N_BYTES (16 * 1024 * 1024)   /* 16 MB */
#define BLOCK   64                    /* SHA256 块大小 */
#define REPS    7

static uint8_t g_data[N_BYTES] __attribute__((aligned(64)));

#if defined(__ARM_FEATURE_CRYPTO) || defined(__ARM_FEATURE_SHA2)
#include <arm_acle.h>
#define HAVE_SHA256_HW 1

/* 硬件 SHA256 单块压缩（简化：固定消息调度，测压缩指令吞吐）
 * 完整实现需 sha256su0/su1 展开 16→64 words，此处用 4 轮循环测指令 */
static void sha256_block_hw(const uint8_t *block, uint32x4_t *h, uint32x4_t *h2) {
    /* 简化：用固定 wk（实际应从 block 算消息调度）*/
    uint32x4_t wk = vld1q_u32((const uint32_t*)block);
    uint32x4_t k = {0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5};
    wk = vaddq_u32(wk, k);
    /* 64 轮压缩（每 4 轮一组，简化为重复测吞吐）*/
    for (int r = 0; r < 16; r++) {
        uint32x4_t new_h = vsha256hq_u32(*h, *h2, wk);
        *h2 = vsha256h2q_u32(*h, *h2, wk);
        *h = new_h;
    }
}
#else
#define HAVE_SHA256_HW 0
static void sha256_block_hw(const uint8_t *block, uint32x4_t *h, uint32x4_t *h2) {
    (void)block; (void)h; (void)h2;
}
#endif

/* 软件 SHA256 单块（查表 + 标准轮函数，完整实现）*/
static const uint32_t K256[64] = {
    0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,
    0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,
    0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,
    0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,
    0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,
    0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,
    0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,
    0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2
};

static inline uint32_t rotr(uint32_t x, int n) { return (x >> n) | (x << (32-n)); }

static void sha256_block_sw(const uint8_t *block, uint32_t state[8]) {
    uint32_t w[64];
    for (int i = 0; i < 16; i++) {
        w[i] = ((uint32_t)block[i*4]<<24) | ((uint32_t)block[i*4+1]<<16) |
               ((uint32_t)block[i*4+2]<<8) | block[i*4+3];
    }
    for (int i = 16; i < 64; i++) {
        uint32_t s0 = rotr(w[i-15],7) ^ rotr(w[i-15],18) ^ (w[i-15] >> 3);
        uint32_t s1 = rotr(w[i-2],17) ^ rotr(w[i-2],19) ^ (w[i-2] >> 10);
        w[i] = w[i-16] + s0 + w[i-7] + s1;
    }
    uint32_t a=state[0],b=state[1],c=state[2],d=state[3];
    uint32_t e=state[4],f=state[5],g=state[6],h=state[7];
    for (int i = 0; i < 64; i++) {
        uint32_t S1 = rotr(e,6) ^ rotr(e,11) ^ rotr(e,25);
        uint32_t ch = (e & f) ^ ((~e) & g);
        uint32_t t1 = h + S1 + ch + K256[i] + w[i];
        uint32_t S0 = rotr(a,2) ^ rotr(a,13) ^ rotr(a,22);
        uint32_t maj = (a & b) ^ (a & c) ^ (b & c);
        uint32_t t2 = S0 + maj;
        h=g; g=f; f=e; e=d+t1; d=c; c=b; b=a; a=t1+t2;
    }
    state[0]+=a; state[1]+=b; state[2]+=c; state[3]+=d;
    state[4]+=e; state[5]+=f; state[6]+=g; state[7]+=h;
}

static double time_sha256_hw(void) {
    uint64_t ts[REPS];
    for (int r = 0; r < REPS; r++) {
        uint32x4_t h = {0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a};
        uint32x4_t h2 = {0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19};
        uint64_t t0 = now_ns();
        for (size_t i = 0; i < N_BYTES; i += BLOCK) {
            sha256_block_hw(&g_data[i], &h, &h2);
        }
        uint64_t t1 = now_ns();
        sink(h[0] + h2[0]);
        ts[r] = t1 - t0;
    }
    for (int i = 1; i < REPS; i++) {
        uint64_t k = ts[i]; int j = i;
        while (j > 0 && ts[j-1] > k) { ts[j] = ts[j-1]; j--; }
        ts[j] = k;
    }
    return (double)ts[REPS/2];
}

static double time_sha256_sw(void) {
    uint64_t ts[REPS];
    for (int r = 0; r < REPS; r++) {
        uint32_t state[8] = {0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,
                             0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19};
        uint64_t t0 = now_ns();
        for (size_t i = 0; i < N_BYTES; i += BLOCK) {
            sha256_block_sw(&g_data[i], state);
        }
        uint64_t t1 = now_ns();
        sink(state[0]);
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
    for (size_t i = 0; i < N_BYTES; i++) g_data[i] = (uint8_t)(rand() & 0xFF);

    printf("== Lab07.2: SHA-256 硬件 vs 软件 (N=%zu MB) ==\n\n",
           (size_t)(N_BYTES/(1024*1024)));
    printf("  硬件 SHA2: %s\n\n", HAVE_SHA256_HW ? "✓ __ARM_FEATURE_SHA2" : "✗");

    printf("%-22s %12s %12s\n", "method", "T(ms)", "GB/s");
    printf("%-22s %12s %12s\n", "-----", "------", "------");

    double t_sw = time_sha256_sw();
    printf("%-22s %12.1f %12.2f\n", "软件 SHA256 (查表)", t_sw/1e6,
           (double)N_BYTES/(t_sw*1e9)*1e9);

    if (HAVE_SHA256_HW) {
        double t_hw = time_sha256_hw();
        printf("%-22s %12.1f %12.2f\n", "硬件 vsha256hq", t_hw/1e6,
               (double)N_BYTES/(t_hw*1e9)*1e9);
        printf("\n  * 硬件加速: %.2fx\n", t_sw/t_hw);
    }

    printf("\n  == 解读 ==\n");
    printf("  * 硬件 vsha256hq 单指令完成 SHA256 轮函数（Ch/Maj/Σ0/Σ1）\n");
    printf("  * 软件 64 轮查表 + 位运算，每轮 ~10 指令\n");
    printf("  * ⚠ 本实验硬件版简化（消息调度不全），完整实现见 OpenSSL\n");
    printf("  * 飞腾还支持 SHA3/SHA512 (v8.4)，SM3 (国密，见 sm_test.c)\n");
    printf("  * 应用: TLS 证书、Git commit hash、区块链、文件校验\n");
    return 0;
}
