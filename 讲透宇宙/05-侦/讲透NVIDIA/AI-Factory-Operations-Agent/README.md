# 讲透 NVIDIA/AI-Factory-Operations-Agent

> NVIDIA AI Factory Operations Agent（AFOA，实验性 release）：部署专用 AI agents 调查集群问题、治理 AI 工厂运维——OpenClaw workspace 人格 + TS 扩展插件族（访问治理/集群远程执行/观测平台桥）+ Helm chart 全家桶（CRD 3999 行/openclaw.yaml 779 行/vLLM 推理子 chart）+ MCP 服务器族。
> 本目录=understand 全链知识库产物（2026-11-06，kylin-fusion-search 会话，NV 舰队 v3.1 全量队列第 11 行仓）。

## 全链状态表

| 阶段 | 状态 | 关键数据 |
|---|---|---|
| prepare | ✅ | 178 文件/20 批 |
| 批分析 | ✅ 20/20 | 312n/376e；scanner 两类盲区手补（kubernetes .ts 被标 infra 致 4 条相对导入漏+动态 import() 全盲 4 条） |
| merge | ✅ | 312n/376e 零节点丢失（tested_by linker 1 条 orphan 边正常语义 drop） |
| layers/tour | ✅ | 16 层 181/181 全覆盖；16 步导览（_helpers.tpl 的 file: 前缀特例首轮断言拦截后修正） |
| finalize | ✅ | 双 validator 0/0；fingerprints 178 文件@47fdcc76 |
| ONBOARDING | ✅ | 7862 不计空格字符/8 节/33 锚（主会话抽验 3/3 含路径段归位） |
| explain | ✅ 12 篇 | 组1 治理与插件 6 篇（42,962 字/278 锚）+组2 部署 MCP 测试 6 篇（39,647 字/142 锚）；worker 自验 117 锚零失败+主会话抽验 5/5 |

图谱：仓内 `.understand-anything/knowledge-graph.json`（312n/376e/16 层/16 步）。

## 勘误清单（源码级实证）

1. **精确计数钉版**（任务书/图谱约数→源码精确值）：diagnostic-policy=36 个程序白名单（exact/flags/pairs 三形态）；remote-ssh=19 个 ssh -o 加固参数（+-F /dev/null 共 20 连接参数）；automation-context=17 导出函数（231 行）；SKILL.md 全仓 8 份（seed 7+headless 1；「技能库 10 节点」=7 SKILL+3 gpu-networking references）；FORBIDDEN_FLAGS=16 长旗+短旗 -s；chart-render.test.mjs=80 个 test 块。
2. **mutation-ledger 指纹语义勘误**：指纹**包含**完整 args（mutation-ledger.ts:80-84）——准确表述是「敏感原文不直接入账」：kubectl stdin 只存 sha256 摘要（kubernetes/index.ts:84）。
3. **grafana 播种链断头**：grafana.SKILL.md+grafana/index.ts 进 seed ConfigMap（:97-100,155-162）但 init-config 只 rm 不装（openclaw.yaml:121-141）、nemoclaw.json skills 白名单也不含 grafana——在产 Grafana 工具实际在 observability 插件内嵌 grafana.ts（openclaw.yaml:238）。
4. **iraop 传输协议勘误**（图谱 summary vs 源码）：实为 **MCP-over-SSE**（DEFAULT_SSE_URL 以 /mcp/sse 结尾，iraop/index.ts:8）非「streamable HTTP」；callMcpTool 107-282 恰 176 行自实现 MCP 客户端。
5. **validation.yaml 无 required**：全部 fail 函数形态；required 形态 fail-fast 在 seed ConfigMap:12 与 afoa ingress:19-20。
6. **vLLM profiles 权重精度**：FP8 只修饰 KV cache dtype（vllm-ultra-4gpu.yaml:26）；两 profile **权重均为 NVFP4**；Ultra 保留 mamba 两条配置（:34-35），仅缺 stochastic-rounding/philox。
7. **bcm-mcp-ssh-server 结构改判**：2 类+3 个 @mcp.tool（execute_cmsh/条件注册 execute_cmsh_admin/slurm_job_evidence）+3 条 custom_route（任务书「2 类 4 函数」不准）。
8. **test_bcm_docs.py 三重死法**：被测 files/docs/download_bcm_docs.py 工作树不存在**且 git 历史从未入库**+unittest FileNotFoundError+CI glob 只收 *.test.mjs（ci.yml:57）根本不执行；对照组 test_bcm_server.py 靠 sys.modules 假件树 5 测全绿——同一目录两种命运。
9. **nemoclaw.json=Helm 模板化 JSON**（:1-33 纯指令，tpl 渲染后改名 openclaw.json 落盘 openclaw.yaml:213）——scanner JSON 解析失败警告属预期勿当坏文件。
10. **AGENTS.md 实为 Helm 模板**（{{- if .Values.modules.edit.enabled }} 条件块+Files.Get 内联 SKILL.md+required 渲染期 fail-fast）。
11. **security_model 三模式矩阵**（Edit 变更须 HITL/Auto 免审批先警告，security_model.md:11-15 ↔ automation-guard/index.ts:62-102 逐格对应）；multitenancy tenant-reader RBAC 仅 get/list/watch。
12. **合规面**：LICENSE-3rd-party 含 AGPL(Grafana)/GPL-2.0(BusyBox) 强传染条目与主仓 Apache-2.0 并存——分发合规关键；spdx.test.mjs 强制源码 SPDX 头+helm 外 Markdown 禁 BCM 缩写；CI 第三方 action 全 SHA 钉版；iraop-stack CI 依赖用 stub Chart.yaml 替身。
13. **Helm 模板 YAML 解析面**：yaml-parser 全部回落 regex（{{ }} 语法），语义靠手写 summary——图谱消费方须知。

## 生成口径

- 16 层层序：项目概览治理 → 社区协作 CI → 文档站 → OpenClaw 人格种子 → 运维技能库 → 插件·访问治理策略 → 插件·集群远程执行 → 插件·观测平台集成 → MCP 服务器边界 → chart 骨架 CRD/Profiles → 部署模板·agent 与推理负载 → 部署模板·Mosaic 安全基线 → afoa-inference 子 chart → 单元契约测试 → Kind E2E → 演示资产。
- 字数口径：不计空格字符；explain 12 篇系列口径 5.9-7.8K（行号锚密度所致）。
