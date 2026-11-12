# MetaGPT（geekan/MetaGPT）全链知识库

SOP 多智能体框架（"one-step software company"）：角色分工流水线范式。本地仓 `/usr-data/data2/repos/agent-repos/agent-projects/MetaGPT`（commit 11cdf466 时锚定）。**注意：understand 产物在 agent-projects/MetaGPT，inventory 清单的 canonical_path 指向 awesome-agents 副本是误导。**

## 全链状态表

| 环节 | 状态 | 产物 |
|---|---|---|
| DeepWiki | ✅ TRUE_100（2026-10-29 轮，57 页） | `deepwiki/` |
| understand 图谱 | ✅ **1718n/3888e/15层/15步tour** · validator 0 issues · fingerprints 686@11cdf466 | 仓内 `.understand-anything/knowledge-graph.json` |
| notes 勘误集 | ✅ 39 批 312 条 | 仓内 `.understand-anything/NOTES-DIGEST.md` |
| ONBOARDING | ✅ 6485 字符（不计空格）/66 锚/8 节 | `onboarding/ONBOARDING.md` |
| explain | ✅ 12 篇 43,941 字符/215 锚（2026-11-01） | `explain/01-12` |
| 锚终验 | ✅ 主会话独立抽验 20/215：15 好/0 坏/5 多候选 basename 按篇主题归位 | — |

**agent-projects 组最大图谱**（MetaGPT 1718n > camel 1698n > agentscope 557n）。字数口径=不计空格总字符。

## 图谱口径钉版（2026-10-31 wave#2）

- 旧 69 批 tests/examples/docs 占 41% → re-prepare 裁至 **39 批 686 文件**（metagpt/ 643 + config/.github/.devcontainer 等合法基础设施）
- 批阶段两次 1302 限流零损失（SendMessage 复活）；merge 0 悬空（b25 预警的跨批前缀错位被 merge 归一化消化）；file 级 686/686 精确对齐
- layers 15 层：ext/ 193 节点独占一层（史上最大单层）；含 config 48/document 33/pipeline 5/step 26/service 2 类别节点

## 勘误精选（全部源码行号实证，全量见 NOTES-DIGEST 312 条）

**架构级（直觉颠覆）**
1. **Team.use_mgx 默认 True 走 MGXEnv**——经典 SOP 三角色在 `software_company.py:51-62` 被注释停用；ProductManager 已改继承 RoleZero（`roles/product_manager.py:21`）靠 use_fixed_sop 降级切换；README 里的经典 SOP 默认已不是默认
2. **metagpt/skills/ 40 个 Semantic Kernel 风格技能是零消费 vendored 死资产**——skill_loader 实际读 `docs/.well-known/skills.yaml`，`const.py:64` SKILL_DIRECTORY 定义后零引用（接线未完成遗迹）
3. **general_api_base 是 openai 0.x APIRequestor vendored fork**（LLM-* 品牌化、错误文案残留 openai.proxy）
4. SWE agent 真身在 `roles/di/swe_agent.py`+`tools/swe_agent_commands/`+`prompts/di/` 三块组合，`ext/swe_agent/` 不存在

**真 bug（高置信）**
5. DFSSolver._dfs 引用不存在的 `self.max_steps`（`ext/aflow/tot.py:193`，DFS 路径必 AttributeError）
6. `Context.deserialize` 丢弃 model_validate_json 返回值（`context.py:127`）——cost_manager 恢复失效
7. MilvusStore.add 循环内覆盖 data 字典，多 id 仅最后一条生效
8. compress_messages 剩余额度 0 时 `-0==0` 切片退化为保留全文（`base_llm.py:386`）
9. rag/benchmark `mean_reciprocal_rank` 用未定义变量 text 必 NameError（`base.py:119`）
10. aflow `extract_test_cases_from_jsonl` 默认调用直接 NameError（枚举成员与 `.value` 字符串比较）

**安全/卫生**
11. fulltest/unittest workflow 用 pull_request_target + checkout head SHA——secrets 暴露给 fork PR（GitHub 警示模式）；fulltest 的 frp 步骤写 authorized_keys 开 SSH 反向调试隧道
12. RunCode 含 `exec()` 无沙箱 + 自动 pip install；Minecraft agent `/step` 用 eval 执行 LLM 生成代码
13. Bedrock 流式路径按 HTTP 头与 provider.usage 各记一次，疑似成本双计（`bedrock_api.py:89/134-136`）
14. `import regex as re`（第三方）与 stdlib re 同名双实现并存（repair 线）

**名实/拼写系**
15. WRTIE_CODE（`actions/__init__.py:38`）、ArgumentsParingAction、actionoutout_、RoleState.PROTECTED="projected"、poignancy_action 模板是 event 版未改死副本（diff 字节级相同）、write_code_an_draft 零消费死代码草稿、write_plan docstring 指向不存在的 plan.py（Plan 实在 schema.py:495）
16. 角色间路由押在人名常量上（"Alex"/"Edward"/TEAMLEADER_NAME="Mike"），改名即静默断路
17. pydantic v2 删同名 property：`roles/role.py:318` 的 name property 是永不生效的死代码

## 与 DeepWiki 的关系

DeepWiki 57 页快照 + 本图谱/explain 深一个版本代（312 条批分析勘误、686 文件全覆盖、mgx 默认线等架构变更实证）。
