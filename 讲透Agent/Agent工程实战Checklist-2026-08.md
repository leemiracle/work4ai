# Agent 工程实战 Checklist（2026-08 版）

> 来源：《AI-Agent全方位经验总结-2026-08》§3/§8 + MAST 精读（NeurIPS 2025）+ Harbor 精读提炼。
> 用法：构建/评审任何 Agent 系统时逐项过；每项都有出处，可追溯。

## 一、上下文工程四操作（write / select / compress / isolate）

每次往上下文里加东西之前，先问它属于哪个操作、有没有更便宜的替代：

### Write（写到窗外）
- [ ] 长任务有 scratchpad/NOTES.md/todo 机制吗？（Anthropic：token 使用解释 BrowseComp 80% 方差）
- [ ] 需要跨会话存活的状态写到了外置存储，而不是堆在对话历史里？
- [ ] 常驻上下文定期校验时效——stale scratchpad 是污染源（timestamp + 主动失效）

### Select（按需拉入）
- [ ] 工具 schema 全量前置了吗？>12 个工具先做 tool search（Lovable：-10% token 且性能反升）
- [ ] 检索走"轻量标识 + just-in-time 加载"而非预取全量（Claude Code 模式）
- [ ] 检索结果有噪声过滤吗？（8/10 chunk 无关时，模型会基于噪声幻觉）

### Compress（压到最小）
- [ ] 长任务有 compaction 触发线吗（如 95% 窗口）？compaction prompt 先保 recall 再修剪 precision
- [ ] 大工具输出（>5k token）截断或落盘只传路径？programmatic tool calling 让模型写代码解析
- [ ] prompt caching 开了吗（90% 输入折扣 + 10x 限流吞吐——ROI 最高的一项）

### Isolate（隔离开来）
- [ ] 深挖型子任务交给干净窗口的 sub-agent，只回收 1-2k token 摘要？
- [ ] sub-agent 全量输出不回流父上下文（cascading sub-agent 防护）？
- [ ] 规划上下文与执行上下文分离（planner 不看每个工具结果——防 context thrashing）

**红线记忆**：context rot 是量化的（46→19 工具恢复准确率；多轮信息冲突 -39%）——**加上下文之前默认它是负资产**。

## 二、多智能体三条件门（默认"不"）

拆分前必须三条全中，任何一条不满足就回到单 agent：
- [ ] ① 任务可分解为**真正独立**、可并行的子任务？
- [ ] ② 质量收益 + 墙钟收益 > 成本（朴素多智能体 ≈15x token；hub-and-spoke 4-6x；错误率 ~17x 累积）？
- [ ] ③ 超出单 agent 容量（上下文超窗 或 工具多样性超配置）？

**一句话说不清第二个 agent 为什么存在，就不要加。**

### 拆了之后（纪律清单，缺一即溃）
- [ ] **契约先行**：每个交接点的输入/输出 schema/失败模式先于 agent 写出（MAST FC1 = 44% 失败）
- [ ] **终止显式**：谁有权终结任务是显式判据（FM-1.5 不知何时停 12.4%，几乎只出现在失败 run）
- [ ] **信息强制传递**：关键参数/格式不靠 agent 自觉（FM-2.4 扣留信息仅 0.85% 但致命）
- [ ] **验证多层**：编译级→运行级→端到端级（FM-3.2/3.3 表面验证 = 带病运转）
- [ ] **编排/执行分离**；spoke 互不通信，全部过 hub
- [ ] **失败剖面监控**：trace 落盘 + 定期 `agentdash` 式分析；改动前后做失败模式 diff 而非只看总分

## 三、评测协议五条（Harbor 加固版）

- [ ] **Oracle 先行**：判卷脚本先喂标准答案验证 100% 通过——没验证过的判卷器产出的所有分数不可信
- [ ] **n≥3-5 重复**：报均值±std；单次跑分在 agent 非确定性下无意义
- [ ] **二值 reward**：过/不过；部分分是 judge 噪声放大器
- [ ] **timeout 锁死并披露**：预定 1.2× 最快配置，全程一致——速度是成绩的一部分
- [ ] **harness card**：脚本版本/prompt 全文/temperature/retry/judge 模型与 seed/判分脚本 hash——同模型换 harness 可差 12-24pp，不披露 harness 的分数不可归因

## 四、快速止损信号（看到就停）

| 信号 | 病灶 | 动作 |
|---|---|---|
| agent 反复输出相同 Thought/动作 | FM-1.3 组织性空转（15.7%）| 查 context 管理与状态机，不是改 prompt |
| 模型回答"编造的数字/事实" | 消融出的 fabricate 倾向（实验 1-1：无工具结果时 4.7 两臂编数）| 检查工具结果是否真进了上下文；加 groundedness 校验 |
| 任务"聊到没话说"才结束 | FM-1.5 终止条件缺失 | 显式终止判据写进系统设计 |
| 换了更强模型没变好 | 协调/规格问题而非模型问题（MAST：模型质量不在失败头部）| 停止换模型，做失败归因 |
| 训练/部署行为不一致 | train-deploy gap（harness 侧 compaction/记忆注入改变分布）| Lego-RL 教训：在部署 harness 里训练/评测 |

---

*出处索引：§一 Anthropic context engineering 2025-09 + LangChain 四动词 + pkhamdee 失败模式；§二 MAST arXiv:2503.13657 v3 + Augment Code + spillwave 成本论；§三 Harbor 精读（paper-deepreads/05）；§四 MAST + ai-agent-book 实验 1-1 实测（glm 系列，2026-08-27）。*
