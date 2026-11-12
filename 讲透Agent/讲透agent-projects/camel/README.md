# camel（camel-ai/camel，18k★）全链知识库

"Communicative Agents for Mind Exploration" 多智能体框架（RolePlaying 双智能体范式起家）。本地仓 `/usr-data/data2/repos/agent-repos/agent-projects/camel`（commit 74469787 时锚定）。

## 全链状态表

| 环节 | 状态 | 产物 |
|---|---|---|
| DeepWiki | ✅ TRUE_100（2026-10-29 轮） | `deepwiki/` |
| understand 图谱 | ✅ **1698n/4118e/16层/16步tour** · validator 0 issues 0 warnings · fingerprints 594@74469787 | 仓内 `.understand-anything/knowledge-graph.json` |
| notes 勘误集 | ✅ 38 批 351 条 | 仓内 `.understand-anything/NOTES-DIGEST.md`（intermediate 外防 finalize 清理） |
| ONBOARDING | ✅ 6491 字符（不计空格）/54 锚/8 节 | `onboarding/ONBOARDING.md` |
| explain | ✅ 12 篇 48,847 字符/235 锚（2026-11-01） | `explain/01-12` |
| 锚终验 | ✅ 主会话独立抽验 18/290 锚：18 好/0 坏/0 歧义 | — |

**agent-projects 组迄今最大图谱**（对比 agentscope 557n）。字数口径=不计空格总字符；explain 六节结构。

## 图谱口径钉版（2026-10-31 wave#2）

- 旧 108 批 docs/examples/test 占 70% → re-prepare 裁剪至 **38 批 594 文件**（camel/ 527 + .github/apps/.camel/.container 等合法基础设施）；批阶段历经 1308 团灭（b31 死前落盘采纳、b32/b33 SendMessage 复活零损失）
- 验收：fileNodes 594/594 精确对齐、被裁目录残留 0；layers 16 层把 toolkits 156 文件拆三层精确对账

## 勘误精选（全部源码行号实证，全量见 NOTES-DIGEST 351 条）

**真 bug（高置信）**
1. FaissStorage `remove_ids` 后位置→ID 映射错位（`faiss.py:462/480` + 死变量 selector）
2. PgVector 索引恒 cosine_ops 与距离参数失配，`similarity` 实为未转换的距离——与其它后端语义相反（`pgvector.py:124/253`）
3. DockerRuntime/RemoteHttpRuntime `add` 循环后引用最后循环变量，一次 add 多函数只登记最后一个（`docker_runtime.py:315`/`remote_http_runtime.py:143` 同构）
4. RoleAssignment 正则 `\d` 单数字使 num_roles≥10 必失败；KG agent `len(groups)==6` 恒真致死代码
5. `ResponseWordsTerminator.reset()` 把状态重置成单 defaultdict——reset 后必 AttributeError
6. MilvusStore.add 循环内覆盖 data（MetaGPT 侧同族 bug 见其 README）
7. `open_api_toolkit.py:307` `'coolie'` 拼写错（cookie 的 apiKey 永注入不上）

**安全/卫生**
8. InternalPythonInterpreter 白名单只管 AST 通道，`execute_command` 走 `shell=True` 完全绕过沙箱（`internal_python_interpreter.py:598-604`）
9. 硬编码 Cloud SQL 凭据（camel230509）入仓（`apps` dilemma 线）
10. docker/subprocess [Y/n] 空回车=Y vs e2b/microsandbox 空回车死循环——四实现语义漂移

**名实/直觉陷阱**
11. `chat_agent.py` 6430 行单类 138 方法；`openai_config.py` 类名实为 ChatGPTConfig；role_playing 实在 `camel/societies/` 非 agents/
12. HybridBrowserToolkit 同名双包：TS 版（ws_wrapper+node WebSocket）与 `_py` 版（Playwright），测试测的是 TS 版
13. cot_datagen 宣称 MCTS 实为 score>0.9 早停爬山；evol_instruct `__all__` 幽灵导出（MathEvolInstructTemplates 必 ImportError）
14. messages 循环导入靠 `__init__` 底部 noqa:E402；MapRole 不存在，真哨兵是 openai_types.py 再导出的 NotGiven
15. BM25 朴素 `split(" ")` 中文失效；AutoRetriever 集合名=路径 md5，内容变更不失效

## 与 DeepWiki 的关系

DeepWiki 快照（2026-10-29）覆盖 docs 与示例视角；本图谱+explain 系列比快照深一个版本代（逐行锚定、含 351 条批分析勘误）。
