# 05 · Agent Skills 与签名评测线：SKILL.md、Sigstore 供应链与双数据集评测

## 角色定位

`skills/g-assist-mcp-skill/` 是与 plugins 平行的第二条扩展线：plugins 面向 G-Assist 引擎本体，skills 面向**外部 MCP 宿主**（Claude Code、Codex 等 agent）——把 `gassist_*` 显示/GPU 控制工具包装成标准 Agent Skill。五件套：`SKILL.md`（本体）、`skill-card.md`（发布卡）、`BENCHMARK.md`（评测报告）、`evals/`（数据集子目录：EVAL.md 评测手册 + evals.json + evals-hardware.json）、`skill.oms.sig`（签名）。这条线回答：一份纯指令型 skill 如何被**验证、签名、CI 化**地发布。

## 内部结构

### SKILL.md：反幻觉行为规范

frontmatter（`SKILL.md:1-12`）含 `license: CC-BY-4.0`、version 1.0.0；正文是 agent 行为法：

- **诚实优先两分支**（`SKILL.md:84-96`）：零个 gassist 工具→等几秒重查，仍无则直说"未连接"，不猜不编；有工具但没用户要的那种→说"此硬件不支持该控制"并列出可用能力。
- **工具禁造令**（`SKILL.md:99-102`）："Never create, invent, register, or guess tools"。
- **确认权在服务器**（`SKILL.md:110-123`）：变更类工具由服务端经 MCP elicitation 收集批准，agent 不得等聊天"yes"或加 `confirm`/`force` 参数绕过。BENCHMARK 唯一 Tier 1 发现即此段——`SKILL.md:119` 被审为 "Excessive Agency: no approval"（`BENCHMARK.md:108-110`）。
- **工具目录表**（`SKILL.md:153-175`）：21 个 `gassist_*` 工具按六类分组，逐个标注参数形态（gamma 是字符串枚举）。硬件门控：亮度/色彩/Pulsar 类仅 Native G-SYNC 显示器才出现（L148-151）。
- **单调用纪律**（`SKILL.md:184-192`）：一次一调用禁并行，开放指令被示范为恰好三步，多做即违规。
- 排障表 L243：调用可能**不带错误却在文本里报告失败**（`isError: false` 假成功）；环境细节 L57-67：rise_mcp.exe 路径含空格，Cursor 须注册 8.3 短路径。

`skill-card.md`：许可 **CC-BY-4.0 AND Apache 2.0**（L10）、无需 API key（L18）。

### skill.oms.sig：Sigstore bundle v0.3 签名

单行 JSON 两部分。**证书链**（openssl 实测）：叶 `CN=NVIDIA Agent Skills Signing 001`（2026-04→2028-04）← 中间 `CN=NVIDIA Agent Capabilities ICA 01` ← 根 `CN=NVIDIA Agent Capabilities CA`（自签，notAfter 9999 年）——任务背景写"IC 01"，DER 实测为 **ICA 01**。**DSSE 信封**：in-toto Statement，predicateType `https://model_signing/signature/v1.0`（Google model-signing 方案复用）；predicate.resources 逐文件列 **6 个 sha256**（BENCHMARK/SKILL/skill-card 三 md+evals 三件）。实测：六摘要与当前仓库文件重算**全部 MATCH**（签名对 HEAD 活验证）；`tlogEntries: []` 为空——无 Rekor 透明日志，保证完全依赖 NVIDIA 私有根。

## 外部连接

三处：**SkillEvaluator**（`skills/g-assist-mcp-skill/evals/EVAL.md:40-46`：`uv tool install "skillevaluator[all] @ git+.../SkillEvaluator.git"`，校验须带 `--external` profile）；**NVCARPS CI**（`.gitlab-ci.yml` 全文 9 行：仅 include `nvcarps/ci-group/nvcarps-ci` 上游模板 + 三变量 `TRIGGER_BRANCH=main`/`UPSTREAM_PROFILE=external`/`AUTO_SIGN=true`，零自有 job，AUTO_SIGN 正是签名生成通道）；**RISE MCP 服务器**（`SKILL.md:124-129` 明令不得枚举实现细节）。

## 数据流

数据集刻意劈两半（`skills/g-assist-mcp-skill/evals/EVAL.md:19-23`）。**evals.json——16 条（11 正 5 负），无硬件可跑**：CI runner 无任何 gassist 工具，"工具缺席"正是被测环境（`skills/g-assist-mcp-skill/evals/EVAL.md:24-29`："the absence of tools is the point"）。正例 001 期望：没工具就说没连上、绝不发明工具名、绝不编造状态；负例 5 条（法国首都/截图缩放/GitHub Actions/键盘背光/只调暗 Chrome 窗口）全部 `expected_skill: null`——考**不该激活时不激活**（近域诱饵）。源码勘误："捏造/谎称"类断言主要在正例组考察，负例组专测路由克制（任务背景归组有误）。**evals-hardware.json——31 条（hw-001..031），RTX 真机**：hw-002 要求 `enable "0"` 字符串（非布尔）且宿主收确认；hw-003 改分辨率**预期结局是回退**；hw-005 限 ≤3 次调用。红线（`skills/g-assist-mcp-skill/evals/EVAL.md:61-72`）：hw 用例真改设置、门控需 elicitation 宿主、绝不造 confirm 参数。

`BENCHMARK.md` 是 2026-09-30 SkillEvaluator 1.5.6 的 PASS 报告（L12-21）：双 agent（Claude Code `bedrock-claude-opus-4-8`、Codex `gpt-5.5`）×16 任务×3 尝试。结果（L36-43）：Correctness 69.5→97.5 / 60.0→100.0，Effectiveness 61.7→84.5 / 51.9→90.0，Security 双 100→100；token 总量带技能 2,382,459 vs 基线 3,111,525（L91）。三层证据门（L97-101）全过，总判 PASS（L3）。

## 设计决策

- **三变体 A/B**（`skills/g-assist-mcp-skill/evals/EVAL.md:6-11`）：同一能力做三份文档风格变体（rise-mcp-skill / g-assist-mcp-skill / rise-mcp-skill-3），任务集共享可直接对比——SKILL.md 写法本身是被实验对象。扩集军规（L92-96）：问题不得点名技能、按环境归档、用例同步进另两份。
- **负例重度加权**（`skills/g-assist-mcp-skill/evals/EVAL.md:80-84`）："failure modes are things an agent does *too readily*"——断言大量以 "did not..." 开头，快乐路径之外才是真风险。
- **签名复用 model-signing**：in-toto DSSE+逐文件 sha256，持 NVIDIA 根信任方可复核；空 tlog 是企业信任与 Sigstore 公共模型的折中。
- **CI 全托管**：227 字节 .gitlab-ci.yml 把 job 定义权全交上游模板，本仓零自有 job。
- **口径维护**：README 插件清单 corsair 死链（`README.md:250`，详见 04 篇）示清单会漂移；skills 线用签名哈希锁死六文件清单，是更强的口径锚。

## 新人提示

顺序：读 `SKILL.md:82-130`（Instructions 六条，灵魂）→对照 `BENCHMARK.md` 看指令如何变成可测断言→跑 CI 套件（`skills/g-assist-mcp-skill/evals/EVAL.md:39-46`，务必 `--external`）。可抄模式：工具缺席两分支话术、假成功防御（L243）、近域诱饵负例。两个坑：`create-eval-dataset` 别裸跑，`--force` 会覆盖 evals/（L88-90）；改 SKILL.md 后需重签名，否则六哈希失配（实测全 MATCH）。
