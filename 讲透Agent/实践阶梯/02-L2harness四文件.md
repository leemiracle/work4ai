# 02 · L2 Harness 四文件：给开发会话上保险

> L2 回答设计问题之二：**"agent 干活不可靠"到底是模型问题还是环境问题？**
> learn-harness-engineering 的立场：多数是环境问题。证据方法：同模型，有无 harness 对照。

## 一、四文件是什么、给谁用

四文件（AGENTS.md / feature_list.json / progress.md / init 脚本）**不是给运行时的端侧 agent 用的**，是给**开发这个 agent 的 AI 编码会话**（opencode 等）用的。它的作用对象是"开发过程"这个元任务。

本单元落盘：[agent-harness/](./agent-harness/)

| 文件 | 作用 | 本项目内容 |
|---|---|---|
| [AGENTS.md](./agent-harness/AGENTS.md) | 指令/宪法：环境、硬约束、代码约定 | 开发-运行分离工作流；5 条硬约束（贪心/预算/固定任务集/对照数字）；校验器单一来源 |
| [feature_list.json](./agent-harness/feature_list.json) | 任务账本：一个会话只做一个 feature | F1-F7 对应 L1-L5+批判章，各带 evidence 字段 |
| [progress.md](./agent-harness/progress.md) | 进度+证据+堵点，WRAP UP 时更新 | 已记第零号证据数字、L1 运行中状态、未验证项 |
| init（本项目并入 AGENTS.md 的"环境"节） | 冷启动自检 | 容器路径/部署命令/轮询方式 |

## 二、会话生命周期（本项目的实操版）

```
START   读 AGENTS.md → 读 progress.md → 读 feature_list.json → cat 最新 log
SELECT  只挑一个 in_progress 的 feature
EXECUTE 写/改代码 → 容器跑 → 回收日志存档
WRAP UP 更新 progress.md（含实测数字）→ feature 状态推进 → 失败也记录
```

对照 learn-harness 原版（START 读 AGENTS.md→跑 init.sh→读 progress.md→…），本项目把 init.sh 省了——因为"部署到容器"是三条固定命令，直接写进 AGENTS.md 比维护脚本更不易漂移。**harness 不是仪式越多越好，是每个仪式都要对得上项目的真实失败模式**。

## 三、四文件防的是什么病（本项目实例）

| 病 | 没有四文件时 | 四文件怎么防 |
|---|---|---|
| 冷启动失忆 | 新会话不知道容器路径/部署命令，重新踩一遍坑 | AGENTS.md 环境节即查即用 |
| 范围漂移 | 会话中途顺手"优化"了不该动的校验器 → 评估口径悄悄变了 | feature_list 一次一个 + AGENTS.md"校验器单一来源"禁令 |
| 幻觉进度 | "实验跑通了"但没存日志 → 数字靠记忆复述 | progress.md 只记有 evidence 的数字，未验证项必须标 |
| 上下文溢出后的断点丢失 | 长会话压缩后丢关键约束（如"贪心解码"） | AGENTS.md 常驻，压缩压不掉磁盘上的文件 |

第三条正是 harness 精华笔记里的"验证即证据"（Verification as Evidence）：**声称完成 = 日志文件存在 + 数字在 progress.md 里**。本单元每次实验的 log 都回收到 experiments/，就是这个纪律。

## 四、诚实声明：四文件的收益在本项目是定性论证

learn-harness 的硬证据（同模型无 harness $9/20min 产出不可用 vs 全套 harness $200/6h 产出可玩）来自 Anthropic 对照实验。本项目是单人+AI 开发，没有做"有/无四文件的平行开发对照"（成本太高）。诚实地说：

- 已验证：四文件在"跨会话接续"上立刻可用（下次任何会话读三个文件即可恢复全部上下文）
- 未验证：开发速度的量化提升
- 风险：四文件本身要维护（漂移的 progress.md 比没有更糟）——所以 WRAP UP 纪律是四文件的生命线

## 五、L2 的完成标志

- [x] 四文件落盘且内容对齐项目真实约束（非模板填空）
- [x] 会话生命周期写入 AGENTS.md 并在本次开发中实际执行（progress.md 的 WRAP UP 记录）
- [ ] 冷启动接续实测：留一个"下次会话只读四文件，5 分钟内说出当前进度+下一步"的验收动作

## 六、不足与批判

- 四文件是给"开发会话"的；运行时 agent 自身的 harness（Instructions/State/Verification/Scope/Session 五子系统）在 L4a 记忆层才落地——两个层次不要混
- 96 核服务器容器不是真端侧设备，部署命令的"端侧版"（真机/树莓派）未覆盖
- 无 init.sh 的决策依赖"部署命令稳定"这个假设；若容器重建（路径变化），需要回头补 init 脚本

---
下一步：[03-L3评估环](./03-L3评估环.md)——34 条固定任务集 × 4 版本终局对照，让所有设计决策过堂受审。
