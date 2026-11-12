# 12 · 已知 bug 与坑专篇

## 角色定位

本篇收口前五篇埋下的所有"文档与实码脱节"点，并补齐散落各处的行为缺陷。Mycel 的代码质量不低——边界测试、哨兵测试、契约测试都很讲究——但**文档层与配置样例层明显滞后于代码重构**，这是读仓者最容易踩的雷区。以下每条都经源码核实，标注精确行号。

## 内部结构（十二坑全录）

**① sessions→sandboxes 命名迁移，3 测试钉住**。runtime 身份列已更名 `sandbox_runtime_id`，`tests/Unit/storage/test_chat_session_row_contract.py` 三个测试锁死新约：create 返回它（:4-17）、get 返回它（:20-40）、`PRAGMA table_info(chat_sessions)` 必含该列（:43-60）。旧列名回潮立即红。

**② e2e workflow 引用 4 个幽灵测试**。`.github/workflows/e2e.yml:32-39` 显式列 7 个 pytest 路径，其中 `tests/test_e2e_providers.py`、`tests/test_sandbox_e2e.py`、`tests/test_e2e_backend_api.py`、`tests/test_p3_e2e.py` **全仓不存在**（tests/ 已重组为 Unit/Integration 子目录布局，现存三兄弟实际在 tests/Integration/ 与 tests/Unit/sandbox/）。pytest 显式路径收集遇缺文件必报 error——每日 02:00 的定时 E2E 在当前树上必炸。

**③ README 幽灵文件群（双语）**。`config/defaults/README.md:10-14` 描述的 `agents/{default,coder,researcher,tester}.json` 与 `model_mapping.json` **全不存在**（实际：4 个 .md 提示词 + models.json，见 09 篇）；:66-71 的六个虚拟名 `leon:fast/balanced/powerful/coding/research/creative` 与 models.json 实际四名 mini/medium/large/max 脱节；:99 `mycel --agent coder`、:106 `load_config(agent="researcher")` 均为死签名。另根 `README.md:200` 与 `README.zh.md:196` 双语都链向 `CONTRIBUTING.md`——该文件全仓不存在（悬空链接），中英两份一起悬。

**④ @@@port-precedence 注释与实码顺序相反**。`backend/web/main.py:11` 注释宣称 "git worktree config > LEON_BACKEND_PORT > PORT > 8001"，但实码 `resolve_app_port`（backend/bootstrap/app_entrypoint.py:20-37）**先查环境变量**（env_key 或 PORT，:21-22）**再查** git worktree（:24-33）——真实优先级是 `LEON_BACKEND_PORT > PORT > worktree > 8001`，注释整个写反。@@@ 标记本该钉住契约，这条钉反了。

**⑤ enrich_from_runtime 整除均摊丢余数**。`eval/tracer.py:107-112`：流式模式拿不到逐调用 usage，就把 runtime 聚合值按 `token.input_tokens // n` 整除均摊到每次 LLM 调用——余数直接丢（100 tokens/3 次调用 → 33×3=99），且六项指标各自独立取整，`per_call_input + per_call_output` 未必等于 `per_call_total`。成本均摊（:114-117）却是浮点除法无此问题——同函数内两种口径并存。

**⑥ .env.example 死配置（src 零消费者）**。`frontend/app/.env.example` 的 `VITE_SUPABASE_URL`/`VITE_SUPABASE_ANON_KEY` 在 `frontend/app/src/` **零引用**（前端全走后端 API，不直连 Supabase）。根 `.env.example` 同病：`MODEL_NAME` 全仓无消费者；`LANGSMITH_API_KEY` 无消费者——langsmith 的 key 实际来自 observation 配置的 `cfg.api_key`（backend/threads/run/observation.py:52-55），不读这个环境变量。照抄样例配置的人会以为改了生效。

**⑦ pre-commit `|| true` 吞错误**。`.pre-commit-config.yaml` 的 eslint（:12）与 tsc（:19）两个本地钩子 entry 都是 `bash -c '... || true'`——**前端 lint/类型错误永远退出 0**，钩子形同虚设。对比同文件 ruff 钩子是真闸。前端的类型安全实际只靠 CI 里是否有独立步骤，本地 pre-commit 给的是假安心。

**⑧ Firecrawl 客户端过滤语义差**。`core/tools/web/searchers/firecrawl.py:50-54` 的 include/exclude_domains 是本地子串匹配 `domain in url`——`evil-example.com` 会命中 `example.com` 过滤；且过滤在取回全部结果之后，`limit` 语义缩水。Tavily/Exa 都是服务端过滤（tavily.py:38-42、exa.py:46-50），同参数不同语义，模型侧无法区分。

**⑨ DESIGN_SYSTEM.md 字体栈代差**。`frontend/app/DESIGN_SYSTEM.md:60` 的 Body 栈止于 `"Noto Sans SC", sans-serif`，而实码 `frontend/app/src/index.css:61` 还有三级兜底 `"Helvetica Neue", Helvetica, Arial`；:136 的等宽栈（SF Mono/Fira Code...）文档完全未记。设计文档落后代码一个代差。

**⑩ WebService 无降级链**（详见 08 篇）：`service.py:136/:152` 只取 `_searchers[0]`/`_fetchers[0]`，构造顺序即优先级，配多家 provider 无容错。

**⑪ eval 默认场景目录不存在**：`eval/harness/runner.py:224` 回退 `eval/scenarios/`，全仓无此目录，CLI 裸跑必打 "No scenarios found"。

**⑫ is_error 字符串启发式**：`runner.py:147` 以 `"error" in content.lower()` 判工具失败——正常输出含 "error" 一词即误报，eval 的工具成功率系统性偏低。

## 外部连接

这些坑的分布有规律：①②⑥⑦全在**自动化链路**（测试钉子/CI 钩子/环境样例），③④⑨全在**文档层**，⑤⑧⑩⑫在**实现启发式**。修复成本排序：④（一行注释）、⑨（补文档）最便宜；②（补 4 个路径或改 workflow）次之；⑧（改客户端过滤为精确域名匹配）要动语义；⑤（余数补偿）要设计分配策略。

## 数据流

无独立数据流——本篇是横向缺陷清单。但注意①与②的联动风险：若有人为修 e2e workflow 的幽灵路径把 Integration 测试挪回 tests/ 根，会同时破坏 Integration/README.md 的零 mock 分层契约（11 篇）与 ci.yml 的路径假设——修一个坑前先看它钉住了谁。

## 设计决策（含批判）

- **@@@ 标记体系本身是好设计**（决策就地留痕），但④证明标记也需要 review——注释写反比没有注释更危险，因为它自带权威感。
- **测试钉死历史决策**（①的列名、schema 哨兵）是防回潮的正确手段；②的幽灵路径则是反面：测试目录重组后没有任何机制校验 workflow 引用的路径存在，CI 的 e2e job 悄悄变成摆设。
- **`|| true` 式钩子**是"为了让 pre-commit 能装上"的妥协，正确做法是 `stages: [manual]` 或显式 warn 级别，而不是假装通过。

## 新人提示

1. 读任何 Mycel 文档（含 README/DESIGN_SYSTEM/defaults 内的说明）先默认落后实码一个版本，动手前以 grep 实码为准。
2. 改 tests/ 目录结构后必查 .github/workflows/ 引用；改前端构建配置后必跑一次真实的 pre-commit 看 eslint/tsc 是否真在拦。
3. 调 eval 成本数字对不上时，先想起⑤的均摊取整——逐调用 token 是估计值不是真值。
4. 想提交 PR 修这些坑：③④⑨是纯文档改（低风险），②要同步 e2e.yml 与真实测试路径，⑦去掉 `|| true` 前先确认前端当前零 lint 错误，否则钩子一开就全队阻塞。
