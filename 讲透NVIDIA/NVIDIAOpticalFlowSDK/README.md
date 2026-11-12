# 讲透 NVIDIA NVIDIAOpticalFlowSDK

> 源码仓：`/usr-data/data2/repos/agent-repos/NVIDIA/NVIDIAOpticalFlowSDK` @ commit `edb50da3`
> 知识图谱：仓内 `.understand-anything/knowledge-graph.json`

## 全链状态表

| 阶段 | 状态 | 产物 |
|---|---|---|
| 批分析（1 批/3 文件） | ✅ 1/1 | 纯声明 C 头零提取属预期（file 节点为基粒度），手扫补 7 个显著 API 子节点 + 1 条 imports |
| understand 图谱 | ✅ 完成 | **10 节点 / 19 边 / 3 层 / 10 步导览**，validator **0 issues 0 warnings**，fingerprints 基线 **3 文件 @ edb50da3** |
| Onboarding | ✅ 完成 | `onboarding/ONBOARDING.md`（8 节 / 5131 不计空格字符，1308 团灭期盘上验收采纳） |
| explain 精讲 | ✅ 2/2 | `explain/01-02`，六节结构、78 锚、抽验 26 处全命中 |

## explain 索引（2 篇）

| # | 篇目 | 主题 | 字数（不计空格）/锚 |
|---|---|---|---|
| 01 | nvOpticalFlowCommon.h | 跨后端公共契约：枚举/参数结构/S10.5 定点光流格式 | 3209 / 48 |
| 02 | nvOpticalFlowCuda.h | CUDA 后端唯一入口 + 12 项 vtable 运行时绑定 | 3732 / 30 |

## 勘误与甄别（源码一手核实）

1. **`#pragma pack` 注释与源码不符**：nvOpticalFlowCommon.h 头注释声称单字节 `#pragma pack` 对齐，源码零 `#pragma` 指令（:35 注释 vs 全文扫描）。
2. **参数名文档漂移**：头文档写 `cuContext`（:88-89），实际签名形参是 `device`（:99）。
3. **`_MSC_VER_` 尾下划线死代码**：nvOpticalFlowCommon.h:42 的尾下划线宏与标准 `_MSC_VER` 永不相等，分支死代码。
4. **`PFNVOF...` 单 N 前缀孤例**：nvOpticalFlowCuda.h:195/219 的函数指针类型前缀少一个 N，与 Win32 惯例 `PFN`+全名不一致（孤例）。
5. **NV_OF_ROI_RECT 是全仓唯一未 typedef 的 struct 声明**。

## 一句话

NVOFA 硬件光流/立体视差引擎的 C API 纸面快照：两个头、一个入口、一张 12 项 vtable——把它当"驱动 ABI 的纸面契约"读，注释里每处 Must/should 都是运行期断言的预告。
