# Capstone-C: 工作负载刻画

> 选自 📕 实战性能分析

---

## 1. 任务

选一个真实工作负载，用 PhyTune + perf 完整 profile，输出一份
"飞腾 D3000M 上 X 工作负载的微架构分析报告"。

---

## 2. 候选工作负载

| 工作负载 | 类型 | 难度 | 价值 |
|---------|------|------|------|
| **llama.cpp 推理** | LLM 推理 | 中 | 高（飞腾 AI 主战场）|
| **Redis 缓存** | K-V 存储 | 低 | 高（数据库后端）|
| **GEMM (OpenBLAS)** | 线性代数 | 低 | 高（HPC 基础）|
| **gcc -O2 编译 Linux 内核** | 编译 | 中 | 中 |
| **zstd 压缩** | 压缩 | 低 | 中 |
| **MySQL TPC-C** | 数据库 | 高 | 高 |

---

## 3. 分析框架（用 PhyTune topdown-tool）

```bash
# Stage 1: Top-Down 微架构分析
sudo python3 /opt/phytune/.../topdown-tool --cpu phytium-ftc862 \
    ./your_workload

# 输出 4 个 Level-1 指标:
#   Frontend Bound  (取指瓶颈)
#   Backend Bound   (执行/访存瓶颈)
#   Bad Speculation (分支预测失败)
#   Retiring        (有效计算比例)
```

---

## 4. 分析维度（必填）

1. **IPC + CPI + 频率**（Lab00 Iron Law）
2. **Cache 行为**（Lab03）：L1D/L2/L3 MPKI
3. **分支行为**（Lab02）：misprediction rate
4. **TLB 行为**：是否需要大页
5. **NUMA 行为**：多核时跨 socket 访问
6. **内存带宽**：DDR4 流量
7. **指令混合**（飞腾 PMU）：int/FP/SIMD/load/store 占比

---

## 5. 输出（已完成）

```
Capstone/workload_characterization/
├── README.md                ← 本文件
├── driver.sh                ← 跑工作负载 + perf stat 自动采集
├── collect.py               ← perf 输出解析 + 报告生成
├── profile_report.md        ← 9 个工作负载的实测数据表（自动生成）
├── recommendations.md       ← 5 条具体优化建议（含数据依据）
└── data/                    ← 9 个 .perf 原始数据
    ├── gemm_single_core.perf
    ├── zstd_random_L{1,3,9,19}.perf
    └── zstd_text_L{1,3,9,19}.perf
```

---

## 6. 推荐：llama.cpp profile 模板

### 6.1 准备
```bash
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp && make -j8
# 用一个 7B Q4 量化模型
wget https://huggingface.co/.../qwen2-7b-instruct-q4_k_m.gguf
```

### 6.2 单次推理 + Top-Down
```bash
sudo python3 /opt/phytune/.../topdown-tool --cpu phytium-ftc862 \
    ./llama-cli -m model.gguf -p "Hello, what is 2+2?" -n 32
```

### 6.3 关键指标预期
- IPC: 0.5-1.5（LLM 推理 IPC 不高，访存密集）
- L2D MPKI: 高（matmul 操作数大）
- Backend Bound: 70%+（访存瓶颈）
- Frontend Bound: 10-20%（decode + i-cache）
- Bad Speculation: 5-10%（少量分支）

### 6.4 优化建议方向
- 用 PhyGCC 重编译 llama.cpp（kpgcc -mcpu=ftc86x）
- 启用 NEON 优化（CMake -DGGML_NEON=ON）
- 大页：`HUGETLB_MORE=... ./llama-cli ...`
- 绑核：`numactl --cpunodebind=0 --membind=0`
