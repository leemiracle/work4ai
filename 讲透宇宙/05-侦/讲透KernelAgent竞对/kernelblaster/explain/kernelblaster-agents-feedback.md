# 深解 `src/kernelblaster/agents/feedback.py` — 性能反馈与 reward 信号的基座

> 层位：Agent 核心层（layer:agent-core，7 节点）。知识图谱定性：`complex`、模板方法 + 并发。
> 一句话：**这个文件本身不解析 NCU、不算 reward——它是"生成→验证→反馈回填"迭代循环的模板基类，把反馈的"传输协议"定死，把反馈的"内容生产"留给子类。**

## ① 角色定位

KernelBlaster（NVIDIA，MAIC-RL 框架）的全部优化 agent——单发版 `MinimalOptimizationAgent`（opt_ncu_minimal.py）与 RL 版 `RLNCUAgent`（opt_ncu_rl.py）——都继承这里的 `FeedbackAgent`。它解决的问题是：LLM 生成 CUDA 代码后，谁来判定好坏、坏消息如何送回模型、好的解如何挑选与断点保存。它是一个**反馈回路调度器**：驱动 `max_attempts` 轮 × `num_pgen` 条并行线程，每轮把子类产出的 `Feedback` 对象里的 `new_messages` 追加回对话历史，形成闭环。

## ② 内部结构（函数级）

- **`FeedbackConfig`**：配置 dataclass——agent 名、目录、模型、GPU 类型、并行数、`file_rules`（对生成代码的静态检查回调）等。
- **`Feedback`**：反馈容器 dataclass，字段即协议：`new_messages`（回填给 LLM 的消息）、`llm_calls`、`success`、`filename/contents`（产物）、`durations`（NamedTimer 自动计时）、`feedback`（文本）。RL 侧的 `RLNCUFeedback` 继承它，额外携带 `elapsed_cycles`、NCU 日志、标注源码、预测/实测改进——**容器扩展而非协议改动**，是刻意的设计。
- **`FeedbackAgent.get_feedback()`**：抽象钩子，子类必须实现。**NCU 指标→反馈文本/reward 的转换全部发生在子类**（见④）。
- **`__run()`**：单线程单轮——prompt 落盘（`attemptN_taskM_prompt.md`，含响应与 usage）→ `generate_code_retry` 生成 → 子类 `get_feedback` 验证 → 把本次 LLM 调用插到 `llm_calls[0]`、计时写入 `durations`。
- **`run()`**：主循环。每轮先 `trim_messages`（上下文裁剪，失败则丢弃该线程），`asyncio.gather` 并发跑活线程，回填消息，任一成功即 `choose_best_task`（默认取第一个，子类可按最低 cycles 选优）后 break；每轮全量重写 `metrics.jsonl`；结束写 `.finished` 哨兵。
- **`check_for_existing_run()`**：断点续跑三分支——有 `success_*.cu` 直接复用（多 attempt 冲突取最新）；只有 `.finished` 无成功文件则按 `retry_failed` 决定重跑或跳过；有残留无哨兵则清场重新生成。
- **`write_metrics()`**：把各线程各 attempt 的 Feedback 展平为 jsonl（含 attempt_id/thread_id、版本号 1.2）。
- **`raise_numerics_verification_error` / `raise_time_measurement_error`**：抛 `FeedbackError`——注意这是**双通道异常**（utils/error.py）：`feedback` 字符串会拼进给 LLM 的纠错 prompt，`logging_message` 进 run.log。写它时你是在"对模型说话"。

## ③ 外部连接

- **依赖**：`utils/query.py`（`generate_code_retry`/`trim_messages`/`process_messages`）、`utils/error.py`（FeedbackError）、`file_operations`（`write_code_to_file`/`write_jsonl`）、`timer.py`（NamedTimer）、`config`。
- **被继承**：`RLNCUAgent`、`MinimalOptimizationAgent`；`Feedback` 被 `RLNCUFeedback` 继承。经 `agents/__init__.py` barrel 导出供工作流节点使用。
- **下游协作**（子类侧）：`OptimizationDatabase`（知识库）、`ReplayBuffer`（轨迹）、`reprofile.py`（重剖析）。

## ④ 数据流：NCU 原始输出 → 结构化反馈 → prompt

1. **采集**：子类以 `ncu --section SpeedOfLight` 剖析二进制，拿 stdout 文本。
2. **解析为数字信号**：`parsing.get_elapsed_cycles_ncu_log` 用三级正则兜底（表格式 `Elapsed Cycles  cycle  12675` → CSV/冒号式 → 任意格式）从 "GPU Speed Of Light Throughput" 段提取 **Elapsed Cycles**；多 kernel 时 minimal 版**求和**作为 total_cycles。
3. **裁剪为文本反馈**：`_extract_speed_of_light_section` 只保留每个 kernel 的 SOL 段（含 kernel 名）——全量 NCU 报告太大，进 prompt 的是经济裁剪版。
4. **进入哪类 prompt**：(a) 错误路径——编译/数值验证失败时，`FeedbackError.feedback` 或 `new_messages=[{"role":"user","content": 错误日志+原代码}]` 回填对话，触发修复重试（有 MAX_FIX 预算）；(b) 优化路径——RL 版每步把 `当前代码+裁剪后 NCU+知识库` 打包成生成 prompt；(c) 降级路径——`KERNELAGENT_RL_NCU_CYCLES_ONLY` 模式下无完整报告时，用 `f"Elapsed Cycles: {cycles:,}"` 合成伪报告喂给状态分析 LLM。

## ⑤ 设计决策

- **为什么用 elapsed cycles 而非 wall time**：cycles 是设备端确定性计数，剔除 host 噪声与频率波动，跨运行可比；改进率定义 `(旧-新)/旧×100`。代价是牺牲了带宽/占用率等 SOL 指标进入 reward——它们只作为文本证据供 LLM 归因。
- **reward 塑形**（`calculate_reward`，opt_ncu_rl.py:1429）：`base = 实测改进%/100`（线性主项）+ **预测准确度奖**（`accuracy=实/预`，0.8–1.2 给 +0.2，否则 `−0.1×|acc−1|`）+ **变慢罚 −0.5**。三重意图：主项驱动真实加速；准确度项持续校准知识库的 `predicted_improvement`，防预测漂移（这是 RL 版独有的"元信号"）；罚项抑制无效探索。探索/利用由 relevance 加权随机选技术 + unused 优先实现，reward 结果经 `update_optimization_result` 回写数据库完成"策略更新"（无梯度）。早停阈值 −500% 极宽容，配合 `policy_update_cycle` 用 `reward<0 或 actual<pred×0.5` 收集失败步做差距分析。
- **循环骨架 vs 反馈内容分离**：并发、裁剪、落盘、断点等易错工程全部收在基类；子类只填 `get_feedback`——这正是 minimal/RL 两版能共享回滚与重试预算的原因。

## ⑥ 新人提示

1. **找 NCU/reward 逻辑别停在这个文件**——顺着 `get_feedback` 的两个子类实现往下读，解析在 `utils/parsing.py`，reward 在 `opt_ncu_rl.py::calculate_reward`。
2. `Feedback.new_messages` 的 role 固定为 `user`——反馈是以"用户纠错"口吻进对话的。
3. `metrics.jsonl` 每轮**全量重写**非追加；调试长跑先看 `.finished`/`success_*` 判断是否续跑。
4. 正则解析是三段兜底而非严谨 parser——NCU 版本升级输出格式变了会静默落到 fallback 模式，改 NCU 命令行参数时先回归这条链路。
5. 阅读顺序建议：本文件 → utils/error.py → utils/parsing.py → opt_ncu_minimal.py（简版闭环）→ opt_ncu_rl.py（reward+知识库闭环）。
