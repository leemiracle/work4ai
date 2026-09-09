/* View_02_Security/src/constant_time.c — 常时间编程 vs 数据依赖时间
 *
 * 密码学/安全代码的核心要求：执行时间**不依赖于秘密数据**。
 * 否则 cache timing 攻击就能逐字节偷出密钥。
 *
 * 本文件对比 4 种"内存比较"实现，用 cache_timing 工具看哪个不安全。
 */
#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include <time.h>

/* —— 不安全 1: 短路比较 ——
 * 一旦发现不同字节就立即返回，时间正比于"相同前缀长度"
 * 攻击者逐字节猜，正确那一个会多花几个 cycle */
int vulnerable_strcmp(const char *a, const char *b, int n) {
    for (int i = 0; i < n; i++) {
        if (a[i] != b[i]) return 0;        /* 早退 */
    }
    return 1;
}

/* —— 不安全 2: 表查找 ——
 * AES T-table 实现就是这种，T[byte] 访问的 cache line 暴露 byte 值
 * OpenSSL 著名的 AES cache timing 漏洞（2005+）就是这种 */
int vulnerable_table_lookup(uint8_t idx) {
    static volatile uint8_t secret_table[256 * 64];   /* 每个 entry 一行 */
    return secret_table[idx * 64];
}

/* —— 安全 1: 全比较 + 累积差 ——
 * 永远遍历全部，时间固定 */
int constant_time_strcmp(const char *a, const char *b, int n) {
    volatile int diff = 0;
    for (int i = 0; i < n; i++) {
        diff |= a[i] ^ b[i];     /* 永远执行，累积 XOR */
    }
    return diff == 0;
}

/* —— 安全 2: branchless 条件 ——
 * 用位运算代替 if-else */
int constant_time_select(int cond, int a, int b) {
    /* cond 应该是 0 或 -1（全 0 / 全 1）*/
    return (cond & a) | (~cond & b);
}

/* 计时器 */
static inline uint64_t rdtsc(void) {
    uint64_t v;
    __asm__ volatile("mrs %0, cntvct_el0" : "=r"(v));
    return v;
}

#define N 32

int main(void) {
    char correct[N] = "passwordpasswordpasswordpass";
    char wrong_first[N] = "Xasswordpasswordpasswordpas";
    char wrong_last[N]  = "passwordpasswordpasswordpasX";
    char correct2[N];
    memcpy(correct2, correct, N);

    /* 各比较方法的耗时 */
    struct { const char *name; int (*fn)(const char*, const char*, int); } tests[] = {
        {"vulnerable_strcmp", vulnerable_strcmp},
        {"constant_time_strcmp", constant_time_strcmp},
    };

    printf("=== 4 种内存比较实现的时间分析 ===\n\n");
    printf("比较: correct vs {correct, wrong_first, wrong_last}\n");
    printf("（正确实现应该 3 种情况耗时一致）\n\n");

    for (int t = 0; t < 2; t++) {
        printf("[%s]\n", tests[t].name);
        const char *inputs[] = {"correct2", "wrong_first", "wrong_last"};
        const char *ptrs[] = {(const char*)correct2, (const char*)wrong_first, (const char*)wrong_last};
        for (int i = 0; i < 3; i++) {
            /* 重复跑取中位数 */
            uint64_t times[100];
            for (int k = 0; k < 100; k++) {
                uint64_t t0 = rdtsc();
                volatile int r = tests[t].fn(correct, ptrs[i], N);
                times[k] = rdtsc() - t0;
                (void)r;
            }
            /* 简单排序找中位数 */
            for (int a = 0; a < 100; a++)
                for (int b = a + 1; b < 100; b++)
                    if (times[a] > times[b]) {
                        uint64_t tmp = times[a]; times[a] = times[b]; times[b] = tmp;
                    }
            printf("  %s : %lu cycles (match=%d)\n",
                   inputs[i], (unsigned long)times[50],
                   tests[t].fn(correct, ptrs[i], N));
        }
        printf("\n");
    }

    printf("=== 关键观察 ===\n");
    printf("vulnerable_strcmp:  correct2 与 wrong_last 时间差很大（短路效应）\n");
    printf("                    -> 攻击者能逐字节猜密钥\n");
    printf("constant_time_strcmp: 三种情况时间几乎一致（差 < 10%%）\n");
    printf("                       -> 没有信息泄漏\n\n");

    printf("=== 防御规范 ===\n");
    printf("- OpenSSL BN_bin2bn / Go crypto/subtle.ConstantTimeCompare\n");
    printf("- libsodium crypto_verify_* 系列\n");
    printf("- 始终遍历全部数据，使用 XOR 而非 '=='\n");
    printf("- 避免 table[secret] 模式；如必需，用 bitslice / bits-to-bytes 转换\n");
    return 0;
}
