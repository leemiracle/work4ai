# 讲透 DLSS

> NVIDIA DLSS SDK 样本仓——NGX（Neural Graphics Framework）DLSS 集成的头文件+二进制库+donut 样本骨架。微仓从简档全链。

## 全链状态表

| 阶段 | 状态 | 产出 |
|---|---|---|
| understand 图谱 | ✅ 2026-11-07 | 仓内 `.understand-anything/knowledge-graph.json`：**140n/189e/10 层/14 步 tour**，fingerprints 102@37495948 |
| onboarding | ✅ 2026-11-07 | `onboarding/ONBOARDING.md`（8 节 5962 字不计空格，69 锚零坏） |
| explain 6 篇 | ✅ 2026-11-07 | `explain/01-06` 合计 15081 字，215 锚全体验证 0 坏（微仓从简档 1884-2963 字/篇） |

## 甄别钉版

1. **二进制矩阵实为 68 个**（18 dll+36 lib+12 so+2 a，1.31GB）——初判"74"系计数笔误，盘上实证修正
2. **NVIDIAImageScaling 是未初始化空子模块**（.gitmodules 指针在 L01 层承载，无 NIS 文件节点）；NGX 枚举 ImageSuperResolution=3 为 NIS/DLSS 双轨旁证
3. `nvsdk_ngx_helpers_dlssd.h` 为 deprecated 转发桩（#pragma message 实证）
4. 23 头按 defs/params/helpers/loader/standalone 五层语义；38 个 ≥10 行 inline 包装函数手补（tree-sitter 对 C 声明头 static inline 全盲，KCCL 轮盲区重现）
5. doc/ 6 PDF 被 ignore 裁掉不入图谱（产物中声明）

*2026-11-07 · cuda-stack-第七轮会话（舰队微仓快通道）*
