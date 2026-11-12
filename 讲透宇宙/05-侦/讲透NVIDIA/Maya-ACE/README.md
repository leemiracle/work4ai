# 讲透 Maya-ACE（NVIDIA Audio2Face-3D Maya 插件）

> understand-anything 全链知识库 · 2026-11-09 · 会话 7514f115
> 仓：/usr-data/data2/repos/agent-repos/NVIDIA/Maya-ACE @f0dc136（2025-09-25）

## 项目一句话

把 NVIDIA Audio2Face-3D（本地 TensorRT 推理 + 云端 NIM gRPC 双工作流）带进 Maya 的动画插件：音频进、面部动画曲线出，直接驱动 blendshape 节点。C++（Maya 插件+gRPC 客户端）/Python（脚本链+gRPC 绑定）混合，12 个 .proto 契约源生成双语言代码。

## 全链状态表

| 阶段 | 状态 | 产物 |
|------|------|------|
| deepwiki | ✅（前轮） | `deepwiki/` |
| 批分析 | ✅ 40/40 批（44 产物） | 957 节点/1530 边，429/429 文件全覆盖 |
| 终验 | ✅ | 零缺失/重复/自环/坏前缀/坏 JSON |
| merge | ✅ | 13 条前缀错位悬空边回补 → 1511e 零悬空 |
| layers/tour | ✅ 14 层/16 步 | 446/446 全覆盖零重复 |
| finalize | ✅ validator 0 issues 0 warnings（内置+独立双验） | 图谱在仓 `.understand-anything/knowledge-graph.json`（957n/1511e），fingerprints 429@f0dc1367 |
| onboarding | ✅ | `onboarding/ONBOARDING.md` 8959 字 8 节 48 锚 |
| explain | ✅ 6 篇 | `explain/01-06` 合计 20969 字 149 锚，锚终验真坏 0 |

## 目录

- `deepwiki/` — DeepWiki 快照（前轮抓取）
- `onboarding/ONBOARDING.md` — 八节上手文档（14 层架构+双工作流数据流+16 步 tour 精讲）
- `explain/` — 六篇深讲：
  1. `01-a2f-player-双播放节点.md` — A2FAnimationPlayer（本地 TRT）vs AceAnimationPlayer（云端 NVCF）：平行实现非继承、快估计+后台全量双速推理、blendshape multiplier 重置 workaround、眼睛旋转角度/弧度陷阱、音频 offset 两节点不对称
  2. `02-ace-client-gRPC客户端群.md` — C++ 客户端四件套：grpc_client.h:64 硬编码默认 NVCF function_id（不填静默连计费云）、CHUNK_SIZE 恰 1 秒 PCM、healthcheck 靠字符串匹配错误分类、FetchFrame 空壳
  3. `03-proto契约层.md` — 12 proto 源→双语言生成物：四 service=四种流形态（双向流/客户端流/四 RPC 有状态会话/Push-Pull 对偶）、controller 无 ID 头 vs a2f 带 ID 头双形态、a2f_authoring+a2x_export_config 只有生成物无 proto 源（mock 先行实证）
  4. `04-python脚本链与trtgen.md` — ace_tools 编排层+AE 模板+TRT engine 构建器；userSetup.mel 实为 10 菜单项非 11（勘误）
  5. `05-mock-server与测试体系.md` — mock_server 4 个 Mock*Servicer+双测试线（Python/C++ GoogleTest）+tested_by 网 34 条
  6. `06-metahuman-batch批处理示例.md` — MetaHuman 批处理：MH_Mapping.json 68 个 ARKit→CTRL_* 映射、BatchList 任务清单、参数文件新旧格式演变（Example1/2 旧扁平→Example3 新嵌套）

## 图谱规模

957 节点（429 file 级）/1511 边/14 层/16 步 tour。层序：proto 契约源→双语言生成物→云端客户端→插件骨架/公共数据→脚本链→Python/C++ 测试→批处理示例→资产→文档→构建→门面。

## 源码级甄别/勘误精选（全部行号实证）

1. **logger.h LOG_ERROR #else 分支误定义 LOG_INFO**——真实宏缺陷（批 3 手扫发现）
2. **a2f_authoring 与 a2x_export_config 的 .proto 全仓未分发**——仅 examples 12 proto 且不含这两个；mock_server 却实现了该服务=云端 avatar 制作预留接口、mock 先行开发中状态（onboard 补充核实）
3. **17 个 .ma 全是 Git LFS 指针**（134B pointer，实资产 15.8-258.9MB 不在仓内）；english_voice_male_p1_neutral.wav 与 audio_6sec 同 LFS oid（同音频两处分发）
4. **files_to_compile.yaml 重复列 animation_data.v1.proto 两次且漏列 services.animation_data.v1.proto**；requirements.txt protobuf-gen 重复两行
5. **docs/gettingstarted-a2f.md 死链**（setupinstructions L71/L127 与 buildandtest 两处引用不存在文件）
6. **grpc_client.h:64 硬编码默认 NVCF function_id** UUID（不填也静默连计费云）
7. **a2f_player 实际在 source/maya_ace/nodes/ 而非 commands/**（explain 组1 纠任务书）；"789 行单函数"=initialize() L122-911 全文件 911 行
8. **userSetup.mel 10 菜单项非 11**（explain 组2 纠）；纯 menu 声明式零 global proc，11/10 个命令经 -sourceType python 转发
9. **Mace README 自带勘误两处**：ACE2MH_Functions.py 实为 ACE2Rig_Functions.py、MH_Mapping.jason 实为 .json；前置要求 v2.0 vs 排障节 v1.2 自相矛盾
10. **protobuf 版本双线**：proto/requirements.txt 4.25.8 vs deps 5.26.1/protoc 5.26.1+grpcio-tools 1.64.1（onboard 补充）
11. **tree-sitter 对 C++ grpc.pb.h service 类全盲**（9-17 批 0 提取，Service/Stub 节点全部手扫花括号配对精确定界）；timeslider.cpp/h 同盲已手补 6 函数；TEST_F 宏误读 44 同名函数已按 Fixture.Case 重建
12. **scanner 盲区清单**（本仓实证）：8 条 grpc.pb.h→pb.h include、30 条跨目录 #include（CMake 双根解析）、mock.grpc.pb.h 34 条、importlib 字符串加载 7 条、test 方法内延迟 import 10 条——全部手扫补齐
13. **VERSION.md（内容仅"2.0.0"）被根 CMakeLists.txt:27 file(READ) 读入 MACE_VERSION**；GoogleTest/gtest LICENSE 重复收录；audio2x-sdk 是 EULA 非 OSS
14. **音频 offset 语义两节点不对称**（本地带前置静音、云端裸发）会导致换节点口型错位（explain 01 发现）

## 采用口径

- 字数=不计空格字符；onboard/onboarding 锚均 basename 消歧后界内验证（唯一坏=IP 地址冒号 regex 误报）
- 图谱节点 summary/tag 中文，保留英文技术词
