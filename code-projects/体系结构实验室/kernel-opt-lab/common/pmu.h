/*
 * common/pmu.h — perf_event_open 简易包装（直接读 PMU 硬件计数器）
 *
 * 为什么不用 perf stat 命令行？
 *   - 命令行 perf stat 启动有开销，且采集的是"整个进程"
 *   - 我们常常想"只测 hot loop 这一段"——所以需要编程式 API
 *
 * 飞腾 D3000 (FTC862/FTC663) 支持的事件示例：
 *   PERF_COUNT_HW_CPU_CYCLES              (cycles)
 *   PERF_COUNT_HW_INSTRUCTIONS            (instructions)
 *   PERF_COUNT_HW_CACHE_REFERENCES        (cache-refs)
 *   PERF_COUNT_HW_CACHE_MISSES            (cache-misses)
 *   PERF_COUNT_HW_BRANCH_INSTRUCTIONS     (branches)
 *   PERF_COUNT_HW_BRANCH_MISSES           (branch-misses)
 *
 * 详细事件名（飞腾自定义）见 PhyTune 文档：
 *   /opt/phytune/pt_agent/.../topdown_tool/metrics/phytium-ftc862.json
 */
#ifndef PMU_H
#define PMU_H

#include <linux/perf_event.h>
#include <sys/syscall.h>
#include <sys/ioctl.h>
#include <unistd.h>
#include <string.h>
#include <stdio.h>
#include <errno.h>

/* 一组事件（最多 8 个，飞腾硬件 PMU 通常只允许 6 个同时计数，
 * 多出来的会被 multiplexing，但 syscall 仍会成功，需自行注意 scaling）
 */
#define PMU_MAX_EVENTS 8

typedef struct {
    int           fds[PMU_MAX_EVENTS];
    size_t        n;
    const char   *names[PMU_MAX_EVENTS];  /* 仅用于打印 */
} pmu_group_t;

/* 内核 perf_event_open 系统调用（glibc 没有封装，需手动 syscall） */
static inline int perf_event_open(struct perf_event_attr *hw_event,
                                  pid_t pid, int cpu, int group_fd,
                                  unsigned long flags) {
    return syscall(__NR_perf_event_open, hw_event, pid, cpu, group_fd, flags);
}

/* 添加一个 hardware 通用事件（PERF_COUNT_HW_*） */
static inline int pmu_add_hw(pmu_group_t *g, uint32_t hw_id, const char *name) {
    if (g->n >= PMU_MAX_EVENTS) return -1;
    struct perf_event_attr pe;
    memset(&pe, 0, sizeof(pe));
    pe.size = sizeof(pe);
    pe.type = PERF_TYPE_HARDWARE;
    pe.config = hw_id;
    pe.disabled = 1;          /* 创建时先 disable */
    /* 注意: exclude_idle 只在 system-wide 模式 (cpu!=-1) 才有意义，
     * 在 attach-to-task 模式 (pid>=0, cpu=-1) 下设置可能被某些内核
     * （如飞腾/麒麟 5.4）拒绝返回 ENOTSUP，故此处不设。 */
    pe.exclude_kernel = 1;
    pe.exclude_hv = 1;

    int fd = perf_event_open(&pe, 0, -1,
                             g->n == 0 ? -1 : g->fds[0],
                             PERF_FLAG_FD_CLOEXEC);
    if (fd < 0) {
        fprintf(stderr, "pmu_add_hw(%s) failed: %s\n",
                name, strerror(errno));
        return -1;
    }
    g->fds[g->n] = fd;
    g->names[g->n] = name;
    g->n++;
    return 0;
}

/* 添加一个 raw 事件（飞腾 PMU 事件码，如 0x0003=L1D_CACHE_REFILL） */
static inline int pmu_add_raw(pmu_group_t *g, uint64_t raw_code, const char *name) {
    if (g->n >= PMU_MAX_EVENTS) return -1;
    struct perf_event_attr pe;
    memset(&pe, 0, sizeof(pe));
    pe.size = sizeof(pe);
    pe.type = PERF_TYPE_RAW;
    pe.config = raw_code;
    pe.disabled = 1;
    pe.exclude_kernel = 1;
    pe.exclude_hv = 1;

    int fd = perf_event_open(&pe, 0, -1,
                             g->n == 0 ? -1 : g->fds[0],
                             PERF_FLAG_FD_CLOEXEC);
    if (fd < 0) {
        fprintf(stderr, "pmu_add_raw(%s, 0x%04lx) failed: %s\n",
                name, (unsigned long)raw_code, strerror(errno));
        return -1;
    }
    g->fds[g->n] = fd;
    g->names[g->n] = name;
    g->n++;
    return 0;
}

/* 启用整组事件（reset + enable） */
static inline void pmu_start(pmu_group_t *g) {
    if (g->n == 0) return;
    ioctl(g->fds[0], PERF_EVENT_IOC_RESET, PERF_IOC_FLAG_GROUP);
    ioctl(g->fds[0], PERF_EVENT_IOC_ENABLE, PERF_IOC_FLAG_GROUP);
}

/* 停止整组事件 */
static inline void pmu_stop(pmu_group_t *g) {
    if (g->n == 0) return;
    ioctl(g->fds[0], PERF_EVENT_IOC_DISABLE, PERF_IOC_FLAG_GROUP);
}

/* 读取整组事件（返回 values 数组，调用方分配至少 g->n 个 uint64_t） */
static inline int pmu_read(pmu_group_t *g, uint64_t *values) {
    /* 每个事件读出一个 8 字节计数；group 模式下用 readn 格式更准，
     * 但简化起见，逐个读 leader-only scaling 略有偏差——
     * 对教学实验足够；严谨场景请用 PERF_FORMAT_GROUP
     */
    for (size_t i = 0; i < g->n; i++) {
        uint64_t v = 0;
        if (read(g->fds[i], &v, sizeof(v)) != sizeof(v)) {
            return -1;
        }
        values[i] = v;
    }
    return 0;
}

/* 关闭整组 */
static inline void pmu_close(pmu_group_t *g) {
    for (size_t i = 0; i < g->n; i++) {
        if (g->fds[i] >= 0) close(g->fds[i]);
        g->fds[i] = -1;
    }
    g->n = 0;
}

/* 打印结果（一行） */
static inline void pmu_print(pmu_group_t *g, uint64_t *values) {
    for (size_t i = 0; i < g->n; i++) {
        printf("%s=%-12lu ", g->names[i], values[i]);
    }
    printf("\n");
}

/* ============================================================ */
/* 飞腾常用事件常量（来自 PMU 手册 + PhyTune 模板）             */
/* ============================================================ */

#define FTC_L1D_CACHE          0x0004   /* L1 数据缓存访问 */
#define FTC_L1D_CACHE_REFILL   0x0003   /* L1 数据缓存未命中 */
#define FTC_L1I_CACHE_REFILL   0x0001
#define FTC_L2D_CACHE          0x0016
#define FTC_L2D_CACHE_REFILL   0x0017
#define FTC_BR_PRED            0x0012
#define FTC_BR_MIS_PRED        0x0010
#define FTC_STALL_FRONTEND     0x0023
#define FTC_STALL_BACKEND      0x0024
#define FTC_L1D_TLB_REFILL     0x0005
#define FTC_DTLB_WALK          0x0034
#define FTC_LD_SPEC            0x0070
#define FTC_ST_SPEC            0x0071
#define FTC_ASE_SPEC           0x0074   /* NEON/SIMD */
#define FTC_INST_RETIRED       0x0008   /* 注意：在 hardware 通用里也能用 PERF_COUNT_HW_INSTRUCTIONS */
#define FTC_BUS_ACCESS         0x0019
#define FTC_REMOTE_ACCESS      0x0031

#endif /* PMU_H */
