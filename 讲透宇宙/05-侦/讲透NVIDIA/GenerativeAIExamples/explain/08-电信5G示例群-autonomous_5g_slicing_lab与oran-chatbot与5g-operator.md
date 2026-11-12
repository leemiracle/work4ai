# 08 · 电信 5G 示例群：autonomous_5g_slicing_lab、oran-chatbot-multimodal、5g-network-operator-agent

## 角色定位

图谱 layer-9「电信 5G 示例群」（100 节点）三个示例正好是电信行业 LLM 落地的三个成熟度阶梯：`autonomous_5g_slicing_lab`（57 节点）是**真网闭环**——在 OAI 5G 仿真网络上跑 LangGraph agent 自动调切片带宽；`oran-chatbot-multimodal`（37 节点）是**知识问答**——对 O-RAN 技术规范做多模态 RAG 聊天机器人；`5g-network-operator-agent`（6 节点，2026 年新增）是**教育沙盘**——纯标准库的合成单小区环境，演示 observe-act-validate-score 的 agent 循环。三者共同点：都把"网络运维"这个时序决策问题映射到 agent 工具调用范式。

## 内部结构

**autonomous_5g_slicing_lab** 双目录：`llm-slicing-5g-lab/` 是实验室本体（`DLI_Lab_Setup.ipynb` 九步搭网：编译 FlexRIC/gNodeB、双切片 core（`docker-compose-oai-cn-slice1/2.yaml` 各含独立 SMF+UPF）、起两个 UE、iPerf3 打 30/120Mbps 交替流量并写 Kinetica 库；`change_rc_slice.sh`+`xapp_rc_slice_dynamic.c` 是 FlexRIC xApp 改配工具）。`agentic-llm/` 是 agent 大脑，四个文件共 784 行：`agents.py`（220 行，两个 LangGraph 节点）、`tools.py`（111 行，两个工具）、`langgraph_agent.py`（130 行，建图）、`chatbot_DLI.py`（316 行，UI）。

**oran-chatbot-multimodal** 是 Streamlit 多页应用：主程序 `Multimodal_Assistant.py`（632 行）+ `pages/`（知识库、评测页）+ `retriever/`（FAISS 本地向量库）+ `vectorstore/`（自定义 PDF/PPT 解析器，PPT 靠 LibreOffice 转换）+ `guardrails/fact_check.py`（二次 LLM 事实核查）+ `evals/`（5 个 notebook 的完整评测流水线）。

**5g-network-operator-agent** 极简两件：notebook + `network_environment.py`（500 行，零第三方依赖），外加 tests 目录。

## 外部连接

slicing_lab 连真基础设施：Kinetica GPU 数据库（`KINETICA_HOST/USERNAME/PASSWORD` 环境变量，`tools.py:40` 附近）、FlexRIC xApp 脚本（`config.yaml:reconfig_script_path`）、LLM 默认 `meta/llama-3.1-70b-instruct`（`config.yaml`）。oran-chatbot 走 build.nvidia.com 端点或本地 NIM，embedding 双轨（NREM 微服务或 API Catalog，`retriever/retriever.py:58-66` 分支）。operator-agent 本地零凭证，可选接 `https://integrate.api.nvidia.com/v1`（默认模型 `nvidia/nemotron-3-super-120b-a12b`）。

## 数据流

**slicing_lab 的自动调优环**（`langgraph_agent.py:68-85` 建图）：`__start__` → Monitoring Agent → Configuration Agent → 条件边（`state['consent']=='yes'` 则回 Monitoring，否则 END）。MonitoringAgent（`agents.py:56`）用文件指针增量读 `gNodeB.log`（state['start'] 记录偏移，1000 字符一块），把每块塞给 LLM 做 yes/no 二分类——"有没有 SDU buffer full 错误"，few-shot 里直接贴了真实 RLC/MAC 日志样例。命中错误后 ConfigurationAgent（`agents.py:114`）两步走：先调 `get_packetloss_logs`（`tools.py:90`，从 Kinetica 查最近 20 条丢包记录判断哪个 UE 更惨），再调 `reconfigure_network`（`tools.py:50`，subprocess 跑改配脚本）。人工闸门：`config.yaml:interrupt_after: 30`，循环 30 次后 `input()` 询问是否继续（`agents.py:161-162`），recursion_limit 设到 1500（`langgraph_agent.py:111`）容忍长跑。

**oran-chatbot 的四档 RAG**（`Multimodal_Assistant.py:49-55`，`--rag_type` 参数）：0 基础 NeMo RAG / 1 查询分解+增强+rerank（默认）/ 2 HyDE / 3 MultiQuery Retriever+rerank。检索用 FAISS 本地库 + 相似度阈值 0.3、k=10（`retriever/retriever.py:69-72`）；rerank 双轨——本地 CrossEncoder 或 `NVIDIARerank` NIM（`Multimodal_Assistant.py:434/451`）。生成后 `fact_check`（`guardrails/fact_check.py:28`）把 context/question/response 再喂一次 LLM，要求逐条核对并输出 `**:green[TRUE]**`/`**:red[FALSE]**` 开头的结论——Streamlit 富文本标记直接嵌进 prompt。

**operator-agent 的评分环**（`network_environment.py`）：`NetworkEnvironment.step`（L238）接收一个工具调用 → `_apply_action`（L269）校验动作边界（`tool_schemas()` L164 定义四个有界动作）→ 非法动作记 rejected 且 `_score`（L451）扣 0.25 分（`"rejected_action": -0.25`，L459）→ 返回 `Transition`（L124）。notebook 把 noop 与脚本化缓解策略作基线对比，hosted NIM adapter "requests one tool call and records malformed output or request errors as rejected actions; it never silently substitutes noop"（README 明文）。

## 设计决策

1. **日志 yes/no 门控而不是全文理解**：MonitoringAgent 每块只问"有没有 buffer full"，把开放问题压成闭集分类，省 token 且误报可控——这是把 LLM 当"带语义的 grep"的典型用法。
2. **reconfigure_network 的"防呆双跳"**（`tools.py:60-66`）：先 `["20","20"]` 重置再设目标值（UE1 → `["80","20"]`），从任意旧状态收敛；代价是参数 `value_1_old/value_2_old` 传进来却没用（函数体硬编码 20/80），`config_value_1/2`（`tools.py:58-59`）赋值后成为死变量——签名与实现脱节。
3. **UE 命名漂移**：README 说 UE1/UE3，`agents.py:127` 提示词说 "UE1 or UE3"，到 L138 又写 "UE1 or UE2"——多处提示词手工维护不同步的活标本。
4. **operator-agent 的"诚实免责"**：README 反复强调这是教育示例、固定合成结果"not evidence of model quality"，rejected 不静默替换 noop——与 slicing_lab 的真网实验形成"严谨度对照组"。
5. **oran-chatbot 的 config.yaml 提交风险**：`fact_check.py:23` 与 `retriever.py:34` 都直接 `yaml.safe_load(open("config.yaml"))['nvidia_api_key']`——API key 明文进配置文件且随仓库走（README 提醒勿提交，但代码路径本身鼓励了这种放法）。
6. slicing_lab 的 `agents.py:40` 读 `config_file['API_KEY']`，而 `config.yaml` 七个键里根本没有 API_KEY——照仓库现状直接 KeyError，需用户手工补键；这是"示例代码默认用户会改配置"的隐含契约。

## 新人提示

- 三个示例按"由虚到实"读：先 operator-agent（500 行无依赖，一天读懂 agent 评测沙盘范式），再 oran-chatbot（看四种 RAG 变体怎么切换），最后 slicing_lab（要 12 核+32G+AVX-512 的物理机才跑得动，读代码学架构即可）。
- slicing_lab 的精华在 `agents.py` 一个文件里的两段提示词工程：日志分类 few-shot（L66-83）与两步工具调度（L118-141）；文件末尾 L180 起还留了一段"练习：把两次 invoke 合成单 prompt"的注释版实现，是天然的教材作业。
- oran-chatbot 的 `evals/` 五个 notebook（合成数据生成→RAG 输出回填→RAGAS 评测→类人评测→复杂查询进阶 RAG）本身就是一条完整的 RAG 评测教程，值得单独精读。
- 甄别备注：任务书称"电信 5G/流式示例群"，经图谱核实 layer-9 全部三个示例均无"流式"特性（流式在 layer-8 fm-asr），本篇按图谱实际内容组织为"真网闭环/知识问答/合成沙盘"三阶梯叙事。行号锚（agents.py:40/56/114/127/138/161、tools.py:50/58/90、langgraph_agent.py:68/111、retriever.py:34/69、Multimodal_Assistant.py:49/434/451、fact_check.py:23、network_environment.py:164/238/269/451/459）均对照源码核实。
