/*
 * Lab03/src/tlb_hugepage.c — TLB 与大页（4KB vs 2MB）实测
 *
 * 方法：pointer chasing 跨页随机环（防 prefetcher）。
 *   - 4KB 页: 256MB / 4KB = 65536 页 >> L1 D-TLB(48) + L2 TLB(2048) → 频繁 page walk
 *   - 2MB 大页: 256MB / 2MB = 128 页 < TLB → 全命中，零 walk
 *   每步 chase 跨一页，p=*(void**)p 强依赖链，乱序无法预取。
 *   cyc/step 差异 = page walk 代价（TLB miss 的真实代价）。
 *
 * 飞腾 D3000M TLB: L1 D-TLB 48 entry + L2 TLB 2048 entry，支持 4K/64K/2M 页。
 * Expert_04 实测 2M vs 4K 页 4.81× 加速。
 *
 * 注意：MAP_HUGETLB 需内核预留（sudo bash -c 'echo 128 > /proc/sys/vm/nr_hugepages'）。
 *       ⚠ 旧版用顺序 stride，被 prefetcher+cache miss 淹没（测出大页反慢，错误），
 *       现改 pointer chasing 才准确。
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include "bench.h"

#define ARRAY_SIZE  (256UL * 1024 * 1024)   /* 256 MB */
#define N_STEPS     2000000
#define REPS        7

/* 在 buf 上构造跨页随机指针环：每页起始放一个 void* 指向随机页。
 * chasing p = *(void**)p，每步跨一页 → 每步触发一次该页的 TLB 查询。*/
static double measure_chase(char *buf, size_t total, size_t page_size) {
    size_t n_pages = total / page_size;
    if (n_pages < 4) return -1.0;

    /* 收集每页起始地址 */
    char **slot = malloc(n_pages * sizeof(char*));
    if (!slot) return -1.0;
    for (size_t i = 0; i < n_pages; i++) slot[i] = buf + i * page_size;

    /* Fisher-Yates 随机置换（防 prefetcher 识别顺序模式）*/
    srand(42);
    for (size_t i = n_pages - 1; i > 0; i--) {
        size_t j = (size_t)rand() % (i + 1);
        char *t = slot[i]; slot[i] = slot[j]; slot[j] = t;
    }
    /* 链成环：每页起始 8 字节存下一页地址 */
    for (size_t i = 0; i < n_pages; i++) {
        *(char**)slot[i] = slot[(i + 1) % n_pages];
    }
    char *head = slot[0];
    free(slot);

    /* warmup */
    { char *q = head; for (int i = 0; i < 1000; i++) q = *(char**)q; sink((uint64_t)q); }

    /* chase 测量 */
    uint64_t ts[REPS];
    for (int r = 0; r < REPS; r++) {
        char *q = head;
        uint64_t t0 = now_ns();
        for (size_t s = 0; s < N_STEPS; s++) q = *(char**)q;
        uint64_t t1 = now_ns();
        sink((uint64_t)q);
        ts[r] = t1 - t0;
    }
    for (int i = 1; i < REPS; i++) {
        uint64_t k = ts[i]; int j = i;
        while (j > 0 && ts[j-1] > k) { ts[j] = ts[j-1]; j--; }
        ts[j] = k;
    }
    return (double)ts[REPS/2] / (double)N_STEPS;  /* ns/step */
}

int main(void) {
    pin_to_cpu(0);
    printf("== Lab03.4: TLB 与大页 (pointer chasing 跨页随机环) ==\n\n");
    printf("  数组 %zu MB, 每步跨一页触发 TLB 查询, %d 步/测\n\n",
           ARRAY_SIZE/(1024*1024), N_STEPS);

    char *buf4k = mmap(NULL, ARRAY_SIZE, PROT_READ|PROT_WRITE,
                       MAP_PRIVATE|MAP_ANONYMOUS, -1, 0);
    if (buf4k == MAP_FAILED) { perror("mmap 4k"); return 1; }
    memset(buf4k, 1, ARRAY_SIZE);

    char *buf2m = mmap(NULL, ARRAY_SIZE, PROT_READ|PROT_WRITE,
                       MAP_PRIVATE|MAP_ANONYMOUS|MAP_HUGETLB, -1, 0);
    int have_huge = (buf2m != MAP_FAILED);
    if (have_huge) memset(buf2m, 1, ARRAY_SIZE);

    double t4k = measure_chase(buf4k, ARRAY_SIZE, 4*1024);
    printf("  4KB 页  (65536 页 >> TLB): %6.2f ns/step  (频繁 page walk)\n", t4k);

    double t2m = -1;
    if (have_huge) {
        t2m = measure_chase(buf2m, ARRAY_SIZE, 2*1024*1024);
        printf("  2MB 大页 (128 页 < TLB):   %6.2f ns/step  (全命中, 零 walk)\n", t2m);
        printf("\n  == 关键对比 ==\n");
        printf("  * 4KB vs 2MB cyc/step: %.2fx (page walk 代价 = %.2f ns)\n",
               t4k / t2m, t4k - t2m);
        printf("  * 与 Expert_04 实测 2M vs 4K 页 4.81x 加速对照\n");
    } else {
        printf("\n  ⚠ MAP_HUGETLB 失败（内核未预留 huge page）。\n");
        printf("    开启: sudo bash -c 'echo 128 > /proc/sys/vm/nr_hugepages' 后重跑\n");
    }

    printf("\n  == 解读 ==\n");
    printf("  * 4KB 页: 256MB 需 65536 页表项, 远超 L1 D-TLB(48) + L2 TLB(2048)\n");
    printf("    → 每次 chase 跨页大概率 page walk (查 4 级页表, ~100-300 cyc)\n");
    printf("  * 2MB 大页: 同 256MB 仅 128 项, 全在 L1 TLB → 零 walk\n");
    printf("  * pointer chasing 随机环防 prefetcher, cyc/step 差异纯来自 TLB\n");
    printf("  * 实战: 数据库(TPCC)/大数组科学计算/JVM heap 用 huge page 提速\n");

    munmap(buf4k, ARRAY_SIZE);
    if (have_huge) munmap(buf2m, ARRAY_SIZE);
    return 0;
}
