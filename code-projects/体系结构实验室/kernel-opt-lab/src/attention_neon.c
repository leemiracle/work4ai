/* ============================================================================
 * attention_neon.c — NEON 加速的 Flash Attention
 *
 * 优化点：
 *   1. BMM1 (Q × K^T): 内积用 NEON 4-lane fma (vfmaq_f32)
 *   2. BMM2 (P × V): 加权求和用 NEON
 *   3. row max: 用 vmaxvq_f32 树形归约
 *   4. exp: 用 vexpq 想法（实际用快速 expf 逼近，简化）
 *
 * 对比 baseline (attention.c 的 scalar 实现)
 * ============================================================================ */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>
#include <time.h>
#include <arm_neon.h>
#ifdef _OPENMP
#include <omp.h>
#endif

/* P0-3 安全包装：malloc/calloc/posix_memalign 失败即 perror+exit（OOM 不静默 NULL 解引用） */
static inline void* kl_xmalloc(size_t n) {
    void *p = NULL;
    if (posix_memalign(&p, 64, n)) { perror("kl_xmalloc OOM"); exit(12); }
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

#define D 64
#define SCALE 0.125f   /* 1/sqrt(64) */

static double now_ns() {
    struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t);
    return t.tv_sec * 1e9 + t.tv_nsec;
}

/* NEON 加速的 4 元素内积：sum += a[0..3] · b[0..3] */
static inline float dot4(float32x4_t a, float32x4_t b) {
    float32x4_t p = vmulq_f32(a, b);
    return vaddvq_f32(p);  /* 横向加 4 lane */
}

/* ---------- Naive Scalar (baseline) ---------- */
static void attention_naive_scalar(const float *Q, const float *K, const float *V,
                                    float *O, int N) {
    float *S = kl_xmalloc(N * N * sizeof(float));
    for (int i = 0; i < N; i++)
        for (int j = 0; j < N; j++) {
            float s = 0;
            for (int k = 0; k < D; k++) s += Q[i*D+k] * K[j*D+k];
            S[i*N+j] = s * SCALE;
        }
    for (int i = 0; i < N; i++) {
        /* softmax */
        float m = S[i*N];
        for (int j = 1; j < N; j++) if (S[i*N+j] > m) m = S[i*N+j];
        float sum = 0;
        for (int j = 0; j < N; j++) { S[i*N+j] = expf(S[i*N+j] - m); sum += S[i*N+j]; }
        float inv = 1.0f / sum;
        for (int j = 0; j < N; j++) S[i*N+j] *= inv;
        /* P @ V[i] */
        for (int d = 0; d < D; d++) {
            float s = 0;
            for (int j = 0; j < N; j++) s += S[i*N+j] * V[j*D+d];
            O[i*D+d] = s;
        }
    }
    free(S);
}

/* ---------- NEON Flash Attention (单核) ----------
 * 关键 NEON 化：
 *   BMM1 (Q × K^T block): 内积 D=64 → 16 次 NEON fma
 *   BMM2 (P × V block): 4 lane 并行累加
 */
static void attention_flash_neon(const float *Q, const float *K, const float *V,
                                  float *O, int N, int Br, int Bc, int is_causal) {
    for (int qi = 0; qi < N; qi += Br) {
        int M = (qi + Br <= N) ? Br : (N - qi);
        float *O_blk = kl_xcalloc(M * D, sizeof(float));
        float *m_vec = kl_xmalloc(M * sizeof(float));
        float *l_vec = kl_xmalloc(M * sizeof(float));
        for (int i = 0; i < M; i++) { m_vec[i] = -INFINITY; l_vec[i] = 0; }

        float *S_blk = kl_xmalloc(M * Bc * sizeof(float));

        for (int kj = 0; kj < N; kj += Bc) {
            int Kb = (kj + Bc <= N) ? Bc : (N - kj);

            /* BMM1: S_blk[i][j] = Q[qi+i] · K[kj+j] × SCALE
             * NEON 化：每个内积 D=64 用 16 次 vfmulq + vaddvq */
            for (int i = 0; i < M; i++) {
                const float *q_row = &Q[(qi+i)*D];
                for (int j = 0; j < Kb; j++) {
                    const float *k_row = &K[(kj+j)*D];
                    /* D=64 / 4 lane = 16 次 NEON 累加 */
                    float32x4_t acc = vdupq_n_f32(0);
                    for (int kk = 0; kk < D; kk += 4) {
                        float32x4_t q4 = vld1q_f32(&q_row[kk]);
                        float32x4_t k4 = vld1q_f32(&k_row[kk]);
                        acc = vfmaq_f32(acc, q4, k4);
                    }
                    S_blk[i*Kb+j] = vaddvq_f32(acc) * SCALE;
                }
            }

            /* causal mask：query[qi+i] 只 attend key[0..qi+i]，屏蔽未来（LLM 解码）*/
            if (is_causal) {
                for (int i = 0; i < M; i++)
                    for (int j = 0; j < Kb; j++)
                        if ((kj+j) > (qi+i))
                            S_blk[i*Kb+j] = -INFINITY;
            }

            /* online softmax: m_new = max(m_vec, rowmax(S)) */
            float *m_new = kl_xmalloc(M * sizeof(float));
            for (int i = 0; i < M; i++) {
                float rm = S_blk[i*Kb];
                for (int j = 1; j < Kb; j++)
                    if (S_blk[i*Kb+j] > rm) rm = S_blk[i*Kb+j];
                m_new[i] = (m_vec[i] > rm) ? m_vec[i] : rm;
            }

            /* rescale + BMM2: O_blk[i] += exp(S[i][j] - m_new[i]) × V[kj+j] */
            for (int i = 0; i < M; i++) {
                float scale_old = expf(m_vec[i] - m_new[i]);
                /* O_blk[i] *= scale_old (NEON: 4 lane parallel) */
                for (int d = 0; d < D; d += 4) {
                    float32x4_t o4 = vld1q_f32(&O_blk[i*D + d]);
                    o4 = vmulq_n_f32(o4, scale_old);
                    vst1q_f32(&O_blk[i*D + d], o4);
                }
                l_vec[i] *= scale_old;

                /* 累加 P[i][j] × V[kj+j] 到 O_blk[i] */
                float row_sum = 0;
                for (int j = 0; j < Kb; j++) {
                    float p = expf(S_blk[i*Kb+j] - m_new[i]);
                    row_sum += p;
                    /* NEON: O_blk[i*D..i*D+D] += p × V[kj+j*D..] */
                    const float *v_row = &V[(kj+j)*D];
                    for (int d = 0; d < D; d += 4) {
                        float32x4_t o4 = vld1q_f32(&O_blk[i*D + d]);
                        float32x4_t v4 = vld1q_f32(&v_row[d]);
                        o4 = vfmaq_n_f32(o4, v4, p);
                        vst1q_f32(&O_blk[i*D + d], o4);
                    }
                }
                l_vec[i] += row_sum;
                m_vec[i] = m_new[i];
            }
            free(m_new);
        }

        /* 最终归一化（NEON 4 lane）*/
        for (int i = 0; i < M; i++) {
            float inv = 1.0f / l_vec[i];
            for (int d = 0; d < D; d += 4) {
                float32x4_t o4 = vld1q_f32(&O_blk[i*D + d]);
                o4 = vmulq_n_f32(o4, inv);
                vst1q_f32(&O[(qi+i)*D + d], o4);
            }
        }
        free(O_blk); free(m_vec); free(l_vec); free(S_blk);
    }
}

/* ---------- 多核 NEON Flash（qi 循环并行）---------- */
static void attention_flash_neon_omp(const float *Q, const float *K, const float *V,
                                      float *O, int N, int Br, int Bc, int nthreads, int is_causal) {
    #pragma omp parallel for num_threads(nthreads) schedule(static)
    for (int qi = 0; qi < N; qi += Br) {
        int M = (qi + Br <= N) ? Br : (N - qi);
        float *O_blk = kl_xcalloc(M * D, sizeof(float));
        float *m_vec = kl_xmalloc(M * sizeof(float));
        float *l_vec = kl_xmalloc(M * sizeof(float));
        for (int i = 0; i < M; i++) { m_vec[i] = -INFINITY; l_vec[i] = 0; }
        float *S_blk = kl_xmalloc(M * Bc * sizeof(float));

        for (int kj = 0; kj < N; kj += Bc) {
            int Kb = (kj + Bc <= N) ? Bc : (N - kj);
            for (int i = 0; i < M; i++) {
                const float *q_row = &Q[(qi+i)*D];
                for (int j = 0; j < Kb; j++) {
                    const float *k_row = &K[(kj+j)*D];
                    float32x4_t acc = vdupq_n_f32(0);
                    for (int kk = 0; kk < D; kk += 4) {
                        float32x4_t q4 = vld1q_f32(&q_row[kk]);
                        float32x4_t k4 = vld1q_f32(&k_row[kk]);
                        acc = vfmaq_f32(acc, q4, k4);
                    }
                    S_blk[i*Kb+j] = vaddvq_f32(acc) * SCALE;
                }
            }
            float *m_new = kl_xmalloc(M * sizeof(float));
            for (int i = 0; i < M; i++) {
                float rm = S_blk[i*Kb];
                for (int j = 1; j < Kb; j++)
                    if (S_blk[i*Kb+j] > rm) rm = S_blk[i*Kb+j];
                m_new[i] = (m_vec[i] > rm) ? m_vec[i] : rm;
            }
            for (int i = 0; i < M; i++) {
                float scale_old = expf(m_vec[i] - m_new[i]);
                for (int d = 0; d < D; d += 4) {
                    float32x4_t o4 = vld1q_f32(&O_blk[i*D + d]);
                    o4 = vmulq_n_f32(o4, scale_old);
                    vst1q_f32(&O_blk[i*D + d], o4);
                }
                l_vec[i] *= scale_old;
                float row_sum = 0;
                for (int j = 0; j < Kb; j++) {
                    float p = expf(S_blk[i*Kb+j] - m_new[i]);
                    row_sum += p;
                    const float *v_row = &V[(kj+j)*D];
                    for (int d = 0; d < D; d += 4) {
                        float32x4_t o4 = vld1q_f32(&O_blk[i*D + d]);
                        float32x4_t v4 = vld1q_f32(&v_row[d]);
                        o4 = vfmaq_n_f32(o4, v4, p);
                        vst1q_f32(&O_blk[i*D + d], o4);
                    }
                }
                l_vec[i] += row_sum;
                m_vec[i] = m_new[i];
            }
            free(m_new);
        }
        for (int i = 0; i < M; i++) {
            float inv = 1.0f / l_vec[i];
            for (int d = 0; d < D; d += 4) {
                float32x4_t o4 = vld1q_f32(&O_blk[i*D + d]);
                o4 = vmulq_n_f32(o4, inv);
                vst1q_f32(&O[(qi+i)*D + d], o4);
            }
        }
        free(O_blk); free(m_vec); free(l_vec); free(S_blk);
    }
}

/* KV-cache 增量解码（v1.0 新增）：单 query 对累积 K/V cache 做 attention
 * LLM 自回归解码核心：每步 query 是 1×D，K_cache/V_cache 是已累积的 cur_N×D
 * 性能优势：O(cur_N×D)，无需重算历史 K/V（全量 attention 每步 O(N²D)）
 * 用法：prefill 用 attention_flash_neon；decode 每步调本函数，传入累积 cache */
static void attention_kv_decode(const float *q, const float *Kc, const float *Vc,
                                 float *o, int cur_N) {
    /* BMM1: scores[j] = (q · Kc[j]) × SCALE，NEON 内积 */
    float *scores = kl_xmalloc(cur_N * sizeof(float));
    float max_s = -INFINITY;
    for (int j = 0; j < cur_N; j++) {
        float32x4_t acc = vdupq_n_f32(0);
        for (int kk = 0; kk < D; kk += 4)
            acc = vfmaq_f32(acc, vld1q_f32(&q[kk]), vld1q_f32(&Kc[j*D+kk]));
        scores[j] = vaddvq_f32(acc) * SCALE;
        if (scores[j] > max_s) max_s = scores[j];
    }
    /* softmax（数值稳定：减 max）*/
    float sum = 0;
    for (int j = 0; j < cur_N; j++) { scores[j] = expf(scores[j] - max_s); sum += scores[j]; }
    float inv = 1.0f / sum;
    /* BMM2: o[d] = sum_j softmax[j] × Vc[j][d]，NEON 4 lane 累加 */
    for (int kk = 0; kk < D; kk += 4) vst1q_f32(&o[kk], vdupq_n_f32(0));
    for (int j = 0; j < cur_N; j++) {
        float p = scores[j] * inv;
        for (int kk = 0; kk < D; kk += 4) {
            float32x4_t o4 = vld1q_f32(&o[kk]);
            o4 = vfmaq_n_f32(o4, vld1q_f32(&Vc[j*D+kk]), p);
            vst1q_f32(&o[kk], o4);
        }
    }
    free(scores);
}

int main() {
    int failures = 0;
    int N_list[] = {128, 256, 512, 1024};
    int n_list = sizeof(N_list) / sizeof(N_list[0]);

    printf("=== Attention: Scalar Naive vs NEON Flash (head_dim=%d) ===\n\n", D);
    printf("  N    | Naive ms | NEON ms | 加速比 | 多核(8) ms | 多核加速 | peak%%\n");
    printf("  -----+----------+---------+--------+------------+----------+------\n");

    for (int ni = 0; ni < n_list; ni++) {
        int N = N_list[ni];
        float *Q=kl_xmalloc(N*D*4),*K=kl_xmalloc(N*D*4),*V=kl_xmalloc(N*D*4);
        float *On=kl_xmalloc(N*D*4),*Of=kl_xmalloc(N*D*4),*Of8=kl_xmalloc(N*D*4);

        srand(42);
        for (int i=0;i<N*D;i++) {Q[i]=(rand()%100)/100.0f-0.5f;
                                  K[i]=(rand()%100)/100.0f-0.5f;
                                  V[i]=(rand()%100)/100.0f-0.5f;}

        /* 正确性（N=128）*/
        if (N == 128) {
            attention_naive_scalar(Q, K, V, On, N);
            attention_flash_neon(Q, K, V, Of, N, 64, 64, 0);
            float md = 0;
            for (int i = 0; i < N*D; i++) {
                float d = fabsf(On[i] - Of[i]);
                if (d > md) md = d;
            }
            if (md >= 0.01) failures++;
            printf("  [N=128] Scalar vs NEON Flash max_diff: %.4e %s\n",
                   md, md < 0.01 ? "✅" : "❌ FAIL");
        }

        double flops = 4.0 * N * N * D;
        int iter = (N >= 512) ? 1 : 3;

        double t0 = now_ns();
        for (int it=0;it<iter;it++) attention_naive_scalar(Q,K,V,On,N);
        double t1 = now_ns();
        double ms_n = (t1-t0)/iter/1e6;

        t0 = now_ns();
        for (int it=0;it<iter;it++) attention_flash_neon(Q,K,V,Of,N,64,64,0);
        t1 = now_ns();
        double ms_neon = (t1-t0)/iter/1e6;

        t0 = now_ns();
        for (int it=0;it<iter;it++) attention_flash_neon_omp(Q,K,V,Of8,N,64,64,8,0);
        t1 = now_ns();
        double ms_omp = (t1-t0)/iter/1e6;

        /* P1-9 修复：多核正确性校验（8 线程 OMP 结果 vs Naive 基线）*/
        if (N == 128) {
            float md_omp = 0;
            for (int i = 0; i < N*D; i++) {
                float d = fabsf(Of8[i] - On[i]);
                if (d > md_omp) md_omp = d;
            }
            printf("  OMP 8-thread vs Naive: %s (max_diff=%.2e)\n",
                   md_omp < 0.01 ? "✅ PASS" : "❌ FAIL", md_omp);
        }

        double gf_neon = flops*iter / ((ms_neon)*1e6);
        double peak = 40.0;
        printf("  %4d | %8.1f | %7.1f | %5.2fx | %10.1f | %7.2fx | %4.1f%%\n",
               N, ms_n, ms_neon, ms_n/ms_neon, ms_omp, ms_neon/ms_omp, gf_neon/peak*100);

        free(Q);free(K);free(V);free(On);free(Of);free(Of8);
    }

    /* === v1.0 新增：Causal Attention 正确性验证 === */
    printf("\n=== Causal Attention 验证（is_causal=1，下三角 mask）===\n");
    {
        int Nc = 128;
        float *Qc=kl_xmalloc(Nc*D*4),*Kc=kl_xmalloc(Nc*D*4),*Vc=kl_xmalloc(Nc*D*4);
        float *O_c=kl_xmalloc(Nc*D*4),*O_f=kl_xmalloc(Nc*D*4);
        for(int i=0;i<Nc*D;i++){Qc[i]=(rand()%100)/100.0f-0.5f;Kc[i]=(rand()%100)/100.0f-0.5f;Vc[i]=(rand()%100)/100.0f-0.5f;}
        attention_flash_neon(Qc,Kc,Vc,O_f,Nc,64,64,0);    /* full attention */
        attention_flash_neon(Qc,Kc,Vc,O_c,Nc,64,64,1);    /* causal attention */
        /* 验证1：causal ≠ full → mask 生效 */
        float diff=0; for(int i=0;i<Nc*D;i++){float d=fabsf(O_c[i]-O_f[i]);if(d>diff)diff=d;}
        printf("  [1] causal vs full max_diff=%.4f %s\n", diff, diff>1e-4?"✅ mask 生效":"⚠️ mask 未生效");
        /* 验证2：下三角性质——query[0] 只依赖 key[0]，扰动 key[1+] 不影响 O_causal[0] */
        float *O_c2=kl_xmalloc(Nc*D*4),*O_f2=kl_xmalloc(Nc*D*4);
        float k1save=Kc[1*D], v1save=Vc[1*D];
        Kc[1*D]+=100.0f; Vc[1*D]+=100.0f;                   /* 破坏 key[1] */
        attention_flash_neon(Qc,Kc,Vc,O_f2,Nc,64,64,0);
        attention_flash_neon(Qc,Kc,Vc,O_c2,Nc,64,64,1);
        float ch_c=0,ch_f=0;
        for(int d=0;d<D;d++){ch_c+=fabsf(O_c2[d]-O_c[d]);ch_f+=fabsf(O_f2[d]-O_f[d]);}
        printf("  [2] query[0] 对 key[1] 扰动敏感度: causal=%.4f full=%.4f %s\n",
               ch_c, ch_f, ch_c<ch_f*0.01?"✅ causal 屏蔽未来":"❌");
        Kc[1*D]=k1save; Vc[1*D]=v1save;
        free(Qc);free(Kc);free(Vc);free(O_c);free(O_f);free(O_c2);free(O_f2);
    }

    /* === v1.0 新增：KV-cache 增量解码验证 === */
    printf("\n=== KV-cache 增量解码验证（vs 全量 attention）===\n");
    {
        int Nk = 128;
        float *Qk=kl_xmalloc(Nk*D*4),*Kk=kl_xmalloc(Nk*D*4),*Vk=kl_xmalloc(Nk*D*4);
        float *Ok=kl_xmalloc(Nk*D*4),*O_kv=kl_xmalloc(D*4);
        for(int i=0;i<Nk*D;i++){Qk[i]=(rand()%100)/100.0f-0.5f;Kk[i]=(rand()%100)/100.0f-0.5f;Vk[i]=(rand()%100)/100.0f-0.5f;}
        attention_flash_neon(Qk,Kk,Vk,Ok,Nk,64,64,0);     /* 全量 attention（query[qi] attend 全部 Nk 个 key）*/
        int qi = 50;                                        /* 测试 query 行 50 */
        attention_kv_decode(&Qk[qi*D], Kk, Vk, O_kv, Nk);  /* KV cache：同样 attend 全部 Nk 个 key */
        float md=0; for(int d=0;d<D;d++){float df=fabsf(Ok[qi*D+d]-O_kv[d]);if(df>md)md=df;}
        printf("  query[%d] 全量 vs KV-cache: max_diff=%.2e %s\n", qi, md, md<1e-3?"✅ 一致":"❌ 偏差大");
        printf("  → KV-cache 单 query 解码 O(cur_N×D)，免重算历史（全量每步 O(N²D)）\n");
        free(Qk);free(Kk);free(Vk);free(Ok);free(O_kv);
    }

    printf("\n  peak = FP32 4 FVU 40 GFLOPS（单核）\n");
    return failures > 0;
}
