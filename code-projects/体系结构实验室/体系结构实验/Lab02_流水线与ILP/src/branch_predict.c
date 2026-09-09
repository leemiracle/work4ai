/*
 * Lab02/src/branch_predict.c — 分支预测实验
 *
 * 测三种分支模式：
 *   1. 单调（i < N/2）：完全可预测
 *   2. 周期（i & 3）：短周期可预测
 *   3. 周期（i & 15）：长周期
 *   4. 随机（r[i] < threshold）：完全不可预测
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include "bench.h"
#include "pmu.h"

#define N 10000000
#define REPS 21

uint32_t rand_data[N];

/* xorshift64* 伪随机生成器 — 比 rand() LCG 更不可预测，减少预测器学到的模式 */
static uint64_t xs_state = 0xDEADBEEFCAFE1234ULL;
static inline uint32_t xorshift32(void) {
    uint64_t x = xs_state;
    x ^= x >> 12; x ^= x << 25; x ^= x >> 27;
    xs_state = x;
    return (uint32_t)((x * 0x2545F4914F6CDD1DULL) >> 32);
}

uint64_t __attribute__((noinline,optimize("no-tree-vectorize","no-if-conversion")))
branch_predictable(void) {
    uint64_t s = 0;
    for (size_t i = 0; i < N; i++) {
        if (i < (size_t)N/2) s += rand_data[i];
        else                 s -= rand_data[i];
    }
    return s;
}

uint64_t __attribute__((noinline,optimize("no-tree-vectorize","no-if-conversion")))
branch_period4(void) {
    uint64_t s = 0;
    for (size_t i = 0; i < N; i++) {
        if ((i & 3) == 0) s += rand_data[i];
        else              s -= rand_data[i];
    }
    return s;
}

uint64_t __attribute__((noinline,optimize("no-tree-vectorize","no-if-conversion")))
branch_period16(void) {
    uint64_t s = 0;
    for (size_t i = 0; i < N; i++) {
        if ((i & 15) == 0) s += rand_data[i];
        else               s -= rand_data[i];
    }
    return s;
}

uint64_t __attribute__((noinline,optimize("no-tree-vectorize","no-if-conversion")))
branch_random(void) {
    uint64_t s = 0;
    for (size_t i = 0; i < N; i++) {
        if (rand_data[i] < 0x80000000U) s += rand_data[i];
        else                            s -= rand_data[i];
    }
    return s;
}

uint64_t __attribute__((noinline,optimize("no-tree-vectorize","no-if-conversion")))
branch_period_long(void) {
    /* 用 LFSR 制造看似随机但可学习的模式 */
    uint64_t s = 0;
    uint64_t lfsr = 0xDEADBEEFCAFEULL;
    for (size_t i = 0; i < N; i++) {
        /* 64-bit LFSR, 周期 2^64-1 */
        uint64_t bit = (lfsr >> 0) ^ (lfsr >> 1) ^ (lfsr >> 3) ^ (lfsr >> 4);
        lfsr = (lfsr >> 1) | ((bit & 1) << 63);
        if (lfsr & 1) s += rand_data[i];
        else          s -= rand_data[i];
    }
    return s;
}

#define MEASURE(BLOCK_NS_VAR, BLOCK) do {            \
    uint64_t _ts[REPS];                               \
    for (int _r = 0; _r < REPS; _r++) {               \
        uint64_t _t0 = now_ns();                      \
        BLOCK;                                         \
        uint64_t _t1 = now_ns();                      \
        _ts[_r] = _t1 - _t0;                          \
    }                                                  \
    BLOCK_NS_VAR = (double)median_u64(_ts, REPS);     \
} while (0)

int main(void) {
    pin_to_cpu(0);

    /* 初始化随机数据：xorshift64*（比 rand() LCG 更不可预测，
     * 否则飞腾 TAGE 预测器能学到 LCG 模式，random miss% 偏低）*/
    xs_state = 0xDEADBEEFCAFE1234ULL;
    for (size_t i = 0; i < N; i++) {
        rand_data[i] = xorshift32();
    }

    printf("== Lab02.2: 分支预测 ==\n\n");
    printf("  N = %d\n\n", N);

    /* 用 PMU 测 cycles + insts + branch-misses */
    pmu_group_t pmu = {0};
    int have_pmu = 1;
    if (pmu_add_hw(&pmu, PERF_COUNT_HW_CPU_CYCLES, "cyc") != 0) have_pmu = 0;
    if (pmu_add_hw(&pmu, PERF_COUNT_HW_INSTRUCTIONS, "ins") != 0) have_pmu = 0;
    if (pmu_add_hw(&pmu, PERF_COUNT_HW_BRANCH_MISSES, "bm") != 0) have_pmu = 0;
    if (pmu_add_raw(&pmu, FTC_BR_PRED, "bp") != 0) have_pmu = 0;

    struct { const char *name; uint64_t (*fn)(void); } tests[] = {
        { "predictable (i<N/2)", branch_predictable },
        { "period 4  (i&3==0)",  branch_period4    },
        { "period 16 (i&15==0)", branch_period16   },
        { "random     (r<0x8...)", branch_random    },
    };

    printf("%-26s %12s %10s %10s %12s %10s\n",
           "pattern", "T_med(ms)", "IPC", "branches", "br_miss", "miss%");
    printf("%-26s %12s %10s %10s %12s %10s\n",
           "--------------------------", "--------", "------", "--------",
           "----------", "------");

    for (size_t i = 0; i < sizeof(tests)/sizeof(tests[0]); i++) {
        /* warmup */
        for (int r = 0; r < 3; r++) tests[i].fn();

        double t_med;
        uint64_t c_med=0, i_med=0, bm_med=0, bp_med=0;
        if (have_pmu) {
            uint64_t times[REPS], cycs[REPS], inss[REPS], bms[REPS], bps[REPS];
            for (int r = 0; r < REPS; r++) {
                pmu_start(&pmu);
                uint64_t t0 = now_ns();
                uint64_t s = tests[i].fn();
                uint64_t t1 = now_ns();
                pmu_stop(&pmu);
                uint64_t v[PMU_MAX_EVENTS] = {0};
                pmu_read(&pmu, v);
                times[r] = t1 - t0; cycs[r] = v[0]; inss[r] = v[1];
                bms[r] = v[2]; bps[r] = v[3];
                sink(s);
            }
            t_med = (double)median_u64(times, REPS);
            c_med = median_u64(cycs, REPS);
            i_med = median_u64(inss, REPS);
            bm_med = median_u64(bms, REPS);
            bp_med = median_u64(bps, REPS);
        } else {
            MEASURE(t_med, { sink(tests[i].fn()); });
        }

        double ipc = (have_pmu && c_med) ? (double)i_med / (double)c_med : 0;
        double miss_pct = (have_pmu && bp_med) ?
                          100.0 * (double)bm_med / (double)(bm_med + bp_med) : 0;
        printf("%-26s %12.1f %10.2f %10llu %12llu %9.2f%%\n",
               tests[i].name, t_med/1e6, ipc,
               (unsigned long long)(bm_med + bp_med),
               (unsigned long long)bm_med, miss_pct);
    }

    if (have_pmu) pmu_close(&pmu);

    printf("\n  == 解读 ==\n");
    printf("  * 随机源: xorshift64* (比 rand() LCG 更不可预测)\n");
    printf("  * 随机分支 IPC 应明显低于单调分支\n");
    printf("  * 随机分支 miss%%: 伪随机 (xorshift/rand) 实测 18-20%%, 非理论 50%%\n");
    printf("    飞腾 TAGE 预测器极强, 对伪随机序列有 ~80%% 预测准确率\n");
    printf("    要 miss%%≈50%% 需密码学随机 (/dev/urandom), 伪随机做不到\n");
    printf("  * 周期 4 的 miss%% 应该接近 0%%（局部预测器识别）\n");
    printf("  * 周期 16 的 miss%% 取决于预测器历史长度\n");
    return 0;
}
