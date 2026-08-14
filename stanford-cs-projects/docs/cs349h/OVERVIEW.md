# CS349H: Software for Emerging Hardware Platforms

> Stanford University | 研究生 | CS349 系列 (主题轮换)
> Instructor: **Sara Achour** (编译器 / 形式化方法专家, Stanford CS / EE 双聘)
> Prerequisites: CS143 (编译器) + CS243 (程序分析) 推荐 / CS107 必备
> Difficulty: ⭐⭐⭐⭐⭐ (编译器 + 硬件 + 系统三层)

---

## 📚 定位

**"AI 硬件 / 新型加速器的软件栈"专题课**。GPU / TPU / Cerebras / Groq / SambaNova 这些异构硬件,光有芯片不够,**还要有让 PyTorch / JAX 跑得起来的软件中间层**——CS349H 讲这层怎么搭。

核心命题:一个新硬件要能用,需要 4 层软件:
1. **IR / Compiler** (TVM / MLIR / XLA / Triton) — 把 PyTorch 算子翻成硬件指令
2. **Runtime** — 调度 / 内存 / kernel launch
3. **Numerics library** (cuBLAS / oneDNN) — 标准算子实现
4. **Framework integration** — PyTorch / JAX 后端

Achour 的背景(形式化 + 编译器 + 数值计算)恰好覆盖最难的部分——**自动生成正确且高效的代码**。

---

## 📅 完整模块(推测,基于讲师方向)

### Week 1: AI 硬件 landscape
- GPU (H100/B200, SIMD + Tensor Core) / TPU (Systolic array) / Cerebras WSE-3 (整片晶圆) / Groq LPU (确定性时延) / SambaNova / Tenstorrent / Gaudi / MI300

### Week 2-3: GPU 编程模型 + MLIR
- CUDA: Thread / Warp / Block / Tensor Core (WMMA);Async copy / TMA (Hopper)
- MLIR 设计哲学 (可组合 dialects);PyTorch → Torch-MLIR → Linalg → NVVM 流水线

### Week 4-5: TVM + XLA + Triton
- TVM / Relay / AutoTVM / Ansor (tensorization)
- XLA / StableHLO;JAX 案例
- 🔴 **Triton** block-level 编程;案例:手写 FlashAttention

### Week 6: TPU Systolic Array
- MXU 数据流;XLA 如何把 matmul 翻成 systolic;TPU v4/v5p/Trillium 演进

### Week 7: 数据流架构 (Cerebras / SambaNova / Groq)
- Cerebras CS-3 (片内全互联) / SambaNova RDU (可重构) / Groq LPU (静态调度);软件栈对比

### Week 8-10: 量化 / Sparsity / 自动并行 / 前沿
- INT8 / FP8 / INT4 编译器视角;GPTQ / AWQ;2:4 structured sparsity
- GSPMD / Alpa 自动并行;Differentiable programming (JAX / Enzyme);HW/SW co-design

---

## 🧮 核心概念

### Triton vs CUDA vs TVM 三角
```
       抽象层级
   高 ── TVM (自动调优, 图级)
        ── Triton (block-level, 平衡)
   低 ── CUDA (极致控制)
```

### Tensorization (翻成 Tensor Core 指令)
1. 识别 matmul pattern (linalg.matmul)
2. tile 切到 m=16, n=8, k=16 (Tensor Core shape)
3. 替换为 mma.sync 指令
4. 插入 cp.async 预取

### Systolic Array (TPU)
每个 PE 每个 cycle 执行 $o += a \cdot w$,然后把 a / w 传给邻居,形成二维脉动数据流。

---

## 💻 项目代码

📁 `topic4-mlsys/` (与 CS349E / CS349F 共享)。典型作业: Triton kernel (FlashAttention 简化版) / MLIR pass / FP8 vs INT8 误差实验。`pip install triton`;看 XLA: `jax.jit(f).lower(x).compiler_ir('stablehlo')`。

---

## 📊 关键论文

### 🔴 P0
1. **Tillet et al. 2019** "Triton" — block-level GPU 编译
2. **Lattner et al. 2021** "MLIR"
3. **Dao 2022** "FlashAttention" NeurIPS (Triton 案例)
4. **Chen et al. 2018** "TVM"
5. **Jouppi et al. 2017** "In-Datacenter Performance of a TPU"

### 🟡 P1
6. **Cerebras WSE / Groq LPU** 白皮书
7. **Vasilache et al. 2019** "Tensor Comprehensions"
8. **Zheng et al. 2022** "Alpa" (自动并行)
9. **Enzyme** (differentiable programming)

---

## 🎯 学习路径

| 角色 | 推荐 |
|------|------|
| **编译器 / runtime eng** | CS143 → CS243 → **CS349H (必)** |
| **GPU kernel eng** | CS149 + CS240 → CS349H |
| **芯片公司 software eng** | CS349H 核心专业课 |
| **PhD (compilers for ML)** | CS349H + CS243 + Achour 组 |

---

## 💡 反思

**优势**: 稀有度极高(AI 芯片软件栈综合课可能就这一门);Achour 形式化视角独特;就业面广(NVIDIA/AMD/Intel/Cerebras/Groq/Tenstorrent 都缺这类人)。

**局限**: 编译器前置重(没 CS143 会吃力);硬件迭代快(Hopper→Blackwell 每年变);实验门槛高(无 GPU/TPU 访问权只能跑模拟)。

---

## 🚀 扩展

完成 CS349H 后推荐: **CS349E** (推理引擎) → **CS349F** (网络架构) → **CS243** (程序分析);实习目标 NVIDIA cuDNN / Google XLA / Modular / Anthropic Infra。关键开源项目: Triton / MLIR / XLA / StableHLO / TVM / IREE / Modular Mojo。

---

**最后更新**: 2026-08-11
**对应代码**: `topic4-mlsys/` (与 CS349E / CS349F 共享)
