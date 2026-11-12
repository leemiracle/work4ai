# 08 · k8s_infra_monitor：K8s 体检 agent 的离线/在线双模

## 角色定位

`k8s_infra_monitor` 是 Kubernetes 集群体检 agent：编排四个诊断工具采集节点/_pod/事件/资源压力数据，产出结构化 markdown 事故报告并附 severity 分级。它在示例仓的独特卖点是**每个工具都带离线/在线双模式**——离线吃预录场景 JSON（无需集群、可进 CI），在线直连 kubectl（真集群），同一套代码两种宿命。包名 `nat_k8s_infra_monitor`，注册名 `k8s_infra_monitor`（`register.py:44`）。

## 内部结构

工作流配置 `K8sInfraMonitorWorkflowConfig`（`register.py:44`）继承 `OptimizableMixin`（暴露给 NAT 超参优化器），字段：`tool_names`（`register.py:56`）、`llm_name`、`offline_mode` 默认 true（`register.py:58`）、`offline_data_path` 默认指向包内数据文件（`register.py:59-62`，常量在 `register.py:41`）、`agent_prompt`（`register.py:63-66`）。

工作流函数（`register.py:69-149`）：`asyncio.gather` 并发取工具（`register.py:85`），`bind_tools(tools, parallel_tool_calls=True)`（`register.py:86`）允许一轮多工具调用；severity_classifier 单独取（`register.py:88`）不进 bind。图是标准 ReAct（`register.py:95-106`）：monitor_assistant 节点把 `K8S_INFRA_MONITOR_PROMPT`（`prompts.py:16`，五步指令：评估范围→采集→交叉关联→分级→出报告，并强调"必须用工具拿真实数据再下结论"）前插后调 LLM（`register.py:90-92`），ToolNode 承接工具调用，`tools_condition` 路由（`register.py:103`）。

四个诊断工具同构（以 `pod_health_tool.py` 为模板）：Config 带 `offline_mode`/`kubeconfig_path`/领域参数（`pod_health_tool.py:30-36`）；运行时先按 `offline_mode` 分支（`pod_health_tool.py:58-65`）——离线路径用 `_extract_scenario_id`（`pod_health_tool.py:70-76`，尝试把 query 解析成 JSON 取 `scenario_id`，失败落 "default"）查缓存（`pod_health_tool.py:60`），查不到返回全健康兜底文本（`pod_health_tool.py:63`）；在线路径 `_run_live`（`pod_health_tool.py:79`）拼 kubectl 子进程（`pod_health_tool.py:91-97`，`subprocess.run` 30 秒超时、失败把 stderr 收进分节），全命名空间模式加 `--field-selector=status.phase!=Running,status.phase!=Succeeded` 只留异常 pod（`pod_health_tool.py:116`）。其余三件：node_status（`node_status_tool.py:30`，节点 NotReady/条件检查）、event_collector（`event_collector_tool.py:30`，Warning 事件，`event_limit` 默认 50）、resource_pressure（`resource_pressure_tool.py:30`，CPU 阈值 80%/内存 85%，`resource_pressure_tool.py:35-39`）。severity_classifier（`severity_classifier.py:32`）是独立 LLM 工具：SEVERITY_CLASSIFIER_PROMPT（`prompts.py:39`）限定 critical/warning/informational 三类输出（`severity_classifier.py:57-63`）。

场景缓存基建在 `utils.py`：模块级 `_offline_data` dict（`utils.py:23`）、`preload_offline_data`（`utils.py:33`，启动时整文件读入）、`get_offline_tool_response`（`utils.py:63`，按 `(scenario_id, tool_name)` 取预录响应）。

## 外部连接

向上经 `@register_function`（`register.py:69`）进 NAT；每个工具与工作流主函数都挂 NAT profiler 插件的 `@track_function()` 装饰器（如 `register.py:108`、`pod_health_tool.py:43`、`severity_classifier.py:44`），函数调用自动上报遥测。向外：kubectl 二进制（在线模式唯一依赖，不加载任何 K8s Python 客户端）；config.yml 里三个 NIM LLM（monitor_agent_llm 用 `nemotron-3-nano-30b-a3b` + 16384 max_tokens 跑诊断，classifier_llm 2048 跑分级，nim_rag_eval_llm 专供 eval）。双配置对照：`config_offline_mode.yml`（全工具 offline + `eval:` 节接 ragas AnswerAccuracy/ResponseGroundedness，数据集 `data/eval_dataset.json`）与 `config_live_mode.yml`（offline_mode 全 false）。

## 数据流

离线模式：用户 query 携带 scenario_id → 各工具离线分支查 `utils.get_offline_tool_response`（`utils.py:63`）拿预录 kubectl 输出 → LLM 在 ReAct 循环里交叉关联（如 CrashLoopBackOff + 内存压力 → OOM 判断，提示词 `prompts.py:26`）→ 报告 → severity 分级追加。工作流启动时 `preload_offline_data` 预载并强校验（`register.py:140-143`，0 个场景直接 FileNotFoundError）。在线模式同构，只是工具内 `_run_live` 真跑 kubectl。收尾统一在 `_analyze_cluster`（`register.py:109`）：`agent_executor.ainvoke`（`register.py:115`）拿 `messages[-1].content`，空报告有专门的"模型能力不足，建议 meta/llama-3.3-70b-instruct"降级提示（`register.py:122-126`），最后 `severity_tool.arun(result)` 拼接返回（`register.py:129`）。

## 设计决策

1. **离线优先默认值**（`register.py:58` 全工具默认 offline）：示例的可运行性优先——没有集群也能完整体验 agent 推理链，同时 eval 节可以在 CI 里跑 ragas。
2. **缓存按 (scenario_id, tool_name) 二元索引**：同一场景下四个工具各取各的预录响应，LLM 看到的是协调一致的多源数据，能练"交叉关联"这一步真实功。
3. **severity 不进 ReAct 图**：分级是对最终报告的后处理，放进图里会污染工具循环（LLM 可能抢答分级），独立成 `severity_tool.arun` 一锤定音（`register.py:129`）。
4. **subprocess kubectl 而非 python k8s 客户端**：零额外重依赖，且预录的缓存响应本来就是 kubectl 文本格式，双模输出同构。
5. 值得批评的点：`_extract_scenario_id` 依赖 LLM 在 query 里原样携带 JSON（`pod_health_tool.py:70-76`），提示词没有强约束这一点，离线模式下 scenario_id 丢失会静默回落 default 场景，评测结果失真且无告警。

## 新人提示

跑离线模式务必先 `git lfs pull`——`data/offline_scenarios.json` 与 `data/eval_dataset.json` 都在 LFS 规则下，克隆后是 130 字节指针文本，`preload_offline_data` 会在 `json.load`（`utils.py:52-53`）抛 JSONDecodeError，报错离根因很远。在线模式只需本机 kubectl 可达。想加第五个诊断工具：复制 `pod_health_tool.py` 骨架（Config + `_run` 双模分支 + `_extract_scenario_id` + `_run_live`），在 `register.py:33-38` 的 import 块挂上自动注册，再把 config.yml 的 functions 与 workflow.tool_names 各加一行。空报告场景先怀疑模型：config 默认 nemotron-3-nano-30b-a3b，复杂交叉关联场景按 `register.py:124-126` 的提示换 70B。测试入口 `tests/test_k8s_infra_monitor.py`，不依赖集群。
