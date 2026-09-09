/*
 * Lab07/src/crc_test.c — CRC32 硬件 vs 软件对比
 *
 * 飞腾 D3000 支持 ARMv8 CRC32 指令集:
 *   crc32b/h/w: 1/2/4 字节 CRC-32 (Castagnoli)
 *   __crc32cw 内建
 *
 * 这是飞腾最简单的硬件加速指令集，先做这个。
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <time.h>
#include "bench.h"

#define N_BYTES (64 * 1024 * 1024)  /* 64 MB */
#define REPS 7

static uint8_t data[N_BYTES] __attribute__((aligned(64)));

/* 软件 CRC-32C (Castagnoli 多项式 0x82F63B78，匹配 ARM __crc32cw) */
static uint32_t crc32_sw(const uint8_t *buf, size_t n) {
    uint32_t crc = 0xFFFFFFFF;
    for (size_t i = 0; i < n; i++) {
        crc ^= buf[i];
        for (int j = 0; j < 8; j++)
            crc = (crc >> 1) ^ (0x82F63B78UL & (-(int32_t)(crc & 1)));
    }
    return crc;  /* 无 final XOR，匹配 ARM __crc32cw 语义 */
}

/* 软件 CRC-32C 查表（Castagnoli 多项式） */
static uint32_t crc32_table[256];
static void crc32_init_table(void) {
    for (uint32_t i = 0; i < 256; i++) {
        uint32_t c = i;
        for (int k = 0; k < 8; k++)
            c = (c >> 1) ^ (0x82F63B78UL & (-(int32_t)(c & 1)));
        crc32_table[i] = c;
    }
}
static uint32_t crc32_table_sw(const uint8_t *buf, size_t n) {
    uint32_t crc = 0xFFFFFFFF;
    for (size_t i = 0; i < n; i++)
        crc = crc32_table[(crc ^ buf[i]) & 0xFF] ^ (crc >> 8);
    return crc;  /* 无 final XOR，匹配 ARM __crc32cw */
}

/* 硬件 CRC-32（飞腾 v8.0 CRC32 扩展） */
#if defined(__ARM_FEATURE_CRC32)
#include <arm_acle.h>
static uint32_t crc32_hw(const uint8_t *buf, size_t n) {
    uint32_t crc = 0xFFFFFFFF;
    /* 4 字节对齐部分 */
    size_t i = 0;
    while (i + 4 <= n) {
        uint32_t v;
        memcpy(&v, &buf[i], 4);
        crc = __crc32cw(crc, v);
        i += 4;
    }
    /* 剩余字节 */
    while (i < n) {
        crc = __crc32cb(crc, buf[i]);
        i++;
    }
    return crc;
}
#define HAVE_CRC_HW 1
#else
#define HAVE_CRC_HW 0
static uint32_t crc32_hw(const uint8_t *buf, size_t n) { return crc32_table_sw(buf, n); }
#endif

static double time_it(uint32_t (*fn)(const uint8_t*, size_t)) {
    uint64_t ts[REPS];
    for (int r = 0; r < REPS; r++) {
        uint64_t t0 = now_ns();
        volatile uint32_t c = fn(data, N_BYTES);
        sink(c);
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
    crc32_init_table();

    /* 准备数据 */
    srand(42);
    for (size_t i = 0; i < N_BYTES; i++) data[i] = (uint8_t)(rand() & 0xFF);

    printf("== Lab07.4: CRC32 硬件 vs 软件 (N=%d MB) ==\n\n", (int)(N_BYTES/(1024*1024)));
    printf("  硬件 CRC32: %s\n\n", HAVE_CRC_HW ? "✓ __ARM_FEATURE_CRC32" : "✗");

    /* 正确性验证 */
    uint32_t c_sw = crc32_sw(data, N_BYTES);
    uint32_t c_tbl = crc32_table_sw(data, N_BYTES);
    uint32_t c_hw = crc32_hw(data, N_BYTES);
    printf("  correctness: sw=%08x  table=%08x  hw=%08x  %s\n\n",
           c_sw, c_tbl, c_hw, (c_sw == c_tbl && c_tbl == c_hw) ? "✓" : "✗");

    double t_sw = time_it(crc32_sw);
    double t_tbl = time_it(crc32_table_sw);
    double t_hw = time_it(crc32_hw);

    printf("%-25s %12s %12s\n", "method", "T(ms)", "GB/s");
    printf("%-25s %12s %12s\n", "-----------------------", "----------", "------");
    printf("%-25s %12.1f %12.2f\n", "软件 bitwise", t_sw/1e6, (double)N_BYTES/(t_sw*1e9)*1e9);
    printf("%-25s %12.1f %12.2f\n", "软件 table (256B)", t_tbl/1e6, (double)N_BYTES/(t_tbl*1e9)*1e9);
    printf("%-25s %12.1f %12.2f\n", "硬件 __crc32cw", t_hw/1e6, (double)N_BYTES/(t_hw*1e9)*1e9);

    printf("\n  == 解读 ==\n");
    printf("  * 硬件加速比: %.2fx (vs table)\n", t_tbl/t_hw);
    printf("  * 应用: 网络包校验、Zlib 解压、Btrfs/ZFS 校验\n");
    return 0;
}
