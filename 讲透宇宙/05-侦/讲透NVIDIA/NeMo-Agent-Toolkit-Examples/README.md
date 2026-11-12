# 讲透 NeMo-Agent-Toolkit-Examples

> NVIDIA NeMo Agent Toolkit 官方示例联邦：**sandbox_agent**（最大示例：宿主/沙箱双轨工具+Docker/Daytona 双后端+GAIA 评测线）+ profiler_agent（LangGraph+Phoenix）+ k8s_infra_monitor + MCP 接入光谱（mcp_rag_demo/unstructured）+ **x402/Spraay 加密支付线** + 纯配置示例群。

## 全链状态表

| 阶段 | 状态 | 产出 |
|---|---|---|
| understand 图谱 | ✅ 2026-11-11 | 仓内 `.understand-anything/knowledge-graph.json`：**378n/565e/14 层/14 步 tour**，双 validate 0/0，fingerprints 154@eadbb757 |
| onboarding | ✅ 2026-11-11 | `onboarding/ONBOARDING.md`（8 节 6495 字不计空格，80 锚） |
| explain 12 篇 | ✅ 2026-11-11 | `explain/01-12` 合计 **51177 字符**，565 锚（组 1 机器全验 BAD=NONE、组 2 368 锚对账 0 坏；主会话抽验 3/3 含语义闭环） |

## 战况（16 批，双段 worker）

前后 8 批两 worker 接力；imports scanner 3 条 1:1+源码重扫补 23 条跨批真实 import（含函数内延迟导入 AST 补）；batch-15 81 节点超限按规范拆 2 part；前批预告的 12 条 tested_by 全部合龙。merge 零悬空。

## 甄别精选（源码级实证）

1. **NAT 注册三件套范式**：`FunctionBaseConfig, name=`+`@register_function`+包 `__init__` import 副作用注册——01 篇主线；system_prompt:84 `[Attached file for this task: …]` 指令行与 enrich_gaia 拼接前缀**逐字闭环**
2. **沙箱隔离三层防线**：容器硬边界/工具软边界/提示词约定；file_ops 组件感知路径白名单（`/workspace2` 不误匹配）；白名单≠安全边界勘误
3. **宿主/沙箱双域按信任边界切分**（API key 不进沙箱）；web_fetch 的 prompt-in-tool-description（四个 JSON API 模板 URL 内嵌 description）；Docker 双层超时防孤儿（Linux timeout 包裹+wait_for+5s）；Daytona stderr 恒空的语义不对等
4. **ReAct 双刹车**：max_iterations 优雅收尾 / recursion_limit×2+10 兜底；答案清洗器三重回退护栏（fail-open）
5. **任务书前提被写手实证纠正**："spraay 双 mock 服务器"不成立——mock_x402_server.py 属 x402、mock_registry_server.py 属 agent_identity，spraay 侧以 dry-run 模式替代 mock
6. **LFS 指针家族**：sample_queries.json 之外连带发现 k8s 的 offline_scenarios.json/eval_dataset.json 同为指针（json.load 报错离根因远）
7. currency_agent_a2a `packages=[]` 纯配置型示例（无 src/）；common.sh:18 "AIQ toolkit" 上游拷贝残留+引用不存在的目录
8. Daytona 无集成测试层=回归盲区；`MagicMock(spec=BaseSandbox)` 契约测试范式

## 分层速览（14 层，157 文件节点）

入口与规范(10) → GitHub 模板(7) → CI(16) → sandbox 容器化(13) → 沙箱后端(5) → 沙箱工具(14) → 注册提示词(4) → sandbox 测试(12) → profiler(16) → k8s(16) → mcp_rag_demo(7) → unstructured(8) → x402/Spraay(13) → 身份与纯配置群(16)

*2026-11-11 · cuda-stack-第七轮会话（舰队夜战 · NeMo-Toolkit 三连之三）*
