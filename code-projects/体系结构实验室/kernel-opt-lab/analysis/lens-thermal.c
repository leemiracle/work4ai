/* ============================================================================
 * lens-thermal.c — 视角 3：Thermal + DVFS（热设计 / 动态频率）
 *
 * D3000 没有 Intel RAPL 那样的能耗计数器，但有 hwmon 温度 + DVFS 频率
 * → 从"热设计"视角看长期持续负载下：
 *   1. CPU 温度上升曲线
 *   2. 是否触发热降频（cpuinfo_cur_freq 下降）
 *   3. GFLOPS 随温度/频率的变化
 *
 * 部署关键问题：边缘设备长时间跑 LLM 推理会不会热降频？
 * ============================================================================ */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <arm_neon.h>

static double now_ns() {
    struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t);
    return t.tv_sec * 1e9 + t.tv_nsec;
}

/* 读 sysfs 文件（一次性 int 值）*/
static long read_sysfs_int(const char *path) {
    FILE *f = fopen(path, "r");
    if (!f) return -1;
    long v = -1;
    if (fscanf(f, "%ld", &v) != 1) v = -1;
    fclose(f);
    return v;
}

/* GEMM MR=8（重负载）*/
static void pack_B(const float *B, float *Bb, int N, int K) {
    for (int jb=0;jb<N/4;jb++) for (int k=0;k<K;k++) for (int j=0;j<4;j++)
        Bb[jb*K*4+k*4+j] = B[(jb*4+j)*K+k];
}
static void gemm_mr8(const float *A, const float *Bb, float *C, int M, int N, int K) {
    for (int i=0;i<M;i+=8) for (int jb=0;jb<N/4;jb++) {
        const float *b=&Bb[jb*K*4];
        float32x4_t c0=vdupq_n_f32(0),c1=vdupq_n_f32(0),c2=vdupq_n_f32(0),c3=vdupq_n_f32(0);
        float32x4_t c4=vdupq_n_f32(0),c5=vdupq_n_f32(0),c6=vdupq_n_f32(0),c7=vdupq_n_f32(0);
        for (int k=0;k<K;k+=4) {
            float32x4_t a0=vld1q_f32(&A[(i+0)*K+k]),a1=vld1q_f32(&A[(i+1)*K+k]);
            float32x4_t a2=vld1q_f32(&A[(i+2)*K+k]),a3=vld1q_f32(&A[(i+3)*K+k]);
            float32x4_t a4=vld1q_f32(&A[(i+4)*K+k]),a5=vld1q_f32(&A[(i+5)*K+k]);
            float32x4_t a6=vld1q_f32(&A[(i+6)*K+k]),a7=vld1q_f32(&A[(i+7)*K+k]);
            float32x4_t b0=vld1q_f32(&b[(k+0)*4]),b1=vld1q_f32(&b[(k+1)*4]);
            float32x4_t b2=vld1q_f32(&b[(k+2)*4]),b3=vld1q_f32(&b[(k+3)*4]);
            c0=vfmaq_laneq_f32(c0,b0,a0,0);c1=vfmaq_laneq_f32(c1,b0,a1,0);
            c2=vfmaq_laneq_f32(c2,b0,a2,0);c3=vfmaq_laneq_f32(c3,b0,a3,0);
            c4=vfmaq_laneq_f32(c4,b0,a4,0);c5=vfmaq_laneq_f32(c5,b0,a5,0);
            c6=vfmaq_laneq_f32(c6,b0,a6,0);c7=vfmaq_laneq_f32(c7,b0,a7,0);
            c0=vfmaq_laneq_f32(c0,b1,a0,1);c1=vfmaq_laneq_f32(c1,b1,a1,1);
            c2=vfmaq_laneq_f32(c2,b1,a2,1);c3=vfmaq_laneq_f32(c3,b1,a3,1);
            c4=vfmaq_laneq_f32(c4,b1,a4,1);c5=vfmaq_laneq_f32(c5,b1,a5,1);
            c6=vfmaq_laneq_f32(c6,b1,a6,1);c7=vfmaq_laneq_f32(c7,b1,a7,1);
            c0=vfmaq_laneq_f32(c0,b2,a0,2);c1=vfmaq_laneq_f32(c1,b2,a1,2);
            c2=vfmaq_laneq_f32(c2,b2,a2,2);c3=vfmaq_laneq_f32(c3,b2,a3,2);
            c4=vfmaq_laneq_f32(c4,b2,a4,2);c5=vfmaq_laneq_f32(c5,b2,a5,2);
            c6=vfmaq_laneq_f32(c6,b2,a6,2);c7=vfmaq_laneq_f32(c7,b2,a7,2);
            c0=vfmaq_laneq_f32(c0,b3,a0,3);c1=vfmaq_laneq_f32(c1,b3,a1,3);
            c2=vfmaq_laneq_f32(c2,b3,a2,3);c3=vfmaq_laneq_f32(c3,b3,a3,3);
            c4=vfmaq_laneq_f32(c4,b3,a4,3);c5=vfmaq_laneq_f32(c5,b3,a5,3);
            c6=vfmaq_laneq_f32(c6,b3,a6,3);c7=vfmaq_laneq_f32(c7,b3,a7,3);
        }
        vst1q_f32(&C[(i+0)*N+jb*4],c0);vst1q_f32(&C[(i+1)*N+jb*4],c1);
        vst1q_f32(&C[(i+2)*N+jb*4],c2);vst1q_f32(&C[(i+3)*N+jb*4],c3);
        vst1q_f32(&C[(i+4)*N+jb*4],c4);vst1q_f32(&C[(i+5)*N+jb*4],c5);
        vst1q_f32(&C[(i+6)*N+jb*4],c6);vst1q_f32(&C[(i+7)*N+jb*4],c7);
    }
}

int main() {
    int N = 1024;
    float *A=malloc(N*N*4),*B=malloc(N*N*4),*Bb=malloc(N*N*4),*C=malloc(N*N*4);
    for(int i=0;i<N*N;i++){A[i]=(float)(i%17)/17.0f;B[i]=(float)(i%19)/19.0f;}
    pack_B(B,Bb,N,N);

    /* sysfs 路径探测 */
    const char *temp_paths[] = {
        "/sys/class/hwmon/hwmon0/temp1_input",  /* EC CPU 温度 */
        "/sys/class/hwmon/hwmon1/temp1_input",  /* acpitz */
        "/sys/class/hwmon/hwmon0/temp2_input",  /* EC 第二温度 */
    };
    const char *freq_path = "/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq";

    printf("# Lens 3: Thermal + DVFS（热设计视角）\n\n");
    printf("## 实验设计\n");
    printf("持续 GEMM 1024³ 负载 20 秒，每秒采样 CPU 温度 + 频率 + GFLOPS\n\n");

    /* 初始温度 */
    long t0_ec = read_sysfs_int(temp_paths[0]);
    long t0_acpi = read_sysfs_int(temp_paths[1]);
    long freq_max = read_sysfs_int("/sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq");
    long freq_min = read_sysfs_int("/sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_min_freq");
    printf("## 初始状态\n");
    printf("- EC CPU 温度: %.1f °C\n", t0_ec/1000.0);
    printf("- ACPI 温度: %.1f °C\n", t0_acpi/1000.0);
    printf("- 频率范围: %.2f - %.2f GHz\n", freq_min/1e6, freq_max/1e6);
    printf("\n## 温度 / 频率 / GFLOPS 时间序列（20 秒持续负载）\n\n");
    printf("| t (s) | EC temp | ACPI temp | Freq (GHz) | GFLOPS | 备注 |\n");
    printf("|---|---|---|---|---|---|\n");

    /* 跑 20 秒 */
    int total_secs = 20;
    long gflops_sum = 0; int gflops_cnt = 0;
    long freq_min_observed = freq_max;
    long temp_max_observed = t0_ec;

    double start_t = now_ns();
    for (int sec = 0; sec < total_secs; sec++) {
        /* 跑 1 秒 GEMM */
        double sec_start = now_ns();
        int iter = 0;
        double gf = 0;
        while (1) {
            double t0 = now_ns();
            gemm_mr8(A, Bb, C, N, N, N);
            double t1 = now_ns();
            gf = 2.0*N*N*N/(t1-t0)*1e9;
            iter++;
            if (t1 - sec_start > 1e9) break;
        }
        gflops_sum += (long)gf;
        gflops_cnt++;

        long temp_ec = read_sysfs_int(temp_paths[0]);
        long temp_acpi = read_sysfs_int(temp_paths[1]);
        long freq = read_sysfs_int(freq_path);
        if (freq > 0 && freq < freq_min_observed) freq_min_observed = freq;
        if (temp_ec > temp_max_observed) temp_max_observed = temp_ec;

        double t = (now_ns() - start_t) / 1e9;
        char note[64] = "";
        if (freq > 0 && freq < freq_max * 0.95)
            sprintf(note, "⚠️ 降频到 %.2f GHz", freq/1e6);
        else if (temp_ec > 75000)
            sprintf(note, "高温 %.1f°C", temp_ec/1000.0);

        printf("| %.1f | %.1f°C | %.1f°C | %.2f | %.2f | %s (iter=%d) |\n",
               t, temp_ec/1000.0, temp_acpi/1000.0,
               freq>0?freq/1e6:0, gf, note, iter);
        fflush(stdout);
    }

    printf("\n## 关键洞察\n\n");
    printf("- 平均 GFLOPS: %.2f\n", (double)gflops_sum/gflops_cnt);
    printf("- 最高温度: %.1f°C\n", temp_max_observed/1000.0);
    printf("- 频率范围: %.2f - %.2f GHz\n",
           freq_min_observed>0?freq_min_observed/1e6:0, freq_max/1e6);
    if (freq_min_observed < freq_max) {
        printf("- ⚠️ 检测到降频（DVFS 触发）：长期负载 GFLOPS 会下降\n");
    } else {
        printf("- ✓ 未检测到明显降频（散热充足）\n");
    }
    printf("\n**部署启示**：\n");
    printf("- 边缘设备长跑 LLM 推理前需做 thermal soak test（30+ 分钟）\n");
    printf("- 若降频明显，需改善散热或限制并发核数（降功耗）\n");
    printf("- 温度每升高 10°C，CPU 寿命约减半（Arrhenius）\n");

    free(A);free(B);free(Bb);free(C);
    return 0;
}
