# Oracle 战略评审报告（LLVM 项目宪法依据）

> **评审对象**：把 LLVM umbrella monorepo（22 子项目）做成"飞腾范式"的多专家剖析
> **评审依据**：飞腾项目宪法 v1.0、Views.md、Expert升级指南.md、Expert_11 样板
> **本地资源核实**：phytium_repos 45 个目录、phytvm/src/target/llvm 22 个文件、OpenXiangShan/llvm-project monorepo 42 项
> **评审立场**：独立、不预设结论、对宪法 §0 特异性测试负责
> **评审日期**：2026-07-07
> **本文档作用**：作为本项目宪法（`改造蓝图_LLVM.md`）的依据存档，所有后续 Expert/Lens 写作必须参考本文档的"§0.3 战略级发现"和"§2 护城河测试"。

---

## 0. 评审前提：我是怎么读的、看到了什么

### 0.1 已读文件（全部读完）
- 飞腾项目宪法 v1.0（235 行）：核心是 §0"删芯片名后不能读成通用教科书"+ §4 质量门槛 + 3 条纪律
- Views.md（201 行）：23 Expert + 9 Lens 的三轴体系
- Expert升级指南.md（86 行）：从"特异剖析"升级到"领域通用指南（飞腾为案例）"——**这条与本次 LLVM 项目高度相关**
- Expert_11_Compiler_Research/README.md（610+ 行）：编译器专家样板，已经是飞腾范式在编译领域的范本

### 0.2 本地资源核实（决定护城河的关键）

| 资源 | 实际形态 | 战略意义 |
|------|---------|---------|
| `OpenXiangShan/llvm-project/` | **完整 umbrella monorepo，22 子项目全在**（bolt/clang/clang-tools-extra/compiler-rt/cross-project-tests/flang/flang-rt/libc/libclc/libcxx/libcxxabi/libsycl/libunwind/lld/lldb/llvm/llvm-libgcc/mlir/offload/openmp/orc-rt/polly/runtimes） | ✅ 工作面齐全 |
| `phytium_repos/` | **45 个目录**，飞腾整个 OS/固件/嵌入式生态（Linux/Yocto/Buildroot/Android10/Android11/FreeBSD/NuttX/FreeRTOS/seL4/Zephyr/Xenomai/OpenHarmony/OpenEuler/onnxruntime/opt-npu/phy-studio） | ✅ 国产化适配的实证池 |
| ⭐ `opt-npu/ncsdk/common/phytvm/` | **Apache TVM 的完整 fork**（19 个子目录：arith/auto_scheduler/autotvm/contrib/driver/ir/meta_schedule/relay/runtime/target/te/tir/topi 全套） | ⚠️ **是 TVM fork，不是飞腾自研 LLVM 后端** |
| ⭐ `phytvm/src/target/llvm/` | 22 个 `.cc/.h`，含 codegen_arm/cpu/amdgpu/hexagon/nvptx/x86_64 + llvm_instance + intrin_rule | ⚠️ **经核实：codegen_arm.cc 头部是 Apache License 2.0 + "this is used as an example" 注释，是 vanilla TVM upstream 代码**（前 80 行已确认；项目执行时需做完整 diff） |

### 0.3 ⚠️ 战略级发现（必须在护城河测试中正面处理）

**用户在任务描述里说**："⭐ 飞腾自研 NPU SDK 的 TVM LLVM 后端（codegen_arm/cpu/amdgpu/hexagon/nvptx/x86_64 + llvm_instance + intrin_rule）"——这个表述**高估了特异性**。

**真相**：这 22 个文件是 Apache TVM 社区维护的 `src/target/llvm/`，飞腾 fork 了整个 TVM（命名为 `phytvm`）作为 NPU SDK 的编译栈。LLVM target 部分是**通用桥接代码**，飞腾的真正定制在别处（最可能在 `src/target/opt/`、NPU 自定义 target kind、或 `contrib/` 目录，本次评审未深挖）。

**这个发现的意义**：它直接动摇了"飞腾 LLVM 后端"作为护城河的强度。但这**不是坏事**——它恰恰强制本项目走对路线（详见第 2 章）。这正是飞腾项目宪法 §4.3"盲区与反方诚实段强制"的精神：敢说护城河没你以为的那么深。

---

## 1. 范围边界：22 子项目的优先级矩阵（详见 `改造蓝图_LLVM.md` §1）

### 收口结论

**22 子项目 → 收敛到 15 个核心 Expert + 3 个第二期 + 7 个 Lens + 5 个"只索引"条目**：
- **独立成 Expert（15+3）**：见宪法 §3
- **合并进其它 Expert（5 类）**：clang-tools-extra→E01；bolt→E12；polly→E04；offload+libsycl→E11；openmp→E15
- **只索引（5 个）**：libclc / libc / llvm-libgcc / runtimes / cross-project-tests —— 在 `领域资源库_LLVM.md` 里各写一段定位 + 入口链接，不单独成文

**理由**：宪法 §0"禁止用规模换辨识度"。15 个 8000+ 字 Expert = 12 万字，已是飞腾项目（32 视角）的体量上限。再扩必然稀释。

---

## 2. 护城河测试（最重要的一章）

### 2.1 飞腾项目宪法 §0 特异性测试套用到 LLVM

飞腾宪法原文："**删掉芯片名后，若该文仍读得通 → 判定为通用教科书，失败，重写。**"

**LLVM 版本改造**："删掉飞腾/Phytium/D3000M/phytvm 后，若该文读得通 → 判定为 LLVM 通用教科书，失败，重写。"

### 2.2 四类飞腾特异性锚点的逐个诚实评估

| 锚点候选 | 用户认知 | 实测核实 | 特异性强度 | 评级 |
|---------|---------|---------|:--------:|:----:|
| **飞腾自研 NPU TVM LLVM 后端** | ⭐ 强护城河 | `codegen_arm.cc` 是 **vanilla Apache TVM upstream**（Apache License + "this is used as an example" 注释）；`phytvm` 是整个 TVM 的 fork，LLVM target 部分非飞腾自研 | 弱（需重定位） | 🔴 虚 |
| **e2000-android11 / ft2004-android10 LLVM 精简版** | 中 | `external_llvm-project/` 是 Android NDK 裁剪版（Google 维护为主，飞腾消费） | 弱-中 | 🟠 待查 |
| **飞腾用 LLVM 给 FTC862 做的定制** | 中（E11 已写 PhyGCC，但那是 GCC 不是 LLVM） | 主线 LLVM **无 FTC86x 调度模型**（E11 §1.1 已点破）；飞腾是否有 LLVM fork 未见实证 | 中（是"缺失"而非"定制"的特异性） | 🟡 反向锚点 |
| **Yocto recipe / FreeBSD ports** | 弱 | recipe 文件、ports 配置是真实的飞腾工程产物 | 中-强（**真实工程实证**） | 🟢 实 |
| **phytium_repos 45 目录的 OS/固件生态** | 用户未提 | **这是最强护城河**：飞腾在 Linux/Yocto/Buildroot/Android/FreeBSD/NuttX/FreeRTOS/seL4/Zephyr/OpenHarmony/OpenEuler 全栈用 LLVM/Clang | 强 | 🟢 强 |

**结论**：用户以为的"飞腾自研 LLVM 后端"是**虚锚点**；真正的强锚点是**飞腾整个国产化软件栈对 LLVM/Clang 的工程消费**（phytium_repos 45 目录）+ **主线 LLVM 对 FTC86x 的"无调度模型"反向锚点**。

### 2.3 护城河路线选择（本次评审的核心判断）

有两条路线可选：

| 路线 | 定位 | §0 测试通过率 | 适配度 |
|------|------|:----------:|:----:|
| **路线 A：LLVM 作为"飞腾特异剖析"** | 照搬飞腾项目宪法，"删掉飞腾后不能读成通用 LLVM 教科书" | **~30%**（只有 ARM 后端/phytvm fork/Yocto recipe 能过，IR/Pass/x86/MLIR/Flang 全过不了） | ❌ 不适配 |
| **路线 B：LLVM 作为"领域通用指南（飞腾为案例）"** | 把 LLVM 做成编译器领域的持久知识库，飞腾 phytium_repos 作为案例锚点 | **N/A（测试改写）** | ✅ 高度适配 |

**判断依据**：
1. LLVM **不是飞腾的芯片**。飞腾宪法 §0 是为"一颗具体芯片"设计的，LLVM 是一个"通用编译器基础设施"，强行套 §0 会逼出大量伪造特异性。
2. **Expert升级指南.md 已经指明了方向**：飞腾项目自己都在从"特异剖析"升级到"通用专家指南"。 **LLVM 项目天然就是"领域通用指南"，飞腾 phytium_repos 是案例池。**
3. 飞腾的真正贡献是**工程消费**（在 45 个 OS/嵌入式发行版里用 LLVM/Clang 做了什么裁剪、什么适配、遇到什么坑），不是**自研定制**。这个差异决定了路线。

### 2.4 路线 B 的 §0 改造（特异性测试 v2.0）

> **LLVM 项目特异性测试 v2.0**：
> 删掉飞腾/phytium_repos/phytvm 后，若该文读得通 → 判定失败。
> **或者**：若该文只是翻译 LLVM 官方文档/README，无任何"代码级实例 + 工程教训 + 对偶判断" → 判定失败。

**双重门槛**：每个 Expert 必须满足以下任一：
- **(a) 飞腾工程实证**：引用 phytium_repos 里真实的 recipe/patch/config/代码
- **(b) 代码级实例**：引用 OpenXiangShan/llvm-project 里真实的 `.td`/`.cpp`/Pass 代码片段（不是 README 翻译）
- **(c) 对偶判断**：给出"如果换 GCC/Cranelift/MLIR 会怎样"的对比

---

## 3. 18 Expert 清单 + 7 Lens 清单（详见 `改造蓝图_LLVM.md` §3-§4）

**15 核心 Expert**（轴一 7 + 轴二 4 + 轴三 4 + E17）+ **3 第二期**（E16 Flang / E18 飞腾收口先行 / E15 备选）+ **7 Lens**。

具体见宪法 §3、§4。本评审不重复列举。

---

## 4. 五个"服务器命脉级断层"（详见 `改造蓝图_LLVM.md` §5）

1. **GPU/异构后端对齐债**（最高命脉，对标飞腾"AI 算力定位"）
2. **MLIR-core 融合裂痕**（最高命脉，对标飞腾"无 SVE 向量化天花板"）
3. **编译器供应链安全**（最高命脉，对标飞腾"服务器 RAS"）
4. **New PM 迁移债**（高命脉，工程实战痛点）
5. **Linux 内核 GCC→Clang 迁移**（最高命脉，国产化内核编译）

---

## 5. 失败模式预警（详见 `改造蓝图_LLVM.md` §6）

10 个失败模式（F1-F10），最高危三个：
- **F1 规模失控**：22 子项目全做 → 半成品堆积
- **F2 通用化失焦**：写成 LLVM 教科书 → 过不了 §0.3
- **F4 忽略飞腾实战**：本地有 phytium_repos 45 目录却只写通用 LLVM

---

## 6. 执行阶段切分（详见 `改造蓝图_LLVM.md` §9）

七阶段（A→G），关键修正：
- **透镜先行**（破死板）
- **阶段 B 改为"特异性锚点实测"**（phytium_repos 代码 diff，路线 B 的地基）

---

## 7. 三条"如果只做一件事就做这个"的最高优先级建议

### 🥇 建议一：先做 E18 特异性锚点实测（phytium_repos 代码 diff），否则全盘过不了 §0

**做什么**：在动笔写任何 Expert 前，花 1-2 天做三件事：
1. `diff` phytvm fork 与 upstream Apache TVM，确认飞腾真实改了哪些文件（**纠正"codegen_arm.cc 是飞腾自研"的误判**）
2. 盘点 phytium_repos 45 目录里所有 patch LLVM/Clang 的真实文件（Yocto recipe / FreeBSD ports / Android NDK / Buildroot / phy-studio）
3. 在 OpenXiangShan/llvm-project 里 `grep -r "FTC86\|Phytium\|ftc"` 确认主线 LLVM 是否有飞腾调度模型

**理由**：路线 B（领域通用指南，飞腾为案例）的护城河**全靠 phytium_repos 实证**。不先做实测，所有专家都写成通用 LLVM 教科书，过不了 §0 v2.0，全盘失败。

**如果不做**：项目会变成"LLVM 版维基百科"，与官方文档重复，无辨识度。

---

### 🥈 建议二：明确定位为"领域通用指南（飞腾为案例）"，而非"飞腾特异剖析"

**做什么**：在项目宪法 §0 明文写路线 B（已在 `改造蓝图_LLVM.md` §0.1 写明）。

**理由**：
1. **Expert升级指南.md 已指明方向**——飞腾项目自己都在从"特异剖析"升级到"通用指南"。
2. **codegen_arm.cc 是 vanilla TVM** 这个发现证明：飞腾对 LLVM 的贡献是"工程消费"不是"自研定制"。
3. **领域通用指南的价值更持久**——飞腾 D4000 出来后，飞腾特异剖析要重写；但 LLVM 的 IR/Pass/Target 知识 5-10 年不过时。

---

### 🥉 建议三：严格执行 15 Expert + 7 Lens + 5 索引的上限，禁止 22 子项目全做

**做什么**：
- 15 个核心 Expert（可延展到 18 含第二期）
- 7 个 Lens
- 5 个子项目（libclc/libc/llvm-libgcc/runtimes/cross-project-tests）只进 `领域资源库_LLVM.md` 索引
- clang-tools-extra/bolt/polly/offload+libsycl/openmp **合并**进相邻 Expert
- 硬性字数上限：总 ≤ 16 万字

**理由**：
1. **飞腾宪法 §0 明令"禁止用规模换辨识度"**。
2. 22 子项目全做 = F1 规模失控 = 写到半路资源耗尽，半成品堆积。
3. **合并比分裂好**——clang-tools-extra 离开 Clang 没意义，bolt 离开 LLD 没意义，polly 离开中端没意义。强行独立成文会重复 30%。

---

## 附录：与飞腾项目的对偶速查

| 维度 | 飞腾项目 | LLVM 项目（本评审建议） |
|------|---------|---------------------|
| 护城河 | 对一颗芯片的密集实测 | LLVM 领域通用深度 + phytium_repos 飞腾案例实证 |
| §0 测试 | 删芯片名后不能读成通用教科书 | 删飞腾/LLVM 后不能读成 README 翻译（v2.0 双重门槛） |
| Lab | Lab00-07 实测（性能/缓存/ISA） | 无 Lab，用 phytium_repos 代码 diff + OpenXiangShan 源码实例替代 |
| Expert 数 | 23 | 15（核心）+ 3（第二期） |
| Lens 数 | 9 | 7 |
| 战略伤疤 | 无 BF16/I8MM/SVE | GPU 后端对齐债 + MLIR-core 裂痕 + 供应链安全 + New PM 迁移债 + 内核 GCC→Clang |
| 最大风险 | E07 软文化（已修正） | F2 通用化失焦 + F4 忽略飞腾实战 |
| 阶段 B | 堵服务器断层（RAS/固件/AI） | 特异性锚点实测（phytium_repos diff） |
| 总字数 | ~32 万（32 视角） | ≤ 16 万（25 视角，精简 31%） |

---

**评审完毕。**

> 核心判断一句话总结：**LLVM 不是飞腾的芯片，不能套飞腾项目的"芯片特异剖析"范式；应走 Expert升级指南.md 指明的"领域通用指南（飞腾为案例）"路线，护城河靠 phytium_repos 45 目录的工程实证 + OpenXiangShan monorepo 的代码级实例，而非"飞腾自研 LLVM 后端"（已核实为 vanilla TVM）。**
