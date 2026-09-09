# Lens_07 — 用国产化战略家的眼睛看 LLVM

> **范式**：国产化战略家——从"自主可控"战略视角审视编译器国产化。
> **核心 named concepts**：
> - **"自主可控"叙事**（信创政策的核心诉求，飞腾项目 E06（`../../体系结构实验/Expert_06_Standards_Policy/README.md`） §3 已铺底）
> - **编译器自主可控三段论**：用 → fork → upstream → 自研
> - **国产 CPU 厂商编译器战略矩阵**（飞腾 / 华为鲲鹏 / 华为昇腾 / 平头哥 / 龙芯 / 申威 / 海光）
> - **ARM v9 不授中国的编译器后果**（飞腾被迫停留在 ARMv8.4 + 主线 LLVM 无 FTC86x 调度模型）
> - **信创市场 vs 全球市场的双轨制**（信创是国产编译器的"保护 niche"，类比 PowerPC 1997–2005 在游戏机存活）
>
> **为什么从业者看不见**：编译器工程师关心"LLVM 怎么用、Pass 怎么写、miscompile 怎么调"，不关心"在信创政策下 LLVM 该不该用 / 用了算不算自主 / fork 一份 LLVM 改个名能不能叫国产编译器"。前者是技术问题，后者是**战略与叙事问题**——而在中国国产化语境里，**叙事的强制力往往大于技术的优劣**。本透镜正是要把从业者刻意回避的"算不算自主"这个政治经济学问题摆到桌面上。
>
> **方法论锚点**：
> - 飞腾项目 Lens_07_VC（`../../体系结构实验/Lenses/Lens_07_VC.md`）（国产化投资视角）+ Lens_01_Historian（`../../体系结构实验/Lenses/Lens_01_Historian.md`）（国产化战略的方法论基底）
> - Chris Miller《Chip War》第 10 章"出口管制"——把芯片供应链武器化的地缘逻辑 `[书]`
> - Bresnahan & Malerba (1999) 《Industry-level computing: 'Windows of opportunity' in the dynamics of computing industries》——半导体产业演化"机会窗口"，移植到编译器产业 `[论文]`
> - 飞腾项目 Expert_06（`../../体系结构实验/Expert_06_Standards_Policy/README.md`） 标准政策（信创政策内容）
> - 飞腾项目 Expert_22（`../../体系结构实验/Expert_22_OpenSource_Ecosystem/README.md`） 开源生态（RISC-V / 国产软件栈）
> - Lee & Oh (2006) 《The political economy of standards: Linux and Windows》——后发国家如何利用开源标准对冲锁定 `[论文]`

> **数字来源分级（全文统一）**：`[实测]` = 本项目 grep/diff LLVM monorepo；`[官方]` = 厂商一手（官网/产品页/白皮书/JD）；`[GitHub]` = 开源仓库 code/commit；`[Discourse]` = LLVM 官方论坛；`[社区]` = 中文社区/公众号；`[报道]` = 权威媒体；`[JD]` = 飞腾招聘 JD；`[推测-依据]` = 基于公开信息推断。所有外部链接访问日期：2026-07-07。

> **⚠️ 边界硬切声明（与其他视角的责任划分）**：
> - **国内信创政策/国密合规/《密码法》《关基条例》的法学分析**归飞腾项目 E06（`../../体系结构实验/Expert_06_Standards_Policy/README.md`）；本透镜只消费其"信创是保护 niche、信创份额飞腾 10–15%"的结论，不重复法学推导。
> - **国际地缘（ARM v9 不授中国的成因、出口管制机制、台海供应链）**归飞腾项目 E19 Geostrategy（`../../体系结构实验/Expert_19_Geostrategy/README.md`）；本透镜把"v9 不授"作为**既成事实**消费，只评估其**编译器侧**的后果。
> - **飞腾固件/驱动合回 Linux/TF-A 主线的工程细节**归本项目 E18 Phytium Adaptation；本透镜只做"主线合入率作为国产化自主度指标"的宏观评估。
> - **LLVM 供应链"谁养着哪个 Target 后端"**的全球公司化分析归本项目 [Lens_03 SupplyChain](Lens_03_SupplyChain.md)；本透镜聚焦**中国厂商**在 LLVM 供应链的位置。

---

## 0. 这个透镜为什么是路线 B 的命脉

本项目宪法 §0.1 判定：LLVM **不是飞腾的芯片**，不能套飞腾项目的"芯片特异剖析"范式，应走"领域通用指南（飞腾为案例）"的路线 B。但路线 B 的护城河**全靠飞腾工程实证**（phytium_repos 45 目录 + 主线 LLVM 对 FTC86x 的"无调度模型"反向锚点）。

**Lens_07 是路线 B 的命脉透镜，因为它直接回答了"飞腾案例为什么不可替代"**：

- 若飞腾对 LLVM 的贡献只是"在 45 个 OS 里消费 LLVM/Clang"，那飞腾与任何一家用 LLVM 的国产厂商（海光、龙芯、申威、华为）没有本质差异——**护城河就垮了**。
- 但若飞腾在"国产化自主可控"这个**中国独有的战略维度**上具有独特性（例如：唯一一家既无主线 LLVM 痕迹、也无主线 GCC 痕迹的主流国产 CPU 厂商），那飞腾案例就成了"国产化战略家透镜"的**不可替代样本**——它让本透镜能讲清楚一个普世命题：**后发国家如何在被锁定的全球编译器基础设施（LLVM/GCC）里追求"自主可控"，以及这种追求的真实成色**。

换言之，**Lens_07 是把"飞腾的国产化尴尬"升华为"所有后发国家的编译器自主困境"的桥梁**。这是路线 B 的精髓：飞腾不是主角，是案例锚点；但锚点的特异性（零 upstream + 全 fork）恰恰让普适命题最锋利。

---

## 1. 这个范式的核心逻辑：国产化战略五块方法论

国产化战略家看 LLVM，不是看 IR 怎么设计、Pass 怎么调度，而是用五块方法论拷问：

### 1.1 "自主可控"叙事的政策经济学

"自主可控"是信创政策的核心诉求（飞腾 E06 §3 已铺底），但它**不是一个技术概念，是一个叙事概念**——它指的是"在关键技术上不被外国卡脖子"的政治承诺，其衡量标准随政策周期（信创 1.0/2.0/3.0）动态变化。在编译器这个维度上，"自主可控"可以分解为三个递进层级 `[推测-叙事分解]`：

| 层级 | 含义 | 衡量指标 |
|------|------|---------|
| **L1 可用** | 能用国产编译器编出可运行二进制 | 有无自有编译器产品（PhyCC/PhyGCC/BiSheng/swLLVM）|
| **L2 可控** | 能独立维护、打补丁、升级，不被上游断供 | fork 的 rebase 节奏、对上游 patch 的依赖度 |
| **L3 可演** | 能影响上游方向、让自研特性进主线 | upstream commit 数、调度模型/指令是否进主线 LLVM/GCC |

**关键洞察**：飞腾在 L1 达标（有 PhyCC/PhyGCC），在 L2 部分达标（PhyGCC 12.3.3 已 rebase 到 GCC 12.3，但落后主线 2–3 年 `[官方]`），在 L3 **完全不达标**（主线 LLVM/GCC 零 FTC86x 痕迹，§2.1 实测）。**国产化叙事最容易在 L1 制造"已自主"的幻觉，掩盖 L3 的真空**——这是本透镜要戳破的第一个叙事陷阱。

### 1.2 编译器自主可控三段论：用 → fork → upstream → 自研

观察全球后发国家/厂商在编译器基础设施上的演化路径，存在一个清晰的四阶段阶梯（Bresnahan-Malerba "机会窗口"框架的编译器版）`[推测-框架移植]`：

```
   编译器自主可控四段论（Bresnahan-Malerba 机会窗口 × 编译器）

   阶段 0：用          阶段 1：Fork        阶段 2：Upstream      阶段 3：自研
   ─────────────       ─────────────       ──────────────        ─────────────
   直接用上游二进制     改名+加 patch       把特性推回主线         重写框架或自研 ISA
   零自主              名义自主            实质自主              深度自主
                                                        (但框架仍是 LLVM/GCC)

   例子：              例子：              例子：                例子：
   - 海光早期用主线     - 飞腾 PhyCC/PhyGCC  - 华为鲲鹏 TSV110     - 龙芯 LoongArch
     GCC/LLVM           (LLVM/GCC fork)      进主线 LLVM          (ISA 自研+主线 LLVM)
   - 申威早期用 SWGCC   - 华为 BiSheng       - 海光 c86-4g-m8      - 华为昇腾 CANN
   - 飞腾早期用开源     - 华为昇腾 CANN      进 GCC 17            (MLIR+TVM fork→
     GCC/LLVM           (TVM/MLIR fork)    - 平头哥 OpenC910       开源 AscendNPU-IR)
                       - 申威 swLLVM         RTL 开源
                       - 平头哥玄铁          - 龙芯 LoongArch
                         (c-sky/buildroot)    主线 GCC/LLVM 一等公民
```

> 图表 1：编译器自主可控四段论（基于 §2.1 厂商矩阵归纳）。

**哪一段"最自主"？** 表面看阶段 3（自研 ISA）最自主，但**龙芯 LoongArch 仍用 LLVM/GCC 框架**（§2.1 实测，LoongArch.td 在主线 LLVM 里），只是 ISA 自研——这是"ISA 自主 + 框架复用"的混合态。**真正的"深度自主"在编译器世界几乎不存在**：连苹果都要 fork LLVM（Apple LLVM → Swift 编译器复用 LLVM 后端），Google 的 Go 编译器后端也曾长期用 GCC/LLVM。**自主可控在编译器领域的现实上限是"upstream 一等公民 + ISA/微架构自主"，不是"框架自研"**——这是本透镜要戳破的第二个叙事陷阱（"用 GCC/LLVM 框架 = 不自主"的伪命题）。

### 1.3 国产 CPU 厂商编译器战略矩阵（核心判断，§2.1 展开）

把六家主流国产 CPU 厂商放进"用/fork/upstream/自研"四象限，会看到**飞腾是唯一一家既无主线 LLVM 痕迹、也无主线 GCC 痕迹的主流厂商**——这个特异性是 Lens_07 不可替代的护城河（§0 已述）。

### 1.4 ARM v9 不授中国的编译器命运（§2.4 展开）

飞腾项目 E21 AI Positioning（`../../体系结构实验/Expert_21_AI_Positioning/README.md`） 已写"无 BF16/I8MM/SVE 是 AI 战略伤疤"。本透镜补充**编译器侧**：主线 LLVM 会持续为 ARMv9 演进（SVE2/MTE/SME/FP8），飞腾停留在 ARMv8.4 意味着**主线 LLVM 的"未来红利"飞腾拿不到**——这不是性能问题，是"编译器技术债永续累积"的战略问题。

### 1.5 信创市场双轨制（§2.5 展开）

信创市场（党政军 + 8 大行业 CIIO，飞腾 E06 §6）是国产编译器的"保护 niche"，类比 PowerPC 1997–2005 在游戏机（GameCube/Wii/Xbox 360）存活——**全球主流市场被 x86/ARM 淹没，但在受保护的细分 niche 里活了下来**。信创对飞腾编译器的保护逻辑类似：**全球编译器市场被 LLVM/GCC 主导，但信创目录强制"国产编译器"，飞腾 PhyCC/PhyGCC 在这个 niche 里能活**。问题是：**niche 存活 vs 主流竞争是两个游戏**，飞腾"用 LLVM"是否违背"信创"诉求？这是双轨制的核心张力。

---

## 2. 用国产化战略框架看 LLVM：五个尖锐判断

### 2.1 判断一：国产 CPU 厂商编译器战略矩阵（真实数据表）

> 这是任务点名必答的核心判断。下表是 2026-07 可核实的国产 CPU 厂商编译器开源状态，**所有数据标来源分级**。

#### 2.1.1 主线 LLVM/GCC 中的国产 CPU 痕迹（实测 grep）

本项目对 `/data/usershare/ai/riscv/OpenXiangShan/llvm-project/llvm/lib/Target/AArch64/` 做 grep 实测（2026-07-07）：

```
   主线 LLVM AArch64 后端 国产 CPU 痕迹实测（grep 实测，2026-07-07）

   厂商              grep 关键词            命中文件                     命中行          评级
   ──────────────    ──────────────────    ────────────────────────    ──────────     ────
   ★ 飞腾 ★          phytium|ftc86|ftc66   (无)                        0              🔴 零痕迹
   华为鲲鹏           tsv110|taishan        AArch64Processors.td        :833, :1544    🟢 一等公民
                                            (SubtargetFeature +          (含 TSV110Model
                                             ProcessorModel)              调度模型)
   华为昇腾           ascend|cann           (NPU 后端在 CANN 仓库，      —             🟡 独立生态
                                            非主线 LLVM)
   平头哥玄铁         thead|xuantie         (RISC-V 后端，非 AArch64)    —             🟢 RISC-V 贡献
   龙芯 LoongArch     loongarch             LoongArch.td (独立后端)      全量           🟢🟢 一等公民
                                            (LLVM 22.x 2026-01 加 LA32)
   海光               hygon|c86             (x86 后端，Phoronix 报道      —             🟢 GCC 17 合入
                                            LLVM 已合 c86-4g-m4/m6/m7)
   申威 SW64          sw64|sunway           (主线支持有限，swLLVM        —             🟠 fork 为主
                                            fork 在软件学报论文)
```

> 表 1：主线 LLVM/GCC 国产 CPU 痕迹实测（grep + websearch 交叉验证）。`[实测]` grep OpenXiangShan/llvm-project；`[报道]` Phoronix 2026-04/06；`[GitHub]` llvm/llvm-project PR #176700。

**这个表的杀伤力**：飞腾是**唯一一家在主线 LLVM AArch64 后端零痕迹的主流国产 ARM 厂商**。华为鲲鹏（TSV110）有完整调度模型；龙芯 LoongArch 有独立后端且 LLVM 22.x 还在持续加特性；海光 c86-4g 系列 2026 年正在密集合入 GCC/LLVM；平头哥在 RISC-V 后端持续贡献；申威有学术论文级的 swLLVM fork。**飞腾有什么？只有 PhyCC（LLVM fork，闭源）和 PhyGCC（GCC fork，闭源）**——两个 fork 都没开源，更没 upstream。

#### 2.1.2 六家厂商编译器战略矩阵（综合判断）

| 厂商 | ISA | 主线 GCC | 主线 LLVM | 自有 Fork | 开源状态 | 自主可控评级 |
|------|-----|:------:|:------:|---------|:------:|:------:|
| **飞腾** | ARMv8.4 (FTC862) | 🔴 零痕迹 | 🔴 零痕迹 | PhyCC(LLVM)+PhyGCC(GCC) | 🔴 全闭源 | **L1（可用）** |
| **华为鲲鹏** | ARMv8.2 (TaiShan v110) | 🟡 待查 | 🟢 TSV110 一等公民 | BiSheng(LLVM) | 🟡 BiSheng 部分开源 | **L2-L3（可控+演）** |
| **华为昇腾** | 自研 NPU ISA | N/A | N/A | CANN(MLIR/TVM)+AscendNPU-IR | 🟢 AtomGit 开源 | **L2-L3** |
| **平头哥玄铁** | RISC-V | 🟢 贡献 | 🟢 贡献 | OpenC910 RTL + c-sky/buildroot | 🟢 RTL 全开源 | **L3（演）** |
| **龙芯** | LoongArch（自研 ISA） | 🟢🟢 一等公民 | 🟢🟢 一等公民 (LA32/LA64) | (主线即自有) | 🟢 主线即开源 | **L3（演+ISA 自研）** |
| **海光** | x86 (Zen 授权) | 🟢 c86-4g-m4/m6/m7/m8 | 🟡 LLVM 跟进中 | (用主线) | 🟢 upstream 贡献 | **L2-L3** |
| **申威** | SW64（自研 ISA） | 🟠 SWGCC fork | 🟠 swLLVM fork | swLLVM+SWUC | 🟠 论文级 fork | **L2（可控）** |

> 表 2：国产 CPU 厂商编译器战略矩阵（2026-07）。数据源：`[实测]` grep + `[官方]` 各家产品页 + `[GitHub]` 各家仓库 + `[报道]` Phoronix/linuxeden + `[社区]` SegmentFault PhyGCC 安装。

#### 2.1.3 矩阵的战略解读

**三个梯队清晰浮现**：

- **第一梯队（upstream 一等公民，L3）**：龙芯（LoongArch 主线 GCC/LLVM 全栈）、平头哥（RISC-V RTL+工具链开源）、华为鲲鹏（TSV110 主线 LLVM）。这三家**把自研特性推回了全球公共品**，是真正的"自主可控 + 国际公共品贡献者"。
- **第二梯队（upstream 积极贡献 + fork 补充，L2-L3）**：华为昇腾（CANN 开源但独立生态）、海光（c86-4g 密集合入 GCC/LLVM 主线）。这两家**正在从 fork 走向 upstream**，是"自主可控的进行时"。
- **第三梯队（fork 为主 + 主线零贡献，L1-L2）**：飞腾（PhyCC/PhyGCC 全闭源 fork）、申威（swLLVM 学术 fork）。这两家**停留在 fork 阶段**，是"名义自主、实质消费"。

**飞腾在六家里排名第五（仅优于申威的纯学术态）**，这是国产化战略家视角最痛的判断：**飞腾在芯片层是"ARMv8.4 + 国密原生 + 军工资质"的差异化选手（飞腾 E06/E07 共识），但在编译器层是"零 upstream + 全闭源 fork"的滞后选手**。芯片层的护城河没有传导到编译器层——这是飞腾"自主可控"叙事最大的断层。

### 2.2 判断二：飞腾在 LLVM 供应链的"纯消费者"位置

> oracle 战略评审 §0.3 已澄清：phytvm 是 Apache TVM fork（非飞腾自研 LLVM 后端），codegen_arm.cc 是 vanilla TVM upstream 代码。本判断把这一发现升级为"飞腾在 LLVM 供应链的位置"判断。

#### 2.2.1 飞腾对 LLVM 的三种"消费姿态"

飞腾对 LLVM 的全部关系，可归纳为三种"消费姿态"——**没有一种是"生产者"姿态**：

1. **PhyCC（LLVM fork，闭源）**：飞腾官方明文"PhyCC 1.0/2.0 基于 LLVM 研发"，集成高性能 malloc/math 库 `[官方]`。这是**改名 fork**——拿 LLVM 改个名加些 Pass，不开源、不 upstream。这是 §1.2 三段论的"阶段 1 Fork"。
2. **PhyGCC（GCC fork，闭源）**：飞腾官方明文"PhyGCC 兼容主流 GCC，针对飞腾微架构做了专门优化"，最新 PhyGCC 12.3.3（2025）rebase 到 GCC 12.3 `[官方]`。同样是改名 fork，且 **rebase 落后主线 2–3 年**（主线 GCC 已到 16 `[GitHub]` gcc-patches 2026-04）。
3. **phytium_repos 45 目录的工程消费**：飞腾在 Yocto（LLVM 13.0.1 recipe）、Android 11（external_llvm-project 精简版）、FreeBSD（contrib/llvm-project ports）里**消费 LLVM/Clang**——这是**纯消费**，连 fork 都不算，是把上游 LLVM 当二进制工具用。

**关键反证**：飞腾 NPU 编译器工程师 JD 明文（`[JD]` phytium.com.cn/recruitment 2024-07）——

> "1.从事飞腾 NPU 编译器开发工作，**在 llvm 基础上移植一个新的后端**，并支持新的指令集；2.针对飞腾处理器进行指令调度优化等优化。"

这条 JD 是飞腾自研 LLVM 后端的**唯一实锤**——但注意三个词：**"在 llvm 基础上"**（消费 LLVM 框架）+ **"移植"**（不是从零写）+ **"新的后端"**（NPU 后端，不是 FTC86x CPU 后端）。**它证明飞腾正在做 NPU 的 LLVM 后端，但 FTC86x CPU 后端在主线 LLVM 仍零痕迹**（§2.1 grep 实测）。换言之，飞腾的 LLVM 后端工作是**面向 NPU 的增量**，不是**面向 FTC86x CPU 的主线贡献**。

#### 2.2.2 "纯消费者"位置对"自主可控"叙事的冲击

飞腾在 LLVM 供应链的位置是**纯消费者（pure consumer）**——这与华为鲲鹏（upstream TSV110）、龙芯（upstream LoongArch）、海光（upstream c86-4g）形成鲜明对比。国产化战略家视角的冲击有三层：

1. **叙事层**：飞腾宣传"PhyCC 自主可控编译器"（`[官方]` 飞腾开发者平台），但 PhyCC 是 LLVM fork + 闭源——这跟"自主可控"的 L3（可演）标准相去甚远。**消费者包装成生产者，是叙事注水**。
2. **工程层**：飞腾每次升级 PhyCC 都要 rebase LLVM（从 LLVM 13 到未来 LLVM N），rebase 成本随 LLVM 演进累积——**fork 越久，rebase 越痛**（本项目 E03 Pass Framework 的 New PM 迁移债、E04 中端 MLIR 融合裂痕都会砸到 PhyCC 上）。PhyGCC 12.3.3 落后主线 GCC 16 约 3 年，是这种债的现实度量。
3. **战略层**：飞腾对 LLVM 主线**零影响力**——ARM v9 的 SVE2/MTE/SME 演进、MLIR 的 AI 编译器融合、New PM 的迁移节奏，**飞腾一个 commit 都投不进去**。这意味着 LLVM 的未来方向由 Apple/Google/AMD/ARM/华为（TSV110 贡献者）决定，飞腾只能**被动跟随**。

#### 2.2.3 飞腾何时 upstream？预测

基于 §2.1 矩阵和飞腾产品节奏，预测飞腾首次向主线 LLVM 提交 FTC86x 调度模型的时间窗口 `[推测-依据]`：

- **2026–2028（概率 < 15%）**：飞腾当前战略重心在 D3000M 服务器出货（信创 3.0 窗口）+ NPU 编译器（JD 明文），无 upstream 投入动机。PhyCC/PhyGCC 闭源是商业护城河（哪怕很薄），开源会削弱"自主编译器"叙事。
- **2028–2030（概率 25–35%）**：若信创 3.0 收尾、PhyCC/PhyGCC 商业价值递减，飞腾可能仿海光（c86-4g upstream）把 FTC86x 调度模型推回主线，换取"主线一等公民"的生态红利（客户用主线 clang 即可，不用装 PhyCC）。
- **2030+（概率 > 50%）**：若 ARM v9 持续不授、RISC-V 编译器栈成熟，飞腾可能**跳过 upstream FTC86x，直接转 RISC-V 自研核的 upstream 贡献**（重演龙芯 LoongArch 路径）。

> **本判断诚实结论**：飞腾在 LLVM 供应链是**纯消费者**，不是生产者。这对"自主可控"叙事的冲击是**结构性的**——飞腾在芯片层是"自主可控"的优等生（国密原生 + 军工 + ARMv8.4 标准 FEAT），在编译器层是"自主可控"的差等生（零 upstream + 全闭源 fork）。**芯片自主 ≠ 编译器自主**，这是飞腾叙事的最大断层。预测飞腾 2030 前 upstream FTC86x 的概率 < 50%，更可能的路径是 2030+ 转 RISC-V 自研核后重新走 upstream 路线。

### 2.3 判断三：编译器自主可控三段论的"最自主"之争

> 任务点名必答：用 → fork → upstream → 自研，哪个阶段"最自主"？"用 GCC/LLVM 框架 + 自研 ISA"是否算自主？

#### 2.3.1 四阶段的"自主度"打分

用"被上游卡脖子的程度"作为自主度的反向指标，给四阶段打分 `[推测-框架评分]`：

| 阶段 | 被上游卡脖子的程度 | 自主度 | 典型 |
|------|:------:|:------:|------|
| 0 用 | 100%（上游断供即死） | 0% | 海光早期、申威早期、飞腾早期 |
| 1 Fork | 60–80%（rebase 痛苦但可活） | 20–40% | 飞腾 PhyCC/PhyGCC、华为昇腾 CANN 早期、申威 swLLVM |
| 2 Upstream | 20–40%（特性在主线，但方向仍由强势方定） | 60–80% | 华为鲲鹏 TSV110、海光 c86-4g、平头哥 RISC-V |
| 3 自研 ISA + upstream 框架 | 10–30%（ISA 自主，框架复用） | 70–90% | 龙芯 LoongArch |
| (假想) 全自研框架+ISA | 0% | 100% | **现实不存在**（连苹果都没做到）|

**"最自主"的答案是阶段 3（自研 ISA + upstream 框架），但它的自主度上限是 70–90%，不是 100%**——因为框架（LLVM/GCC）仍是别人的。这就是 §1.2 说的"编译器深度自主在现实不存在"。

#### 2.3.2 "用 GCC/LLVM 框架 + 自研 ISA"算不算自主？

这是国产化叙事里最纠缠的问题。**龙芯 LoongArch 的案例给出了最清晰的答案**：

- **LoongArch 是自研 ISA**（2020 年发布，近 2000 条指令，ELF Machine 258 号 `[官方]` loongson.cn）。
- **但 LoongArch 用 LLVM/GCC 框架**（主线 LLVM `llvm/lib/Target/LoongArch/LoongArch.td` 全量存在，LLVM 22.x 2026-01 还加了 LoongArch32 支持 `[GitHub]` PR #176700；主线 GCC 16 2026-04 加了 LoongArch FMV + 向量 intrinsics `[GitHub]` gcc-patches）。
- **龙芯员工（heiher/xiwei/mengqinggang 等）是 LLVM LoongArch 后端的活跃 maintainer**——他们既是 ISA 设计者，又是 upstream 框架贡献者。

**这个组合（自研 ISA + upstream 框架 + 自家员工任 maintainer）是当前编译器自主可控的现实最优解**。它的"自主"体现在三层 `[推测-自主度分层]`：
1. **ISA 自主**：龙芯可以自由演进 LoongArch（加 LSX/LASX 向量扩展、加 LA32/LA64、加二进制翻译），不受任何外国厂商约束。
2. **框架复用但不依赖**：龙芯用 LLVM/GCC 框架是为了**复用全球公共品**（IR/Pass/MC 层），不是被框架锁定——因为龙芯员工是 maintainer，能直接影响框架对 LoongArch 的支持质量。
3. **生态自主**：LoongArch 已获 Linux/Binutils/GDB/.NET/Go/Chromium/V8/FFmpeg 等全栈上游支持 `[官方]`——这意味着龙芯不需要"国产 OS/编译器"的封闭生态，直接吃全球公共品。

**对比飞腾**：飞腾用 ARMv8.4（ISA 不自主，受 ARM v9 锁定）+ PhyCC/PhyGCC（框架 fork 但闭源，不是 upstream maintainer）。**飞腾在 ISA 层和框架层都比龙芯少一层自主**——这是"用 GCC/LLVM 框架 + 自研 ISA"vs"用 ARM ISA + fork LLVM/GCC 框架"的本质差异。

> **本判断诚实结论**：四阶段里"最自主"是**阶段 3（自研 ISA + upstream 框架 + 自家 maintainer）**，代表是龙芯 LoongArch。"用 GCC/LLVM 框架 + 自研 ISA"**算自主**，且是当前编译器自主可控的现实最优解——它复用全球公共品（框架）的同时保住了 ISA 主权。飞腾的悲剧在于：**它连这个最优解都没走到**——既没自研 ISA（停在 ARMv8.4），也没 upstream 框架（PhyCC/PhyGCC 闭源 fork），双重滞后。

### 2.4 判断四：ARM v9 不授 → 飞腾在 ARMv8.4 冻结的编译器命运

> 飞腾 E21 已写"无 BF16/I8MM/SVE 是 AI 战略伤疤"。本透镜补充编译器侧的命运。

#### 2.4.1 主线 LLVM 的 ARMv9 演进红利

主线 LLVM 在 ARM 后端的演进是**跟随 ARM v9 路线图**的（本项目 E08 AArch64 Backend 会详述）。2019–2026 的关键演进：

| ARM 特性 | 进主线 LLVM 版本 | 飞腾 FTC862 能否用 |
|---------|:--------------:|:----------------:|
| SVE（可扩展向量，v8.2+） | LLVM 8+（2019）| ❌ 无 SVE |
| BF16（AI 数据类型，v8.6+） | LLVM 11+（2020）| ❌ 无 BF16 |
| I8MM（int8 矩阵乘，v8.6+） | LLVM 11+（2020）| ❌ 无 I8MM |
| MTE（内存标签，v8.5+） | LLVM 10+（2019）| ❌ 无 MTE |
| SVE2（v9 基线） | LLVM 11+（2020）| ❌ v9 不授 |
| SME（矩阵扩展，v9） | LLVM 14+（2022）| ❌ v9 不授 |
| FP8/FP4（AI 低精度，v9.x） | LLVM 18+（2024）| ❌ v9 不授 |

> 表 3：主线 LLVM ARM 后端演进 vs 飞腾 FTC862 能力（`[官方]` ARM ARM + `[GitHub]` llvm-project commit history + `[实测]` 飞腾项目扩展专题）。

**这个表的杀伤力**：主线 LLVM 从 2019 起就在持续为 ARMv8.5/v8.6/v9 演进，**飞腾 FTC862（ARMv8.4）能用的 LLVM 红利停留在 2019 年之前**。这意味着：

- 飞腾的 PhyCC（即便 rebase 到最新 LLVM）**编出的代码用不了 SVE/BF16/I8MM/SVE2/SME/FP8**——因为 FTC862 硬件没这些指令。
- 飞腾的自动向量化（本项目 E07 AutoVec）天花板锁在 **NEON + UDOT + FCMLA**（ARMv8.4 能力），与主线 LLVM 的 SVE2 auto-vec、SME tile 调度**代差 5+ 年**。
- 飞腾的 AI 推理编译器栈（KleidiAI/ACL）会**自动降级到 NEON 基线**（飞腾 E05/E21 已述），性能损失 20–40%——这个损失的**编译器侧根因**就是"FTC862 拿不到主线 LLVM 的 v9 红利"。

#### 2.4.2 飞腾是否会被迫切 RISC-V（重演 Apple 2005 切 x86）？

历史学家视角（本项目 Lens_01 + 飞腾 Lens_01）会指出一个先例：**Apple 2005 年从 PowerPC 切 x86**，原因是 PowerPC 性能追不上 x86（G5 散热问题 + IBM 不更新移动 PowerPC）——**ISA 被上游锁死后，下游被迫切轨**。

飞腾在 ARMv8.4 冻结的处境与 Apple 2005 有**结构相似性** `[推测-历史类比]`：

| 维度 | Apple 2005（PowerPC→x86） | 飞腾 2026+（ARMv8.4→?）|
|------|--------------------------|----------------------|
| ISA 锁定方 | IBM/Motorola（PowerPC 联盟）| ARM（v9 不授中国，地缘归 E19）|
| 锁定后果 | 性能落后 x86 一代 | 性能落后 ARMv9 一代 + AI 算力天花板 |
| 切轨选项 | x86（Intel/AMD）| RISC-V（开源 ISA，无授权锁）|
| 切轨成本 | macOS 全栈重编 + 二进制翻译 | 信创全栈重适配 + 二进制翻译 |
| 切轨时机 | 2005（PowerPC 与 x86 差距拉大到临界）| **2028–2032（RISC-V 生态成熟 + v9 持续锁）**|

**但有两个关键差异让飞腾切 RISC-V 比 Apple 切 x86 更难**：

1. **Apple 切 x86 是切到"更主流"的 ISA**（x86 是服务器/桌面主流），飞腾切 RISC-V 是切到"更边缘"的 ISA（RISC-V 服务器生态落后 ARM 3–5 年，飞腾 E22 §2.2 已证）。**切到主流 = 顺势，切到边缘 = 逆势**。
2. **Apple 是垂直整合的端到端公司**（硬件+OS+应用全自研），切 ISA 的协调成本内部可控；飞腾是纯 CPU 公司，切 ISA 要联动麒麟/达梦/统信等外部厂商，**协调成本外部化**。

**预测**：飞腾在 **2028–2032** 会启动 RISC-V 自研核的编译器栈预研（参考平头哥 OpenC910 + c-sky/buildroot 路径），但**不会在 2030 前切换主产品线**——沉没成本（ARMv8.4 RTL + PhyCC/PhyGCC + 信创资质）太大。**真正的切轨窗口在 2032–2035**，且取决于两个触发条件：① RISC-V 服务器单核性能追平 Neoverse V2（飞腾 E22 §2.3 时间表）；② ARM v9 持续不授中国 + 中美科技脱钩加剧。

> **本判断诚实结论**：飞腾在 ARMv8.4 冻结意味着主线 LLVM 的"未来红利"（SVE2/SME/FP8）永远拿不到——这是"编译器技术债永续累积"的战略伤疤，与 E21 的 AI 算力伤疤同源。飞腾切 RISC-V 的历史类比是 Apple 2005 切 x86，但**飞腾切 RISC-V 比 Apple 切 x86 更难**（切到边缘 + 外部协调）。预测切轨窗口 2032–2035，触发条件是 RISC-V 服务器成熟 + 地缘恶化。

> **🔒 2026-07 校准（C930/V3 让"切到边缘"和"触发条件①"需重大修正）**：
>
> 上文判"飞腾切 RISC-V 是切到更边缘的 ISA（服务器生态落后 ARM 3-5 年）"+"触发条件① RISC-V 服务器单核性能追平 Neoverse V2"写成于 2026-06。**2025-03 ~ 2025-07 的两颗新核让这两条判断需校准**：
>
> 1. **玄铁 C930**（2025-03 交付，首款国产服务器级 RISC-V CPU IP，3.4 GHz/15.2 SPECint2006/GHz = C920 的 2×，**TITAN 512-4096 位向量 + TPE 张量引擎 GEMM 96.8% + 8 TOPS INT8 Matrix**，平头哥**对外授权 IP**）`[官方-2025 RISC-V 中国峰会 贾昊䶮]`——**关键修正**：上文说"切到边缘 ISA"，但 C930 的 TPE/Matrix 让 RISC-V **首次有原生 AI 矩阵算力引擎**（飞腾 D3000M 无 BF16/Matrix），在 AI 维度上 RISC-V 已不"边缘"。且 C930 **对外授权 IP**（不像倚天 710 = ARM v9 + SVE2 自用 `[官方-阿里云]`），飞腾可买——**切轨路径从"自研 RISC-V 核"简化为"买 C930 IP 授权 + 适配"**。编译器侧：LLVM RISC-V 后端已有 15 套调度模型（含香山/SpacemiT 完整 upstream，本项目 Lens_03 §2.5.3 已证），编译器就绪度高于 OS/DB 层。
> 2. **Ventana Veyron V3**（15-wide OoO@4.2 GHz，11+ SPECint2017 rate-1，24 TFLOPS/core FP8）`[官方-ventanamicro.com]`——**触发条件①已被满足**：上文说"RISC-V 服务器单核性能追平 Neoverse V2"是切轨前提，V3 的 11+ SPECint2017 rate-1 已接近 Neoverse-V2 区间（~40-45）。**但 Veyron V3 飞腾实体清单买不到**（美国公司）——V3 证明"RISC-V 性能上限够"，但飞腾能买的国产 C930 单核（3.4GHz/Cortex-A76 级）仍落后 V2 约 1.2-2×。
>
> **校准后的切轨判断**：原判"切到边缘 = 逆势"在**硬件层被削弱**（C930/V3 让 RISC-V 不再边缘），但在**生态层仍成立**——OS/DB/ISV 国产适配（麒麟/达梦/统信/中间件）仍落后 ARM 3-5 年，这是"边缘"的真含义。**切轨窗口从 2032-2035 可前移到 2030-2033**（C930 IP 可买 + 编译器已就绪缩短了硬件/编译器准备期），但"不会在 2030 前切换主产品线"的核心判断不变（沉没成本 + 信创重适配太重）。**预研路径更新**：飞腾最现实的 RISC-V 预研 = 买玄铁 C930 IP 授权（Expert_22 §7.2 预研三路径（`../../体系结构实验/Expert_22_OpenSource_Ecosystem/`）），而非纯自研。深度数据见 Expert_22 §2.1 七类核诚实定位表（`../../体系结构实验/Expert_22_OpenSource_Ecosystem/`） + Lens_03 §节点③ ARM 替代方案（`../../体系结构实验/Lenses/Lens_03_SupplyChain.md`）。

### 2.5 判断五：信创市场的"双轨制"——飞腾"用 LLVM"是否违背"信创"

> 这是任务点名必答的最尖锐判断——它直接拷问"自主可控"叙事的内在矛盾。

#### 2.5.1 信创 niche 的"PowerPC 游戏机"类比

飞腾项目 E22 §2.3 提到"PowerPC 1997–2005 在游戏机存活"的 niche 现象。本透镜把它**移植到编译器**：

```
   信创 niche 的"PowerPC 游戏机"类比（双轨制模型）

   全球主流市场                          信创 niche（保护市场）
   ──────────────                        ──────────────────
   主导者：LLVM/GCC（全球公共品）          主导者：信创目录强制"国产编译器"
   规则：技术优劣 + 生态网络效应           规则：国产化率 + 资质 + 政策目录
   玩家：Apple/Google/AMD/ARM/华为         玩家：飞腾 PhyCC/PhyGCC、华为 BiSheng、
   (upstream 一等公民)                     龙芯、海光、申威 swLLVM
                                          (国产 fork + 信创资质)
   ──────────────────────────────────────
   类比：PowerPC 在全球 PC 市场           类比：PowerPC 在 GameCube/Wii/Xbox 360
   被 x86 淘汰（2005 Apple 切 x86）       存活到 2010s（任天堂/微软/索尼保护 niche）

   ▲ 信创 niche 让飞腾 PhyCC/PhyGCC 能活——不是因为它技术好，
     而是因为信创目录强制"国产编译器"准入
   ▲ 但 niche 存活 ≠ 主流竞争——飞腾"用 LLVM"在 niche 内是"国产编译器"，
     在全球市场是"LLVM 闭源 fork"，两个身份的认知冲突
```

> 图表 2：信创 niche 的 PowerPC 游戏机类比（`[推测-框架移植]`）。

#### 2.5.2 "用 LLVM"是否违背"信创"诉求？

**这是双轨制的核心张力，答案是"在信创 niche 内不违背，但暴露了'自主可控'叙事的内在矛盾"**：

- **信创诉求的字面解读**："国产编译器"= 由中国厂商维护、可控、可审计的编译器。PhyCC 由飞腾（中国公司）维护、闭源可控、可审计（信创采购方可审源码）——**字面达标**。
- **信创诉求的精神解读**："自主可控"= 不被外国卡脖子、能独立演进。PhyCC 是 LLVM fork，**LLVM 主线由 Apple/Google/ARM 主导**（本项目 Lens_03 供应链会详述），飞腾对 LLVM 主线零影响力——**精神不达标**。

**这个张力的本质**：信创政策的"国产编译器"准入标准是**L1（可用）层面**的（有中国厂商维护即可），但"自主可控"的政治承诺是**L3（可演）层面**的（能独立演进、不被卡脖子）。**用 L1 的准入标准满足 L3 的政治承诺，是信创双轨制的叙事缝隙**。

#### 2.5.3 飞腾、华为、龙芯在双轨制里的不同处境

| 厂商 | 信创 niche 内（L1 达标？）| 全球市场（L3 达标？）| 双轨制处境 |
|------|:---:|:---:|------|
| **飞腾** | ✅（PhyCC/PhyGCC 进信创）| ❌（零 upstream）| **niche 内活，主流外死** |
| **华为鲲鹏** | ✅（BiSheng 进信创）| ✅（TSV110 upstream）| **双轨都活**（但被制裁挤压）|
| **龙芯** | ✅（LoongArch 主线即国产）| ✅（upstream 一等公民）| **双轨都活 + ISA 自主**（信创叙事最纯）|
| **海光** | ✅（c86 进信创）| ✅（c86-4g upstream）| **双轨都活 + x86 兼容**（但 x86 授权风险）|

**飞腾是双轨制里处境最尴尬的**：在信创 niche 内，它靠"PhyCC 国产编译器 + 信创资质 + 国密原生"活下来（飞腾 E06/E07 共识）；但在全球市场，它的编译器零 upstream、全闭源 fork，**完全不具备主流竞争力**。华为/龙芯/海光都在双轨里有 upstream 支撑，飞腾没有——**这是飞腾"自主可控"叙事最脆弱的一环**。

> **本判断诚实结论**：信创市场的"双轨制"让飞腾"用 LLVM（fork 成 PhyCC）"在 niche 内不违背信创诉求（L1 达标），但暴露了"自主可控"叙事的内在矛盾（L1 准入标准 vs L3 政治承诺）。**飞腾在双轨制里处境最尴尬**：niche 内活（靠资质 + 国密），主流外死（零 upstream + 全闭源 fork）。**信创保护了飞腾的生存权，但没赋予飞腾的演进权**——这是双轨制对"国产编译器"最深刻的结构性约束。

---

## 3. 对 LLVM/飞腾命运的具体下注（5 注，可证伪）

> 宪法 §7.2 Lens 硬性下限：必须给出具体预测/下注。以下 5 注到 2030 年回看可证伪。

### 下注 1：飞腾 2030 前向主线 LLVM 提交 FTC86x 调度模型的概率 < 20%

**赌注**：飞腾在 2030-12-31 前，向 `llvm/llvm-project` 主线提交并被合入 FTC86x（或后续 FTC863/864）的调度模型（`AArch64SchedFTC86x.td` 类似 TSV110Model）。

**概率**：< 20%。

**理由**：飞腾 PhyCC/PhyGCC 闭源是商业护城河（哪怕很薄），开源会削弱"自主编译器"叙事；飞腾当前战略重心在 NPU 编译器（JD 明文）+ 信创出货，无 upstream 投入动机；§2.1 grep 实测零痕迹 + PhyCC rebase 节奏滞后，反映 upstream 不是优先级。

**证伪条件**：2030 前飞腾官方公告或 llvm-project 主线出现 FTC86x 调度模型 commit。

### 下注 2：龙芯 LoongArch 编译器自主度 2030 达 90%，成为"国产编译器自主可控"标杆

**赌注**：到 2030，龙芯 LoongArch 在主线 GCC + 主线 LLVM + 主线 Binutils + 主线 Linux 全栈达到"一等公民 + 龙芯员工任 maintainer"状态，自主度（§2.3 评分）≥ 90%。

**概率**：70–85%。

**理由**：龙芯 LoongArch 已在主线 GCC/LLVM 全栈（`[GitHub]` PR #176700 LA32 合入 + `[GitHub]` gcc-16 LoongArch FMV）；龙芯员工（heiher/xiwei/mengqinggang/chenglulu）是活跃 maintainer；龙芯是六家里唯一"自研 ISA + upstream 框架 + 自家 maintainer"三合一的厂商（§2.3）。

**证伪条件**：2030 龙芯 LoongArch 在主线 LLVM/GCC 出现重大回退，或被其他国产 ISA（如 RISC-V 国产核）取代标杆地位。

### 下注 3：华为昇腾 AscendNPU-IR 会成为国产 AI 编译器事实标准（2028–2030）

**赌注**：华为昇腾 2025-05 开源的 AscendNPU-IR（基于 MLIR）在 2028–2030 成为国产 AI NPU 编译器的事实标准，被非华为国产 AI 芯片（寒武纪、燧原、壁仞、摩尔线程等）参考或采用。

**概率**：55–70%。

**理由**：AscendNPU-IR 基于 MLIR（AI 编译器未来方向，本项目 E04 会详述）；华为昇腾是国内唯一规模化部署的国产 AI 算力（CANN 社区版 8.3.RCX `[官方]`）；AtomGit/GitCode 开源 + 华为生态势能；平头哥/寒武纪等没有同量级的 AI 编译器开源项目。

**证伪条件**：2028–2030 国产 AI 芯片厂商普遍选择自研 MLIR dialect 或跟随 MLIR 主线（不参考 AscendNPU-IR），AscendNPU-IR 沦为华为独占。

### 下注 4：海光 2027 前在 LLVM 主线合入完整 c86-4g 系列，成为"国产 x86 upstream"标杆

**赌注**：海光在 2027-12-31 前，在主线 LLVM 合入 c86-4g-m4/m6/m7/m8 全系列调度模型（对齐 GCC 17 已合入的 c86-4g-m8 `[报道]` Phoronix 2026-06）。

**概率**：60–75%。

**理由**：海光已在 GCC 17 (2026-06) 合入 c86-4g-m8 `[报道]`，作者刘鑫、维护者 Kewen Lin、沟通方 Uros Bizjak——证明海光有 upstream 协作能力；LLVM/Clang 已合入 c86-4g-m4/m6/m7 `[报道]` linuxeden，m8 跟进是时间问题；海光有强烈动机（x86 服务器市场需要主线编译器支持以降低客户迁移成本）。

**证伪条件**：2027 前海光 LLVM upstream 进度停滞，或中美科技脱钩导致海光退出 LLVM 社区。

### 下注 5：飞腾 2032 前启动 RISC-V 编译器栈自研的概率 > 60%

**赌注**：飞腾在 2032-12-31 前启动 RISC-V 自研核的编译器栈（参考平头哥 OpenC910 + c-sky/buildroot 路径，向主线 LLVM RISC-V 后端贡献飞腾自研核调度模型）。

**概率**：60–75%。

**理由**：ARM v9 持续不授中国（地缘归 E19）+ RISC-V 服务器 2028–2032 成熟（飞腾 E22 §2.3）+ 飞腾在 ARMv8.4 编译器侧零 upstream（§2.1）三重压力叠加；切 RISC-V 是飞腾**重新走 upstream 路线**的唯一机会（ARMv8.4 已无 upstream 价值）；龙芯 LoongArch 的"自研 ISA + upstream 框架"路径为飞腾提供了可复制的模板。

> **🔒 2026-07 校准（C930 让下注 5 的概率支撑更强）**：
>
> 下注 5 理由中的"RISC-V 服务器 2028–2032 成熟"已有实质进展：**玄铁 C930**（2025-03 交付，首款国产服务器级 RISC-V CPU IP，3.4 GHz/15.2 SPECint2006/GHz，**TITAN 向量 + TPE 张量引擎 GEMM 96.8% + 8 TOPS INT8 Matrix**，平头哥**对外授权 IP**）`[官方-2025 RISC-V 中国峰会]` 让飞腾启动 RISC-V 编译器栈有了具体硬件载体——**最现实路径不再是"自研核"，而是"买 C930 IP + 向主线 LLVM RISC-V 后端贡献飞腾版 C930 调度模型"**（重演平头哥/进迭时空的 upstream 路径，本项目 Lens_03 §2.5.2 已证中国 RISC-V 厂商在 LLVM 是"生产者"）。编译器侧准备期因此缩短（C930 有公开微架构文档 + LLVM RISC-V 后端已有 15 套调度模型可参照）。**Veyron V3**（15-wide@4.2GHz）证明性能上限够但飞腾买不到 `[官方-ventanamicro.com]`。**校准**：下注 5 概率 60-75% 维持甚至略升（路径更清晰），但"自研核"应修正为"买 IP + upstream 调度模型"。详见 Expert_22 §7.2 预研三路径（`../../体系结构实验/Expert_22_OpenSource_Ecosystem/`）。

**证伪条件**：2032 前飞腾仍坚持 ARMv8.x 路线且未启动 RISC-V 编译器栈，或 ARM v9 解禁中国（极低概率）。

---

## 4. 这一视角的盲区与反方（诚实段——"自主可控"叙事的局限）

> 国产化战略家视角**看不见什么**？这是宪法 §7.3 强制要求。

### 4.1 本视角的系统性盲区

1. **高估"upstream 自主度"的工程价值，低估"fork 实用性"**。本视角把"upstream 一等公民"奉为自主度金标准，但**对信创客户而言，PhyCC 能编出跑得快的二进制比"是否 upstream"重要得多**。反方：信创采购方完全不在意 PhyCC 是否 upstream，只要"国产 + 够用 + 有资质"就买——本视角的"upstream 自主度"在信创市场可能是**伪指标**。
2. **"自主可控"叙事的西方本位偏见**。本视角用 Bresnahan-Malerba + Lee & Oh 等西方产业经济学框架丈量中国国产化，但**中国"自主可控"的政治经济学不是单纯的技术自主**——它是**国家安全 + 产业政策 + 党的领导**的复合体。用"upstream commit 数"衡量"自主可控"，可能漏掉"党的领导权"这个中国语境的核心维度。
3. **看不见 fork 的工程学习价值**。本视角贬低 fork（"名义自主"），但**飞腾做 PhyCC/PhyGCC 的过程本身就是培养编译器团队的工程学习**——这些工程师未来可能成为 upstream 贡献者。本视角的"四段论"是线性的，但**真实的工程能力积累是非线性的**，fork 阶段的沉淀可能在 5–10 年后开花结果。
4. **RISC-V "自主"的幻觉**。本视角把 RISC-V 当"自主出路"，但**RISC-V ISA 虽开源，其核心扩展（RVV/Matrix）的演进仍由 RISC-V International 主导，中国厂商话语权有限**（飞腾 E22 §7）。切 RISC-V 不等于"自主可控"，只是从"ARM 锁"换到"RISC-V 国际共识锁"。
5. **份额数据的可信度**。§2.1 矩阵的"主线痕迹"是 grep 实测（可信），但"自主可控评级"是主观打分（L1/L2/L3），可能被反驳为"标签游戏"。
6. **短期 vs 长期的错位**。本视角的 5 个下注到 2030/2032 回看，但**地缘政治（v9 是否解禁、台海局势、中美脱钩程度）可能在 2027 就重写所有判断**——本视角的预测建立在"现状延续"假设上，对黑天鹅事件无免疫力。

### 4.2 反方意见（站在飞腾/信创辩护方）

- **"飞腾零 upstream 不是不自主，是商业选择"**——部分有理。PhyCC/PhyGCC 闭源是商业护城河（哪怕很薄），upstream 等于把护城河填平。但反方：**海光 c86-4g upstream 后，海光的商业护城河没塌**——upstream 与商业护城河不是零和。飞腾的"商业选择"论证掩盖了"upstream 能力不足"的可能。
- **"信创市场够大，不需要全球市场"**——部分有理。信创 3.0 市场万亿级（飞腾 E06 §4.1），飞腾 10–15% 份额够活。但反方：**信创 4.0 边际递减**（飞腾 E06 §4.1），且信创客户越来越看重"技术先进性"（不止"国产"），飞腾长期靠政策保护不可持续。
- **"用 LLVM/GCC 框架是国际惯例，不算不自主"**——完全有理（§2.3 已论证）。但反方：**飞腾的问题不是"用框架"，是"用框架但零 upstream + 全闭源"**——龙芯也用框架，但龙芯是 upstream maintainer。框架复用与 upstream 贡献不矛盾，飞腾是两者都没做好。
- **"PhyGCC 12.3.3 已经很努力了"**——有理，PhyGCC 12.3.3 加了自动向量化增强、指针压缩、分支布局优化 `[官方]`，是实打实的工程投入。但反方：**这些优化都没 upstream**，是"自家庭院里的花"——全球 GCC 社区享受不到，飞腾自己也得每次 rebase 重新合并。

### 4.3 本视角最可能误导决策之处

**把"upstream 自主度"等同于"国家安全价值"，把"零 upstream"等同于"不自主可控"**。

如果决策者据本分析得出"飞腾 PhyCC/PhyGCC 是假的国产编译器，应该强制 upstream 或弃用"的结论，那恰恰忽略了两个事实：① 信创 niche 内 PhyCC 是合规且可用的（L1 达标）；② upstream 不是国产化的唯一标准，** ISA 主权 + 工程团队 + 信创资质**都是自主可控的维度。**国产化战略家视角最危险的认知陷阱是"upstream 原教旨主义"——用全球开源社区的指标丈量中国国家安全诉求，可能逼出"为了 upstream 而 upstream"的错误决策**（例如强制飞腾开源 PhyCC，反而削弱其商业可持续性）。

---

## 5. 与其他视角对偶（强制）

| 对偶视角 | 一致 / 冲突 | 核心交汇点 |
|---------|:----------:|----------|
| **本项目 Lens_01 历史学家** | ✅ 强共鸣 | Lens_01 用 GCC→LLVM→MLIR 兴衰周期看编译器产业演化，本透镜用 Bresnahan-Malerba"机会窗口"看后发国家如何在这个演化里卡位。**Apple 2005 切 x86 是两者共享的历史先例**——Lens_01 看技术周期，本透镜看 ISA 锁定后果。 |
| **本项目 Lens_02 Christensen** | ✅ 强共鸣 | Lens_02 用"低端颠覆"看 Cranelift/MLIR 是否颠覆 LLVM，本透镜看 RISC-V 是否颠覆 ARM（对飞腾）。**两者共享"颠覆从边缘来"的 Christensen 框架**——Lens_02 看编译器内部颠覆，本透镜看 ISA 颠覆。 |
| **本项目 Lens_03 供应链** | ✅ 强互补 | Lens_03 看"每个 LLVM Target 后端是哪个公司养着的"（Apple/AMD/NVIDIA/ARM/Huawei），本透镜看"中国厂商在这个供应链里是消费者还是生产者"。**两者拼成"全球 + 中国"的完整供应链图景**——飞腾在 Lens_03 是"ARM 后端的纯消费者"，在本透镜升级为"零 upstream 的滞后国产化选手"。 |
| **本项目 E17 治理 License** | ⚠️ 张力 | E17 看 LLVM 的 Apache 2.0 with LLVM Exception License 与公司化治理（Apple/Google/AMD/NVIDIA/ARM commit 份额），本透镜追问"中国厂商在这个治理结构里的话语权"。**张力在于**：LLVM 治理是开放的（任何公司可贡献），但**主线方向由强势公司主导**——中国厂商（除华为 TSV110）话语权弱，这是"开放 ≠ 平等"的治理悖论。 |
| **本项目 E18 Phytium Adaptation** | ✅ 强互补 | E18 做 phytium_repos 45 目录的 LLVM/Clang patch 完整 diff（具体工程实证），本透镜把 E18 的实证升华为"飞腾是纯消费者"的战略判断。**E18 给证据，本透镜给结论**。 |
| **飞腾项目 Lens_07_VC** | ⚠️ 冲突 | 飞腾 Lens_07_VC 问"投不投飞腾下一代"，本透镜（LLVM 版）说"飞腾编译器自主度低"。**VC 可能据此看空飞腾**，但反方：飞腾的芯片层自主度（国密+军工+ARMv8.4 标准 FEAT）仍是投资亮点——**芯片自主 vs 编译器自主的分裂，是 VC 评估飞腾的关键张力**。 |
| **飞腾项目 Lens_01_Historian** | ✅ 强共鸣 | 飞腾 Lens_01 看"飞腾 ARM 路线的历史选择"，本透镜看"飞腾在 LLVM 历史里的位置"。**两者共享"后发者如何在全球基础设施里卡位"的历史视角**。 |
| **飞腾项目 E06 标准政策** | ✅ 强互补 | E06 讲"信创政策如何造市场"（飞腾 10–15% 份额的来源），本透镜讲"信创市场如何保护国产编译器"（PhyCC/PhyGCC 的 niche 存活）。**E06 给政策，本透镜给编译器后果**。 |
| **飞腾项目 E22 开源生态** | ✅ 强互补 | E22 讲"RISC-V 高性能化 + 飞腾 vs 鲲鹏生态厚度"，本透镜讲"国产 CPU 厂商编译器战略矩阵"。**两者共享"开源是否救中国芯片"的命题**——E22 看 OS/DB 生态，本透镜看编译器生态。 |
| **飞腾项目 E19 地缘战略** | ⚠️ 硬切 | E19 讲"v9 不授中国 + 出口管制的地缘成因"，本透镜把"v9 不授"作为**既成事实**消费，只评估其**编译器侧**后果（§2.4 ARMv8.4 冻结的编译器命运）。两者拼成"地缘因 + 编译器果"。 |

---

## 6. 参考文献（≥ 8 条，分级标注）

### 论文 / 学术（产业演化 + 编译器经济学）

1. **[论文]** Bresnahan, T. & Malerba, F., "Industrial-level computing: 'Windows of opportunity' in the dynamics of computing industries", *Research Policy*, 28(9), 1999. —— 后发国家产业演化的"机会窗口"框架，§1.2 编译器自主可控三段论的方法论基底。
2. **[论文]** Lee, S. & Oh, D., "The political economy of standards: Linux and Windows", *Information Economics and Policy*, 18(4), 2006. —— 后发国家如何利用开源标准对冲锁定，§1.5 信创双轨制 + §2.3 龙芯路径的框架来源。
3. **[论文]** Lerner, J. & Tirole, J., "Some Simple Economics of Open Source", *Journal of Industrial Economics*, 50(2), 2002. —— 开源经济学奠基，§1.1 自主可控叙事的政策经济学 + §4.1 fork 工程学习价值。
4. **[书]** Miller, C., *Chip War: A Fight for the World's Most Critical Technology*, Scribner, 2022. —— 第 10 章"出口管制"提供芯片供应链武器化的地缘逻辑，§0 方法论锚点。
5. **[论文]** 沈莉, 周文浩, 王飞, 肖谦, 武文浩, 张鲁飞, 安虹, 漆锋滨, "swLLVM: 面向神威新一代超级计算机的优化编译器", 《软件学报》, 35(5): 2359–2378, 2024. —— 申威 swLLVM fork 的学术论文，§2.1 矩阵 + §1.2 fork 阶段的实证依据。

### 官方文档 / 标准 / JD（一手）

6. **[官方]** 飞腾信息技术有限公司, *PhyCC 1.0/2.0 产品页*（phytium.com.cn/developer/36）, 访问 2026-07-07. —— "PhyCC 1.0/2.0 基于 LLVM 研发"官方表述，§2.2.1 判断一核心证据。
7. **[官方]** 飞腾信息技术有限公司, *PhyGCC 10.3.3/12.3.3 产品页与用户手册*（phytium.com.cn/developer）, 访问 2026-07-07. —— PhyGCC 12.3.3 rebase 到 GCC 12.3 + 自研优化特性，§2.2.1 fork 落后主线证据。
8. **[JD]** 飞腾信息技术有限公司, *编译器开发工程师（NPU、底层）招聘 JD*（phytium.com.cn/recruitment + liepin.com/job/1983294167）, 2024-07 发布, 访问 2026-07-07. —— "在 llvm 基础上移植一个新的后端，并支持新的指令集"——飞腾自研 LLVM 后端的唯一实锤。
9. **[官方]** 华为昇腾, *CANN 社区版 8.3.RCX 开发文档 + AscendNPU-IR 项目*（hiascend.com + gitcode.com/Ascend/AscendNPU-IR）, 2025-05 升级, 访问 2026-07-07. —— 华为昇腾 CANN 基于 MLIR，AscendNPU-IR 开源，§2.1 矩阵 + 下注 3 依据。
10. **[官方]** 龙芯中科, *LoongArch 自主指令系统介绍*（loongson.cn/system/loongarch）, 访问 2026-07-07. —— LoongArch 自研 ISA + ELF Machine 258 + 全栈上游支持，§2.3 龙芯路径依据。
11. **[官方]** 华为鲲鹏, *毕昇编译器 BiSheng 介绍*（hikunpeng.com/developer/hpc/bisheng + docs.oepkgs.net/zh-CN/Repos/huawei-bisheng）, BiSheng 2.4.0 (2025-05), 访问 2026-07-07. —— BiSheng 基于 LLVM 开发，针对鲲鹏优化，§2.1 矩阵华为鲲鹏 fork 依据。

### GitHub / 开源仓库（实测）

12. **[GitHub]** llvm/llvm-project, *PR #176700: release/22.x: [LoongArch] Add support for LA32R/LA32S*（github.com/llvm/llvm-project/pull/176700）, merged 2026-01-22. —— LLVM 22.x 加 LoongArch32 支持，§2.1 矩阵龙芯一等公民证据。
13. **[GitHub]** gcc-patches, *[PATCH] gcc-16: LoongArch: Update changes for code model and vector intrinsics*（gcc.gnu.org/pipermail/gcc-patches/2026-April/715312.html）, 2026-04-30. —— GCC 16 加 LoongArch FMV + 向量 intrinsics，§2.1 矩阵龙芯 GCC 一等公民证据。
14. **[实测]** 本项目 grep `/data/usershare/ai/riscv/OpenXiangShan/llvm-project/llvm/lib/Target/AArch64/`，关键词 `phytium|ftc86|ftc66`（2026-07-07）—— **零命中**。§2.1 判断一核心实测证据：飞腾在主线 LLVM AArch64 后端零痕迹。
15. **[实测]** 本项目 grep 同上路径，关键词 `tsv110|taishan`——命中 `AArch64Processors.td:833`（SubtargetFeature<"tsv110">）+ `:1544`（ProcessorModel<"tsv110", TSV110Model>）。§2.1 判断一核心实测证据：华为鲲鹏 TSV110 是主线 LLVM 一等公民。

### 报道 / 第三方（媒体）

16. **[报道]** Larabel, M., "Hygon C86-4G CPU Support Added To The GCC 17 Compiler", *Phoronix*, 2026-04-29（phoronix.com/news/Hygon-C86-4G-CPU-GCC-17）. —— 海光 c86-4g 进 GCC 17，§2.1 矩阵海光 upstream 证据。
17. **[报道]** Larabel, M., "New Hygon Model 8 'Suzhou' x86 CPU Support Appears In The GCC Compiler", *Phoronix*, 2026-06-23. —— 海光 c86-4g-m8 "苏州" 进 GCC 17（作者刘鑫，维护者 Kewen Lin），§2.1 矩阵 + 下注 4 依据。
18. **[报道]** linuxeden, "LLVM/Clang 合入对海光 x86 CPU 的初始编译器目标支持"（linuxeden.com/a/161541）, 访问 2026-07-07. —— LLVM/Clang 合入海光 c86-4g-m4/m6/m7，§2.1 矩阵海光 LLVM 进展。
19. **[社区]** SegmentFault, "基于飞腾 CPU 的高性能编译器 PhyGCC 的安装及配置说明"（segmentfault.com/a/1190000044680095）, 2024-03, 访问 2026-07-07. —— PhyGCC 10.3.1 安装实操（含 `-mtune=ftc66x` 选项），§2.2.1 PhyGCC fork 的社区佐证。
20. **[社区]** openEuler, "openEuler LLVM 平行宇宙计划 RISC-V 架构进展"（openeuler.org/zh/blog/.../20240429-oerv）, 2024-04-29. —— openEuler 用 LLVM 替换 GCC 构建发行版的探索，§2.5 双轨制 + 国产 OS 编译器路线参考。

---

## § 国产化战略方法论与资源（通用化）

> 本章把本透镜的飞腾/中国国产化分析上升为**任何后发国家/厂商在编译器基础设施上追求自主可控都可复用的方法与资源**。飞腾是案例锚点，方法普适。通用编译器资源见 [`领域资源库_LLVM.md`](../领域资源库_LLVM.md)。

### 方法论一：后发国家编译器自主可控的四阶段阶梯

任何后发国家/厂商在编译器基础设施（LLVM/GCC）上追求自主可控，都会经历"用 → fork → upstream → 自研"四阶段（§1.2）。**每阶段的自主度上限**：
- 用（0%）：纯消费，上游断供即死。
- Fork（20–40%）：改名+闭源，rebase 痛苦但可活。
- Upstream（60–80%）：特性进主线，但方向仍由强势方定。
- 自研 ISA + upstream 框架（70–90%）：ISA 自主 + 框架复用 + 自家 maintainer——**当前现实最优解**。

**全球案例**：苹果（fork LLVM + 自研 Swift 前端）、华为（upstream TSV110 + fork BiSheng）、龙芯（自研 LoongArch + upstream LLVM/GCC）、RISC-V International（开源 ISA + 全球贡献）。**没有任何厂商达到"全自研框架 + ISA"的 100% 自主**。

### 方法论二：信创 niche 的"PowerPC 游戏机"模型

受保护市场（信创 / 印度 Make in India / 越南国产化）让后发厂商的"国产 fork"能存活，类比 PowerPC 1997–2010 在游戏机 niche 存活。**但 niche 存活 ≠ 主流竞争**——niche 内 L1（可用）达标即可，主流市场要 L3（可演）才活。**双轨制的核心张力**：用 L1 准入标准满足 L3 政治承诺，是所有受保护市场的叙事缝隙。

### 方法论三：ISA 锁定与切轨决策（Apple 2005 模型）

当 ISA 被上游锁定（ARM v9 不授 / PowerPC 性能落后 / MIPS 衰退），下游厂商面临切轨决策。Apple 2005 切 x86 的决策模型：
1. **锁定后果临界**：性能/能力差距拉大到生存威胁（PowerPC G5 散热 + IBM 不更新移动芯片）。
2. **切轨选项成熟**：目标 ISA 生态足够支撑迁移（x86 有 Windows + 海量 ISV）。
3. **切轨成本可控**：垂直整合度足够内部消化迁移成本（Apple 自研 macOS + 二进制翻译 Rosetta）。

**应用到飞腾切 RISC-V**：① 锁定后果（v9 持续不授 + AI 算力天花板）2028–2032 达临界；② 切轨选项（RISC-V 服务器生态）2030+ 成熟；③ 切轨成本（信创全栈重适配）需要 5–10 年协调。**飞腾切轨窗口 2032–2035**，比 Apple 2005 更难（切到边缘 + 外部协调）。

### 国产化战略专属资源

> 通用编译器资源见 [`领域资源库_LLVM.md`](../领域资源库_LLVM.md) §11（飞腾专属）+ §11.4（国产 CPU 厂商矩阵）；以下为**国产化战略 / 信创政策 / 后发国家产业演化**专属资源。

**📚 后发国家产业演化（编译器版）**
- ⭐ **Bresnahan & Malerba** (1999), *Industrial-level computing: Windows of opportunity* —— 后发国家产业演化的"机会窗口"
- 🔥 **Lee & Oh** (2006), *The political economy of standards: Linux and Windows* —— 后发国家利用开源标准对冲锁定
- 🔥 **Lerner & Tirole** (2002), *Some Simple Economics of Open Source* —— 开源经济学奠基
- 📎 **Rodrik** (2004), *Industrial Policy for the Twenty-First Century* —— 产业政策评估（与飞腾 E06 共享）

**🌍 国产 CPU 厂商编译器官方入口**
- **飞腾**：[phytium.com.cn/developer/36](https://www.phytium.com.cn/developer/36/)（PhyCC/PhyGCC）
- **华为鲲鹏 BiSheng**：[hikunpeng.com/developer/hpc/bisheng](https://www.hikunpeng.com/developer/hpc/bisheng)
- **华为昇腾 CANN/AscendNPU-IR**：[hiascend.com](https://www.hiascend.com/) + [gitcode.com/Ascend](https://gitcode.com/Ascend)
- **龙芯 LoongArch**：[loongson.cn/system/loongarch](https://loongson.cn/system/loongarch) + [github.com/loongson](https://github.com/loongson)
- **平头哥 OpenC910/c-sky**：[github.com/c-sky](https://github.com/c-sky) + [occ.t-head.cn](https://occ.t-head.cn/)
- **海光**：GCC/LLVM 主线 commit（搜 Hygon/c86-4g）
- **申威**：swLLVM 论文（软件学报 2024）+ PaddlePaddle SW64 支持

**📜 中国信创政策（飞腾 E06 共享）**
- 《密码法》《关基条例》原文（全国人大/国务院官网）
- 信通院/赛迪 信创产业白皮书（年度）
- 飞腾项目 E06（`../../体系结构实验/Expert_06_Standards_Policy/README.md`） 标准政策专家视角

---

> **五个最重磅的诚实判断（全文提炼）**：
> 1. **飞腾是六家国产 CPU 厂商里编译器自主度最低的之一**（仅优于申威学术态）——主线 LLVM/GCC 零痕迹（grep 实测）+ PhyCC/PhyGCC 全闭源 fork。**华为鲲鹏（TSV110 upstream）、龙芯（LoongArch 自研+upstream）、海光（c86-4g upstream）、平头哥（RISC-V 贡献）都比飞腾更"自主可控"**。
> 2. **飞腾在 LLVM 供应链是纯消费者，不是生产者**——phytvm 是 Apache TVM fork（oracle §0.3），PhyCC 是 LLVM fork，phytium_repos 45 目录是工程消费。NPU JD 明文"在 llvm 基础上移植新后端"是面向 NPU 的增量，不是 FTC86x CPU 的主线贡献。**芯片自主 ≠ 编译器自主，这是飞腾叙事的最大断层**。
> 3. **"用 GCC/LLVM 框架 + 自研 ISA + upstream maintainer"是当前编译器自主可控的现实最优解**（龙芯 LoongArch 路径），自主度 70–90%。飞腾连这个最优解都没走到——既没自研 ISA（停在 ARMv8.4），也没 upstream 框架（闭源 fork），双重滞后。
> 4. **ARM v9 不授让飞腾在 ARMv8.4 冻结，主线 LLVM 的 SVE2/SME/FP8 红利永远拿不到**——这是"编译器技术债永续累积"的战略伤疤。飞腾切 RISC-V 的历史类比是 Apple 2005 切 x86，但切到边缘 + 外部协调让飞腾切轨更难，窗口 2032–2035。
> 5. **信创双轨制保护了飞腾的生存权，但没赋予飞腾的演进权**——niche 内 PhyCC 是"国产编译器"（L1 达标），主流外是"LLVM 闭源 fork"（L3 不达标）。**用 L1 准入标准满足 L3 政治承诺，是信创双轨制的叙事缝隙**，也是飞腾"自主可控"叙事最脆弱的一环。
