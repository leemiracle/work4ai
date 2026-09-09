/* Expert_04_OS_Kernel/src/syscall_bench.c — 测 syscall 真实代价
 *
 * 操作系统专家必测：每个 syscall 多少 ns？哪个 syscall 最贵？
 * 通过 /usr/include/asm-generic/unistd.h 找最简单的 syscall 来测量裸开销。
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <sys/time.h>
#include <sys/stat.h>
#include <time.h>
#include <fcntl.h>

#define N_ITER 1000000

static double now_s(void) {
    struct timespec ts; clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec + ts.tv_nsec / 1e9;
}

int main(void) {
    printf("=== syscall_bench: 飞腾 D3000M 实测各 syscall 代价 ===\n");
    printf("每次测量跑 %d 次取平均\n\n", N_ITER);

    /* —— getpid：最简单的 syscall —— */
    double t0 = now_s();
    for (int i = 0; i < N_ITER; i++) {
        syscall(SYS_getpid);
    }
    double dt = now_s() - t0;
    printf("getpid()       : %6.1f ns/call  (%.0f ops/sec)\n",
           dt * 1e9 / N_ITER, N_ITER / dt);

    /* —— getuid：另一个轻量 syscall —— */
    t0 = now_s();
    for (int i = 0; i < N_ITER; i++) {
        syscall(SYS_getuid);
    }
    dt = now_s() - t0;
    printf("getuid()       : %6.1f ns/call\n", dt * 1e9 / N_ITER);

    /* —— clock_gettime：用户态 vDSO 不进内核 —— */
    struct timespec ts;
    t0 = now_s();
    for (int i = 0; i < N_ITER; i++) {
        clock_gettime(CLOCK_MONOTONIC, &ts);
    }
    dt = now_s() - t0;
    printf("clock_gettime() (vDSO): %4.1f ns/call  ← 不进内核\n",
           dt * 1e9 / N_ITER);

    /* —— read(pipe[0]) EAGAIN：进内核但立即返回 —— */
    int pipefd[2];
    pipe(pipefd);
    fcntl(pipefd[0], F_SETFL, O_NONBLOCK);
    char buf[4];
    t0 = now_s();
    for (int i = 0; i < N_ITER; i++) {
        read(pipefd[0], buf, sizeof(buf));
    }
    dt = now_s() - t0;
    printf("read(EAGAIN)   : %6.1f ns/call\n", dt * 1e9 / N_ITER);

    /* —— stat：会做路径解析，较重（用 libc stat() 函数）—— */
    t0 = now_s();
    for (int i = 0; i < N_ITER / 10; i++) {
        struct stat st;
        stat("/tmp", &st);
    }
    dt = now_s() - t0;
    printf("stat(\"/tmp\")   : %6.1f ns/call  (10× 更重)\n",
           dt * 1e9 / (N_ITER/10));

    close(pipefd[0]);
    close(pipefd[1]);

    printf("\n=== 解读 ===\n");
    printf("- getpid/syscall 基线：约 80-300 ns（飞腾推测 ~150 ns）\n");
    printf("- clock_gettime 是 vDSO（user-space）：~20 ns（不进内核）\n");
    printf("- 每次真实 syscall = 200-500 cycles = ~80-200 ns（飞腾 2.5 GHz）\n");
    printf("- 高 IO 应用优化方向：io_uring / 共享内存 / batching\n");
    return 0;
}
