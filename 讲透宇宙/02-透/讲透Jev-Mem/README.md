# 讲透 Jev-Mem

> [libingzheren/Jev-Mem](https://github.com/libingzheren/Jev-Mem) · System-One-Controlled
> Agentic Memory（arXiv [2609.23986](https://arxiv.org/abs/2609.23986)，2026-09-21 开源）
> 本地仓：/usr-data/data1/agent/Jev-Mem（main @7ab0c73c）

一句话：把**高频记忆管理决策**（写入/检索路由/关系判定）交给轻量 System-One 控制器
Jev，把**深层推理**留给 System-Two LLM——LoCoMo 上 GPT-4o-mini 报告答案质量 +11.0%、
记忆构建 6.6×、查询延迟 −36.7%。三件套：System One 控制 + 共享记忆（语义/时序/因果/
实体四关系图视图）+ System Two 答题。

## 产物状态（2026-10-13 全链收官 ✅）

| 步骤 | 状态 | 产物 |
|---|---|---|
| DeepWiki 全量 | ✅ | [deepwiki/](deepwiki) 26/26 页 100%，267K 字符（7 章+19 子页，含 3.3 下两层嵌套） |
| understand 图谱 | ✅ | 仓内 `.understand-anything/knowledge-graph.json`：**307 节点/641 边/9 层/15 步 tour**，validator 0 issues，fingerprints 90 文件基线@7ab0c73c |
| onboarding | ✅ | [onboarding/ONBOARDING.md](onboarding/ONBOARDING.md) 8 节 6893 字，54 文件引用零缺失 |
| explain 精讲 | ✅ 全量 | [explain/](explain) **39 篇六节结构覆盖全部 60 个代码文件**，合计 183106 字、1673 个 `文件:行号` 锚全回源校验（字数口径：单文件篇 3400-6300、合集篇 4500 内、重批篇至 4800，随信息密度渐进） |

## DeepWiki 结构速览

1. **Overview**（Getting Started / Configuration Reference）
2. **Core System and CLI**（JevMemSystem Orchestrator / CLI）
3. **Memory Subsystem**（写入路径 / 存储层 / 检索与查询引擎【3.3.1 引擎内幕 / 3.3.2 答案格式化与 Best-of-N】/ 时序处理）
4. **System-One Controller (Jev)**（写读策略 / Noul-Choice 问题协议与客户端）
5. **Benchmarks and Evaluation**（LoCoMo / LongMemEval / 评分与裁判 / 数据集）
6. **Project Infrastructure**（打包发布 / 测试 / 工具与文档）
7. **Glossary**

抓取通道：`mcp.deepwiki.com/mcp`（网页端 Vercel 盾，MCP 直连可用），工具
`~/ai/pipeline-bin/deepwiki/dw_fetch_mcp.py`。每页自带 `<details>`
源文件清单 + file:line 引用锚（understand 阶段交叉对账已用）。

> 坑（钉版）：dw_fetch_mcp.py 结构解析只认两层缩进，3.3.1/3.3.2 三层嵌套子页会被
> 误记"结构外页"（x1/x2）+ coverage 报 INCOMPLETE——实际不缺页，正名归位即可。

## understand 图谱速览（9 层 90 文件）

| 层 | 文件数 | 一句话 |
|---|---|---|
| 编排、CLI 与兼容入口 | 11 | system 门面 + cli + 根目录 6 个 sys.modules 兼容 shim |
| System-One 决策控制 | 6 | jev_client/policies/questions/retrieval/配置（fan-in 冠军 jev_mem_config） |
| 记忆存储与检索子系统 | 13 | TRG 记忆图/图库/向量库/查询引擎/构建器（组内密度 0.343 全场最高） |
| 评测与答案质量 | 7 | LLMJudge/Evaluator/Best-of-N/答案格式化 |
| 基准与数据集 | 6 | LoCoMo/LongMemEval runner + 数据集加载 |
| 测试 | 9 | test_jev_mem（度数冠军 95）+ 专项测试 |
| 共享工具与维护脚本 | 7 | utils 兼容层 + 公开发布导出脚本 |
| 文档与示例 | 15 | README/architecture/evaluation + 两个演示数据集 |
| 配置与项目支撑 | 16 | 四份实验档 JSON + CI（ubuntu×macos 矩阵）+ 打包清单 |

15 步 tour 主线：概览 → CLI 门面 → 配置 → Jev 客户端 → Noul 协议 → 写路径 →
存储（TRG/图/向量）→ 检索 → 时间解析 → 答案格式化 → 评测闭环 → LoCoMo →
LongMemEval → 实验档 → 测试/CI/发布。

## explain 索引（12 篇，行号全实证）

| # | 篇 | 源文件 | 最核心发现 |
|---|---|---|---|
| 01 | [编排门面](explain/01-编排门面-jev-mem-system.md) | jev_mem/system.py（75 行） | 纯门面零业务，但 query 里 `top_k=5` 硬编码与 config `answer_top_k=15` 口径分裂 |
| 02 | [控制面配置](explain/02-控制面配置-jev-mem-config.md) | memory/jev_mem_config.py | `type(value) is not int` 防 bool 混入；权重校验=打分公式除法分母的防线 |
| 03 | [Jev 决策客户端](explain/03-jev-决策客户端-jev-client.md) | memory/jev_client.py | SDK retry 归零+外层预算单权威；Choice 答案"选中项必为最高概率"自洽校验 |
| 04 | [Noul-Choice 协议](explain/04-noul-choice-协议-jev-questions.md) | memory/jev_questions.py | 三段式命题把 prompt 工程变成测量仪器；问题 ID 不进模型 |
| 05 | [写读策略](explain/05-写读策略-jev-mem-policies.md) | memory/jev_mem_policies.py | admission 打分 redundancy 用减法非乘法——刻意放过"高价值高冗余"更新 |
| 06 | [记忆构建写路径](explain/06-记忆构建写路径-memory-builder.md) | memory/memory_builder.py（1388 行） | Jev+MAGMA 双构建器同居保消融可比；1187-1190 猴子补丁有异常安全隐患 |
| 07 | [TRG 记忆结构](explain/07-trg-记忆结构-trg-memory.md) | memory/trg_memory.py | **610-639 休眠缺陷**：`_infer_latent_edges` 拼 prompt 从未发送，时序启发式冒充因果推理 |
| 08 | [图存储](explain/08-图存储-graph-db.md) | memory/graph_db.py（707 行） | `LinkStatus`/DEPRECATED 为预留未用机制；`delete_link` 裸 except 吞异常 |
| 09 | [向量存储](explain/09-向量存储-vector-db.md) | memory/vector_db.py | `IndexType` HOT/WARM/COLD 温度分层**预留未生效**（无生产消费者） |
| 10 | [检索引擎](explain/10-检索引擎-query-engine.md) | memory/query_engine.py（2113 行） | **181-188 过拟合**：temporal_keywords 硬编码把 LoCoMo 会话编号焊进引擎 |
| 11 | [时间解析](explain/11-时间解析-temporal-parser.md) | memory/temporal_parser.py | 相对时间锚定机制；畸形 JSON 容错解析 |
| 12 | [LoCoMo 基准](explain/12-locomo-基准-benchmarks-locomo.md) | jev_mem/benchmarks/locomo.py（877 行） | **266 行真 bug**：`score_only_mode` 引用未定义 `test_results`（应为 `updated_results`），低分题必触发 NameError |

## explain 扩编索引（篇 13-39，挖透剩余全部代码文件）

| 篇 | 主题 | 源文件 | 核心发现 |
|---|---|---|---|
| 13 | LongMemEval 基准 runner | benchmarks/longmemeval.py（2333 行） | **金标泄漏**：baseline 用 answer_session_ids 直取会话+prompt 标 "CONTAINS ANSWER"，与 Jev 分支口径倒挂 |
| 14 | 答案格式化 | memory/answer_formatter.py（984 行） | "保守化转向"历史（:305 注释钉版）；三个旧规范化器+validate_answer 全成死代码 |
| 15 | 主测试套件 | tests/test_jev_mem.py（874 行） | 54 测试函数+4 夹具≈百用例九族覆盖；mock 协议即文档 |
| 16 | 记忆分层兼容层 | utils/memory_layer.py（801 行） | 五个 *_AVAILABLE 旗标设完即弃；add_document 增量路径三处断裂 |
| 17 | 测试工装 | memory/test_harness.py（631 行） | 串行/并行取证粒度漂移；BERTScore 全局锁=并行评测串行热点 |
| 18 | 通用工具箱 | utils/utils.py（375 行） | 不可答判定与 llm_judge 双实现口径分裂；aggregate_metrics 零消费 |
| 19 | 会话分段器 | memory/episode_segmenter.py（331 行） | **跨日快路径死代码**：builder 传 isoformat 字符串而 detector 期望 .date() |
| 20 | Best-of-N 选择器 | memory/best_of_n_selector.py（300 行） | **装配未用**：主路径实例化后真正执行体是 test_harness 内联重写；:85 调不存在的方法 |
| 21 | Laya 后端测试 | tests/test_laya_backend.py（279 行） | HEAD 提交的验收测试；usage 按前向次数/预算按 evaluate 次数双语义钉死 |
| 22 | 关键词增强 | memory/keyword_enrichment.py（269 行） | **口径分裂**：trg 传入 'keywords' 键被静默丢弃；"may" 绕过停用词；CJK 静默 no-op |
| 23 | LoCoMo 数据集 | jev_mem/datasets/locomo.py（246 行） | 图片证据预扫描产出只进 print 不进数据模型；空数据集必崩 |
| 24 | LLM 裁判 | memory/llm_judge.py（231 行） | gpt-4o-mini 硬编码；reasoning 解析后丢弃再编程式化理由；平方级写入换断点续跑 |
| 25 | LongMemEval 评测器 | memory/longmemeval_evaluator.py（210 行） | benchmark 里构造一次零调用；metrics 垫片把 f1/bleu 伪造成 judge 分 |
| 26 | LoCoMo 评测器 | memory/evaluator.py（208 行） | :151-152 恒真条件+直接索引取值的 KeyError 雷；None 键序列化成 "null" 桶 |
| 27 | 发布完整性检查 | scripts/check_public_release.py（207 行） | 四模式漏斗+"永不打印被扫值"自我一致性设计 |
| 28 | 检索路由 | memory/jev_mem_retrieval.py（206 行） | 五阶段状态机；预算"看过即扣"=注意力配额语义；while 条件永假全靠 break |
| 29 | LongMemEval 数据集 | jev_mem/datasets/longmemeval.py（181 行） | sys.modules 别名替换保 pickle 类身份；同文件防御口径分裂 |
| 30 | LongMemEval Jev 桥接 | memory/longmemeval_jev.py（165 行） | timing 先 answer 后 build 会 AttributeError；close 后 engine 悬挂引用 |
| 31 | 发布测试 | tests/test_public_release.py（155 行） | credential 形状集非完备；manifest 测试=仓库根快照测试 |
| 32 | 桥接测试 | tests/test_longmemeval_jev.py（139 行） | `__new__` 直造 tester 的属性契约隐式化 |
| 33 | 原生运行时测试 | tests/test_native_runtime.py（89 行） | 重测试 Linux CI 腿整段跳过；"leaked semaphore" 字符串嗅探 |
| 34 | 锚点召回评估 | scripts/evaluate_anchor_recall.py（83 行） | 复刻 query_engine 私有方法的漂移风险；limit 硬编码 60 与线上 40 不同档 |
| 35 | 命令行接口 | jev_mem/cli.py（80 行） | --input 双语义；build/query 两路径零测试覆盖 |
| 36 | 兼容入口与包结构（合集×14） | 根目录 6 shim + barrel/`__init__` 族 + setup.sh | sys.modules 别名转发三保（类身份/pickle/monkeypatch）；双 PEP 562 惰性 barrel；双 __version__ 双出口 |
| 37 | 编码后端族（合集×5） | openai/mock/local_device/cache_compat/laya_backend | 真/假/本地三实现可替换；降级链 catch Exception 过宽致维度静默换档；laya 全程持锁串行 |
| 38 | 结构命名守卫测试（合集×4） | test_project_layout/test_backend_cache/test_naming/test_metric_resources | 四组元测试守护 sys1mem→jev-mem 迁移四正交切面；mock 缓存静默复用理论通道 |
| 39 | 演示与发布导出（合集×2） | jev_mem/demo.py + scripts/export_public_repo.py | demo 三重替身独立可拆；export 失败残留拒覆盖；SHA256SUMS 只生成不回读 |

> 扩编方法论：23 个实质文件（≥80 行）单篇精讲；25 个微小文件按主题并入 4 个合集篇——每个被覆盖文件均有 ≥2 个行号锚。质量门：六节结构、行号锚实读+脚本验界 0 越界、数值黑名单防误转换、import 关系 grep 实测（图谱仅参考，口径差注明）、批判性发现显式化。

## 流水线工具（本轮固化）

understand 步全链五件套已固化 `~/ai/pipeline-bin/understand/`：
`prepare_understand.sh`（scan+import-map+batches）→ `phase4_prep.py`（file 级精简输入）
→ `finalize_graph.py`（组装+0 issues 闸+fingerprints+meta）→ `onboard_prep.py`
（子代理安全输入）→ `ua-inline-validate.cjs`。批分析 4 并发子代理派发模板
`/tmp/ua-dispatch-jm.txt`（Jev-Mem 轮实例）。

## 勘误与边界（相对 DeepWiki 快照）

- explain 系列发现多处 DeepWiki 快照未覆盖的实现层问题（top_k 口径分裂、
  temporal_keywords 硬编码、TRG 休眠路径、locomo.py:266 NameError）——
  本目录文档比 DeepWiki 快照深一层（源码行号实证）。
- README 自述边界如实保留：LongMemEval 不声称结果、宽松 scorer 非官方指标、
  合成样本非基准质量、best-of-n 默认 3 有参考偏置。
