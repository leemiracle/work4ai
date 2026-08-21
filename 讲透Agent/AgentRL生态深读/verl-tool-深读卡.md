# verl-tool 深读卡 —— 工具调用 RL 扩展（TMLR 2026）

> **定位**：verl 的工具 agent 训练扩展（vendored verl v0.6.0）。核心卖点：**Tool-as-Environment 范式** + 核心 agent loop **<200 行**。
> **本地**：`~/ai/verl-tool`（24M，872 文件）｜**深读**：deepwiki 50+ 子页（2026-03-07 索引，含行号级引用）

## 一、三大架构原则（deepwiki 1.3/2.x 蒸馏）

1. **Tool-as-Environment**：工具交互修改持久环境状态（IPython kernel 跨轮保变量）；按 `trajectory_id` 缓存环境状态——**不是无状态函数调用**
2. **训练-环境完全解耦**：全部工具交互走 HTTP POST `/get_observation`；**一致哈希** `crc32(trajectory_id) % num_workers` 保证同轨迹同后端（有状态路由）；无轨迹则 round-robin；工具可任意语言实现
3. **混合训练**：`use_tool` 字段逐样本控制——同一管线训"要工具"和"不要工具"的混合数据集

## 二、组件替换机制（_mapping 字典，ray_trainer.py:24-37）

不动 verl 核心、替换 4 个组件实现工具化：
| 原组件 | 替换 | 增益 |
|---|---|---|
| VLLMHttpServer | VerlToolvLLMHttpServer | trajectory_id 粘性会话 |
| compute_reward | +RewardManagerWorker 集成 | 任务级奖励管理器 |
| compute_data_metrics | +tool_call_rate 等工具指标 | 可观测 |
| compute_advantage | GRPO 组内归一（n>1）| 组采样 |

**AgentLoop（verltool_agent_loop.py，<200 行）**：`running_prompt_ids` 跨轮累积 token；`response_mask`（mask_observations=True 时观察不计 KL/梯度）；`available_length = max_response_length - len(running)` 防溢出；`max_obs_length=512` 截断。

## 三、训练配方五域 + 安全五层

| 域 | 工具 | 奖励管理器 |
|---|---|---|
| 数学 | PythonCodeTool | ToRL（sympy 验证）|
| 代码 | IPythonTool | AceCoder（测试执行）|
| SQL | SqlTool | SQLCoder（执行比对）|
| 深搜 | GoogleSearchTool | DeepSearch |
| 视觉 | PixelReasonerTool | PixelReasoner |

安全层：Firejail 沙箱/资源限额/FORBIDDEN_IMPORTS/Ray actor 隔离/SQL 只读事务（BEGIN+ROLLBACK）。异步 rollout 模式 **1.69-2.06× 加速**（轨迹独立推进，消除批屏障）。

## 四、与本项目知识的对位（对照密集区）

| verl-tool | 本项目 | 互证 |
|---|---|---|
| Tool-as-Environment 状态持久 | rl_agent 四层记忆 | 讲透Agent/04 记忆的工业版 |
| 一致哈希粘性路由 | ——（串行）| —— |
| Firejail/FORBIDDEN_IMPORTS | _code_ok 安全闸 | 同一思想两级实现 ✅ |
| mask_observations（观察不训梯度）| —— | GRPO 多轮的关键细节（讲透RL/03 可补）|
| tool_call_rate 可观测 | skill meta usage/success | harness"验证即证据"互证 ✅ |
| <200 行 agent loop | rl_agent 849 行 | 混合引擎的工程纯度标杆 |

## 五、关键入口（本地验证）

```
verl_tool/trainer/main_ppo.py            # Hydra 入口（TaskRunner @ray.remote）
verl_tool/trainer/ppo/ray_trainer.py     # AgentRayPPOTrainer + _mapping
verl_tool/agent_loop/verltool_agent_loop.py  # <200 行核心循环
verl_tool/servers/serve.py:213,291       # 路由器 + CRC32 一致哈希
verl_tool/servers/tool_server.py:200     # RayToolManager（Ray actor 池）
verl_tool/servers/tools/base_tool.py:15  # @register_tool 自动发现
```

## 六、与"我们"的关系（一句话）

**rl_agent 的"工业成熟形态"最近参照**——我们的工具注册表/安全闸/进化环在 verl-tool 里分别对应 @register_tool/Firejail 沙箱/RewardManagerWorker；差距清晰可列（异步 rollout/分布式/状态路由），且其 <200 行 agent loop 是"最小完整实现"的纯度标杆。

---
生成：2026-08-17 · deepwiki 索引 2026-03-07（b26cd3b）+ 本地 24M 克隆验证
