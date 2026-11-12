# 讲透 G-Assist（NVIDIA Project G-Assist Plugins）

NVIDIA RTX 本地 AI 助手的插件生态仓：本地 SLM 跑在 RTX GPU 上、经 Overlay 交互，三语言插件 SDK（Python/C++/Nodejs）+ 17 个示例插件 + 插件模拟器测试引擎 + Agent Skills 签名评测线。

## 全链状态表（2026-11-07 实例B）

| 阶段 | 状态 | 产物 |
|---|---|---|
| prepare（scan/batches） | ✅ | 212 文件/31 批（prepare 阶段既有） |
| 批分析 31 批 | ✅ | intermediate batch-1..31（496n/640e 原始产出） |
| 终验 | ✅ | 0 问题/0 重复 ID/imports 对账全 OK（47=53 scanner+21 手扫） |
| merge | ✅ | assembled-graph 496n/639e（1 条 tested_by orphan 规范 drop） |
| layers/tour | ✅ | 10 层/15 步/212 文件节点全覆盖零交集 |
| finalize | ✅ | **knowledge-graph.json 496n/639e/10层/15步，validator issues=0 warnings=0，fingerprints=212@2f8b3b62（444 只读锁）** |
| onboarding | ✅ | onboarding/ONBOARDING.md 8177 字 8 节 54 锚（真坏 0） |
| explain | ✅ | 5 篇 26,337 字符/229 锚（真坏 0） |
| README | ✅ | 本文件 |

图谱在仓内：`/usr-data/data2/repos/agent-repos/NVIDIA/G-Assist/.understand-anything/knowledge-graph.json`

## 十层架构（图谱导读）

仓库治理与工程基础(7) → RISE C++ API 与 NVAPI 头(18) → Python RISE 绑定(15) → 插件协议 V2 与三语言 SDK(15) → 插件模拟器测试引擎(17) → plugin-builder 脚手架(9) → 示例插件·入门与模板(31) → 示例插件·在线服务集成(57) → 示例插件·硬件灯效(35) → Agent Skills 与签名评测(8)

## explain 索引

1. `explain/01-rise-cpp-api.md` — RISE C++ API 与 CLI 示例（nvapi.h RISE 段/miniaudio/DemoASRMicrophone）
2. `explain/02-gassist-sdk-python.md` — gassist_sdk Python SDK（V2 协议/@plugin.command/MCP）
3. `explain/03-plugin-emulator.md` — 插件模拟器测试引擎（10 文件/LLM judge/get_tool_catalog）
4. `explain/04-plugin-ecosystem.md` — 17 示例插件解剖学（共性骨架+spotify OAuth 深案例+差异矩阵）
5. `explain/05-skills-signing-eval.md` — Agent Skills 与 Sigstore 签名评测线

## 源码级甄别清单（写作期核实，钉版）

1. **nvapi.h 尾部 25311-25533 行是本仓扩展的 RISE 接口段**（NV_RISE_* 枚举/NvAPI_RegisterRiseCallback/NvAPI_RequestRise）——api/c++ 线与 api/bindings/python 线在此合流；NV_RISE_CONTENT_TYPE_RESERVED=10 是 main.cpp:178 客户端 constexpr，nvapi.h 枚举只到 UPDATE_INFO=9。
2. **PING_TIMEOUT_MS 1000/HEARTBEAT_TIMEOUT_MS 5000 常量真身在 plugins/plugin_emulator/protocol.py:26-38**（非 SDK protocol.py；另有 PING_INTERVAL_MS=2000）——SDK 与模拟器两份协议实现，常量以模拟器层为基准。
3. **gassist_sdk plugin.py 延迟 import mcp 实为 4 处**（587/613/681/758），非 5 处。
4. **llm_judge.py 全仓零命中**：engine.py:491/504 引用的 llm_judge 模块仓内不存在——autonomous 模式开箱即 ImportError，真实供应链缺口。
5. **11 个 .exe 全是 Git LFS 指针存根**（真身 7.97MB；批分析期 b29 报 9 个/b30 报 7 个为批内错数，onboard 期全仓实证 11/11）；python_binding.dll 是真 PE；nvapi64.lib 是真 COFF。
6. **plugin-builder 是 Cursor 规则目录非可运行插件**：plugin.py 为 0 字节空文件、manifest 是 52 字节注释占位；README 声称的 .mdc 文件不存在（实际规则在 .cursor/rules/RULE.md）。
7. **README 官方插件清单死链**：Corsair iCUE（plugins/examples/corsair）目录不存在。
8. **sln 只聚合两工程**（rise_demo_client+gassist_cli）；python_binding.vcxproj 在 api/bindings/python/ 下（:124 编 wrapper.cpp），非"三工程同 sln"。
9. **MCP 协议版本代差**：mcp.py:68 实现 MCP_PROTOCOL_VERSION='2024-11-05'，docstring 引用规范 2025-06-18。
10. **setup.py:18 "2.0.0" 与 __init__.py:65 "3.1.0" 双版本并存**。
11. **intiate_rise_install 拼写错误**（initiate 之误）已作为公共 API 导出不可改名（api/bindings/python/rise/rise.py）。
12. **old_v1=logiled V1 协议实证**：裸 ReadFile+整体 json::parse 无分帧，与新 V2（4 字节大端帧头/10MB 上限）成代际对照。
13. **skill.oms.sig=Sigstore bundle v0.3**（NVIDIA Agent Capabilities IC 01 证书链+in-toto DSSE，predicate 覆盖 6 文件 sha256）。
14. 厂商头零空格 `#include"foo.h"` 陷阱（常规正则全漏）；nvapi_lite 六头 SAL 注解宏书挡（salstart/salend）结构。
15. spotify OAuth redirect URI 必须精确 `http://127.0.0.1:8888/callback`（localhost 拒收）；onboarding_timeout=300 全仓最长。
16. .gitlab-ci.yml 仅 include nvcarps-ci 上游模板+3 变量，无自有 job。
17. **EVAL.md 位于 skills/g-assist-mcp-skill/evals/ 子目录**（与两个数据集 json 同层），不在 skill 根五件套（SKILL.md/skill-card.md/BENCHMARK.md/skill.oms.sig+evals/）之列——引用须带 evals/ 路径。

## 已知 bug/占位（供上游修复参考）

- gemini.key.txt 为明文 API key 占位文件入库；discord config.json 三凭据全空串占位
- mcp-stdio 示例 read_file 标 DEPRECATED（由 read_text_file 取代）
- miniaudio.h 95,649 行/1090 函数，工程实际只调 5 个生命周期入口（ma_context_init/ma_context_get_devices/ma_device_config_init/ma_device_init/ma_device_start）

## 流水线备注

- 台账：仓内 `.understand-anything/PROGRESS.md`（含跨实例误判勘误：b6-b13 "另一实例"实为本实例首轮派发的误报成功）
- 字数口径：不计空格字符；explain 系列实际区间 4.0K-6.2K（钉版 norm）
