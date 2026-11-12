# 讲透 deer-flow

> bytedance/deer-flow @76803b8（85k star A 层，agent-projects 集群）· 全链 2026-11-01 20:15→22:5x 单夜完成（B 实例，CopilotKit 轮钉版模板复用）

| 链路 | 状态 | 产物 |
|---|---|---|
| deepwiki | ✅ 2026-10-30 补抓轮 | `deepwiki/`（INDEX+全页+coverage） |
| understand 图谱 | ✅ 2026-11-01 | 仓内 `.understand-anything/knowledge-graph.json`：**653 节点/1376 边/16 层/16 步 tour**，validator 0 issues 0 warnings，fingerprints 258 文件@76803b8 |
| onboard | ✅ | `onboarding/ONBOARDING.md`：8626 字（不计空格）8 节 77 锚 |
| explain | ✅ | `explain/` 12 篇：54940 字符/375 锚（组 A 核心链路 01-06 + 组 B 外围生态 07-12） |
| 锚终验 | ✅ | 主会话独立抽验 **14/14 全中 0 坏**（全产品 459 锚池随机） |

## 裁剪口径
/frontend/（304 文件 Next.js UI，OpenHands 轮先例——fingerprint 增量通道留后）+ /docs/ + tests 资产 + .env*（**仓根 .env.zhipu untracked 用户实验残留，零泄漏**）→ 258 文件/25 批。

## 架构一句话
双进程（FastAPI gateway `backend/app/` + LangGraph Server harness `backend/packages/harness/deerflow/`）；harness 核心=**langchain create_agent + 11 环 AgentMiddleware 栈 + subagents**（非旧版 LangGraph planner/researcher/reporter 流水线——README 残留旧叙事）。

## 勘误精选（源码级实证，详见 NOTES-DIGEST 195 条）
1. **文档三方代差**：中间件计数 README 9 vs CLAUDE.md 10 vs 磁盘 11；README/CONTRIBUTING 仍写 backend/src/ 旧布局——**CLAUDE.md 是唯一当代准确文档**
2. ARCHITECTURE.md 路径漂移五处（mcp/manager.py→client.py+tools.py+cache.py 等）
3. **generate_spreadsheet 死规格**：SKILL.md 称 26 图但 CHART_TYPE_MAP 仅 25 键，调用必败（文档超前实现）
4. run_eval.py 假关联：实为"触发评估"（claude -p 流事件检测），与 evals.json 无关
5. sandbox release 空操作：docstring 称不释放，实际 release 是 no-op（语义效果非字面行为）
6. 评测三件套：analyzer 双角色防火墙/grader 反幻觉闸门（text/passed/evidence 硬契约）/comparator→analyzer 揭盲链+blinded_history 防窥测试集
7. channels 安全闸门：/mnt/user-data/outputs/ 前缀白名单+resolve 二次校验防 IM 外泄
8. image_url=thumbnail_url 同取 DuckDuckGo thumbnail 字段（image_search/tools.py:122）
9. skills "13 技能"口径实为 **17 个**（磁盘实证）
10. client.py 907 行巨石：DeerFlowClient 842 行 26 方法；SubagentExecutor 300 行
11. tool-error 检测脚本消费私有 API `_build_middlewares`（下划线私有被跨层消费）
12. compose-dev 注释笔误（默认 nginx.conf 非 nginx.local.conf）+ provisioner 供应链弱项（裸 pip vs 主镜像 uv 锁定）

## 本轮新钉版
- Python scanner 跨层导入系统性漏报（batchImportData 8/14 空数组）——**空数组文件必须 AST 全量重扫**成为硬条款
- shell 批运行时语义边范式（脚本互调/heredoc 真实 import，b18 24 条先例）；tested_by 方向 source 必须本批
- 1302 死于自检段的产物盘上验收采纳（b8）+ cwd 相对路径校验框架误判教训
- Dockerfile/Makefile steps/targets 不建节点（step 不在 11 种合法类型，语义并入 summary）
