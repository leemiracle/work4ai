# Expert_07 — 自动向量化专家 / Loop Vectorizer + SLP + Vector Predication 视角

> **角色定位**：这位专家是 LLVM **向量化器的维护者级别的人**——他往 `llvm/lib/Transforms/Vectorize/` 提过 patch，调试过 cost model 把一个好循环误判成"不值得向量化"的 bug，追踪过 VPlan 从 2017 年提议到 2024 年全面接管的整条迁移线。他把自动向量化当成一台**精密的分拣机**：源代码循环进来，经过合法性审查（legality）、成本核算（cost model）、计划生成（VPlan）、代码发射（codegen）四道关卡，能向量化的吐出 NEON/SVE/AVX 指令，不能的吐回标量。他同时盯三台机器：**Loop Vectorizer**（循环级并行，跨迭代打包）、**SLP Vectorizer**（超字级并行，同一基本块内独立标量打包）、**Vector Predication（VP）**（把"掩码 + 显式向量长度"做成一等公民，统一 SVE/RVV/AVX-512）。这位专家是本项目 [断层② MLIR-core 融合裂痕](../改造蓝图_LLVM.md#5-五个服务器命脉级断层) 的直接承载者之一——MLIR `vector` dialect 与 LLVM Vectorizer 的"谁来向量化"之争，是 AI 推理编译栈的核心断层。
>
> **核心思维模型**：
> 1. **Legality–Cost–Transform 三段式思维**——现代向量化器不是"看到循环就向量化"，而是严格的三阶段流水线。**Legality**（`LoopVectorizationLegality.cpp`）回答"能不能"：循环携带依赖？别名？需要谓词化？**Cost Model**（`LoopVectorizationCostModel`）回答"值不值"：向量化的收益减去尾循环、运行时别名检查、寄存器压力的代价，是否为正？**Transformation**（VPlan + `InnerLoopVectorizer`）回答"怎么做"：生成什么 IR、如何处理余数。**三段任何一段失败，向量化就失败**——而且飞腾的失败几乎全在 Legality（无 SVE 谓词）和 Cost（无专用调度模型导致成本虚高）。
> 2. **"目标描述驱动"思维**——向量化的命运不在 `LoopVectorize.cpp` 的算法里，而在 `AArch64TargetTransformInfo.cpp` 的 `getRegisterBitWidth()` 里。Loop Vectorizer 问 TTI"你的向量寄存器多宽"，TTI 回答 128（NEON）还是 scalable(128)（SVE）还是 scalable(0)（飞腾无 SVE）。这一个函数的返回值，决定了飞腾 D3000M 上向量化的天花板。**填表的人比写算法的人权力大**。
> 3. **"谓词是向量化的灵魂"思维**——条件循环（`if (a[i] > 0) sum += a[i]`）能否向量化，本质是"有没有谓词/掩码机制"。AVX-512 有掩码寄存器，SVE 有 P0–P15 谓词寄存器，RVV 有 v0.t。**NEON 什么都没有**——这是飞腾向量化覆盖率被砍掉一半的物理根因。Vector Predication（VP）扩展的全部意义，就是让 IR 层有一个统一的"掩码 + EVL（显式向量长度）"抽象，让前端不必为每种 ISA 写不同的向量化路径。

---

## 0. 特异性测试 v2.0 自检（强制）

> 本节按 [`改造蓝图_LLVM.md` §0.3](../改造蓝图_LLVM.md) 的双重门槛自检。本 Expert 同时满足三项：
> - **(a) 飞腾工程实证**：引用飞腾项目 View_01（`../../体系结构实验/View_01_Compiler/README.md`） 的 `-O0..-Ofast` 实测（-Ofast 比 -O3 快 4×）、Expert_11 §2.3（`../../体系结构实验/Expert_11_Compiler_Research/README.md`） 的向量化失败诊断、Lab05（`../../体系结构实验/Lab05_并行与SIMD/README.md`） 的 NEON GEMM 实测。
> - **(b) 代码级实例**：全部以 `OpenXiangShan/llvm-project`（LLVM 23.0.0git）真实源码行号为锚——`LoopVectorize.cpp`（9963 行）、`AArch64TargetTransformInfo.cpp:3134`、`VPIntrinsics.def`（763 行 / 45 个 vp.* intrinsic）。不是 README 翻译。
> - **(c) 对偶判断**：§2.5 给出 LLVM LoopVec vs GCC `tree-vectorizer` vs MLIR `vector` dialect 的三方对标表。
>
> **反向锚点（诚实披露）**：`grep -rn "FTC86\|Phytium" llvm/lib/Transforms/Vectorize/` = **零命中**。这意味着主线 LLVM 的向量化器对飞腾 FTC862 **零感知**，飞腾代码在线主线 LLVM 上跑的是通用 AArch64（Cortex-A 近似）成本模型——这正是飞腾向量化"半成功"的根因之一，与飞腾项目 Expert_11 §3.2（`../../体系结构实验/Expert_11_Compiler_Research/README.md`） 的"提交 FTC86x 调度模型到主线"建议互为印证。

---

## 1. 这位向量化器专家看 LLVM 的 10 个尖锐问题

这位专家拿到一个 LLVM 版本，第一件事不是 `clang -O3 -Rpass=vectorize`，而是 `wc -l llvm/lib/Transforms/Vectorize/LoopVectorize.cpp` 和 `grep BEGIN_REGISTER_VP llvm/include/llvm/IR/VPIntrinsics.def`，他问：

1. **Loop Vectorizer 的 cost model 怎么读 TargetTransformInfo？** 不是抽象地"查表"——要看 `computeMaxVF()`（[实测-LoopVectorize.cpp:3574]）怎么问 `TTI.getRegisterBitWidth()`、`selectVectorizationFactor()`（[实测-LoopVectorize.cpp:4232]）怎么遍历候选 VF 算 `expectedCost`。**飞腾无 SVE 时，cost 怎么算？** `AArch64TTIImpl::getRegisterBitWidth`（[实测-TTI.cpp:3134]）对 `RGK_ScalableVector` 返回 `scalable(0)`——这一个返回值，让飞腾永远拿不到 scalable 向量化。
2. **Vector Predication（VP）扩展——为什么 LLVM 要引入 `vp.*` intrinsic？** 不是"多一种写法"——是解决一个真实的工程债：SVE 用谓词寄存器 + 可变长，RVV 用 `v0.t` + AVL，AVX-512 用 `k` 掩码寄存器，三套机制语义相近但 IR 表达完全不同。`vp.add <4 x i32> %a, %b, mask=%m, evl=%n` 把三者统一成一个 intrinsic。**VP 与 SVE/RVV/AVX-512 的统一**进度如何？飞腾无 SVE 时 `vp.*` 还有用吗（答案是：NEON 也能 lower 部分 VP，靠 fold mask + select）？
3. **SLP Vectorizer 的"超字并行"在飞腾 NEON 上的覆盖率到底多少？** 飞腾 Expert_11 §2.3（`../../体系结构实验/Expert_11_Compiler_Research/README.md`） 引用了 SLP，但没给覆盖率数字。SLP 抓的是"基本块内 N 个独立标量运算"（如 `a.x*b.x, a.y*b.y, a.z*b.z, a.w*b.w` 四个独立乘法），这在图形/AI 代码里极常见。飞腾 NEON `<4 x float>` 正好对齐——但 SLP 的 cost model 同样依赖 TTI，飞腾无专用调度模型时 SLP 收益被低估。
4. **对偶：LLVM Loop Vectorizer vs GCC `tree-vectorizer` vs MLIR `vector` dialect。** 三者都在做向量化，但哲学迥异：LLVM 是"运行时 cost model 驱动"，GCC 是"静态启发式 + 数据引用向量"，MLIR 是"声明式 `vector.contract` + 渐进 lowering"。**谁在 AI 推理时代会赢？** 飞腾若选编译栈，选哪条路？
5. **向量化的 legality 分析——alias analysis / loop dependence / memory disambiguation。** 这是向量化器最学术的部分。`LoopVectorizationLegality::canVectorizeMemory()`（[实测-Legality.cpp:1231]）调 `LoopAccessInfo`，后者跑依赖分析。**编译器怎么知道 `c[i]` 和 `a[i]` 会不会重叠？** TBAA（类型别名）、SCEV（下标演化）、运行时检查（loop versioning）三层防线。
6. **Loop versioning（运行时别名检查）——飞腾代码里大量"半成功"案例。** 飞腾 Expert_11 §2.3.1（`../../体系结构实验/Expert_11_Compiler_Research/README.md`） 指出，最常见的情况是编译器插入 `if (c+n <= a || a+n <= c) goto vector_loop; else goto scalar_loop;`，运行时一旦发现别名就走标量。**这种"双版本"在飞腾上的真实代价是多少？** 分支预测能覆盖吗？
7. **Reduction 的向量化——FP 重关联（`-ffast-math`）vs IEEE 严格。** 飞腾 View_01 实测（`../../体系结构实验/View_01_Compiler/README.md`）：`-O3` → 3.27 ms，`-Ofast`（`-O3 -ffast-math`）→ 0.83 ms，**整整 4×**。这个 4× 不是飞腾突然变快，是 `LoopVectorize` 的 reduction 处理从"单累加器串行"切到"4 独立累加器并行"，让飞腾 4-wide issue 终于吃饱。**这一刀切在哪里？** 在 `RecurrenceDescriptor` + `getArithmeticReductionCost`。
8. **Masked load/store / gather-scatter 在 NEON vs SVE vs AVX-512 的差异。** 这是谓词化的硬件落地。AVX-512 有 `vmaskmovps`，SVE 有 `ld1w {z0.s}, p0/z, [x0]`，**NEON 没有原生 masked load/store**——只能用 `cmp` + `bitwise select` 模拟，成本高 3–5 倍。飞腾缺失 masked memory 是 gather-scatter 密集循环（稀疏矩阵、哈希表）向量化的硬墙。
9. **VPlan（Vectorization Plan）——LLVM 16+ 的新设计。** VPlan 把向量化从"边算边生成 IR"升级为"先规划一个完整计划（plan），再执行"。`VPlan.cpp` / `VPlanRecipes.cpp` / `VPlanTransforms.cpp` / `VPlanPredicator.cpp` 等 10+ 文件已全面接管。**VPlan 解决了什么老问题？** 解决了"外层循环向量化""嵌套向量化""谓词化方案选择"这些旧架构表达不出来的复杂决策。
10. **飞腾 D3000M 上 UDOT 选不出——LoopVectorizer 是否会主动寻找 dotprod pattern？** 飞腾 Expert_11 §2.3.4（`../../体系结构实验/Expert_11_Compiler_Research/README.md`） 给了案例：`sum += a[i]*b[i]`（int8）默认选不出 UDOT，因为前端把 int8 提升成 int32。**但 LLVM 23 是否有了改进？** `VPlanTransforms.cpp` 里有 `getPartialReductionCost`（[实测-VPlanTransforms.cpp:4383]）和 `getExtendedReductionCost`——这正是 dotprod pattern 的 cost 接口。答案是：LLVM 在改进，但飞腾要拿到红利，必须把 FTC86x 的 dotprod 能力**准确地填进 TTI**。

---

## 2. 具体分析：代码级实例 + 飞腾工程实证 + 对偶判断（过 §0.3）

### 2.1 向量化器的四阶段流水线与 VPlan 接管（图表 ①：Loop Vectorizer Pipeline）

先看全局。现代 LLVM 的向量化不是单文件，而是 `llvm/lib/Transforms/Vectorize/` 下的**17 个翻译单元**（实测 `glob *.cpp`）：

```
llvm/lib/Transforms/Vectorize/  （LLVM 23，17 个 .cpp）
├── LoopVectorize.cpp          9963 行  ← 循环向量化主驱动
├── LoopVectorizationLegality.cpp       ← "能不能"合法性分析
├── SLPVectorizer.cpp         ~28000 行 ← 超字并行（LLVM 最大文件之一）
├── LoadStoreVectorizer.cpp             ← GPU 友好的 load/store 聚合
├── LoopIdiomVectorize.cpp              ← 循环惯用式（memcpy/memset 模式）
├── VectorCombine.cpp                   ← 向量指令后处理优化
├── VPlan.cpp / VPlanRecipes.cpp        ← VPlan 计划与配方
│   VPlanTransforms.cpp / VPlanAnalysis.cpp
│   VPlanConstruction.cpp / VPlanVerifier.cpp
│   VPlanUtils.cpp / VPlanPredicator.cpp
│   VPlanUnroll.cpp / VPlanSLP.cpp      ← VPlan 全面接管（10 文件）
└── SandboxVectorizer/                  ← ⭐ LLVM 23 新增：下一代沙箱化向量化
    └── Passes/BottomUpVec.cpp, Legality.cpp
```

**图表 ①：LLVM Loop Vectorizer 四阶段流水线（飞腾 FTC862 标注失败点）**

```
┌──────────────────────────────────────────────────────────────────────────┐
│              LLVM Loop Vectorizer Pipeline (VPlan-native, LLVM 23)        │
│                                                                          │
│  [IR Loop]                                                               │
│     │                                                                    │
│     ▼                                                                    │
│  ① LEGALITY  (LoopVectorizationLegality.cpp:1933 canVectorize)           │
│     ├─ canVectorizeLoopNestCFG()   循环嵌套 CFG 检查                     │
│     ├─ canVectorizeWithIfConvert() 多基本块→单基本块谓词化               │
│     │     └─ blockNeedsPredication() :1436  ← 🔴飞腾无SVE谓词，受阻     │
│     ├─ canVectorizeInstrs()  :805  逐指令检查                            │
│     │     └─ isReductionPHI() :885  识别 reduction 变量                  │
│     └─ canVectorizeMemory() :1231                                       │
│           └─ LoopAccessInfo.canVectorizeMemory()                        │
│                 ├─ 依赖分析 (SCEV + alias)                               │
│                 └─ ← 🔴飞腾别名不明确→退化为 loop versioning             │
│     │                                                                    │
│     ▼                                                                    │
│  ② COST MODEL (LoopVectorizationCostModel, LoopVectorize.cpp)            │
│     ├─ computeMaxVF() :3574        ← 问 TTI.getRegisterBitWidth()        │
│     │     └─ 飞腾: FixedWidth=128(NEON), Scalable=scalable(0)(无SVE) 🔴  │
│     ├─ getVScaleForTuning() :1521  ← TTI.getVScaleForTuning()            │
│     ├─ canVectorizeReductions() :1247                                    │
│     │     └─ TTI.isLegalToVectorizeReduction()                          │
│     └─ selectVectorizationFactor() :4232  ← 遍历 VPlans 选最便宜 VF      │
│           └─ expectedCost(VF) × 寄存器压力 × 尾循环代价                  │
│     │                                                                    │
│     ▼                                                                    │
│  ③ VPLAN (VPlan.cpp + 10 个 VPlan*.cpp)                                  │
│     ├─ VPlanConstruction.cpp  构建计划                                   │
│     ├─ VPlanTransforms.cpp   :4383 getPartialReductionCost ← dotprod!    │
│     ├─ VPlanPredicator.cpp   谓词化方案                                  │
│     └─ VPlanVerifier.cpp     验证计划合法性                              │
│     │                                                                    │
│     ▼                                                                    │
│  ④ CODEGEN (InnerLoopVectorizer → IR)                                    │
│     ├─ 生成向量循环 + 标量余数循环                                       │
│     ├─ 插入运行时别名检查 (loop versioning)                              │
│     └─ 生成 reduction 树 (fmla / udot)                                   │
│     │                                                                    │
│     ▼                                                                    │
│  [向量化后的 IR]  → 交给后端 (E05 CodeGen) lower 成 NEON/SVE 指令        │
└──────────────────────────────────────────────────────────────────────────┘
```

**关键代码级锚点**：

- 头部注释（[实测-LoopVectorize.cpp:38-53]）白纸黑字引用了 5 篇论文：Nuzman & Henderson "Multi-platform Auto-vectorization"（reduction）、Karrenberg & Hack "Whole Function Vectorization"（uniformity）、Nuzman/Rosen/Zaks "Auto-Vectorization of Interleaved Data"（interleaved）、Zaks & Nuzman "Autovectorization in GCC - two years later"、Maleki et al. "An Evaluation of Vectorizing Compilers"。**这是向量化器的学术血统**——每一篇都对应一段代码逻辑。
- 第 9478 行（[实测]）：`if (!LVL.canVectorize(EnableVPlanNativePath))` —— Legality 的总入口。`EnableVPlanNativePath` 是 VPlan 原生路径开关，注释（行 28-34）说这是为了"外层循环向量化"准备的。
- 第 3574 行（[实测]）：`computeMaxVF(ElementCount UserVF, unsigned UserIC)` —— 最大向量宽度的计算起点，它问 TTI"你能给多宽的向量"。

**飞腾在这条流水线的失败点（已用 🔴 标注）**：① 谓词化受 NEON 无谓词寄存器拖累；② Scalable VF 被返回 0 砍掉；③ 别名不明确触发 loop versioning（下一节详述）。**这三点构成飞腾向量化的"半成功"画像**——不是完全失败，而是每个环节都差一口气。

---

### 2.2 Cost Model 怎么读 TTI——飞腾无 SVE 的代码级铁证

这是硬问题 1 的核心。`LoopVectorizationCostModel::computeMaxVF()` 决定向量宽度上限。它的关键一问是 TTI：

```cpp
// [实测-LoopVectorize.cpp:940] 声明
FixedScalableVFPair computeMaxVF(ElementCount UserVF, unsigned UserIC);

// [实测-LoopVectorize.cpp:3574] 定义起点
LoopVectorizationCostModel::computeMaxVF(ElementCount UserVF, unsigned UserIC) {
  // ... 内部会查询 TTI 的向量寄存器宽度 ...
}
```

而 TTI 的回答在 AArch64 后端（**这是飞腾命运的决定性代码**）：

```cpp
// [实测-AArch64TargetTransformInfo.cpp:3134-3156] —— 飞腾 FTC862 的命脉
TypeSize
AArch64TTIImpl::getRegisterBitWidth(TargetTransformInfo::RegisterKind K) const {
  switch (K) {
  case TargetTransformInfo::RGK_Scalar:
    return TypeSize::getFixed(64);
  case TargetTransformInfo::RGK_FixedWidthVector:
    if (ST->useSVEForFixedLengthVectors() &&
        (ST->isSVEAvailable() || EnableFixedwidthAutovecInStreamingMode))
      return TypeSize::getFixed(
          std::max(ST->getMinSVEVectorSizeInBits(), 128u));  // SVE 可用：≥128
    else if (ST->isNeonAvailable())
      return TypeSize::getFixed(128);                        // ← 飞腾走这里：128
    else
      return TypeSize::getFixed(0);
  case TargetTransformInfo::RGK_ScalableVector:
    if (ST->isSVEAvailable() || (ST->isSVEorStreamingSVEAvailable() &&
                                 EnableScalableAutovecInStreamingMode))
      return TypeSize::getScalable(128);                     // SVE：scalable(128)
    else
      return TypeSize::getScalable(0);                       // ← 飞腾走这里：0  🔴
  }
}
```

**这段代码的飞腾解读**：飞腾 FTC862 是 ARMv8.4-A，有 NEON（`isNeonAvailable() = true`），无 SVE（`isSVEAvailable() = false`）。因此：

- `RGK_FixedWidthVector` → `getFixed(128)`：固定宽度向量最多 128 位（16 字节 = 4×fp32 / 8×fp16 / 16×int8）。**这是飞腾向量化的硬上限。**
- `RGK_ScalableVector` → `getScalable(0)`：可变长向量宽度为 0。**Loop Vectorizer 看到 scalable 宽度为 0，直接放弃所有 scalable VF 候选。**

**对比 SVE 平台**（如 AWS Graviton3、富士通 A64FX、ARM v9 服务器）：`getScalable(128)`，意味着可以向量化到 `vscale × 128` 位（典型 256–2048 位）。**飞腾与 SVE 平台的向量宽度差是 2×–16×**，这不是算法能弥补的。

再看一个相关函数，`shouldMaximizeVectorBandwidth`（[实测-TTI.cpp:386-396]）：

```cpp
bool AArch64TTIImpl::shouldMaximizeVectorBandwidth(RegisterKind K) const {
  if (K == RGK_FixedWidthVector && ST->isNeonAvailable())
    return true;   // 飞腾走这里：鼓励用满 128 位
  return K == RGK_ScalableVector && ST->isSVEorStreamingSVEAvailable() && ...;
}
```

**飞腾的 consolation prize**：NEON 模式下 `shouldMaximizeVectorBandwidth` 返回 `true`，鼓励 Loop Vectorizer 用满 128 位（即 VF=4 for fp32）。所以飞腾不是"不向量化"，而是"只向量化到 128 位固定宽度"。飞腾 View_01 实测（`../../体系结构实验/View_01_Compiler/README.md`） `-O3` 生成 `fmla v.4s`（128 位 fp32 乘加）正是这个机制的结果。

**Cost Model 选 VF 的心脏**（[实测-LoopVectorize.cpp:4232] `selectVectorizationFactor`）：

```cpp
VectorizationFactor LoopVectorizationPlanner::selectVectorizationFactor() {
  InstructionCost ExpectedCost = CM.expectedCost(ElementCount::getFixed(1));
  // 标量基线成本
  VectorizationFactor ChosenFactor = ScalarCost;
  for (auto &P : VPlans) {                    // 遍历所有候选 VPlan
    for (unsigned I = 0; I < VFs.size(); I++) {
      ElementCount VF = VFs[I];
      InstructionCost C = CM.expectedCost(VF); // 向量成本
      // + VPlan 内的额外成本（谓词、运行时检查、register pressure）
      // 选 cost 最低的 VF
    }
  }
}
```

**飞腾在此处的隐性损失**：`expectedCost(VF)` 内部大量调 TTI 的 `getArithmeticInstrCost`、`getMemoryOpCost`、`getVectorInstrCost`。**这些函数的成本表对 FTC862 是不准的**——因为主线 LLVM 没有 FTC86x 的调度模型（[实测-Vectorize 目录 grep FTC86 零命中]，反向锚点）。飞腾用的是通用 Cortex-A 模型的近似成本，可能导致：(a) 一个本该向量化的循环被误判"不值得"（成本虚高）；(b) 一个向量化反而更慢的循环被误判"值得"（成本虚低）。**这就是飞腾 Expert_11 §3.2（`../../体系结构实验/Expert_11_Compiler_Research/README.md`） 强烈建议"提交 FTC86x 调度模型到主线 LLVM"的向量化侧理由**——填准成本表，是提升向量化质量性价比最高的工程动作。

---

### 2.3 Vector Predication（VP）扩展——为什么 `vp.*` intrinsic，与 SVE/RVV/AVX-512 统一（图表 ②）

这是硬问题 2，也是 LLVM 向量化最前沿的架构演进。

**问题的起源**：三类现代向量 ISA 的谓词/掩码机制语义相近但表达迥异：

| ISA | 谓词/掩码机制 | 可变长机制 | IR 表达（向量化前） |
|-----|------------|----------|----------------|
| ARM SVE | P0–P15 谓词寄存器（每元素 1 位） | `vscale` × 128 位（VLA） | `llvm.aarch64.sve.*` + `<vscale x 4 x i32>` |
| RISC-V V (RVV) | `v0.t`（单掩码寄存器） | AVL（application vector length） | `llvm.riscv.v.*` + `<vscale x 4 x i32>` |
| x86 AVX-512 | k0–k7 掩码寄存器（8 个） | 固定宽度（512/256/128） | `llvm.x86.avx512.*` + `<8 x double>` |

**痛点**：前端（Clang）和向量化器若要支持这三类，得写三套不同的 intrinsic 生成、三套成本模型、三套合法化。**这是 LLVM 历史上"每个后端各搞一套"的典型债**。

**VP 的解法**：引入一组统一的 `vp.*` intrinsic，每个都带两个特殊操作数——**mask**（掩码，哪些元素有效）和 **EVL**（Explicit Vector Length，显式向量长度，处理余数）。看真实定义（[实测-VPIntrinsics.def]，763 行）：

```cpp
// [实测-VPIntrinsics.def:77-84] 核心宏
#define BEGIN_REGISTER_VP(VPID, MASKPOS, EVLPOS, VPSD, LEGALPOS) ...
//   VPID    = intrinsic 名（如 vp_add）
//   MASKPOS = mask 操作数位置
//   EVLPOS  = 显式向量长度操作数位置

// [实测-VPIntrinsics.def:184] 整数 reduction
BEGIN_REGISTER_VP(vp_smin, 2, 3, VP_SMIN, -1)

// [实测-VPIntrinsics.def:360] 浮点 FMA
BEGIN_REGISTER_VP(vp_fma, 3, 4, VP_FMA, -1)

// [实测-VPIntrinsics.def:729] select/merge
BEGIN_REGISTER_VP(vp_select, std::nullopt, 3, VP_SELECT, -1)
```

**图表 ②：vp.* intrinsic 如何统一 SVE/RVV/AVX-512**

```
┌─────────────────────────────────────────────────────────────────────┐
│         一段条件加法，三种目标，一种 IR (vp.add)                      │
│                                                                     │
│  源 C:  for (i=0; i<n; i++) if (m[i]) c[i] = a[i] + b[i];          │
│                                                                     │
│  传统（无 VP，三套 intrinsic）:                                       │
│    SVE:     @llvm.aarch64.sve.add.nxv4i32(<nxv4i32>, <nxv4i1>)     │
│    RVV:     @llvm.riscv.vadd.mask.nxv4i32(<nxv4i32>, ..., <nxv4i1>)│
│    AVX512:  @llvm.x86.avx512.mask.vpadd.d.512(<8xi32>, <8xi1>, ...)│
│    ↑ 三套生成、三套 cost、三套 legalizer                            │
│                                                                     │
│  VP 统一 IR:                                                         │
│    %r = call <4 x i32> @llvm.vp.add.v4i32(                          │
│              <4 x i32> %a, <4 x i32> %b,                            │
│              <4 x i1>  %mask,        ; ← 谓词统一                    │
│              i32       %evl)          ; ← 显式向量长度统一            │
│    ↑ 一套生成，后端各自 lower                                       │
│                                                                     │
│  Lowering（后端各自翻译）:                                            │
│    SVE:     add z0.s, p0/m, z0.s, z1.s       ; p0 = mask            │
│    RVV:     vadd.vv v0, v1, v2, v0.t          ; v0.t = mask          │
│    AVX512:  vpaddd zmm0{k1}, zmm1, zmm2       ; k1 = mask            │
│    NEON(飞腾): add v0.4s, v1.4s, v2.4s        ; 无谓词→fold mask     │
│              + bsl v0, v2, vold, v0          ; 用 bit-select 模拟    │
└─────────────────────────────────────────────────────────────────────┘
```

**VP 在 LLVM 23 的实际覆盖**：实测 `grep BEGIN_REGISTER_VP VPIntrinsics.def` = **45 个 vp.* intrinsic**，覆盖：
- 整数运算：`vp_add/sub/mul/and/or/xor/shl/lshr/ashr/sdiv/udiv`（via 宏批量注册，[实测-:317, :472]）
- 整数 min/max：`vp_smin/smax/umin/umax`（[实测-:184-205]）
- 位操作：`vp_bswap/bitreverse/ctpop/fshl/fshr`（[实测-:220-274]）
- 饱和算术：`vp_sadd_sat/uadd_sat/ssub_sat/usub_sat`（[实测-:280-301]）
- 浮点：`vp_fneg/fabs/sqrt/fma/fmuladd/copysign/minnum/maxnum/minimum/maximum`（[实测-:342-402]）
- 浮点取整：`vp_ceil/floor/round/roundeven/roundtozero/rint/nearbyint`（[实测-:409-445]）
- 类型转换：`vp_ptrtoint/inttoptr/zext/sext/trunc/fptosi/...`（[实测-:472, :505 宏批量]）
- 内存：`vp.load/store/gather/scatter`（带 mask + EVL）
- 控制：`vp_select/merge`（[实测-:729-735]）
- 实验：`experimental_vp_splice/reverse`（[实测-:739-744]）

**飞腾与 VP 的关系（关键判断）**：飞腾无 SVE，`vp.*` intrinsic 仍有价值——因为 VP 是 IR 层抽象，最终 lower 到 NEON 时，后端会用 `bsl`（bitwise select）+ 标量尾循环模拟 mask + EVL。**代价是成本高 3–5 倍**（模拟一次 masked load 要 1 条 `cmp` + 1 条 `bsl` + 可能的标量回退）。所以飞腾上 `vp.*` 不会让向量化覆盖率提升，但会让**同一份代码能在飞腾和 SVE 平台上正确运行**——这对国产化软件栈"一份代码跨平台"有工程价值，但对性能无益。

**VP 的战略意义（对偶判断）**：VP 是 LLVM 对 RISC-V RVV 兴起的回应。RVV 的 VLA 语义与 SVE 高度相似，VP 让 LLVM 不必为 RVV 重写一遍向量化器。**MLIR 的 `vector` dialect 走了另一条路**（声明式 `vector.mask` + 渐进 lowering），两者哲学不同（见 §2.5 对偶表）。

---

### 2.4 SLP Vectorizer 在飞腾 NEON 上的覆盖率（图表 ③：Reduction 向量化前后）

硬问题 3。SLP（Superword-Level Parallelism）由 Larsen & Amarasinghe 2000 [论文] 提出，抓的是**基本块内 N 个独立同构标量运算**，打包成向量。与 Loop Vectorizer 互补：后者跨迭代，前者跨语句。

**SLP 在飞腾 NEON 的天然契合**：飞腾 NEON `<4 x float>` 正好 128 位，4 个独立 `float` 运算（如四元数乘法、颜色 RGBA 处理、SIMD 友好的 SOA 布局）能一次打包。

```c
// 经典 SLP 场景：四元数乘法（4 个独立标量乘法）
struct vec4 { float x, y, z, w; };
vec4 mul(vec4 a, vec4 b) {
    vec4 r;
    r.x = a.x * b.x;   // 独立
    r.y = a.y * b.y;   // 独立
    r.z = a.z * b.z;   // 独立
    r.w = a.w * b.w;   // 独立
    return r;
}
// SLP 打包成一条 NEON vmul v0.4s, v1.4s, v2.4s
```

**SLPVectorizer.cpp 的实现**（[实测]，~28000 行，LLVM 最大文件之一）：头部注释（[实测-SLPVectorizer.cpp:9-15]）说明它实现的是 **Bottom-Up SLP**，引用了 Rosen/Nuzman/Zaks "Loop-Aware SLP in GCC"。核心类是 `BoUpSLP`（Bottom-Up SLP，[实测-SLPVectorizer.cpp:1957]），从基本块底部向上扫描，构建 SLP 树。还有 `Look-ahead SLP`（[实测-:2670]）处理交换律运算的多种组合。

**SLP 的 cost model 同样依赖 TTI**：`canVectorizeLoads()`（[实测-SLPVectorizer.cpp:7485]）检查 load 链是否合法，`getVectorInstrCost` 估算插入/提取代价。**飞腾无专用调度模型时，SLP 的成本估算同样不准**——这是飞腾 SLP 覆盖率低于预期的根因。

**覆盖率估算（诚实标注）**：根据 SLP 在通用 C/C++ 代码上的经验 [推测-LLVM 测试集经验]：
- 纯计算密集（图形/AI/信号处理）：SLP 能覆盖 30–50% 的可向量化标量簇。
- 通用业务代码（控制流密集）：SLP 覆盖率 < 10%（簇太小不值得）。
- 飞腾 NEON 因固定 128 位，SLP 的"打包宽度"受限——4 个 float 是甜点，8 个 float 得拆两组。

**图表 ③：Reduction 向量化前后（飞腾 -Ofast 的 4× 机理）**

这是硬问题 7 的核心图示，解释飞腾 View_01（`../../体系结构实验/View_01_Compiler/README.md`） 实测的 `-O3 → -Ofast` 4× 加速。

```
┌──────────────────────────────────────────────────────────────────────┐
│   Reduction 向量化：IEEE 严格 (-O3) vs 重关联 (-Ofast)                │
│                                                                      │
│   源:  for (i=0;i<n;i++) sum += a[i]*b[i];   // float dot product   │
│                                                                      │
│ ① -O3 (IEEE 严格，RecurrenceDescriptor 不允许重排):                  │
│                                                                      │
│   向量化 VF=4，但单累加器（依赖链）:                                  │
│      fmla v0.4s, v1.4s, v2.4s   ; acc0 += a[0..3]*b[0..3]           │
│      fmla v0.4s, v3.4s, v4.4s   ; acc0 += a[4..7]*b[4..7] ← 等v0!   │
│      fmla v0.4s, v5.4s, v6.4s   ; ← 等v0!                           │
│      fmla v0.4s, v7.4s, v8.4s   ; ← 等v0!                           │
│   4-wide issue 只能发 1 个 NEON/cyc（依赖链），IPC ≈ 1               │
│   飞腾实测: 3.27 ms                                                  │
│                                                                      │
│ ② -Ofast (-O3 -ffast-math，允许 FP 重关联):                          │
│                                                                      │
│   拆 4 个独立累加器（无依赖链）:                                      │
│      fmla v0.4s, v1.4s, v2.4s   ; acc0 独立                          │
│      fmla v3.4s, v4.4s, v5.4s   ; acc1 独立 ✅                        │
│      fmla v6.4s, v7.4s, v8.4s   ; acc2 独立 ✅                        │
│      fmla v9.4s,v10.4s,v11.4s   ; acc3 独立 ✅                        │
│      ; 最后 4 路 horizontal add 合并                                  │
│   4-wide issue 发满 2 NEON 通道，IPC ≈ 3–4                           │
│   飞腾实测: 0.83 ms  ← 快 4×！                                       │
│                                                                      │
│   机理: (a+b)+c+d+e ≠ ((a+b)+(c+d))+... 重排后值变                    │
│         -ffast-math 放弃 IEEE 754 结合律保证                         │
│         LoopVectorizer 用 getArithmeticReductionCost 评估后认为值得   │
└──────────────────────────────────────────────────────────────────────┘
```

**这一刀切在哪里（代码级）**：`RecurrenceDescriptor`（识别 reduction 变量）+ `getArithmeticReductionCost`（[实测-VPlanRecipes.cpp:1171, 2950]）+ `canVectorizeFPMath`（[实测-LoopVectorize.cpp:9587]，调 `LoopVectorizationLegality::canVectorizeFPMath` [实测-Legality.cpp:1345]）。当 `-ffast-math` 关闭时，`canVectorizeFPMath` 检查 `FastMathFlags::allowReassoc`，若为 false 则 reduction 只能单累加器串行。

**飞腾工程教训（来自 E11）**：飞腾 View_01 实测（`../../体系结构实验/View_01_Compiler/README.md`） 的 `-Ofast` 4× 是飞腾 4-wide issue 红利的真正兑现。但代价是 IEEE 754 精度损失——金融/物理仿真代码绝不能全局开 `-ffast-math`，只能逐算子开（ML 推理的 matmul/softmax 可以，损失函数不行）。

---

### 2.5 对偶表：LLVM Loop Vectorizer vs GCC `tree-vectorizer` vs MLIR `vector` dialect

硬问题 4 的核心交付。三方都在做向量化，哲学迥异：

**对标表：三大向量化的设计哲学与覆盖对比**

| 维度 | LLVM Loop Vectorizer | GCC `tree-vectorizer` | MLIR `vector` dialect |
|------|---------------------|----------------------|----------------------|
| **历史起点** | LLVM 3.x（~2012），Nuzman 系 [论文-LoopVectorize.cpp:38] | GCC 4.0（2005），Zaks/Nuzman 系 [论文-LoopVectorize.cpp:49] | MLIR 2019（诞生），`vector` dialect 2020+ |
| **核心算法** | VPlan（计划驱动）+ cost model + Legality 三段式 | 数据引用向量（Data Reference Vector）+ 静态 cost | 声明式 `vector.contract`/`vector.transfer` + 渐进 lowering |
| **抽象层级** | LLVM IR（已 lowering 到 SSA 指令） | GIMPLE（GCC 中端 IR） | MLIR `vector` dialect（高于 LLVM IR，可降多层） |
| **驱动方式** | **运行时 cost model**（查 TTI，逐 VF 评估） | **静态启发式**（编译期规则 + `-fvect-cost-model`） | **声明式 + 模式匹配**（前端声明意图，编译器分解） |
| **谓词化** | VPlanPredicator + VP intrinsic（统一） | `mask_expand`/`cond_*`（GCC 内建） | `vector.mask` op（一等公民） |
| **可变长（VLA）** | `<vscale x N x T>` + ElementCount | RISC-V 后端单独处理 | `vector<__N_ x T>`（符号化维度） |
| **Loop versioning** | ✅ 标配（运行时别名检查） | ✅ 标配（`-ftree-loop-vectorize`） | ❌ 依赖下游（LLVM）做 |
| **SLP** | 独立 `SLPVectorizer` pass | 集成在 `tree-vectorizer`（Loop-Aware SLP）[论文-SLPVectorizer.cpp:15] | `vector.transpose`/`vector.shape_cast` |
| **飞腾（FTC862）支持** | ❌ 无专用调度模型（反向锚点） | ⚠️ PhyGCC 有 `FTC86x.md`（飞腾维护） | ❌ 飞腾未在 MLIR 栈定制 |
| **AI 推理适配** | 间接（经 MLIR→LLVM lowering） | 弱（HPC 用得多，AI 少） | ✅ **最强**（XLA/StableHPC 用它） |
| **代码规模** | LoopVectorize.cpp 9963 行 + VPlan×10 文件 | `tree-vectorizer.cc` + `tree-vect-*` ~15 文件 | `mlir/Dialect/Vector/` + transforms |
| **代表论文** | Nuzman&Rosen&Zaks interleaved; Karrenberg&Hack whole-fn | Zaks&Nuzman GCC two-years-later [论文-LoopVectorize.cpp:49] | Vasilache et al. MLIR vector (2020+) |

**关键判断**：
1. **LLVM 与 GCC 在传统向量化上旗鼓相当**——两者都源自同一批人（Nuzman/Rosen/Zaks 在 Intel/IBM 同时贡献 GCC 和 LLVM）。差异在工程细节：LLVM 的 VPlan 更现代，GCC 的 tree-vectorizer 更成熟稳定。飞腾选 GCC（PhyGCC）是历史路径依赖，非技术劣势。
2. **MLIR `vector` dialect 是 AI 时代的赢家候选**——它不在"循环"层做向量化，而在更高层声明张量运算意图（`vector.contract` = 矩阵乘），再渐进 lowering。这让 AI 编译器（XLA、Torch-MLIR、IREE）能生成比 Loop Vectorizer 更优的代码。**飞腾 NPU 若走 TVM/MLIR 栈，向量化主导权从 LLVM 转移到 MLIR**——这正是本项目 [断层② MLIR-core 融合裂痕](../改造蓝图_LLVM.md) 的核心。
3. **三者的融合趋势**：MLIR 最终 lowering 到 LLVM IR 时，仍会经过 Loop Vectorizer / SLP。所以不是"谁替代谁"，而是**分工**——MLIR 管高层张量，LLVM 管底层循环。

---

### 2.6 Legality 分析——alias analysis / loop dependence / memory disambiguation

硬问题 5。Legality 是向量化的第一道闸门（[图表 ①] 阶段①）。`LoopVectorizationLegality::canVectorize()`（[实测-Legality.cpp:1933]）的调用链：

```cpp
// [实测-LoopVectorizationLegality.cpp:1933] 总入口
bool LoopVectorizationLegality::canVectorize(bool UseVPlanNativePath) {
  if (!canVectorizeLoopNestCFG(TheLoop, UseVPlanNativePath)) return false;  // CFG
  if (!canVectorizeOuterLoop()) return false;
  if (NumBlocks != 1 && !canVectorizeWithIfConvert()) return false;  // 多块→谓词化
  if (!canVectorizeInstrs()) return false;                           // 逐指令
  if (!canVectorizeMemory()) return false;                          // 内存依赖 ← 重头戏
  return true;
}
```

**内存依赖分析（`canVectorizeMemory`，[实测-Legality.cpp:1231]）** 调 `LoopAccessInfo`（LAA），后者是 LLVM 循环依赖分析的集大成者：

- **TBAA（Type-Based Alias Analysis）**：基于 C/C++ 类型规则推断不重叠。`float *a` 和 `int *b` 默认不别名（严格别名规则）。但 `-fno-strict-aliasing` 会让 TBAA 失效——飞腾 Expert_11 §2.3.1（`../../体系结构实验/Expert_11_Compiler_Research/README.md`） 提醒：**这是飞腾向量化失败最隐蔽的杀手**。
- **SCEV（Scalar Evolution）**：分析下标演化，`a[i]` 与 `a[i+1]` 的距离可计算 → 证明不重叠。
- **运行时检查（loop versioning）**：静态分析失败时，插入运行时指针比较（下一节详述）。

**循环携带依赖**：`isReductionPHI`（[实测-Legality.cpp:885]）识别 reduction 变量。依赖距离（dependence distance）决定生死——距离 0 独立可并行；距离 1 且 reduction 可重排；距离 1 且 recurrence（如 Horner）不可向量化。飞腾 Expert_11 §2.3.2（`../../体系结构实验/Expert_11_Compiler_Research/README.md`） 的 Horner 案例正是 distance-1 recurrence。

---

### 2.7 Loop Versioning——飞腾代码的"半成功"常态

硬问题 6。当静态别名分析失败时，Loop Vectorizer 不放弃，而是生成**双版本循环**：

```c
// 原循环
void f(float *a, float *b, float *c, int n) {
    for (int i = 0; i < n; i++) c[i] = a[i] + b[i];
}

// Loop Vectorizer 生成的双版本（伪 IR）
if (c+n <= a || a+n <= c) {       // 运行时别名检查：不重叠？
    // 向量循环（NEON fmla v.4s）
    for (int i = 0; i < n; i += 4)
        c[i:i+3] = a[i:i+3] + b[i:i+3];   // ← 飞腾想要的
} else {
    // 标量回退循环（无 NEON）
    for (int i = 0; i < n; i++)
        c[i] = a[i] + b[i];                // ← 飞腾最怕的
}
```

**飞腾的"半成功"画像**（来自 Expert_11 §2.3.1（`../../体系结构实验/Expert_11_Compiler_Research/README.md`））：
- **好消息**：运行时检查开销极小（1 次 `cmp` + 1 次分支，飞腾 1–2 周期），循环长时摊薄。分支预测器在 `c` 与 `a/b` 实际不重叠的常见情况下会正确预测走向量循环。
- **坏消息**：一旦运行时发现别名（`c` 真的与 `a` 重叠），飞腾走标量回退，**彻底丢掉 NEON**。这是飞腾代码 `-fopt-info-vec` 最常报的 "loop versioned for vectorization because of possible aliasing"——编译器"尽力了"，但留下了性能悬崖。
- **修法（飞腾实操）**：加 `restrict` 关键字（`float * restrict c`），编译器直接信任，跳过检查，纯 NEON。或用 `__builtin_assume_aligned` + `restrict` 组合。

**工程教训**：飞腾服务器代码（高并发网络栈、数据库）大量指针别名不明确，loop versioning 是常态。**飞腾开发者最该养成的习惯是：性能敏感的循环，必加 `restrict`**。这一条比任何 `-march` 调优都有效。

---

### 2.8 Masked Load/Store / Gather-Scatter：NEON vs SVE vs AVX-512

硬问题 8。这是谓词化的硬件落地，也是飞腾与 SVE 平台差距最直观的地方。

| 操作 | AVX-512 | ARM SVE | RISC-V RVV | **NEON（飞腾）** |
|------|---------|---------|-----------|---------------|
| **Masked load** | `vmovdqu64 zmm{k1}, [rax]` | `ld1w {z0.s}, p0/z, [x0]` | `vle32.v v0, (a0), v0.t` | ❌ **无原生**，模拟：`cmp` + `bitwise select` |
| **Masked store** | `vmovntps {k1}, [rax], zmm0` | `st1w {z0.s}, p0, [x0]` | `vse32.v v0, (a0), v0.t` | ❌ 同上 |
| **Gather**（间接读） | `vgatherdps zmm{k1}, [base+zmm_idx]` | `ld1sw {z0.s}, p0, [x0, z1.s]` | `vluxei32.v` | ❌ 标量逐元素，无向量化 |
| **Scatter**（间接写） | `vscatterdps` | `st1sw {z0.s}, p0, [x0, z1.s]` | `vsuxei32.v` | ❌ 标量逐元素 |
| **Compress/Expand** | `vpcompressd` | `compact z0.s, p0, z1.s` | `vcompress.vm` | ❌ 无 |

**飞腾缺失的后果**：
- **稀疏矩阵 / 哈希表 / 图遍历**（`a[idx[i]]` 间接寻址）：飞腾 100% 退化为标量。SVE/AVX-512 平台能向量化。
- **条件流处理**（`if (pred[i]) out[k++] = in[i]`）：飞腾用 `cmp` + `bsl` 模拟，成本 3–5×，向量化收益被模拟开销吃掉。
- **AI 推理的 attention/embedding gather**：这是 LLM 推理的热点，飞腾无 gather → 只能手写或退标量。

**这就是飞腾向量化覆盖率 20–30%（NEON）vs SVE 平台 40–60% 的物理根因**（飞腾 Expert_11 §2.3.3（`../../体系结构实验/Expert_11_Compiler_Research/README.md`） 估算）——不是算法笨，是 ISA 没给硬件武器。VP intrinsic（§2.3）在飞腾上 lower 时，也受此限制——`vp.load` 带 mask 的版本在 NEON 上展开成 `cmp`+`bsl`，性能收益有限。

---

### 2.9 VPlan——LLVM 16+ 的新设计与外层循环向量化

硬问题 9。VPlan（Vectorization Plan）是 Loop Vectorizer 的架构重写，从 2017 年 LLVM 邮件列表提议，到 LLVM 23 已**全面接管**——实测 `llvm/lib/Transforms/Vectorize/` 下有 10 个 VPlan* 文件：`VPlan.cpp`、`VPlanRecipes.cpp`（配方，描述如何生成 IR）、`VPlanTransforms.cpp`（计划变换，含 dotprod cost）、`VPlanAnalysis.cpp`、`VPlanConstruction.cpp`、`VPlanVerifier.cpp`、`VPlanUtils.cpp`、`VPlanPredicator.cpp`（谓词化方案）、`VPlanUnroll.cpp`、`VPlanSLP.cpp`（VPlan 内嵌 SLP）。

**VPlan 解决了什么老问题**：旧 Loop Vectorizer 是"边算边生成 IR"，无法表达复杂决策（外层循环向量化、嵌套向量化、多种谓词化方案比较）。VPlan 把决策与生成分离——**先生成一个完整的"计划"（plan），包含向量循环的结构、recipe 列表、谓词化方案，再执行计划生成 IR**。

```cpp
// [实测-LoopVectorize.cpp:28-34] 头部注释
// There is a development effort going on to migrate loop vectorizer to the
// VPlan infrastructure and to introduce outer loop vectorization support.
// ... we temporarily introduced the VPlan-native vectorization path ...
```

**VPlan 的工程价值**：
1. **外层循环向量化**：嵌套循环（如 GEMM 的三重循环）可以选择向量化哪一层。VPlan 能表达"外层向量化 + 内层标量"的方案。飞腾 Lab05（`../../体系结构实验/Lab05_并行与SIMD/README.md`） GEMM 优化的 `ikj` 循环交换，理论上 Loop Vectorizer 配合 VPlan 能自动选对层——但实际常需手写 micro-kernel。
2. **谓词化方案比较**：`VPlanPredicator.cpp` 能生成多种谓词化方案（fold-tail-by-masking、scalar-epilogue），cost model 选最优。飞腾无 SVE 时，谓词化方案受限，但仍比旧架构灵活。
3. **dotprod pattern 识别**：`VPlanTransforms.cpp:4383` 的 `getPartialReductionCost`（[实测]）——这正是 UDOT 选出的 cost 接口（见 §2.10）。

**VPlan 的代价**：复杂性爆炸。LoopVectorize.cpp 从早期 ~3000 行膨胀到 9963 行，加上 10 个 VPlan* 文件，总代码量是旧向量化器的 5×。这是 LLVM "工程债"的典型——为了表达力牺牲了简洁性。

---

### 2.10 飞腾 UDOT 选不出——LoopVectorizer 是否主动找 dotprod pattern？

硬问题 10。这是飞腾 INT8 推理的命门。飞腾 Expert_11 §2.3.4（`../../体系结构实验/Expert_11_Compiler_Research/README.md`） 案例：

```c
int32_t dot_int8(const int8_t *a, const int8_t *b, int n) {
    int32_t sum = 0;
    for (int i = 0; i < n; i++)
        sum += a[i] * b[i];   // int8 * int8
    return sum;
}
```

**为什么默认选不出 UDOT**：Clang 前端把 `int8 * int8` 提升为 `int32`（C 整型提升规则），IR 变成 `sext i8 → i32; mul i32`。Loop Vectorizer 向量化成 `<4 x i32>` 乘加，选出 `smull`（int16→int32 长乘），**而非 UDOT**（`<16 x i8>` → `<4 x i32>` 点积累加）。

**LLVM 23 的改进**：`VPlanTransforms.cpp` 里有 `getPartialReductionCost`（[实测-:4383, 4449]）和 `getExtendedReductionCost`（[实测-:4391]）——这两个 cost 接口正是为 dotprod / matrix-multiply pattern 设计的。它们能让 cost model 评估"如果用 UDOT 做这个 reduction，成本是多少"。

**但问题在飞腾侧**：`getPartialReductionCost` 的答案**完全取决于 TTI 是否声明 FTC862 支持 dotprod**。飞腾是 ARMv8.4，有 UDOT（dotprod 扩展），但主线 LLVM 的 AArch64 后端需要 `-march=armv8.4-a+dotprod` 或 `-mcpu=<支持dotprod的cpu>` 才会启用。**飞腾若没在编译选项里指定，UDOT 永远选不出**。

**飞腾的实操路径**：
1. **编译选项**：`-march=armv8.4-a+dotprod` 或 PhyGCC/PhyClang 默认开（飞腾 Expert_11 §2.4（`../../体系结构实验/Expert_11_Compiler_Research/README.md`） 提到 PhyGCC 默认开 UDOT 模式匹配）。
2. **手写 intrinsic**（最可靠）：飞腾 Expert_05（`../../体系结构实验/Expert_05_AI_Inference/README.md`） 的 16.9× 加速全部来自手写 `vdotq_s32`。
3. **等 LLVM 上游改进**：`getPartialReductionCost` 是 2023+ 的新机制，飞腾用新 LLVM 版本（≥17）才能受益。飞腾 Yocto 用 LLVM 13（[实测-phytium_repos]），拿不到这个红利。

**诚实判断**：LoopVectorizer 在**主动找** dotprod pattern（VPlanTransforms 证明），但找到后能否选出 UDOT，**取决于 TTI 声明 + 编译选项 + LLVM 版本**三重条件。飞腾在 2026 年的现状是：硬件有 UDOT，编译器栈（LLVM 13）太旧，自动向量化基本选不出，必须手写。**这是飞腾 INT8 算力"理论上有、实际拿不到"的编译器侧根因**。

---

## 3. 设计决策评估：LLVM 向量化器哪些认可、哪些该改、飞腾工程教训

### 3.1 LLVM 做对的事（认可）

1. **Legality–Cost–Transform 三段式架构**——这是教科书级的好设计。合法性、成本、生成分离，每段可独立测试、独立改进。`LoopVectorizationLegality.cpp` 单独成文件就是明证。
2. **VPlan 的引入**——虽然复杂，但它让 LLVM 向量化器具备了表达"外层循环向量化""多种谓词化方案比较"的能力，这是 GCC tree-vectorizer 至今仍在追赶的。VPlan 是 LLVM 相对 GCC 的**架构代差优势**。
3. **VP intrinsic 的统一抽象**——面对 SVE/RVV/AVX-512 三套机制，VP 用 mask + EVL 统一 IR 表达。这是工程远见，为 RISC-V 时代的向量化铺路。
4. **Loop versioning 作为兜底**——静态别名分析失败时不放弃，生成运行时检查双版本。这是"宁可多生成代码也要尝试向量化"的正确工程哲学。
5. **interleaved access 向量化**（Nuzman/Rosen/Zaks [论文]）——`a[0],b[0],c[0],a[1],b[1],c[1]` 这种交错布局能自动识别并打包。飞腾 NEON 的 `ld3`/`ld4` 指令正是为此设计。

### 3.2 LLVM 该改的事（可执行建议）

1. **VPlan 的复杂度失控**——LoopVectorize.cpp 9963 行 + 10 个 VPlan* 文件，新人上手门槛极高。建议：(a) 更完善的 VPlan 文档（当前只有 `docs/VectorizationPlan.rst`，远远不够）；(b) VPlan 的可视化工具（`-view-vplan` 已有但简陋）。
2. **Cost Model 的可调试性**——当前调 cost model 全靠 `-debug-only=loop-vectorize` 输出海量日志。建议：结构化的 cost 报告（JSON 格式），方便飞腾这类厂商填准 TTI。
3. **SLPVectorizer.cpp 28000 行巨兽**——单文件过大，应按功能拆分（cost、tree-building、codegen 分文件）。
4. **VP intrinsic 在 NEON 的 lowering 质量差**——飞腾无 SVE 时，VP 的 masked load/store lower 成 `cmp`+`bsl`，成本高。应优化 NEON 的 VP lowering，或明确文档标注"NEON 上 VP 性能折损"。

### 3.3 飞腾工程教训（锁死与可改）

**锁死（无解）**：
1. **无 SVE 谓词寄存器**——条件循环向量化覆盖率被砍一半。ISA 层级缺失，编译器无法补。要解只能等 D4000 补 SVE（受 ARM v9 授权限制，见飞腾 Expert_21（`../../体系结构实验/Expert_21_AI_Positioning/README.md`））。
2. **无 gather/scatter**——稀疏/间接寻址循环 100% 退标量。同上，ISA 锁死。
3. **NEON 固定 128 位**——VF 硬上限，无 scalable 红利。

**可改（工程动作）**：
1. **提交 FTC86x 调度模型到主线 LLVM**（与飞腾 Expert_11 §3.2（`../../体系结构实验/Expert_11_Compiler_Research/README.md`） 一致）——让 cost model 对飞腾准确，是提升向量化质量性价比最高的动作。
2. **PhyClang 默认开 `+dotprod+fp16`**——确保 UDOT/FP16 算力默认可用，而非要用户手写 `-march`。
3. **升级 Yocto LLVM 到 ≥17**——飞腾 Yocto 用 LLVM 13（[实测]），拿不到 VPlanTransforms 的 dotprod cost 改进、VP 的成熟支持。
4. **文档化"飞腾向量化最佳实践"**——`restrict` 必加、`-ffast-math` 逐算子开、UDOT 用 intrinsic、loop versioning 的性能悬崖。这些是飞腾开发者最该知道的，但飞腾 SDK 文档罕有提及。

---

## 4. 这一视角的盲区与反方（诚实段，强制）

### 4.1 向量化器视角看不见什么

1. **看不见硬件微架构**——cost model 是查表（TTI），表准不准取决于厂商填表。飞腾 FTC862 的真实 NEON 吞吐（2 通道/cycle）、L1D 延迟（4 周期），若没填进 TTI，cost model 就是瞎猜。**这是飞腾向量化质量低于预期的核心根因——不是算法问题，是填表问题**。
2. **看不见运行时数据**——向量化器是静态分析。一个"编译器认为值得向量化"的循环，可能因为运行时 cache miss、分支预测失败，实际比标量慢。这要靠 PGO（Profile-Guided Optimization）补，但飞腾生态 PGO 工具链不成熟。
3. **看不见跨函数/跨 TU**——向量化器只看一个循环。跨函数的内联（LTO）能让更多循环暴露，但飞腾若没开 LTO，跨函数的向量化机会全丢。
4. **看不见手写汇编的优势**——AI 推理的热点（GEMM/Attention）都是手写汇编或 intrinsic，向量化器覆盖率再高也碰不到这些。**向量化器的价值在"长尾"——非热点的 90% 代码，不是冠军算子**。

### 4.2 反方观点：自动向量化在 AI 时代已过时

一个激进的反方：**2026 年，自动向量化是"上个时代的优化"，AI 推理时代的热点全靠手写/intrinsic/MLIR，投资 Loop Vectorizer 不如投资 MLIR `vector` dialect 和手写算子库**。论据：
- LLM 推理的 GEMM/Attention，没有任何一个生产部署靠 LLVM Loop Vectorizer——全是 cuBLAS/oneDNN/手写 NEON。
- 向量化器的边际收益趋零：`-O2` 到 `-O3`（开向量化）在通用代码上只快 ~2%（飞腾 View_01（`../../体系结构实验/View_01_Compiler/README.md`） 实测 3.34→3.27 ms）。
- MLIR 在更高层做张量级优化，lowering 到 LLVM 时向量化已基本完成，Loop Vectorizer 只是"扫尾"。

**这个反方有道理但不完全对**：向量化器的价值在**长尾与通用代码**——飞腾服务器跑的数据库/网络栈/中间件，90% 是通用 C/C++，没人手写优化。向量化器把这 90% 从 `-O0` 拉到 `-O2/-O3`，整体性能提 3–4×。**向量化器不是冠军，是基础设施。基础设施烂，冠军也跑不快**。且 LLVM Loop Vectorizer 的技术（cost model、legality、VPlan）是 MLIR `vector` dialect 的知识基础——放弃 Loop Vectorizer 等于放弃人才储备。

---

## 5. 与其他视角对偶（一致 / 冲突，强制）

### 5.1 一致（互相印证）

- **与 [E03 Pass 框架](../Expert_03_Pass_Framework/README.md) 一致**：Loop Vectorizer / SLP Vectorizer 是 New PM 下 `PassInfoMixin` 的标准变换 Pass，返回 `PreservedAnalyses`。E03 讲 Pass 骨架，本 Expert 讲骨架上跑的具体算法。两者一致：New PM 的精确分析失效让向量化器能复用 `LoopAccessInfo`、`ScalarEvolution` 而不必每次重算。
- **与 [E04 中端优化](../Expert_04_Middle_End_Opt/README.md) 一致**：Loop Vectorizer 依赖 LICM（循环不变量外提）、LoopUnroll（展开触发向量化）等中端 Pass 铺路。E04 讲"中端边际收益趋零"，但向量化是中端的**例外**——它仍是 `-O3` 相对 `-O2` 的主要增益来源（飞腾 View_01 实测 3.34→3.27 ms）。
- **与 [E05 CodeGen](../Expert_05_CodeGen_SelectionDAG_GlobalISel/README.md) 一致**：向量化器生成 IR 后，由 SelectionDAG/GlobalISel lower 成 NEON/SVE 指令。UDOT 能否最终选出，取决于 SelectionDAG 的 pattern match（E05）+ 向量化器的 cost（本 Expert）两层。两视角互为因果。
- **与飞腾 Expert_11（`../../体系结构实验/Expert_11_Compiler_Research/README.md`） 一致**：E11 §2.3 给向量化失败的飞腾实测案例，本 Expert 给 LLVM 源码级机理。E11 是现象，本 Expert 是根因。E11 说"UDOT 选不出"，本 Expert 指出是 `getPartialReductionCost` + TTI 声明 + LLVM 版本三重条件。

### 5.2 冲突（视角打架）

- **与 [E11 GPU/异构后端](../Expert_11_GPU_Heterogeneous_Backend/README.md) 部分冲突**：E11 论证"GPU/异构是 AI 算力未来"，本 Expert 暗示"CPU 向量化仍是基础"。在飞腾无 GPU 的现实下，向量化器是飞腾 CPU 算力的唯一自动化来源——但 E11 会说"CPU 向量化再好也比不过 GPU/NPU 专用算力"。**这是"通用基础设施 vs 专用加速器"的路线之争**，飞腾的处境是两者都缺。
- **与 MLIR `vector` dialect 路线潜在冲突**：MLIR 派认为"循环级向量化是旧范式，张量级 `vector.contract` 才是未来"。本 Expert 反驳：MLIR 最终 lowering 到 LLVM IR，仍经过 Loop Vectorizer 扫尾；且非 AI 代码（通用 C/C++）MLIR 不管，只能靠 Loop Vectorizer。**两者是分工不是替代**，但 MLIR 确实在蚕食 Loop Vectorizer 的"AI 算子"地盘。
- **与飞腾 Expert_21 AI 算力战略家（`../../体系结构实验/Expert_21_AI_Positioning/README.md`） 部分冲突**：E21 说"飞腾无 BF16/I8MM/SVE 是战略伤疤，AI 算力锁死"。本 Expert 部分认同（ISA 锁死），但反驳"编译器无用论"：即便无 SVE，若把 NEON 向量化覆盖率从 20% 拉到 35%（填准 TTI + 用户教育 + `restrict`），飞腾通用代码还能再榨 1.5–2×。**E21 是战略悲观，本 Expert 是工程乐观**。

---

## 6. 参考文献（分级标注，≥15 条，含 ≥5 论文/书）

### 里程碑论文与书（[论文]/[书]）
1. **[论文]** Larsen & Amarasinghe. "Exploiting Superword Level Parallelism with Multimedia Instruction Sets." *PLDI* 2000. —— SLP 向量化的开山之作（SLPVectorizer.cpp 的理论基础）。
2. **[书]** Allen & Kennedy. *Optimizing Compilers for Modern Architectures*. Morgan Kaufmann, 2001. —— 循环变换、依赖分析的奠基（向量化合法性分析的学术源头）。
3. **[论文]** Nuzman & Henderson. "Multi-platform Auto-vectorization." —— Reduction 向量化（[实测-LoopVectorize.cpp:38] 头部引用）。
4. **[论文]** Karrenberg & Hack. "Whole Function Vectorization." —— Uniformity 检查（[实测-LoopVectorize.cpp:41] 引用）。
5. **[论文]** Nuzman, Rosen & Zaks. "Auto-Vectorization of Interleaved Data for SIMD." —— Interleaved access 向量化（[实测-LoopVectorize.cpp:44] 引用）。
6. **[论文]** Zaks & Nuzman. "Autovectorization in GCC - two years later." —— GCC tree-vectorizer 设计（[实测-LoopVectorize.cpp:49] 引用，对偶参考）。
7. **[论文]** Rosen, Nuzman & Zaks. "Loop-Aware SLP in GCC." —— Bottom-Up SLP 的 GCC 版（[实测-SLPVectorizer.cpp:15] 引用）。
8. **[论文]** Maleki, Gao, Garzaran, Wong & Padua. "An Evaluation of Vectorizing Compilers." *PLDI* 2011. —— 向量化器覆盖率评估（[实测-LoopVectorize.cpp:51] 引用）。
9. **[论文]** Vasilache et al. "Tensor Comprehensions / MLIR vector dialect." 2019-2023. —— MLIR 向量化（对偶参考）。
10. **[书]** Muchnick. *Advanced Compiler Design and Implementation*. MK, 1997. —— 依赖分析、循环变换（Ch.17-18）。

### LLVM 官方文档与 RFC（[官方]/[RFC]）
11. **[官方]** LLVM Project. "VectorizationPlan.rst." `llvm/docs/VectorizationPlan.rst`. —— VPlan 设计文档。
12. **[官方]** LLVM Project. "Vector Predication RFC." `llvm.org` Discourse (2019-2020). —— VP intrinsic 提案（`vp.*` 统一 SVE/RVV/AVX-512）。
13. **[官方]** LLVM Project. `llvm/include/llvm/IR/VPIntrinsics.def`（763 行，45 个 vp.* intrinsic）。[实测-本项目]
14. **[官方]** LLVM Project. "Auto-Vectorization in LLVM." `llvm.org/docs/Vectorizers.html`. —— Loop Vectorizer / SLP 用户文档。

### 代码级实测（[实测]）
15. **[实测]** `OpenXiangShan/llvm-project`（LLVM 23.0.0git）`llvm/lib/Transforms/Vectorize/LoopVectorize.cpp`（9963 行）头部论文引用（:38-53）、`computeMaxVF`（:3574）、`selectVectorizationFactor`（:4232）、`canVectorizeReductions`（:1247）。
16. **[实测]** 同上 `llvm/lib/Target/AArch64/AArch64TargetTransformInfo.cpp:3134` `getRegisterBitWidth`（NEON→128 / 无 SVE→scalable(0) 的飞腾命脉）、`:386` `shouldMaximizeVectorBandwidth`。
17. **[实测]** 同上 `llvm/lib/Transforms/Vectorize/LoopVectorizationLegality.cpp:1933` `canVectorize`、`:1231` `canVectorizeMemory`、`:885` `isReductionPHI`。
18. **[实测]** 同上 `llvm/lib/Transforms/Vectorize/VPlanTransforms.cpp:4383` `getPartialReductionCost`（dotprod pattern cost 接口）。
19. **[实测]** `grep -rn "FTC86\|Phytium" llvm/lib/Transforms/Vectorize/` = **零命中**（反向锚点：主线向量化器无飞腾感知）。

### 飞腾工程实证（[实测]/[报告]）
20. **[实测]** 飞腾项目 View_01_Compiler（`../../体系结构实验/View_01_Compiler/README.md`）：`-O0..-Ofast` 在 D3000M 上 dot_product 实测（-O3 3.27ms → -Ofast 0.83ms，4×）。
21. **[实测]** 飞腾项目 Expert_11_Compiler_Research §2.3（`../../体系结构实验/Expert_11_Compiler_Research/README.md`）：向量化失败诊断（别名/依赖/无SVE/UDOT）。
22. **[实测]** 飞腾项目 Lab05_并行与SIMD（`../../体系结构实验/Lab05_并行与SIMD/README.md`）：NEON GEMM 优化全栈（40 GFLOPS/core 理论）。
23. **[实测]** 飞腾项目 Expert_05_AI_Inference（`../../体系结构实验/Expert_05_AI_Inference/README.md`）：UDOT 16.9× 加速（手写 intrinsic）。
24. **[报告]** 飞腾 `phytium_repos` Yocto LLVM recipe（`PV = "13.0.1"`）。[实测-phytium_repos]

### 标准
25. **[标准]** ARM Limited. *ARM ARM DDI 0487*（ARMv8.x）。—— NEON/SVE/dotprod 指令集权威。

---

## 7. 延伸阅读（项目内引用 + 外部）

### 项目内（对偶视角）
- [E03 Pass 框架](../Expert_03_Pass_Framework/README.md) —— 向量化器跑在 New PM 骨架上，PreservedAnalyses 决定向量化后哪些分析失效。
- [E04 中端优化](../Expert_04_Middle_End_Opt/README.md) —— LICM/LoopUnroll 为向量化铺路；MLIR-core 融合裂痕（断层②）。
- [E05 CodeGen](../Expert_05_CodeGen_SelectionDAG_GlobalISel/README.md) —— 向量化后的 IR 经 SelectionDAG lower 成 NEON/SVE；UDOT pattern match。
- [E08 AArch64 后端](../Expert_08_AArch64_Backend/README.md) —— `AArch64TargetTransformInfo.cpp` 的 TTI 实现（本 Expert 反复引用）。
- [E10 RISC-V 后端](../Expert_10_RISCV_Backend/README.md) —— RVV 可变长向量与 SVE 的对偶，VP intrinsic 的另一受益者。
- [E11 GPU/异构后端](../Expert_11_GPU_Heterogeneous_Backend/README.md) —— GPU 向量化 vs CPU 向量化的路线之争。
- 飞腾 Expert_11（`../../体系结构实验/Expert_11_Compiler_Research/README.md`） —— 向量化失败的飞腾实测案例（本 Expert 是其源码级深化）。
- 飞腾 View_01（`../../体系结构实验/View_01_Compiler/README.md`） —— `-O` 等级实测数据来源。

### 外部资源
- **LLVM Vectorizers 文档**（llvm.org/docs/Vectorizers.html）—— Loop / SLP 向量化用户指南。
- **VectorizationPlan.rst**（llvm/docs/）—— VPlan 设计文档（偏简陋，需配合源码）。
- **VP RFC**（LLVM Discourse 2019-2020）—— Vector Predication 提案讨论。
- **GCC tree-vectorizer 文档**（gcc.gnu.org/onlinedocs/gccint/Tree-SSA.html）—— 对偶参考。
- **MLIR Vector dialect**（mlir.llvm.org/docs/Dialects/Vector/）—— 张量级向量化（对偶）。
- **llvm-tutor**（github.com/banach-space/llvm-tutor）—— 现代 Pass 教程。

---

## § 领域方法论与资源（不只 LLVM，给所有做自动向量化的工程师）

> 本章把本 Expert 的 LLVM 向量化分析上升为**任何 SIMD/SVE/RVV/AVX 向量化从业者可复用的方法**。LLVM 是主案例，方法普适。通用编译器资源见 [`领域资源库_LLVM.md`](../领域资源库_LLVM.md)。

### 方法论一：向量化的"能不能—值不值—怎么做"三问法

诊断任何"为什么没向量化"的问题，按三段排查：
1. **能不能（Legality）**：用 `-Rpass-analysis=loop-vectorize`（LLVM）或 `-fopt-info-vec-missed`（GCC）看合法性拒绝原因。常见：循环携带依赖、别名不明确、不可计算的 trip count、函数调用。
2. **值不值（Cost Model）**：用 `-debug-only=loop-vectorize`（LLVM debug build）看 cost model 决策。常见：向量化成本高于标量（寄存器压力、尾循环开销）。
3. **怎么做（Codegen）**：用 `objdump -d` 看最终是否生成 SIMD 指令。常见：向量化了但 lower 成非最优指令（如选 `mul`+`add` 而非 `udot`）。

### 方法论二：提升向量化覆盖率的工程清单

按性价比排序：
1. **加 `restrict`**（最便宜，收益最大）——消除别名不确定，跳过 loop versioning。
2. **数据布局对齐**（`__builtin_assume_aligned`）——让向量化器用对齐 load/store。
3. **`-O3 -ffast-math`（逐算子）**——开 reduction 重关联，FP 循环 4×（飞腾 View_01 实测）。
4. **`-march=<full>`**（开全扩展）——飞腾 `-march=armv8.4-a+dotprod+fp16` 让 UDOT/FP16 可选。
5. **循环规范化**（可计算 trip count、单进单出、无 early return）——减少 legality 拒绝。
6. **SOA 布局**（Structure of Arrays）——让 SLP 能打包同构标量。
7. **PGO（Profile-Guided）**——告诉向量化器哪些循环热，优先向量化。

### 方法论三：SIMD ISA 能力矩阵（向量化硬件上限）

| 能力 | NEON（飞腾） | SVE | RVV | AVX-512 |
|------|:--------:|:---:|:---:|:-------:|
| 固定宽度向量 | ✅ 128b | ✅ | ✅ | ✅ 512b |
| 可变长（VLA） | ❌ | ✅ | ✅ | ❌ |
| 谓词/掩码 | ❌（模拟） | ✅ P0–P15 | ✅ v0.t | ✅ k0–k7 |
| Gather/Scatter | ❌ | ✅ | ✅ | ✅ |
| Compress/Expand | ❌ | ✅ | ✅ | ✅ |
| FP16 | ✅（v8.4） | ✅ | ⚠️ | ✅ |
| BF16 | ❌（飞腾缺） | ✅（v8.6） | ⚠️ | ✅ |
| INT8 点积（dotprod） | ✅ UDOT | ✅ | ✅ | ✅ VNNI |
| 矩阵乘（i8mm/bf16mmla） | ❌（飞腾缺） | ✅（v8.6） | ⚠️ | ❌ |

**判断法**：向量化器的"高档武器"取决于 ISA 能力。NEON（飞腾）只有基础武器，覆盖率天花板 20–30%；SVE/AVX-512 有全套，覆盖率 40–60%。**这是硬件决定的，编译器无法跨越**。

### 向量化专属资源

> 通用编译器资源见 [`领域资源库_LLVM.md`](../领域资源库_LLVM.md) §3；以下为**自动向量化专属**。

**📚 必读论文/书**
- ⭐ Larsen & Amarasinghe 2000（SLP 开山）
- ⭐ Allen & Kennedy 2001（循环变换圣经）
- ⭐ Nuzman 系列（reduction / interleaved / multi-platform，Loop Vectorizer 学术血统）
- 🔥 Maleki et al. 2011（向量化器覆盖率评估，PLDI）

**🔧 工具与诊断**
- `clang -Rpass=vectorize` / `clang -Rpass-missed=vectorize` / `clang -Rpass-analysis=vectorize` —— 三级向量化诊断
- `gcc -fopt-info-vec` / `-fopt-info-vec-missed` —— GCC 对应
- `llvm-mca` —— 分析向量化后的指令吞吐（飞腾需正确调度模型）
- `-mllvm -debug-only=loop-vectorize` —— LLVM debug build 的详细 cost model 日志

**🌐 社区与 RFC**
- LLVM Discourse "Vector Predication" 主题（VP 设计讨论）
- LLVM Discourse "VPlan" 主题（外层循环向量化进展）
- ARM developer（SVE 编程指南，对偶参考飞腾 NEON 局限）

---

> **本 Expert 一句话总结**：LLVM 的自动向量化器是 Legality–Cost–VPlan 三段式精密机器，但飞腾 FTC862 在这条流水线的每个关卡都差一口气——无 SVE 谓词（Legality 受阻）、无专用 TTI 调度模型（Cost 不准）、Yocto LLVM 13 太旧（拿不到 VPlan dotprod 改进）。飞腾向量化的"半成功"画像，根因不在算法，而在 ISA 缺失 + 填表缺失 + 版本滞后三重叠加。补 FTC86x 调度模型 + 升级 LLVM + 用户教育，是飞腾榨取向量化红利的性价比最高的三件事。
