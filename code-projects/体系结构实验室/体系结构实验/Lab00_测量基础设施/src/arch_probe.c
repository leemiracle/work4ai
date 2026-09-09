/*
 * Lab00/src/arch_probe.c — 飞腾 D3000 架构实测探测
 *
 * 输出 CPU / Cache / NUMA / PMU 全套关键参数。
 * 不抄手册——所有数字都是当时当地实测的。
 *
 * 用法: ./arch_probe
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <ctype.h>
#include <unistd.h>
#include <fcntl.h>
#include <dirent.h>
#include <sys/utsname.h>

#include "pmu.h"

/* ---------- 小工具：读 /sys/devices/ 下某个文件第一行 ---------- */
static int sysfs_read(const char *path, char *buf, size_t bufsz) {
    int fd = open(path, O_RDONLY);
    if (fd < 0) return -1;
    ssize_t n = read(fd, buf, bufsz - 1);
    close(fd);
    if (n <= 0) return -1;
    buf[n] = 0;
    /* 去掉末尾换行 */
    while (n > 0 && (buf[n-1] == '\n' || buf[n-1] == ' ')) buf[--n] = 0;
    return 0;
}

/* ---------- CPU 信息 ---------- */
static void probe_cpu(void) {
    printf("== CPU ==\n");

    char buf[256];

    /* 实现者 + partnum（MIDR_EL1） */
    if (sysfs_read("/sys/devices/system/cpu/cpu0/regs/identification/midr_el1",
                   buf, sizeof(buf)) == 0) {
        unsigned long midr = strtoul(buf, NULL, 16);
        unsigned impl = (midr >> 24) & 0xFF;
        unsigned var  = (midr >> 20) & 0x0F;
        unsigned arch = (midr >> 16) & 0x0F;
        unsigned part = (midr >> 4)  & 0xFFF;
        unsigned rev  = midr & 0xF;
        const char *impl_name = "(unknown)";
        const char *part_name = "(unknown)";
        if (impl == 0x70) {
            impl_name = "Phytium";
            if (part == 0x663) part_name = "FTC663 (D3000)";
            else if (part == 0x862) part_name = "FTC862 (D3000M)";
            else if (part == 0x860) part_name = "FTC860";
        } else if (impl == 0x41) {
            impl_name = "ARM";
            if (part == 0xd0c) part_name = "Neoverse N1";
            else if (part == 0xd49) part_name = "Neoverse N2";
            else if (part == 0xd40) part_name = "Neoverse V1";
        } else if (impl == 0x48) impl_name = "HiSilicon";

        printf("  midr_el1 = 0x%016lx\n", midr);
        printf("  implementer = 0x%02X (%s)\n", impl, impl_name);
        printf("  part        = 0x%03X (%s)\n", part, part_name);
        printf("  variant/rev = %d/%d\n", var, rev);
        printf("  arch ver    = ARMv%d\n", arch + 4);
    }

    /* 核数 / 在线 */
    long ncpu_online = sysconf(_SC_NPROCESSORS_ONLN);
    long ncpu_conf   = sysconf(_SC_NPROCESSORS_CONF);
    printf("  cores online = %ld / configured = %ld\n", ncpu_online, ncpu_conf);

    /* 频率 */
    char path[256];
    snprintf(path, sizeof(path),
             "/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq");
    if (sysfs_read(path, buf, sizeof(buf)) == 0) {
        printf("  freq_cur = %s kHz\n", buf);
    }
    snprintf(path, sizeof(path),
             "/sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq");
    if (sysfs_read(path, buf, sizeof(buf)) == 0) {
        printf("  freq_max = %s kHz\n", buf);
    }
    snprintf(path, sizeof(path),
             "/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor");
    if (sysfs_read(path, buf, sizeof(buf)) == 0) {
        printf("  governor = %s\n", buf);
    }

    /* SMT/Threads */
    if (sysfs_read("/sys/devices/system/cpu/smt/active", buf, sizeof(buf)) == 0) {
        printf("  smt_active = %s\n", buf);
    }

    /* 内核版本 */
    struct utsname uts;
    if (uname(&uts) == 0) {
        printf("  kernel = %s %s\n", uts.release, uts.machine);
    }
    printf("\n");
}

/* ---------- Cache 层级 ---------- */
static void probe_caches(void) {
    printf("== Caches ==\n");

    /* 每个 index 几个目录: /sys/devices/system/cpu/cpu0/cache/index0..N */
    for (int idx = 0; idx < 8; idx++) {
        char base[256];
        snprintf(base, sizeof(base),
                 "/sys/devices/system/cpu/cpu0/cache/index%d", idx);
        DIR *d = opendir(base);
        if (!d) break;
        closedir(d);

        char buf[256], path[512];
        const char *type = "?", *level = "?", *shared = "?";
        long size = 0, ways = 0, line = 0, sets = 0;

        snprintf(path, sizeof(path), "%s/type", base);
        if (sysfs_read(path, buf, sizeof(buf)) == 0) type = buf;

        snprintf(path, sizeof(path), "%s/level", base);
        if (sysfs_read(path, buf, sizeof(buf)) == 0) level = buf;

        snprintf(path, sizeof(path), "%s/size", base);
        if (sysfs_read(path, buf, sizeof(buf)) == 0)
            sscanf(buf, "%ldK", &size);  /* e.g. "64K" */

        snprintf(path, sizeof(path), "%s/ways_of_associativity", base);
        if (sysfs_read(path, buf, sizeof(buf)) == 0) ways = atol(buf);

        snprintf(path, sizeof(path), "%s/coherency_line_size", base);
        if (sysfs_read(path, buf, sizeof(buf)) == 0) line = atol(buf);

        snprintf(path, sizeof(path), "%s/number_of_sets", base);
        if (sysfs_read(path, buf, sizeof(buf)) == 0) sets = atol(buf);

        snprintf(path, sizeof(path), "%s/shared_cpu_list", base);
        if (sysfs_read(path, buf, sizeof(buf)) == 0)
            shared = (strchr(buf, '-') || strchr(buf, ','))
                     ? "shared" : "private";

        printf("  L%s %s: size=%3ldK ways=%2ld line=%2ld sets=%5ld  (%s)\n",
               level, type, size, ways, line, sets, shared);
    }
    printf("\n");
}

/* ---------- NUMA ---------- */
static void probe_numa(void) {
    printf("== NUMA ==\n");
    DIR *d = opendir("/sys/devices/system/node");
    if (!d) { printf("  (no NUMA info)\n\n"); return; }

    struct dirent *e;
    int n_nodes = 0;
    while ((e = readdir(d))) {
        if (strncmp(e->d_name, "node", 4) != 0) continue;
        if (!isdigit(e->d_name[4])) continue;
        char base[256];
        snprintf(base, sizeof(base), "/sys/devices/system/node/%s", e->d_name);
        char path[300], buf[256];

        snprintf(path, sizeof(path), "%s/cpulist", base);
        if (sysfs_read(path, buf, sizeof(buf)) == 0)
            printf("  %s cpus: %s\n", e->d_name, buf);

        snprintf(path, sizeof(path), "%s/meminfo", base);
        int fd = open(path, O_RDONLY);
        if (fd >= 0) {
            char membuf[4096];
            ssize_t n = read(fd, membuf, sizeof(membuf)-1);
            close(fd);
            if (n > 0) {
                membuf[n] = 0;
                /* 抽取 MemTotal 和 MemFree 行 */
                char *p = membuf;
                while (*p) {
                    char *nl = strchr(p, '\n');
                    if (nl) *nl = 0;
                    if (strstr(p, "MemTotal:") || strstr(p, "MemFree:"))
                        printf("    %s\n", p);
                    if (!nl) break;
                    p = nl + 1;
                }
            }
        }
        n_nodes++;
    }
    closedir(d);
    printf("  total NUMA nodes: %d\n\n", n_nodes);
}

/* ---------- PMU 可用性 ---------- */
static void probe_pmu(void) {
    printf("== PMU sanity ==\n");
    struct {
        uint32_t hw_id; const char *name;
    } hw_tests[] = {
        { PERF_COUNT_HW_CPU_CYCLES,         "PERF_COUNT_HW_CPU_CYCLES" },
        { PERF_COUNT_HW_INSTRUCTIONS,       "PERF_COUNT_HW_INSTRUCTIONS" },
        { PERF_COUNT_HW_CACHE_REFERENCES,   "PERF_COUNT_HW_CACHE_REFERENCES" },
        { PERF_COUNT_HW_CACHE_MISSES,       "PERF_COUNT_HW_CACHE_MISSES" },
        { PERF_COUNT_HW_BRANCH_INSTRUCTIONS,"PERF_COUNT_HW_BRANCH_INSTRUCTIONS" },
        { PERF_COUNT_HW_BRANCH_MISSES,      "PERF_COUNT_HW_BRANCH_MISSES" },
    };
    for (size_t i = 0; i < sizeof(hw_tests)/sizeof(hw_tests[0]); i++) {
        pmu_group_t g = {0};
        if (pmu_add_hw(&g, hw_tests[i].hw_id, hw_tests[i].name) == 0) {
            printf("  %-32s OK\n", hw_tests[i].name);
            pmu_close(&g);
        } else {
            printf("  %-32s FAIL\n", hw_tests[i].name);
        }
    }

    /* 飞腾 raw 事件码测试 */
    struct { uint64_t code; const char *name; } raw_tests[] = {
        { FTC_L1D_CACHE_REFILL,   "RAW(0x03 L1D_CACHE_REFILL)" },
        { FTC_L1D_CACHE,          "RAW(0x04 L1D_CACHE)" },
        { FTC_L2D_CACHE_REFILL,   "RAW(0x17 L2D_CACHE_REFILL)" },
        { FTC_BR_MIS_PRED,        "RAW(0x10 BR_MIS_PRED)" },
        { FTC_BR_PRED,            "RAW(0x12 BR_PRED)" },
        { FTC_STALL_FRONTEND,     "RAW(0x23 STALL_FRONTEND)" },
        { FTC_STALL_BACKEND,      "RAW(0x24 STALL_BACKEND)" },
        { FTC_ASE_SPEC,           "RAW(0x74 ASE_SPEC/NEON)" },
    };
    for (size_t i = 0; i < sizeof(raw_tests)/sizeof(raw_tests[0]); i++) {
        pmu_group_t g = {0};
        if (pmu_add_raw(&g, raw_tests[i].code, raw_tests[i].name) == 0) {
            printf("  %-32s OK\n", raw_tests[i].name);
            pmu_close(&g);
        } else {
            printf("  %-32s FAIL\n", raw_tests[i].name);
        }
    }
    printf("\n");
}

/* ---------- perf / tools ---------- */
static void probe_tools(void) {
    printf("== Tooling ==\n");
    const char *tools[] = {
        "perf", "taskset", "numactl", "numastat", "lscpu", "lspcu",
        "gcc", "kpgcc", "clang", "objdump", "linux64"
    };
    char buf[256];
    for (size_t i = 0; i < sizeof(tools)/sizeof(tools[0]); i++) {
        snprintf(buf, sizeof(buf), "which %s 2>/dev/null", tools[i]);
        FILE *fp = popen(buf, "r");
        if (fp) {
            if (fgets(buf, sizeof(buf), fp)) {
                /* 去掉末尾换行 */
                buf[strlen(buf)-1] = 0;
                printf("  %-12s -> %s\n", tools[i], buf);
            } else {
                printf("  %-12s -> (not found)\n", tools[i]);
            }
            pclose(fp);
        }
    }
    printf("\n");
}

/* ---------- 入口 ---------- */
int main(void) {
    printf("================================\n");
    printf("  arch_probe — 飞腾体系结构实测\n");
    printf("================================\n\n");

    probe_cpu();
    probe_caches();
    probe_numa();
    probe_pmu();
    probe_tools();

    printf("== Hints ==\n");
    printf("  - 跑 Lab00 实验前，建议把 governor 切到 performance：\n");
    printf("      sudo cpupower frequency-set -g performance\n");
    printf("  - 绑核 CPU 0：\n");
    printf("      taskset -c 0 ./your_app\n");
    printf("  - 查看飞腾 PMU 完整事件码：\n");
    printf("      /opt/phytune/pt_agent/.../topdown_tool/metrics/phytium-ftc862.json\n");
    return 0;
}
