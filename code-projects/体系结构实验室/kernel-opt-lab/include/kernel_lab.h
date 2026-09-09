/* ============================================================================
 * kernel_lab.h — Kernel-Lab 统一 C ABI（v0.9 P0，落地应用集成专家建议）
 *
 * 历史：v0.8 之前所有 kernel 都是 static + main()，无法被外部链接
 *      v0.9 引入此 header + libkernel_lab.so，从"实验室"到"库"的第一步
 *
 * 设计原则：
 *   - extern "C" 兼容 C++/pybind11/ctypes
 *   - void* + dtype enum 支持 FP32/FP16/INT8/BF16 多精度
 *   - lda/ldb/ldc leading dim 支持 strided tensor（PyTorch/NumPy 兼容）
 *   - kl_status_t 返回码，NULL/维度不合法返回 KL_EINVAL
 *   - KL_API_VERSION 锁 ABI，未来按 semver 升级
 *
 * 使用：
 *   #include "kernel_lab.h"
 *   kl_gemm(KL_F32, A, B, C, 1024, 1024, 1024, 1024, 1024, 1024, 4);
 *
 * 编译库：
 *   make lib  # 产出 lib/libkernel_lab.so + lib/libkernel_lab.a
 * ============================================================================ */
#ifndef KERNEL_LAB_H
#define KERNEL_LAB_H

#include <stdint.h>
#include <stddef.h>   /* size_t */
#include <stdlib.h>   /* malloc/calloc/posix_memalign/exit */
#include <stdio.h>    /* perror */

#ifdef __cplusplus
extern "C" {
#endif

/* === 版本 === */
#define KL_API_VERSION_MAJOR 1
#define KL_API_VERSION_MINOR 0
#define KL_API_VERSION       ((KL_API_VERSION_MAJOR << 8) | KL_API_VERSION_MINOR)

/* === 数据类型 === */
typedef enum {
    KL_F32 = 0,   /* 32-bit float（默认）*/
    KL_F16 = 1,   /* 16-bit float（半精度）*/
    KL_S8  = 2,   /* 8-bit int（量化，输出 int32 累加器）*/
    KL_BF16 = 3,  /* 16-bit brain float（LLM 标准，v0.10 待实现）*/
} kl_dtype_t;

/* === 返回码 === */
typedef enum {
    KL_OK      =  0,   /* 成功 */
    KL_EINVAL  = -1,   /* 参数非法（NULL 指针、维度 ≤ 0、K%4≠0 等）*/
    KL_OOM     = -2,   /* 内部分配失败 */
    KL_UNSUP   = -3,   /* 不支持的 dtype/配置 */
} kl_status_t;

/* === 内存布局 === */
typedef enum {
    KL_ROW_MAJOR = 0,  /* C 行主序（默认，匹配 C/PyTorch）*/
    KL_COL_MAJOR = 1,  /* Fortran 列主序（部分 BLAS 兼容）*/
} kl_layout_t;

/* ============================================================================
 * GEMM: C = A × B
 *   A: [M, K], B: [K, N], C: [M, N]
 *   lda/ldb/ldc: leading dimension（支持 strided tensor，0 = 紧凑）
 *   nthreads: OpenMP 线程数（0/1 = 单核）
 * ============================================================================ */
kl_status_t kl_gemm(kl_dtype_t dt,
                    const void *A, const void *B, void *C,
                    int M, int N, int K,
                    int lda, int ldb, int ldc,
                    int nthreads);

/* 便捷宏：紧凑布局（无 stride）*/
#define kl_gemm_dense(dt, A, B, C, M, N, K, nt) \
    kl_gemm((dt), (A), (B), (C), (M), (N), (K), (K), (N), (N), (nt))

/* ============================================================================
 * 卷积（v0.10 待实现，占位声明）
 *   input: [N][H][W][CIN] row-major NHWC
 *   weight: [KH][KW][CIN][COUT]
 *   output: [N][H][W][COUT]（stride=1, pad=1 假设）
 * ============================================================================ */
kl_status_t kl_conv2d_3x3(kl_dtype_t dt,
                          const void *input, const void *weight, void *output,
                          int H, int W, int CIN, int COUT,
                          const char *algo);  /* "winograd_f22" | "winograd_f44" | "im2col" | "direct" */

/* ============================================================================
 * Flash Attention（v0.10 待实现）
 *   Q/K/V: [N, head_dim], output: [N, head_dim]
 * ============================================================================ */
kl_status_t kl_attention(kl_dtype_t dt,
                         const void *Q, const void *K, const void *V, void *O,
                         int N, int head_dim,
                         int is_causal,    /* 1 = 因果 mask */
                         int nthreads);

/* === 工具 === */
const char *kl_status_str(kl_status_t s);  /* 错误码 → 字符串 */
const char *kl_version(void);               /* "kernel-lab v0.9, API 1.0" */

/* ============================================================================
 * P0-3 安全包装：malloc/calloc/posix_memalign 失败即 perror+exit(12)
 * （OOM 不静默 NULL 解引用；库内部与外部均可直接使用）
 * ============================================================================ */
static inline void* kl_xmalloc(size_t n) {
    void *p = malloc(n);
    if (!p) { perror("kl_xmalloc OOM"); exit(12); }
    return p;
}
static inline void* kl_xcalloc(size_t n, size_t sz) {
    void *p = calloc(n, sz);
    if (!p) { perror("kl_xcalloc OOM"); exit(12); }
    return p;
}
static inline int kl_xposix_memalign(void **p, size_t align, size_t n) {
    int r = posix_memalign(p, align, n);
    if (r || !*p) { perror("kl_xposix_memalign OOM"); exit(12); }
    return r;
}

#ifdef __cplusplus
}
#endif

#endif /* KERNEL_LAB_H */
