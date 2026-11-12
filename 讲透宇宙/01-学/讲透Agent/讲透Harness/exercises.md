# 讲透Harness · 练习题（exercises）

> 做题纪律与讲透Prompt 相同：先自己答，再跑实验对答案。所有题可在本单元 experiments/ 基座上改 10-30 行完成。标 ★ 的是值得写进你简历的题。

## Ch01-02（动机与解剖）

1. **FCR 手感**：把 E1 的任务池换成 3 个你自己写的函数（含一个故意的模糊 spec），跑 naive vs harness。FCR 还会出现吗？模糊 spec 时"测试说了算"还公平吗？
2. **组件认领**：打开 [deepseek-agent-harness/agent_host.py](../../deepseek-agent-harness/agent_host.py)，给 run() 的每个代码块标 E/T/C/S/L/V——找出"一个函数同时是两个组件"的位置（提示：maybe_compact）。

## Ch03（验证即证据）★

3. **V0 换强模型**：把 E2 的 v0_self 换成 glm-4-flash（改 common 调用），过度自信率会降吗？——你正在亲手测 harness dependence 的模型轴。
4. **盲测集防御**：给 E1 的 harness 加一个"模型可写实现、不可读测试文件"的 Scope 隔离（测试从 prompt 里抽走，改为只回传 pass/fail）。完成率掉多少？信息换 gaming 的汇率是多少？

## Ch04-05（状态与预算）

5. **账本格式消融**：E3 的 progress.md 是 Markdown 列表。改成 JSON / 表格 / 倒序排列，C 组的精确恢复率变化多少？——你在测"状态文本的格式也是超参"。
6. **自适应 cap**：E4 的 cap 是常数。写一个"连续失败 N 次且错误相同则提前熔断"的守卫，在矛盾任务上比 cap=2 再省几次调用？

## Ch06-07（生命周期与参数）

7. **WRAP UP 缺席实验**：把 E1 harness 的 feature_list 更新删掉（只留验证），跑 8 任务会话在中途 kill，用 E3 的协议恢复——L 和 S 组件哪个更不可或缺？
8. **参数错配**：把 FILE_MAX_LINES 从 2000 改成 20，模拟"上下文饥饿"，观察 agent 行为退化模式（放弃工具？重复读？）。

## Ch08-09（多模型与进化）★

9. **难分布 E6b**：设计 3 个 glm-4-flash 会挂的任务（如：精确 JSON 输出+边界 case/多步算术/长指令跟随），重跑 E6 观察救回侧：cascade 能否追平 all_glm5？成本单位落在哪？
10. **E7 扩轴**：给配置空间加第三维（max_new_tokens ∈ {128, 224}），重跑贪心——train 最优是否变了？held-out gap 方向？

## Ch10-12（前沿与批判）★

11. **私有回归集起步**：把 E1-E7 你跑挂过的所有 case 收集成 `regression.jsonl`（任务/配置/结果），这就是你的 harness 私有 benchmark v0（手册 11 章"任务失败史=私有 benchmark"的落地）。
12. **配置级报告**：为你手头任何一个 agent 项目写一份 HarnessCard：model×harness 矩阵一格的完整字段（模型/方言参数/验证层级/预算/账本格式/结果）——这是 Harness-Bench 主张的最小实践。

## 提交格式

每题：改动 diff + 结果 json/png + 3 句读数（发生了什么/为什么/边界在哪）。优秀答案的标志：**报告里写明哪些路径没被 exercise**（E6 的诚实标注是范本）。
