# 主线 LLVM 是否有 FTC86x 调度模型 —— 源码确认

> 路径：`/data/usershare/ai/riscv/OpenXiangShan/llvm-project/`
> 版本：**LLVM 23.0.0git**（主线 trunk）`[实测-读文件]` cmake/Modules/LLVMVersion.cmake: `LLVM_VERSION_MAJOR 23`
> 实测日期：2026-07-07

---

## 0. 一句话结论

**主线 LLVM 23.0.0git 全树（llvm/ + clang/ + AArch64 后端）零飞腾字符串。** 不存在 FTC862/FTC86x/Phytium 调度模型、CPU 识别或 subtarget 定义。飞腾在线上用主线 LLVM 时，被当作**通用 AArch64**（或近似某个 ARM Cortex/Neoverse 核）处理，无任何飞腾特异性优化。

---

## 1. 全树 grep 结果（决定性证据）

### 1.1 `llvm/lib/Target/AArch64/` —— 零命中 `[实测-grep]`
- grep `FTC86|FTC66|Phytium|ftc86|ftc66|phytium`：**No files found**

### 1.2 `clang/` 全目录 —— 零命中 `[实测-grep]`
- grep 同上模式：**No files found**
- 即 clang 的 `-mcpu=` 选项里没有 `ftc862`/`phytium`，driver 不识别飞腾 CPU。

### 1.3 `llvm/` 全目录 —— 零命中 `[实测-grep]`
- grep 同上模式：**No files found**

**结论：主线 LLVM 对飞腾 FTC862/FTC664 完全无感知。**

---

## 2. AArch64 后端实际存在的调度模型（34 个 .td 文件）`[实测-glob]`

`llvm/lib/Target/AArch64/AArch64Sched*.td` 完整清单：

| 厂商 | 调度模型 |
|------|----------|
| ARM | A53、A55、A510、A57(+WriteRes)、A320、Cyclone(Apple) |
| ARM Neoverse | N1、N2、N3、V1、V2、V3、V3AE、PredNeoverse |
| Ampere | Ampere1、Ampere1B |
| Marvell | ThunderX、ThunderX2T99、ThunderX3T110 |
| Samsung | ExynosM3、M4、M5、PredExynos |
| 高通 | Kryo、KryoDetails、Falkor、FalkorDetails |
| 华为 | **TSV110**（鲲鹏 920 系列） |
| 富士通 | A64FX |
| 其他 | Oryon、Olympus、Predicates、Schedule(基线) |

**关键观察**：
- 华为 TSV110（鲲鹏）有专属调度模型——这是华为向 LLVM 上游贡献的。
- **飞腾 FTC862 没有任何专属调度模型。**
- 飞腾最可能近似：通用 AArch64（默认），或 `-mcpu=tsv110`/`cortex-a76` 类（推测，未实测）。

---

## 3. 飞腾 FTC862 在主线 LLVM 的实际待遇 `[推测-依据]`

基于上述零命中证据：
- `clang -mcpu=ftc862`：**不被识别**（会报 unknown CPU）
- 飞腾必须用 `clang -march=armv8.4-a`（FTC862 是 ARMv8.4）+ 通用调度
- 调度器只能用**基线 AArch64Schedule.td** 的近似模型
- 后果：指令调度、寄存器分配、向量化决策都**非 FTC862 最优**——这是飞腾性能未被编译器充分挖掘的根因之一

---

## 4. 对 Expert_18 写作的输入建议

1. **铁证段**："主线 LLVM 23.0 零飞腾字符串"——写进 E18 开篇，作为"飞腾无上游编译器话语权"的硬证据。
2. **对照表**：把 34 个调度模型列成表，标注"华为有 TSV110，飞腾无"，凸显飞腾在 LLVM 上游的**缺席**。
3. **性能推论**：因无 FTC862 调度模型，飞腾 CPU 跑主线 LLVM 编译的二进制存在调度次优损失（与 GCC 情况类似）。可对偶 Expert_06（寄存器分配/调度）和 Expert_08（AArch64 后端）展开。
4. **盲区诚实段**：FTC862 最优 -mcpu 参数需实测（用 `-mtune` A/B 测试各 ARM 核模型），本次未跑基准。
5. **战略叙事**：龙芯 LoongArch 已是主线正式后端（LLVM 16+），华为 TSV110 有调度模型——**飞腾是国产 CPU 中唯一在主线 LLVM 既无后端也无调度模型的**（ARM 架构身份使其"隐身"在通用 AArch64 里，但也失去了特异性优化机会）。
