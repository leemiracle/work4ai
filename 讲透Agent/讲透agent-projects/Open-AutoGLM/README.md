# Open-AutoGLM（zai-org/Open-AutoGLM）全链知识库

智谱 phone-use agent 开源实现（AutoGLM 系）：agent loop 编排 / 系统提示词契约 / Android-ADB 与 HarmonyOS-HDC 双设备栈 / iOS-XCTest / 部署校验脚本。本地仓 `/usr-data/data2/repos/agent-repos/agent-projects/Open-AutoGLM`（commit 86f55382 时锚定）。

## 全链状态表

| 环节 | 状态 | 产物 |
|---|---|---|
| DeepWiki | ✅ TRUE_100（agent-projects 轮） | `deepwiki/` |
| understand 图谱 | ✅ 191n/449e/14层/15步tour · validator 0 issues · fingerprints 54@86f55382（2026-10-30 wave#1） | 仓内 `.understand-anything/knowledge-graph.json` |
| ONBOARDING | ✅ 5990 字/65 锚 | `onboarding/ONBOARDING.md` |
| explain | ✅ 12 篇 40,000+ 字符 | `explain/01-12` |
| 锚终验 | ✅ **2026-11-01 补跑：121/121 界内 0 坏 0 未解析**（主会话独立终验，含 basename 消歧） | — |

字数口径=不计空格总字符。explain 六节结构。

## explain 索引

01 agent-loop 编排 · 02 系统提示词契约 · 03 model-client 消息层 · 04 action-handler ·
05 device-factory · 06 ADB 设备栈 · 07 HDC 鸿蒙设备栈 · 08 iOS-XCTest 栈与 agent 行 ·
09 CLI 入口与示例 · 10 部署校验脚本 · 11 应用清单与时序 · 12 隐私与贡献流程

## 与 DeepWiki 的关系

DeepWiki 快照对应上游完整仓；explain 系列按本地 commit 86f55382 源码逐行锚定，深一个版本代。
