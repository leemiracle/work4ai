/*
 * 临时测试程序：看哪种 attr 配置在飞腾内核下能工作
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <unistd.h>
#include <signal.h>
#include <sys/syscall.h>
#include <sys/wait.h>
#include <linux/perf_event.h>

static inline int perf_event_open(struct perf_event_attr *hw, pid_t pid, int cpu, int g, unsigned long f) {
    return syscall(__NR_perf_event_open, hw, pid, cpu, g, f);
}

int try_open(const char *label, struct perf_event_attr *pe, pid_t pid, int cpu, int g, unsigned long flags) {
    pe->size = sizeof(*pe);
    pe->type = PERF_TYPE_HARDWARE;
    pe->config = PERF_COUNT_HW_CPU_CYCLES;
    int fd = perf_event_open(pe, pid, cpu, g, flags);
    if (fd < 0) {
        printf("  [%-30s] FAIL: %s\n", label, strerror(errno));
        return -1;
    }
    printf("  [%-30s] OK (fd=%d)\n", label, fd);
    close(fd);
    return 0;
}

int main(void) {
    printf("== attr 配置矩阵测试 ==\n\n");

    /* 1. 完全默认（什么都不设）*/
    struct perf_event_attr pe1 = {0};
    pe1.disabled = 1;
    try_open("default (just disabled=1)", &pe1, 0, -1, -1, 0);

    /* 2. exclude_kernel=1 */
    struct perf_event_attr pe2 = {0};
    pe2.disabled = 1; pe2.exclude_kernel = 1; pe2.exclude_hv = 1;
    try_open("exclude_kernel=1 (我原来的)", &pe2, 0, -1, -1, 0);

    /* 3. exclude_kernel=0 */
    struct perf_event_attr pe3 = {0};
    pe3.disabled = 1; pe3.exclude_kernel = 0; pe3.exclude_hv = 0;
    try_open("exclude_kernel=0", &pe3, 0, -1, -1, 0);

    /* 4. 完全 perf stat 风格 */
    struct perf_event_attr pe4 = {0};
    pe4.disabled = 1;
    pe4.inherit = 1;
    pe4.enable_on_exec = 1;
    pe4.exclude_kernel = 0;
    pe4.exclude_hv = 0;
    pe4.exclude_idle = 0;
    pe4.exclude_guest = 1;
    pe4.read_format = PERF_FORMAT_TOTAL_TIME_ENABLED | PERF_FORMAT_TOTAL_TIME_RUNNING;
    try_open("perf-stat style (with read_format)", &pe4, 0, -1, -1, PERF_FLAG_FD_CLOEXEC);

    /* 5. PERF_FLAG_FD_CLOEXEC 单独 */
    struct perf_event_attr pe5 = {0};
    pe5.disabled = 1;
    try_open("just PERF_FLAG_FD_CLOEXEC", &pe5, 0, -1, -1, PERF_FLAG_FD_CLOEXEC);

    /* 6. 用 child PID 而不是 self */
    pid_t child = fork();
    if (child == 0) {
        sleep(2);
        _exit(0);
    }
    struct perf_event_attr pe6 = {0};
    pe6.disabled = 1;
    pe6.exclude_kernel = 0;
    try_open("attach to child PID", &pe6, child, -1, -1, PERF_FLAG_FD_CLOEXEC);
    kill(child, SIGTERM);

    /* 7. 系统级（cpu != -1）*/
    struct perf_event_attr pe7 = {0};
    pe7.disabled = 1;
    try_open("system-wide (cpu=0)", &pe7, -1, 0, -1, PERF_FLAG_FD_CLOEXEC);

    return 0;
}
