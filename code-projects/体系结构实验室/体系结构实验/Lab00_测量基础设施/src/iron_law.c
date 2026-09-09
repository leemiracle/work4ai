/*
 * Lab00/src/iron_law.c — CPU 时间公式分解 (Iron Law)
 *
 * Time = IC × CPI × τ
 *
 *   IC = Instruction Count
 *   CPI = Cycles per Instruction = cycles / IC
 *   τ = 1 / freq
 *
 * 测量三种工作负载：
 *   1. 数组求和（向量化后 IPC 高）
 *   2. 链表追逐（依赖链长，IPC 低）
 *   3. 分支密集（rand 后又 reset，看分支预测失败代价）
 *

CPI 反映处理器的执行效率，主要受以下因素影响：现代高性能 CPU 的 CPI 通常 0.25–2.0（IPC = 0.5–4），但在极端内存密集型负载中（如随机链表的指针追逐），CPI 可以飙升到 100 以上。

因素	如何影响 CPI
指令级并行（ILP）	处理器同时发射多条独立指令 → CPI 降低
缓存失效	指令或数据不在缓存中，需等待内存 → CPI 升高（比如你的链表遍历）
分支预测失败	流水线被冲刷，浪费多个周期 → CPI 升高
数据依赖	下一条指令需要上一条的结果，无法并行 → CPI 升高
指令混合	复杂指令（除法、内存访问）需要更多周期 → CPI 升高



 * 用法: ./iron_law [N]
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <inttypes.h>
#include <math.h>
#include <string.h>

#include "bench.h"
#include "pmu.h"

#define REPS 21

/* ----- 工作负载 1：数组求和（容易 ILP） ----- */
static double w_array_sum(const double *a, size_t n) {
    double s = 0;
    for (size_t i = 0; i < n; i++) s += a[i];
    return s;
}

/* ----- 工作负载 2：链表追逐（依赖链长，IPC 低） ----- */
typedef struct node { struct node *next; uint64_t pad[7]; } node_t;
static uint64_t w_linked_list(const node_t *head) {
    uint64_t n = 0;
    const node_t *p = head;
    while (p) {
        n++;
        p = p->next;
    }
    return n;
}

/* ----- 工作负载 3：分支密集（随机比较） ----- */
static uint64_t w_branchy(const uint32_t *r, size_t n) {
    uint64_t s = 0;
    for (size_t i = 0; i < n; i++) {
        if (r[i] < 0x80000000U) s += r[i];
        else                    s -= r[i];
    }
    return s;
}

/* ----- 工作负载 4：分支密集（可预测比较） ----- */
static uint64_t w_branchy_pred(const uint32_t *r, size_t n) {
    uint64_t s = 0;
    for (size_t i = 0; i < n; i++) {
        /* i 单调递增，编译器和分支预测器都能猜对 */
        if (i < n/2) s += r[i];
        else         s -= r[i];
    }
    return s;
}

/* ----- 通用测量 ----- */
typedef struct {
    const char *name;
    uint64_t    work;
} metric_t;

static double cpu_freq_ghz(void) {
    /* 读 cntfrq_el0 在用户态可能没权限；用 /sys 查 */
    FILE *fp = fopen("/sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq", "r");
    if (fp) {
        long khz;
        if (fscanf(fp, "%ld", &khz) == 1) { fclose(fp); return khz / 1e6; }
        fclose(fp);
    }
    return 2.5;  /* 飞腾 D3000M 实测 2500 MHz (旧版误为 2.6) */
}

int main(int argc, char **argv) {
    size_t N = argc > 1 ? strtoull(argv[1], NULL, 0) : 1000000;
    if (pin_to_cpu(0) != 0) fprintf(stderr, "warn: pin failed\n");

    /* 准备数据 */
    double *arr;
    posix_memalign((void **)&arr, 64, N * sizeof(double));
    for (size_t i = 0; i < N; i++) arr[i] = (double)i * 0.001;

    node_t *nodes;
    posix_memalign((void **)&nodes, 64, N * sizeof(node_t));
    /* 构造一条乱序链（地址随机分布） */
    size_t *perm = malloc(N * sizeof(size_t));
    for (size_t i = 0; i < N; i++) perm[i] = i;
    srand(42);
    for (size_t i = N-1; i > 0; i--) {
        size_t j = rand() % (i+1);
        size_t t = perm[i]; perm[i] = perm[j]; perm[j] = t;
    }
    for (size_t i = 0; i < N-1; i++)
        nodes[perm[i]].next = &nodes[perm[i+1]];
    nodes[perm[N-1]].next = NULL;

    uint32_t *rand_data;
    posix_memalign((void **)&rand_data, 64, N * sizeof(uint32_t));
    for (size_t i = 0; i < N; i++)
        rand_data[i] = ((uint32_t)rand() << 16) ^ (uint32_t)rand();

    /* 频率 */
    double freq = cpu_freq_ghz();
    printf("== Iron Law (N=%zu, freq=%.2f GHz) ==\n\n", N, freq);
    printf("%-22s %12s %12s %12s %8s %8s %14s\n",
           "workload", "T_med(us)", "cycles", "insts", "CPI", "IPC", "T_pred(us)");
    printf("%-22s %12s %12s %12s %8s %8s %14s\n",
           "----------------------", "----------", "----------", "----------",
           "------", "------", "----------");

    /* 定义工作负载列表 */
    struct { const char *name; double (*fn_arr)(const double*, size_t);
             uint64_t (*fn_ll)(const node_t*);
             uint64_t (*fn_br)(const uint32_t*, size_t);
             const void *arg1; size_t arg2; int kind; } ws[] = {
        { "array_sum",     w_array_sum,   NULL, NULL,         arr, N, 1 },
        { "linked_list",   NULL, w_linked_list, NULL, nodes, N, 2 },
        { "branchy_random",NULL, NULL, w_branchy,      rand_data, N, 3 },
        { "branchy_predict",NULL, NULL, w_branchy_pred, rand_data, N, 3 },
    };

    pmu_group_t pmu = {0};
    int have_pmu = 1;
    if (pmu_add_hw(&pmu, PERF_COUNT_HW_CPU_CYCLES, "cyc") != 0) have_pmu = 0;
    if (pmu_add_hw(&pmu, PERF_COUNT_HW_INSTRUCTIONS, "ins") != 0) have_pmu = 0;

    for (size_t i = 0; i < sizeof(ws)/sizeof(ws[0]); i++) {
        uint64_t times[REPS], cycs[REPS], instss[REPS];
        /* warmup */
        for (int r = 0; r < 3; r++) {
            if (ws[i].kind == 1) sink((uint64_t)ws[i].fn_arr(ws[i].arg1, ws[i].arg2));
            else if (ws[i].kind == 2) sink(ws[i].fn_ll(ws[i].arg1));
            else sink(ws[i].fn_br(ws[i].arg1, ws[i].arg2));
        }
        for (int r = 0; r < REPS; r++) {
            if (have_pmu) pmu_start(&pmu);
            uint64_t t0 = now_ns();
            uint64_t acc;
            if (ws[i].kind == 1) acc = (uint64_t)ws[i].fn_arr(ws[i].arg1, ws[i].arg2);
            else if (ws[i].kind == 2) acc = ws[i].fn_ll(ws[i].arg1);
            else acc = ws[i].fn_br(ws[i].arg1, ws[i].arg2);
            uint64_t t1 = now_ns();
            if (have_pmu) pmu_stop(&pmu);
            times[r] = t1 - t0;
            if (have_pmu) {
                uint64_t v[PMU_MAX_EVENTS] = {0};
                pmu_read(&pmu, v);
                cycs[r] = v[0];
                instss[r] = v[1];
            }
            sink(acc);
        }
        uint64_t med_t = median_u64(times, REPS);
        uint64_t med_c = have_pmu ? median_u64(cycs, REPS)  : 0;
        uint64_t med_i = have_pmu ? median_u64(instss, REPS): 0;
        double cpi = med_i > 0 ? (double)med_c / (double)med_i : 0;
        double ipc = cpi > 0 ? 1.0/cpi : 0;
        /* Iron Law: Time_pred = IC × CPI × τ = med_c × (1/freq) */
        double t_pred_us = (double)med_c / freq / 1000.0;
        printf("%-22s %12.1f %12llu %12llu %8.2f %8.2f %14.1f\n",
               ws[i].name, (double)med_t / 1000.0,
               (unsigned long long)med_c, (unsigned long long)med_i,
               cpi, ipc, t_pred_us);
    }

    printf("\n== 解读 ==\n");
    printf("  * array_sum: IPC 应该 > 1（向量化 + ILP）\n");
    printf("  * linked_list: IPC 通常 0.2-0.4（每次访存阻塞后续）\n");
    printf("  * branchy_random vs branchy_predict: 看 IPC 差距，反映分支预测收益\n");
    printf("  * T_pred vs T_med: 理论 cycles × (1/freq) 应当 ≈ 实测时间\n");

    if (have_pmu) pmu_close(&pmu);
    free(arr); free(nodes); free(perm); free(rand_data);
    return 0;
}
