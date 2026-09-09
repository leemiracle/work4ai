/*
 * Lab07/src/sm_test.c — 国密 SM3/SM4 硬件加速探测
 *
 * 飞腾 D3000 支持 SM3/SM4 (v8.4 SSE 扩展)，这是中国市场的核心优势。
 * 本实验：
 *   1. HWCAP 探测硬件支持
 *   2. 软件 SM4 实现 + 吞吐测量
 *   3. 标注硬件加速（vsm4eq intrinsic 需 GCC 10+ 或 +sm4 重编译）
 *
 * SM4: 分组密码，128-bit key，128-bit block，32 轮
 * SM3: 哈希，类似 SHA256，输出 256-bit
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <sys/auxv.h>
#include "bench.h"

#ifndef HWCAP_SM3
#define HWCAP_SM3 (1 << 18)
#endif
#ifndef HWCAP_SM4
#define HWCAP_SM4 (1 << 19)
#endif
#ifndef HWCAP_SHA3
#define HWCAP_SHA3 (1 << 17)
#endif
#ifndef HWCAP_SHA512
#define HWCAP_SHA512 (1 << 21)
#endif

#define N_BYTES (8 * 1024 * 1024)
#define BLOCK   16         /* SM4 块大小 */
#define REPS    7

static uint8_t g_data[N_BYTES] __attribute__((aligned(64)));

/* SM4 S-box (GB/T 32907-2016) */
static const uint8_t SM4_SBOX[256] = {
    0xd6,0x90,0xe9,0xfe,0xcc,0xe1,0x3d,0xb7,0x16,0xb6,0x14,0xc2,0x28,0xfb,0x2c,0x05,
    0x2b,0x67,0x9a,0x76,0x2a,0xbe,0x04,0xc3,0xaa,0x44,0x13,0x26,0x49,0x86,0x06,0x99,
    0x9c,0x42,0x50,0xf4,0x91,0xef,0x98,0x7a,0x33,0x54,0x0b,0x43,0xed,0xcf,0xac,0x62,
    0xe4,0xb3,0x1c,0xa9,0xc9,0x08,0xe8,0x95,0x80,0xdf,0x94,0xfa,0x75,0x8f,0x3f,0xa6,
    0x47,0x07,0xa7,0xfc,0xf3,0x73,0x17,0xba,0x83,0x59,0x3c,0x19,0xe6,0x85,0x4f,0xa8,
    0x68,0x6b,0x81,0xb2,0x71,0x64,0xda,0x8b,0xf8,0xeb,0x0f,0x4b,0x70,0x56,0x9d,0x35,
    0x1e,0x24,0x0e,0x5e,0x63,0x58,0xd1,0xa2,0x25,0x22,0x7c,0x3b,0x01,0x21,0x78,0x87,
    0xd4,0x00,0x46,0x57,0x9f,0xd3,0x27,0x52,0x4c,0x36,0x02,0xe7,0xa0,0xc4,0xc8,0x9e,
    0xea,0xbf,0x8a,0xd2,0x40,0xc7,0x38,0xb5,0xa3,0xf7,0xf2,0xce,0xf9,0x61,0x15,0xa1,
    0xe0,0xae,0x5d,0xa4,0x9b,0x34,0x1a,0x55,0xad,0x93,0x32,0x30,0xf5,0x8c,0xb1,0xe3,
    0x1d,0xf6,0xe2,0x2e,0x82,0x66,0xca,0x60,0xc0,0x29,0x23,0xab,0x0d,0x53,0x4e,0x6f,
    0xd5,0xdb,0x37,0x45,0xde,0xfd,0x8e,0x2f,0x03,0xff,0x6a,0x72,0x6d,0x6c,0x5b,0x51,
    0x8d,0x1b,0xaf,0x92,0xbb,0xdd,0xbc,0x7f,0x11,0xd9,0x5c,0x41,0x1f,0x10,0x5a,0xd8,
    0x0a,0xc1,0x31,0x88,0xa5,0xcd,0x7b,0xbd,0x2d,0x74,0xd0,0x12,0xb8,0xe5,0xb4,0xb0,
    0x89,0x69,0x97,0x4a,0x0c,0x96,0x77,0x7e,0x65,0xb9,0xf1,0x09,0xc5,0x6e,0xc6,0x84,
    0x18,0xf0,0x7d,0xec,0x3a,0xdc,0x4d,0x20,0x79,0xee,0x5f,0x3e,0xd7,0xcb,0x39,0x48
};

static inline uint32_t sm4_tau(uint32_t x) {
    return ((uint32_t)SM4_SBOX[(x>>24)&0xff]<<24) |
           ((uint32_t)SM4_SBOX[(x>>16)&0xff]<<16) |
           ((uint32_t)SM4_SBOX[(x>> 8)&0xff]<< 8) |
           ((uint32_t)SM4_SBOX[ x     &0xff]);
}

static inline uint32_t sm4_L(uint32_t b) {
    return b ^ ((b<<2)|(b>>30)) ^ ((b<<10)|(b>>22)) ^ ((b<<18)|(b>>14)) ^ ((b<<24)|(b>>8));
}

static inline uint32_t sm4_T(uint32_t x) { return sm4_L(sm4_tau(x)); }

/* SM4 密钥扩展用的线性变换 L'（与加密 L 不同）*/
static inline uint32_t sm4_L_prime(uint32_t b) {
    return b ^ ((b<<13)|(b>>19)) ^ ((b<<23)|(b>>9));
}
static inline uint32_t sm4_T_prime(uint32_t x) { return sm4_L_prime(sm4_tau(x)); }

/* SM4 系统参数 FK 与固定参数 CK (GB/T 32907-2016 §7.3) */
static const uint32_t SM4_FK[4] = {0xa3b1bac6, 0x56aa3350, 0x677d9197, 0xb27022dc};
static const uint32_t SM4_CK[32] = {
    0x00070e15,0x1c232a31,0x383f464d,0x545b6269,0x70777e85,0x8c939aa1,0xa8afb6bd,0xc4cbd2d9,
    0xe0e7eef5,0xfc030a11,0x181f262d,0x343b4249,0x50575e65,0x6c737a81,0x888f969d,0xa4abb2b9,
    0xc0c7ced5,0xdce3eaf1,0xf8ff060d,0x141b2229,0x30373e45,0x4c535a61,0x686f767d,0x848b9299,
    0xa0a7aeb5,0xbcc3cad1,0xd8dfe6ed,0xf4fb0209,0x10171e25,0x2c333a41,0x484f565d,0x646b7279
};

/* SM4 密钥扩展：128-bit key → 32 个轮密钥 rk (GB/T 32907 §7.3) */
static void sm4_key_expansion(const uint8_t key[16], uint32_t rk[32]) {
    uint32_t k[36];
    k[0] = ((uint32_t)key[0]<<24)|((uint32_t)key[1]<<16)|((uint32_t)key[2]<<8)|key[3];
    k[1] = ((uint32_t)key[4]<<24)|((uint32_t)key[5]<<16)|((uint32_t)key[6]<<8)|key[7];
    k[2] = ((uint32_t)key[8]<<24)|((uint32_t)key[9]<<16)|((uint32_t)key[10]<<8)|key[11];
    k[3] = ((uint32_t)key[12]<<24)|((uint32_t)key[13]<<16)|((uint32_t)key[14]<<8)|key[15];
    k[0] ^= SM4_FK[0]; k[1] ^= SM4_FK[1]; k[2] ^= SM4_FK[2]; k[3] ^= SM4_FK[3];
    for (int i = 0; i < 32; i++) {
        k[i+4] = k[i] ^ sm4_T_prime(k[i+1] ^ k[i+2] ^ k[i+3] ^ SM4_CK[i]);
        rk[i] = k[i+4];
    }
}

/* SM4 单块加密（ECB）。GB/T 32907-2016 §7.4 正确轮函数：
 *   tmp = x0 ^ T(x1 ^ x2 ^ x3 ^ rk[i])   ← 旧版错为 x3^T(x0^x1^x2^x3^rk)
 *   x0=x1; x1=x2; x2=x3; x3=tmp;         ← 旧版移位方向反了
 * 32 轮后输出 (x35,x34,x33,x32) 反序。*/
static void sm4_encrypt_block_sw(const uint8_t *in, uint8_t *out, const uint32_t rk[32]) {
    uint32_t x0,x1,x2,x3;
    x0=((uint32_t)in[0]<<24)|((uint32_t)in[1]<<16)|((uint32_t)in[2]<<8)|in[3];
    x1=((uint32_t)in[4]<<24)|((uint32_t)in[5]<<16)|((uint32_t)in[6]<<8)|in[7];
    x2=((uint32_t)in[8]<<24)|((uint32_t)in[9]<<16)|((uint32_t)in[10]<<8)|in[11];
    x3=((uint32_t)in[12]<<24)|((uint32_t)in[13]<<16)|((uint32_t)in[14]<<8)|in[15];
    for (int i = 0; i < 32; i++) {
        uint32_t tmp = x0 ^ sm4_T(x1 ^ x2 ^ x3 ^ rk[i]);
        x0 = x1; x1 = x2; x2 = x3; x3 = tmp;
    }
    /* 32 轮后 (x0,x1,x2,x3)=(X32,X33,X34,X35)，密文反序输出 (X35,X34,X33,X32) */
    out[0]=x3>>24; out[1]=x3>>16; out[2]=x3>>8;  out[3]=x3;
    out[4]=x2>>24; out[5]=x2>>16; out[6]=x2>>8;  out[7]=x2;
    out[8]=x1>>24; out[9]=x1>>16; out[10]=x1>>8; out[11]=x1;
    out[12]=x0>>24;out[13]=x0>>16;out[14]=x0>>8; out[15]=x0;
}

/* 用 GB/T 32907 标准测试向量自检 SM4 实现：
 *   key  = 0123456789abcdeffedcba9876543210
 *   in   = 0123456789abcdeffedcba9876543210
 *   out  = 681edf34d206965e86b3e94f536e4246   (期望)
 * 返回 0 = 通过。*/
static int sm4_self_test(void) {
    static const uint8_t key[16]  = {0x01,0x23,0x45,0x67,0x89,0xab,0xcd,0xef,
                                     0xfe,0xdc,0xba,0x98,0x76,0x54,0x32,0x10};
    static const uint8_t in[16]   = {0x01,0x23,0x45,0x67,0x89,0xab,0xcd,0xef,
                                     0xfe,0xdc,0xba,0x98,0x76,0x54,0x32,0x10};
    static const uint8_t expect[16] = {0x68,0x1e,0xdf,0x34,0xd2,0x06,0x96,0x5e,
                                       0x86,0xb3,0xe9,0x4f,0x53,0x6e,0x42,0x46};
    uint32_t rk[32];
    sm4_key_expansion(key, rk);
    uint8_t out[16];
    sm4_encrypt_block_sw(in, out, rk);
    return memcmp(out, expect, 16);
}

/* 真实密钥扩展生成的 round key（旧版用简化伪 rk 是错的）*/
static uint32_t g_rk[32];
static void init_rk(void) {
    /* 用标准测试向量的 key 做密钥扩展，得到真实 rk */
    static const uint8_t key[16] = {0x01,0x23,0x45,0x67,0x89,0xab,0xcd,0xef,
                                    0xfe,0xdc,0xba,0x98,0x76,0x54,0x32,0x10};
    sm4_key_expansion(key, g_rk);
}

static double time_sm4_sw(void) {
    uint64_t ts[REPS];
    static uint8_t out[BLOCK];
    for (int r = 0; r < REPS; r++) {
        uint64_t t0 = now_ns();
        for (size_t i = 0; i < N_BYTES; i += BLOCK) {
            sm4_encrypt_block_sw(&g_data[i], out, g_rk);
        }
        uint64_t t1 = now_ns();
        sink(out[0]);
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
    unsigned long hw = getauxval(AT_HWCAP);
    init_rk();
    srand(42);
    for (size_t i = 0; i < N_BYTES; i++) g_data[i] = (uint8_t)(rand() & 0xFF);

    printf("== Lab07.3: SM3/SM4 国密探测 (N=%zu MB) ==\n\n",
           (size_t)(N_BYTES/(1024*1024)));

    /* SM4 标准测试向量自检（确保算法实现正确）*/
    int st = sm4_self_test();
    printf("  SM4 自检 (GB/T 32907 标准向量 key=0123..3210): %s\n\n",
           st == 0 ? "✓ 通过" : "✗ 失败！算法实现有误");

    printf("  HWCAP 探测:\n");
    printf("    SM3 (国密哈希):    %s\n", (hw & HWCAP_SM3)   ? "✓ 支持" : "✗");
    printf("    SM4 (国密分组):    %s\n", (hw & HWCAP_SM4)   ? "✓ 支持" : "✗");
    printf("    SHA3:              %s\n", (hw & HWCAP_SHA3)  ? "✓ 支持" : "✗");
    printf("    SHA512:            %s\n\n", (hw & HWCAP_SHA512)? "✓ 支持" : "✗");

    double t = time_sm4_sw();
    printf("%-22s %12s %12s\n", "method", "T(ms)", "GB/s");
    printf("%-22s %12s %12s\n", "-----", "------", "------");
    printf("%-22s %12.1f %12.2f\n", "软件 SM4 (查表)", t/1e6,
           (double)N_BYTES / t);  /* bytes/ns = GB/s */

    printf("\n  == 解读 ==\n");
    printf("  * 软件 SM4: 32 轮 × (S-box 查表 + 线性变换 L), 每轮 ~10 指令\n");
    printf("  * 硬件 vsm4eq (v8.4): 单指令完成 SM4 轮函数, 预期 10-25x 加速\n");
    printf("  * ⚠ 硬件 intrinsic (vsm4eq_u32) 需 GCC 10+ 或 -march=armv8.4-a+sm4\n");
    printf("    飞腾 GCC 9.3 可能不支持，需 kpgcc 或新版 GCC 重编译\n");
    printf("  * 国密合规: GB/T 32907-2016 (SM4), GB/T 32905-2016 (SM3)\n");
    printf("  * 应用: 政务/金融 TLS、电子签名、区块链（国内合规场景）\n");
    printf("  * 完整实现: GmSSL、OpenSSL 3.x + SM4 engine\n");
    return 0;
}
