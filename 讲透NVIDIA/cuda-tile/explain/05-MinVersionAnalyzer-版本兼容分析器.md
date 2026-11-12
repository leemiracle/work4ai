# 05 · MinVersionAnalyzer —— "这个模块最早能用哪个版本序列化"

> 文件：`include/cuda_tile/Bytecode/Analysis/MinVersionAnalyzer.h`（33 行）+ `lib/Bytecode/Analysis/MinVersionAnalyzer.cpp`（74 行）
> 真正的判定逻辑在三个 tblgen 生成物里（见第 6 篇），本文件是编排壳

## 一、角色定位

字节码格式的版本体系（13.1→13.4，见第 2/3 篇）给每个工具链出了一道题：**手头这个模块，最早可以用哪个版本合法序列化？** 写 13.4 当然永远合法，但兼容面最窄；默认写 kCurrentCompatibilityVersion（=13.1，Version.cpp:39-43）兼容面最宽，可模块里只要出现一个 `mmaf_scaled`（13.3 引入，第 1 篇版本表），13.1 文件就装不下它。MinVersionAnalyzer 就是这道题的求解器：`getMinBytecodeVersion(ModuleOp)`（MinVersionAnalyzer.h:29）遍历整个模块，对每个操作、每个类型、每个属性、每个枚举值取版本下界，返回全部下界的**最大值**。

它在仓库里只有一个生产调用方：`lib/Bytecode/Translation/BytecodeTranslation.cpp:100`，注册成 `analyze-min-version` 翻译命令——"输入 MLIR，输出每个 cuda_tile.module 一行所需最低版本"（BytecodeTranslation.cpp:91-108）。这是一个离线规划工具的定位：工具链集成者用它决定发布产物的版本策略，而不是每次写文件时都跑。

## 二、内部结构

### 2.1 头文件：一个函数的接口（MinVersionAnalyzer.h）

全接口就一个自由函数：`FailureOr<BytecodeVersion> getMinBytecodeVersion(ModuleOp module)`（L29）。返回 `FailureOr` 而非裸值，为将来"遇到无法判定版本的对象"留失败通道（当前实现恒成功）。头文件注释（L26-28）把检查范围列得很清楚："operations, types, enum values, and attributes"——四个维度。

### 2.2 实现文件：30 行编排 + 三个生成物（MinVersionAnalyzer.cpp）

函数体（L44-74）短得可以背下来，但每个 include 都有讲究：

- **L27-30 `GEN_ATTR_VERSION_MAP` / `GEN_ENUM_VALUE_VERSION_MAP` / `GEN_ATTR_PARAM_VERSION_MAP`**（来自 AttrBytecode.inc）：展开出 `detail::getAttrMinVersionRecursive`——递归求属性版本：属性本体引入版本、枚举值各自的引入版本、结构化属性每个参数的版本，三者取最大。注释（L24-26）特意说明这个 include 必须在类型版本表之前——因为类型版本表会回调它。
- **L34-35 `GEN_TYPE_VERSION_MAP`**（TypeBytecode.inc）：`detail::getTypeMinVersionRecursive`——类型版本递归，嵌套类型（`tile<ptr<f32>>` 里的 `ptr<f32>`）与**属性值类型参数**（回调属性递归，L32-33 注释）都被覆盖。
- **L38-39 `GEN_OP_VERSION_CHECKERS` + L68-69 `GEN_OP_VERSION_CHECK_DISPATCH`**（Bytecode.inc）：每个 op 一个 `getMinVersionFor_Xxx` 检查函数 + 一个 TypeSwitch dispatch。

主循环就是一次 `module->walk`（L67-71）：每个操作经 dispatch 得 `opVersion`，与全局 `maxVersion`（初始为 kMinSupportedVersion=13.1，L46）取 max。两个回调做去重与委托：`getTypeVersion`（L52-58）用 `DenseSet<Type> processedTypes` 保证每个唯一类型只递归一次——重复出现时直接返回 kMinSupportedVersion（其贡献已在首次计入 max，注释 L50-51 讲得很清楚）；`getAttrVersion`（L61-64）无状态转发。

### 2.3 生成物侧的判定规则（BytecodeGen.cpp:940-1070）

逐 op 检查函数由 `generateOpVersionChecker` 发射，规则分五档，全部围绕"晚于 op 本体引入的东西才抬版本"：

1. **op 本体**：检查函数开头先以 op 的 `operationVersion`（Ops.td 里那个字符串）为初始 max；
2. **操作数**：晚于 op 引入且**变长非空**才 bump（BytecodeGen.cpp:958-962）——空变长操作数等于"没用新功能"；定长操作数只要版本化就 bump，且无论新旧都递归查类型版本（L963-970）；
3. **结果**：最精细的一档（L987-994）——**版本化的定长结果，仅在"被使用"（`!use_empty()`）时才 bump 并查类型**。这条与 Writer 侧"只索引被序列化结果"（第 2 篇 2.4）是一对：未被使用的新结果在序列化时本就可裁剪，自然不应抬高整个模块的版本下界；
4. **属性**：三种子形态（L1024-1057）——基线版本 UnitAttr 直接跳过（无枚举值无版本可查）；**版本化 UnitAttr 存在即 bump**（presence 本身就是版本信号，如 mmaf 的 `fast_acc`）；可选属性先查存在性，存在才 bump 本体版本并递归查值版本（枚举值、参数都在这一步深入）；
5. **region 块参数**：遍历所有 region 所有 block 的参数类型递归（L1063-1068）。

### 2.4 前向覆盖 13.2-13.4 的具体口径

把第 1 篇的版本增量表代入本分析器，就得到完整的判定矩阵：纯 13.1 基线 op 的模块 → 13.1；出现 `atan2`（op 级 13.2）→ 13.2；出现 `mmaf_scaled`/`pack`/`unpack`/`make_strided_view` 等（op 级 13.3）、或 mmaf 带 `fast_acc`（属性级 13.3）、或 13.3 引入的类型/枚举值 → 13.3；出现 `gdc_launch_dependents_tko`/`gdc_wait_tko`/`insert`/`fpowi`/`memory_fence_alias_tko`（op 级 13.4）、或任何 13.4 枚举 case/类型（如新 FP8 变体）→ 13.4。多层取 max 保证了"混搭"模块的正确性：一个满是 13.1 op 但角落里有个 13.4 枚举值的模块，会正确地要求 13.4——**版本下界由最年轻的那个构件决定，与它多冷门无关**。

## 三、外部连接

上游：`Version.h`（BytecodeVersion 全套常量）、mlir 的 walk/LogicalResult。生成物三件（AttrBytecode.inc/TypeBytecode.inc/Bytecode.inc）全部由 `tools/cuda-tile-tblgen` 的 BytecodeGen.cpp（L1161-1171 的四个 `#ifdef` 段）发射，源头元数据是 Ops.td/AttrDefs.td/Types.td 上的 `sinceVersion` 字段——**从 .td 注解到判定代码全程零手写**。下游：唯一调用方 BytecodeTranslation.cpp 的 `analyze-min-version` 翻译注册。无 pass、无 Python 绑定——它目前是纯工具命令。

## 四、数据流

输入 ModuleOp → walk 按逆后序访问每个 Operation → TypeSwitch dispatch 到具体 op 的 `getMinVersionFor_Xxx`（不认识的 op 走 Default 返回 kMinSupportedVersion，BytecodeGen.cpp:1164-1166）→ 检查函数内部：op 版本打底 → 遍历操作数/结果/属性，逐个委托 getTypeVersion/getAttrVersion 回调 → 回调里 DenseSet 去重后进递归版本表（类型→嵌套类型/属性参数→枚举值）→ 各层版本沿调用链冒泡取 max → walk 结束返回单值。输出经 `toString()` 打成 "13.x" 一行。整个分析 O(操作数)，类型去重把重复类型的递归成本摊平。

## 五、设计决策

**为什么实现只有 30 行？** 判定规则的本质是"把 Ops.td 上的版本注解机械翻译成检查代码"——这正是代码生成最擅长、人手最不擅长（抄漏一个属性就是静默错版本）的活。手写层只保留编排与去重策略，规则全部下沉生成物，是"单一真源"原则的彻底执行。

**为什么"未使用的结果"不抬版本？** 这是精确性与实用性的平衡点：序列化端本可裁剪未使用结果（Writer 有此能力），如果分析器仍因其抬版本，用户会被迫为死代码升级文件版本。反过来，这也要求"裁剪未使用结果"必须在写低版本文件时真的发生——分析假设与写侧行为强耦合，改 Writer 裁剪策略时要复查这里。

**为什么返回"最小"版本而不是布尔"能否写 13.x"？** 布尔版只能回答一个问题；最小版本能回答一族问题（能否写 13.1？差多少？哪个构件卡住了？——对后者，未来可加 verbose 模式）。返回下界让调用方自己跟目标版本比较，分析器保持中立。

**为什么类型检查要做 DenseSet 去重？** 大模块里类型高度重复（同一个 `tile<f32>` 出现上千次），递归版本表查询虽是 O(深度)，架不住量大；去重把类型维度成本压到 O(唯一类型数)。

## 六、新人提示

1. **给 op/属性/类型/枚举加版本时**，只要 .td 侧的 `sinceVersion` 写对，本分析器自动跟上——但要注意 2.3 的五档规则里"变长非空""use_empty"这些条件性 bump：新增变长操作数或可裁剪结果时，想清楚空/未使用时到底要不要求新版本，这个语义决定生成器该走哪个分支（生成器模板在 BytecodeGen.cpp:940-1070，见第 6 篇）。
2. 诊断"为什么我的模块要 13.4"：目前分析器只输出终值，不输出归因。临时排查可以二分——注释掉可疑 op 再跑 `cuda-tile-translate --analyze-min-version`；长期方案是给生成物加 verbose 输出（哪些构件贡献了 max）。
3. `Default` 分支对未知 op 返回最低版本（BytecodeGen.cpp:1164-1166）——这意味着**混入方言外 op（如 builtin）不会抬版本**，合理（它们不进字节码）；但若你新增 op 忘记登记操作码，分析器同样沉默——版本闸门真正卡人的地方在 Writer/Reader（第 2/3 篇），这里是规划工具不是防线。
4. 修改 `getMinBytecodeVersion` 签名时记得 BytecodeTranslation.cpp 的唯一调用点；它是 `FailureOr`，失败传播路径要接住。
5. 三个 `#include "xxx.inc"` 的顺序有依赖（属性表必须先于类型表，MinVersionAnalyzer.cpp:24-35 注释），调整 include 顺序前先读那段注释——类型递归会回调属性递归。
