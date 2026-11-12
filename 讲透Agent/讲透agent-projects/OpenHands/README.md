# 讲透 OpenHands（OpenHands/OpenHands，92.2k star）

全链知识基座：DeepWiki 全量 + understand 图谱 + ONBOARDING + explain 12 篇。本仓是 A 层清库迄今最大图谱仓（638 文件）。

| 链路 | 终态 |
|---|---|
| deepwiki | 79 页全量（INDEX+coverage，2026-10-30 A 层补抓轮） |
| 图谱 | **1590n/4310e/16层/16步tour**，validator 0 issues 0 warnings，fingerprints 638 文件@4dfcd681 |
| onboarding | ONBOARDING.md 5800+ 字 8 节，54 锚终验全好（1 短锚消歧归位） |
| explain | 12 篇 144,193 字符，568 锚终验真坏=0（519 全路径直验+49 短锚 enterprise/openhands 消歧全归位），内容抽验 14 处全命中 |
| 图谱位置 | 仓内 `.understand-anything/knowledge-graph.json`（/usr-data/data2/repos/agent-repos/agent-projects/OpenHands） |

## 核心发现（写手×批阶段甄别精华）

- **Legacy-V0→V1 大重构代际是全仓主线**：V0=agenthub 工具/runtime/事件流旧线（头注 2026-04-01 移除）；V1=openhands/app_server/ Injector DI+integrations。`server/app.py` 双栈并存物证（v1_router+V1 lifespan 嫁接，`ENABLE_V1` 默认开）；判代靠会话 ID 形态（V1=UUID）+服务异常保守回落 V0。
- **安全/隐私线 10 处**：feedback.store_feedback 日志 elide 但 POST 完整 trajectory 到硬编码外部网关 / FileSecretsStore expose_secrets 明文 / InvariantAnalyzer 构造期自动拉 ghcr.io 容器 / MCP api_key 明文三头注入 / file_readers 按 SANDBOX_ENV_OPENAI_API_KEY 动态扩容沙箱直连 / 技能教 agent token 拼 git remote URL 落 .git/config / Dockerfile.j2 双空密码+pam_rootok+sudo NOPASSWD / compose docker.sock / VSCode 扩展 webview XSS 注入面+cdn.jsdelivr 公网加载。
- **模块边界**：linter/file_editor/repo_ops=openhands-aci 外移 re-export 门面本仓零实现；resolver 22 模板生产消费方全在被裁 enterprise/；Linear 模板逐字拷贝 Jira 连首句没改（md5 相同）。
- **scanner 盲区账（Python 仓）**：stdlib 同名假边两变体（io/types）+PEP420 无 `__init__` 包解析（`openhands/core/__init__.py` 物理不存在）+from-包-import-子模块加载链——全部已进派发模板条款。
- 文档笔误 3 处（OpenHnads/promot/description 复制残留）+AGENTS.md 引用已拆分 cli/utils.py 滞后。

## explain 索引

01 V0/V1 双栈并存 · 02 app_server Injector DI · 03 integrations mixin-composition · 04 EventStream 事件流核心 · 05 LLM 层 · 06 runtime/sandbox · 07 memory/condenser 家族 · 08 StuckDetector/controller · 09 resolver 六平台 pipeline · 10 security analyzers · 11 agenthub agents · 12 storage/config/migrations
