/* Expert_04_OS_Kernel/src/tlb_cost.c — 测 TLB miss 的代价
 *
 * 操作系统专家的关键知识：4K 页 vs 2M 大页，TLB miss 差多少？
 *
 * 实验设计：随机访问 N 个页（确保 TLB 满了），测每次访问延迟。
 *   - 4K 页：访问 4 KB × N（很快 TLB 满）
 *   - 2M 页：访问 2 MB × N（同样的页数，地址空间大很多）
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <sys/mman.h>
#include <malloc.h>

#define PAGE_4K  (4 * 1024)
#define PAGE_2M  (2 * 1024 * 1024)

static double now_s(void) {
    struct timespec ts; clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec + ts.tv_nsec / 1e9;
}

/* 随机访问 stride 个 page，每个 page 一次读 */
static double bench_random_access(char *base, int n_pages, int page_size, int iters) {
    /* 准备随机 page index */
    int *idx = malloc(n_pages * sizeof(int));
    for (int i = 0; i < n_pages; i++) idx[i] = i;
    srand(42);
    for (int i = n_pages - 1; i > 0; i--) {
        int j = rand() % (i + 1);
        int t = idx[i]; idx[i] = idx[j]; idx[j] = t;
    }
    /* 先 touch 所有页（避免首次访问的 minor fault）*/
    volatile char v_sink = 0;
    for (int i = 0; i < n_pages; i++) v_sink ^= base[idx[i] * page_size];
    (void)v_sink;

    double t0 = now_s();
    volatile long sink = 0;   // volatile 防止 DCE
    long sum = 0;
    for (int it = 0; it < iters; it++) {
        for (int i = 0; i < n_pages; i++) {
            sum += base[idx[i] * page_size];
        }
    }
    sink ^= sum;
    double dt = now_s() - t0;
    free(idx);
    (void)sink;
    return dt / (iters * n_pages) * 1e9;   // ns per access
}

int main(void) {
    printf("=== tlb_cost: 4K vs 2M 页的随机访问延迟 ===\n");
    printf("TLB 越满，每次访问的 page walk 代价越大\n\n");

    /* 4K 页：分配 4096 个 4K 页 = 16 MB（远超 L2 + L3 TLB 容量）*/
    int n4k = 4096;
    char *base4k = memalign(PAGE_4K, n4k * PAGE_4K);
    memset(base4k, 1, n4k * PAGE_4K);

    /* 2M 页：用 mmap + MAP_HUGETLB */
    int n2m = 32;   // 64 MB
    char *base2m = mmap(NULL, n2m * PAGE_2M, PROT_READ | PROT_WRITE,
                        MAP_PRIVATE | MAP_ANONYMOUS | MAP_HUGETLB, -1, 0);
    if (base2m == MAP_FAILED) {
        base2m = memalign(PAGE_2M, n2m * PAGE_2M);   // fallback
        memset(base2m, 1, n2m * PAGE_2M);
    } else {
        memset(base2m, 1, n2m * PAGE_2M);
    }

    double t_4k = bench_random_access(base4k, n4k, PAGE_4K, 100);
    double t_2m = bench_random_access(base2m, n2m, PAGE_2M, 100);

    printf("配置                      ns/access   备注\n");
    printf("---                       ---------   ----\n");
    printf("4K 页 × %d 页 (%.0f MB)    %.1f ns     TLB 满载\n",
           n4k, (double)n4k * PAGE_4K / 1024 / 1024, t_4k);
    printf("2M 页 × %d 页 (%.0f MB)    %.1f ns     TLB 宽松\n",
           n2m, (double)n2m * PAGE_2M / 1024 / 1024, t_2m);
    printf("\n加速比（2M vs 4K）：%.2fx\n", t_4k / t_2m);
    printf("\n=== 解读 ===\n");
    printf("- 飞腾 D3000M L1 DTLB 48 entry + L2 TLB 2048 entry\n");
    printf("- 4K 页 × 4096 个 → 远超 L2 TLB 容量，每次访问 page walk\n");
    printf("- 2M 大页 × 32 个 → 仅 32 entry，全部装 L1 DTLB\n");
    printf("- 实际数据库/LLM 推理应用启用 THP 通常 +5-15%% 性能\n");

    free(base4k);
    munmap(base2m, n2m * PAGE_2M);
    return 0;
}
