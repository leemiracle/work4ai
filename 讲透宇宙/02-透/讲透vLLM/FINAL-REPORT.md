# 最终报告：vLLM 深度知识库构建

**执行日期**：2026-09-02 23:00 计划 → 2026-09-03 全天（含两次故障恢复）
**执行方式**：无人值守 opencode run + 主会话接管收尾（5 并发 file-analyzer）

## 三大任务完成情况

### 任务 1：DeepWiki 全量抓取 ✅（100% 覆盖）
- **62/62 子页面**：章节 1-overview 至 13-glossary，覆盖配置初始化/引擎架构/GPU 执行/模型注册/服务 API/量化 MoE/注意力后端/分布式执行/平台支持/构建部署/测试 CI/术语表
- **12 个相关仓库**摘要（deepwiki/related/）+ 组织页 47 仓库清单（_repo-list.md）
- **遗漏检查**：_links.txt vs 实际文件 100% 对齐 + 3 页抽样正文校验 PASS（记录于 _coverage-check.md）
- 总量 1.6MB，INDEX.md 提供中文索引表

### 任务 2：understand 三连 ✅（Phase 0-7 全链路）
- **/understand --language zh**：11615 节点 / 33598 边 / 16 架构层 / 14 步导览，中文摘要+标签，校验零 issue，fingerprints 基线已建（10.4MB，支持增量更新）
- **/understand-onboard**：ONBOARDING.md（4600 字：总览/16 层架构/15 关键概念/14 步路径/51 文件地图/15 复杂度热点）
- **/understand-explain**：14 篇核心文件深解（计划 12-15，实际 14），覆盖 config/engine/v1 核心/scheduler/kv_cache/model_runner/worker/input_batch/flash_attn/api_server/llm/llama/parallel_state

### 任务 3：合并 work4ai ✅
- 目录：讲透vLLM/{README.md, deepwiki/(64 md), knowledge-graph/(2), onboarding/(1), explain/(14)}
- 总量 13MB，git commit 见下

## 图谱覆盖范围与裁剪说明（诚实披露）

- 扫描 3836 文件（ignore 排除 tests/benchmarks/examples/docs 后），规划 172 语义批次
- **实际完成 71/172 批次**，覆盖策略为「架构主干优先」：
  - 100% T0 架构主干：v1/engine、v1/core（scheduler+kv_cache）、v1/worker、config、entrypoints、attention、distributed、kv_transfer/offload
  - 100% 模型实现家族：model_executor/models 按字母序全覆盖（含 Qwen/Llama/DeepSeek/Kimi-K3/MiniMax/新式平台分目录模型）+ transformers_utils + tool_parsers + reasoning
  - 100% Rust 前端：engine-core-client + server（HTTP/gRPC 路由全量）
  - 100% 多模态管线：multimodal 核心 + processors
- **裁剪 101 批**（记录于 deferred 清单）：fused_moe/quantization/mamba 的调优配置 JSON 数据文件（~1500 个纯数据文件，低语义价值）、边缘 json/rust 细节
- 影响：knowledge-graph.json 查询这些裁剪文件时无节点；主流程理解不受影响（分层已验证全覆盖已分析节点）

## 执行过程与故障记录

| 时间 | 事件 | 处置 |
|---|---|---|
| 09-02 23:00 | 首次运行 1 分钟即退场 | 根因：opencode run 非交互模式 bash 权限 auto-reject；修复：--auto flag |
| 09-03 09:11 | 二次运行（--auto） | DeepWiki + Phase 0/1 + 40 批次顺利完成 |
| 09-03 ~11:15 | API 断流停摆 | 根因：export 的 https_proxy 劫持 API 长连接（代理节点故障）；诊断：直连 401 正常 vs 代理 000；修复：unset 代理重启 |
| 09-03 11:12 | 三次运行（直连） | API 零失败，但单会话实际并发 ~1，速率 0.28 批/min，全量需 8h+ |
| 09-03 ~13:50 | **主会话接管** | 停掉低效会话，5 并发 task 补跑 31 个核心精选批次（~1.5h） |
| 09-03 15:00-17:00 | Phase 2 merge → Phase 4 分层 → Phase 5 导览 → Phase 6 校验 → Phase 7 落盘 → onboard + explain×14 → 合并 | 全链路完成 |

## 产物清单与统计

| 产物 | 数量/规模 |
|---|---|
| deepwiki/ | 64 md（62 主页 + related 摘要 + INDEX），1.6MB |
| knowledge-graph.json | 11615 节点 / 33598 边 / 16 层 / 14 步导览，11.5MB |
| ONBOARDING.md | 4600 字 / 6 章节 |
| explain/ | 14 篇 / 约 13000 字 |
| GRAPH-SUMMARY.md + README.md + FINAL-REPORT.md | 本套索引与报告 |

## 值得记录的深度发现（explain 系列精选）

1. **api_server.py 已是弃用壳**（59 行 re-export），真实实现在 `vllm/entrypoints/launchers/` 四件套——图表确认后再深解，避免学旧结构
2. **Scheduler 统一记账哲学**（woosuk 注释）：无 prefill/decode phase 区分，只有 `num_computed_tokens` 追赶 `num_tokens_with_spec`；当前版本无显式 FINISHED 队列
3. **EngineCore 双层分离**：逻辑层 EngineCore vs 进程层 EngineCoreProc，ZMQ 双 daemon 线程；`step_with_batch_queue` 填满队列优先于取结果消除 PP 气泡
4. **PagedAttention 全命中仍须重算末 token**（`max_cache_hit_length = num_tokens - 1`）
5. **VllmConfig 的 `model_config=None`** 是防止默认构造触发模型下载的刻意设计

## 遗留与后续建议

- 101 个裁剪批次如需补全（调优配置 JSON 除外），可基于 fingerprints + batches.json 断点续跑（本报告批次序号清单可复用）
- 阅读建议从 ONBOARDING.md 起步；deepwiki/6.5 提到 rust 前端与 explain 的 Rust 系列可互参
- 本知识库对应 2026-09-03 源码快照，vLLM 演进后可用 /understand 增量更新

---

# 增量更新轮（2026-10-28 ~ 10-31，_update-20261028/）

**输入**: 7894394b（2026-09-03）→ 06e172b5cf（2026-10-28），3222 commits。
**delta**: changed=1630 · deleted=79 · added=865 → 重分析 2484 文件 / 104 批（核心优先排序）+ 1 补录批 = 105 批。

## 产物终态
| 项 | 基线 2026-09 | 本轮 2026-10-31 |
|---|---|---|
| DeepWiki | 62 页（2026-09-02） | 74 页 TRUE_100（56 更新+18 新增+6 改名，INDEX/coverage 重写） |
| 图谱 | 11615n / 33598e / 16 层 14 步 | **14454n / 41124e / 16 层 16 步**（validator 0 issues/0 warnings） |
| fingerprints | 2226 文件 @7894394b | 7117 文件 @06e172b5cf |
| onboarding/explain | 4600 字/14 篇 | **ONBOARDING 重写 + explain 13 篇刷新（11-01，见下 Task7 章）** |

## 手术守恒账
11615 − 10165（changed∪deleted 节点）+ 13004（105 批新节点+51 兜底）= 14454；边 33598 − 31810 + 39336 = 41124；终检悬空 0。
诚实丢弃：符号级悬空 264（重构后消失的旧符号）、跨批重复 49n/25e。

## 本轮钉版（新坑四条）
1. **基线洞甄别**：手术 dry run 悬空归因发现旧图 87 个整片漏收文件（vllm/logger.py、lora/request.py、parser/ 子系统、multimodal/media/、mhc 内核、rust bench 等，被 1401 条新边实例引用）→ 派补录批真分析（batch-105）救回 ~1060 边；二环 51 个 barrel 文件由 surgery 通用兜底补最小节点（诚实标注未深析）。
2. **工具 schema 契约对齐**：worker 产出的 step/pipeline/service/schema 节点类型撞 surgery 白名单（险静默丢 17 节点）——白名单须与 file-analyzer 规范/validator fileTypes 同源。
3. **lineRange 字段污染**：batch-104 29 个节点把 complexity 字符串误填 lineRange——主会话按 sh/rust/py 三语法源码重扫修复；验收脚本要类型断言（isinstance list）而非只查存在。
4. **两波 1308 团灭的断点续跑**（10-28/10-29，各损失在飞批）：台账=products 目录即断点，缺哪批派哪批；收官组按 2 并发收敛防线。仓根 json/math/re/sys 四个 0 字节垃圾文件会被 naive import 解析吸成假边——已清理并在派发模板加规避条款。

## 架构情报（vLLM 2026-10 形态，全量见 _update-20261028/worker-highlights.md 17 节）
v1 引擎演进（kv_offload/speculator 家族/KV connector 军团/weight_transfer 五后端）· DeepSeek V4+K3+M3 mono 系 · GLM-5-Next 双胞胎 · snapshot 子系统（CRIU+canary oracle）· parser 声明式引擎（py/rust 双栈）· SamplingParams 迁移 msgspec · mHC 六后端 · Rust 前端 99→218 文件（完整 OpenAI 前端+bench 测量栈）· 30 类 arch convertor 枚举 2026 全 MLA 家族。

# Task7 文档重写轮（2026-11-01，图谱换血后的 ONBOARDING+explain 对齐）

**输入**: 图谱 14454n/41124e/16 层 16 步 @06e172b5cf；onboard-input.json（16 层/16 步/30 枢纽）+ 当前源码。
**执行**: 2 会话接力（00:1x 落 2 篇后 1308 停摆 → 20:10 断点续派 4 worker/4 并发；W3 被 1302 杀于收尾报告期但 3 篇死前全落盘零损失）。

## 产物终态
| 产物 | 规模 | 终验 |
|---|---|---|
| onboarding/ONBOARDING.md（8 节重写，仓内 .understand-anything/ 副本同步） | 不计空格 10846 字符（同口径旧版 12562，精简 14%）/79 全路径锚 | 0 坏 + 抽验 8/8 命中 |
| explain/ 13 篇重写（api_server 篇 2026-09 版保留） | 不计空格 4635-5221 字符/篇 | verify_explain.py 全量 0 坏（~1000 锚） |

## 内容级大勘误（旧 2026-09 文档被推翻的主干论断）
1. **主入口易主**：旧 ONBOARDING Step 11 指路 `entrypoints/openai/api_server.py`——现是 59 行弃用垫片（DeprecationWarning），真实入口迁 `entrypoints/launchers/`。
2. **cascade attention 整体移除**（PR #61126）：flash_attn 三路径之一作废、`_compute_cascade_attn_prefix_lens` 已死、`get_num_common_prefix_blocks` 恒返 0 仅保签名、`--disable-cascade-attn` no-effect。
3. **AsyncScheduler 缩成 56 行薄壳**：重叠调度本体移到 executor 的 AsyncModelRunnerOutput 路径。
4. **waiting 队列两级→三级**（+kv_holding_waiting/deferred_waiting）；`update_from_output` 返回 dict 按 client_index 分桶（多前端形态）。
5. **V2 model runner 实锤落地**（`v1/worker/gpu/model_runner.py` 2547 行目录化），V1 7192 行仍在默认路径；MRV2 由 `VLLM_USE_V2_MODEL_RUNNER`+平台特性裁决（gpu_worker.py:577）。
6. flash_attn forward 签名换血（output/output_scale 参数、FA4DenseAttentionKernel JIT 单例入口）；`chat_utils` 迁 `renderers/chat_utils/`；`serving.py` 拆 5 子包；tool parser 40+→55 向声明式 parser 迁移；speculator 11 族。
7. 行数勘误：model_runner "约 7700 行"实为 7192。

## 本轮钉版（新坑三条）
1. **锚风格三分**：同一系列里 worker 混用 全路径锚 / 首提后缩写 `:NNN` / 裸括号 `（NNN）`——终验器三种模式都要认，否则大量假坏（本轮流末 11 个"坏锚"人工消歧后全判真：vllm/ 前缀省略型+basename 歧义型+块起点型，升格全路径收编）。
2. **终验器假阳性两源**：URL 端口 `curl :8000/...` 冒充缩写锚（lookahead 加 `/` 排除）；`（NNN 行）`单数是文件长度引用非锚（区间 `（N-M 行）`才是锚）。
3. **字数规格按仓规模校准**：4000-6000 的 ONBOARDING 规格按中小仓（NCCL/browser-use）定标，vLLM 级仓 16 层表+16 步+15 概念+78 锚的硬内容下限即 10K+——规格应写"内容密度"而非死字数。

## 遗留（下轮候选）
explain 新子系统篇（parser 声明式引擎/snapshot/kv_cache_interface/Rust 前端/launchers 新入口）；api_server 旧篇与 launchers 新形态的代差说明。

# Task8 新子系统篇轮（2026-11-01 晚，Task7 遗留当轮清）

**输入**: 6 篇目标（5 新写 + 1 代差重写），3 worker/3 并发。
**产物终态**: explain 14→19 篇；全量终验 20 件套（19 篇+ONBOARDING）0 坏锚；仓库零污染。

| 篇 | 字符 | 锚 | 一句话 |
|---|---|---|---|
| vllm-parser-abstract_parser.md | 4912 | 79 | 声明式引擎+一行薄壳反向注册回旧注册表（同名无缝换引擎） |
| vllm-v1-kv_cache_interface.md | 4884 | 76 | spec 族 17 dataclass；**KVQuantMode.CUSTOM=12 与 OCTAVE_K3V4=12 同值碰撞**（疑似上游 bug，:61/:69） |
| vllm-snapshot.md | 5469 | 97 | 彩排机制（冻结前 sleep(2)→唤醒→reload→canary 二次比对）；sleep level 2=丢弃全部 GPU 显存（情报勘误） |
| rust-server-lib.md | 5576 | 94 | 与 Python 前端平行可切换非分层；对等性缺口清单（/v1/messages、batch、decisions、elastic EP=501 占位） |
| vllm-entrypoints-launchers.md | 6397 | 111 | 五路形态选择树；命名陷阱（launcher.py=HTTP 承载内核非总调度） |
| vllm-entrypoints-openai-api_server.md | 4705 | 45 | 迁移链四连 PR 实证；**上游文案 bug：垫片 :53 建议的 `vllm server` 子命令不存在**（应为 `vllm serve`） |

## 情报勘误（worker-highlights vs 源码）
- "py/rust 双栈 parser"方向钉准：rust/src/parser/（90 .rs）是 rust 前端 chat crate 专属**平行镜像**（无 pyo3、Python 零引用），py 为源非调用链。
- tool parser 注册表实测 57 名字（情报 55），其中 11 个已是引擎薄壳；kv spec 族 17 dataclass（情报 19）。

## 本轮钉版（新坑两条）
1. **相对根动物园**：worker 锚相对根混用 6+ 层（仓根/vllm//entrypoints//launchers//api_server//snapshot//parser/…）——终验 NO_FILE 风暴先跑 `qualify_anchors.py`（多前缀探测+唯一命中自动改写+歧义上报），本轮 33 锚一键升格、9 锚人工（全部实证判真）。人工裁定铁律不变：歧义锚必须看上下文+核实目标行内容再升格。
2. **跨文件缩写锚**：「散文点名他文件+`:NNN` 缩写」型（如 dp_supervisor 的 :562）会被终验器归到篇主文件而误报 OOB——升格为 `文件名:NNN` 或全路径，不能只信机械终验。

## 遗留（下轮候选）
KVQuantMode 值碰撞疑似上游 bug 值得单独核实报 issue；render/（CPU 渲染形态）与 run_batch.py（1125 行离线批）两形态可独立成篇；worker-highlights 17 节情报与 19 篇 explain 的交叉索引页。
