# 04 · claude-api 文档线：八语言 SDK 指南、Managed Agents 与 preserved-thinking 双探针

> 仓根 = `/usr-data/data2/repos/agent-repos/anthropics/skills`，锚为仓根相对路径，行号现场核实。

## 1. 角色定位

`skills/claude-api/` 是全仓最大的"文档即技能"：一个把 **Claude API/SDK 官方参考知识**完整搬运进模型上下文的技能，注册为独立插件（`.claude-plugin/marketplace.json` 三号位）。它的 SKILL.md 603 行全仓最长，frontmatter（`SKILL.md:5-6`）用一段超长 description 同时写死 TRIGGER（提到 Claude/Anthropic/Fable/Opus 等一律先读本技能）与 SKIP（先跑 `grep -rE 'openai|langchain_openai|…'`，命中他厂 provider 就让路）——**把技能触发逻辑写成可执行程序性判定**。反幻觉宣言在 `:49`："The `{lang}/` files in this skill are authoritative over recalled patterns"——技能内文件压倒模型训练记忆。

## 2. 内部结构

三层金字塔：

- **总纲 `SKILL.md`**：三纪律（`:22-27`：官方 SDK 优先/绝不裸 HTTP/绝不凭记忆猜用法）、默认值（`:35`：claude-opus-5-5+adaptive thinking+默认流式+工具 eager input streaming）、API 漂移表（`:43-47`：五列"陈旧先验 vs 当前 API"，如 `budget_tokens` 在新模型上 400）、八个子命令路由（`:57-65`：migrate/prompt-audit/upgrade/cost-optimize/build-eval/preserved-thinking-migration/hillclimb）、语言探测规则（`:75-80`：按项目文件推断语言，Kotlin/Scala 归 Java SDK）。
- **八语言目录**：`csharp/curl/go/java/php/python/ruby/typescript` 同构覆盖 streaming/tool-use/managed-agents。python 最全（`python/claude-api/README.md` 566 行，另含 batches/files-api/sdk-upgrade/streaming/tool-use）；curl 最薄（仅 `curl/managed-agents.md` 369 行+`examples.md` 257 行）；csharp 363 行含 Microsoft.Extensions.AI 集成；php 175 行含 Bedrock/Vertex/Foundry 客户端。
- **`shared/` 事实层**：33 个 md+工具目录——`models.md`（149 行，精确 model ID 唯一来源，`:3`）、`model-migration.md`（2252 行迁移总指南）、`prompt-caching`/`token-counting`/`cost-optimization` 成本三件套、`error-codes`/`platform-availability` 运维对、**managed-agents 子产品手册 14 件**、`evals/` 评测工具线、`preserved-thinking-migration/` 双探针。

## 3. 外部连接

- **`shared/live-sources.md`** 是对外网关：列出各 SDK 官方仓库与文档 URL，`SKILL.md:27` 授权"技能文档没有的绑定就 WebFetch 官方 repo 再写代码"；`:29` 给网络受限时的降级路径（按 `{lang}/` 文件的命名空间表写代码+编译错迭代）。
- **Managed Agents 21 件套**：`shared/managed-agents-*.md` 14 件（overview/core/environments/memory/multiagent/events/tools/webhooks/scheduled-deployments/self-hosted-sandboxes/outcomes/onboarding/client-patterns/api-reference）+ 六语言目录各一份入口（curl 是单文件）。`managed-agents-overview.md:3` 一句话心智模型：**每 session 一个容器当 agent 工作区，agent loop 跑在 Anthropic 编排层**；`:5-18` 是最常被违反的强制流程——Agent 对象建一次存 ID（`POST /v1/agents`），每跑一次建 Session（`POST /v1/sessions`）只传指针，"If you're about to write `sessions.create()` with `model` on the session body - **stop**"。
- **对评测工具线**：`shared/evals/build-eval.md` 面试式建评流程（Step 0 问评估对象→来源→评分法→成本签收）；`report/SCHEMA.md` 定"适配器宽容产出、渲染器严格消费"契约；两个 .mjs 脚手架（下文）。
- **skills 生态内**：与 skill-creator 的评测哲学互为参照（前者评 API 代码质量，后者评技能触发率）。

## 4. 数据流：两条可执行工具线

**preserved-thinking 双探针**（诊断"思维块签名失配"——API 只认产生该 thinking block 的那次对话）：

1. `SKILL.md:64` 子命令路由到 `shared/preserved-thinking-migration.md` 工作流：Step 0.5 先跑三请求自证检查在跑。
2. **capture 侧**：抓真实请求体存 jsonl。
3. **diff 探针** `prefix_diff.py`：本地比对相邻请求对，规范化层（canon_*）先把与签名无关的形状差异抹平，避免把合法重排误报为编辑。
4. **probe 探针** `drop_block_probe.py`：把捕获对话重放给 API（挂 `prefix_mismatch_behavior: "drop_block"` 与 `thinking-binding-controls-2026-08-01` 头），数被丢弃的块。工程纪律全在 docstring（`drop_block_probe.py:1-30`）：零依赖（urllib）、凭据只从环境读且绝不打印、双凭据同设只发 token（API 拒双头）、重放前最小整形（max_tokens=16 判词已在首 token 前定、tool_choice=none 防真跑工具、温度 1 去 top_p——**绝不动 tools** 因为工具集本身在比对范围内）、org 隔离警示（跨组织 key 重放无诊断意义）、first-party only（Bedrock/Vertex 不适用）。
5. 归因查 `shared/preserved-thinking-migration/causes.md`——逐条注明在哪些模型上实测、error 与 drop_block 两种模式各自的日期。

**evals 报告线**：`report/runner-scaffold.mjs`（602 行）是评测跑批脚手架——harness_sha 人审门、冻结基线配对评审、崩溃安全逐行落盘、429 指数退避、单例墙钟上限、served-model 断言、失败进 errors.jsonl 带计费信息；`report/build-report-lite.mjs`（488 行）把结果渲染成可分享 HTML，`:26-38` 全量拒符号链接（O_NOFOLLOW 打开 fd 后 fstat 防 TOCTOU；Windows 上 Node 未定义该 flag 则降级 lstat 拒绝）、磁盘字符串全量 HTML 转义、绝不执行数据内代码——**防模型影响目录里的提示注入把 `~/.ssh/id_rsa` 塞进报告**。

## 5. 设计决策

- **文档权威级声明压倒记忆**（`SKILL.md:27,49`）：LLM 时代 API 文档技能的核心风险是训练先验过时，本技能用"漂移表+权威声明+WebFetch 兜底"三层反幻觉。
- **SKIP 规则带 grep**（`:6`）：触发判定不是自然语言而是先跑正则——避免在 OpenAI 项目里硬塞 Anthropic SDK（`prompt-audit` 子命令例外，非交互不停下，`:16`）。
- **大文件导航约定**：`model-migration.md` 自称大文件指示按节名跳转；语言系列 README 开篇即功能表而非安装节——**面向模型的文档把"怎么找"置于"怎么装"之前**。
- **Managed Agents 的版本化说教**：overview 用加粗 stop 与表格（`managed-agents-overview.md:11-16`）反复阻止"每次运行 create 新 agent"反模式——文档主动预判最可能的误用。
- **工具脚本零依赖+凭据卫生**：两个探针均纯 stdlib，凭据规则写在最前面——文档技能内嵌工具同样执行生产级安全纪律。

## 6. 新人提示

- 把 `SKILL.md` 的子命令表（`:57-65`）当路由器用，七个流程各自链到 shared/ 的专文，**勿试图一次读完 603 行总纲+33 文件**。
- 查模型 ID 只信 `shared/models.md:3` 起的目录表或直接调 Models API（`models.md:9-25` 的程序化发现代码块）。
- 写新集成前先过 `:43-47` 漂移表自检训练先验；迁移任务直接走 `migrate` 子命令的 Step 0/1 流程。
- 双探针按"diff 问本地、probe 问 API"分工选；重放花钱，先 `--dry-run` 再 `--count-tokens` 免费通道（`drop_block_probe.py:13-16`）。
- 八语言目录同构，精读 python 版后其他语言 diff 着看——curl 版是"裸 HTTP 形状"的语义基准。
