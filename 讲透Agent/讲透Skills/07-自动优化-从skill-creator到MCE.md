# 07 — 自动优化：从 skill-creator 到 MCE

> 「讲透 Skills」第八篇 ★（用户五问之三：**自动优化 skills 的工具，详细说明与探索**）。三层工具栈：官方工程层（skill-creator，已讲透触发优化）/ 学术前沿层（MCE 自动进化）/ 实践复用层（本仓方法论映射）。核心问题：**skill 的哪些部分可以被机器优化，哪些必须人来？**

---

## 1. 优化对象拆解：一个 skill 有五个可调旋钮

```
skill = {
  ① description   —— 路由键（决定被不被用）
  ② body 指令集    —— 程序性知识（决定用得好不好）
  ③ 结构组织       —— 分层/指路/何时读 references（决定 token 效率）
  ④ scripts/      —— 确定性代码（决定下界）
  ⑤ eval 集        —— 什么算"好"的定义（决定优化方向）
}
```

自动优化工具的能力边界一览：

| 旋钮 | 官方 skill-creator | 学术 MCE | 人工不可替代性 |
|---|---|---|---|
| ① description | ✅ **run_loop 全自动闭环**（60/40 防过拟合 + 3 次采样） | △ 随 body 共同进化 | 低（机器占优） |
| ② body 指令 | △ 人机协作循环（人看 viewer 反馈，机器执行+提议） | ✅ **agentic crossover 自动重写** | 中（品味/泛化判断） |
| ③ 结构组织 | 半自动（>500 行时提示拆分） | ✅ 作为 context artifact 一起进化 | 中 |
| ④ scripts | ✅ 检测重复劳动并建议捆绑（"3 个 case 都自写了 create_docx.py → 应进 scripts/"） | ✬ 代码类 artifact 直接优化 | 中高（正确性审计） |
| ⑤ eval 集 | △ 机器起草 query/assertion，**人审**（"坏 eval 优化出坏 description"官方原文） | 外生（论文用领域基准） | **最高**（目标函数的定义权） |

## 2. 官方工程层：skill-creator 全景（485 行 SKILL.md 一手拆解）

[03 章](03-路由与触发-description即检索键.md) 已详解其 trigger eval 优化协议，这里补全它的另外三件武器：

### 2.1 创建循环（draft → test → review → improve）

```
① 意图捕获：从当前对话提取工作流（用户说"把这个变成 skill"时，历史即素材）
② 访谈补全：边界/格式/成功标准/依赖
③ 起草 SKILL.md
④ 测试：with-skill 与 baseline（无 skill/旧版）**同轮双跑**——子agent并行,
   一个带技能一个不带, 消除时间混淆
⑤ 评估三通道：人看 eval-viewer（qualitative）+ assertion 打分（quantitative）
   + analyzer 扫模式（non-discriminating assertion / flaky case / token-time 权衡）
⑥ 改进哲学四条（官方原文精华）：
   - 从反馈泛化, 防过拟合（"skill 要能被用一百万次, 不是过拟合这 3 个例子"）
   - 保持精简（"读 transcript, 删没拉力的部分"）
   - 解释 why 优于 MUST 排比（强模型理论的心智）
   - 重复劳动 → scripts/（agent 三次独立写出同款脚本 = 捆绑信号）
⑦ 迭代直到用户满意 / 反馈全空 / 无实质进展
```

### 2.2 盲评对比（blind comparison）

"新版真的更好吗"——两个版本的输出给**独立 agent 盲评**（不知道哪个是哪个），再让 analyzer 解释赢家赢在哪。这是本仓 A/B 方法论（prompt 手册 09 章 McNemar、性能优化 Agent E4）的 skills 官方版。

### 2.3 工程细节里的评估学

- benchmark.json 统一 schema（pass_rate / time / tokens 的 mean±stddev + delta）
- timing 数据从任务通知抓取（"唯一机会，不持久化"——真实工程教训）
- Claude.ai 无子agent环境降级路径（跳过 baseline/盲评，人审补偿）

## 3. 学术前沿层：MCE（arXiv:2601.21557，一手核实）

**Meta Context Engineering via Agentic Skill Evolution**（北大通用人工智能全国重点实验室，Ye Haoran/Song Guojie 等，2026-01-29 v1 / 02-11 v2，46 页）——第一篇把"skill 自动进化"做成完整系统的论文。

### 3.1 双层框架（bi-level）

```
meta-level agent（元层）:
  维护 skill 库 + 执行历史 + 评估记录
  核心操作 = agentic crossover（代理式交叉）:
    对 skill 的历史版本/执行轨迹/评估反馈做审议式搜索,
    杂交出新的 skill 版本（进化算子, 但由 agent 推理驱动而非遗传随机）

base-level agent（基层）:
  执行当前 skills 完成任务
  从训练 rollouts 中学习
  把 context 当"灵活的文件与代码"来优化（context artifact 也是进化对象）
```

### 3.2 结果与主张

- 5 个领域 × 离线/在线设定，相对 SOTA agentic CE 方法 **+5.6%~53.8%**（均值 16.9%）
- 同时保持 context 适应性、可迁移性、上下文用量与训练效率的优势
- 定位主张（原文）：现有 CE 方法"依赖手工 harness、结构僵化、限制在直觉绑定的窄设计空间"——MCE 把 skill 从**静态制品**变成**共同进化的活资产**

### 3.3 与官方工具的互补

| | skill-creator | MCE |
|---|---|---|
| 范式 | 人机协作循环（人在评估环内） | 自动双层进化（人只定基准） |
| 优化信号 | 人反馈 + assertion + trigger eval | 环境评估（领域基准/在线回报） |
| 进化算子 | LLM 提议重写（单亲） | agentic crossover（历史杂交, 多亲） |
| 可用性 | 今日可用（官方仓库） | 论文系统（复现成本高） |
| 对 skill 的假设 | 结构固定（SKILL.md 三层） | 连分层本身都可进化（context=files+code） |

**诚实边界**：MCE 的 5.6%~53.8% 是相对"静态 CE 方法"的增益——静态基线里就包括 muratcankoylan 的 context-eng skills 仓（被论文引用为 static skill architecture 代表）。MCE 需要训练 rollouts 与评估基建，个人 skill 作者用不起；它的直接启示是：**当你的 skill 库大到几十个且任务可评估时，"维护 skill"该被当作进化搜索问题而非手工艺**。

## 4. 实践复用层：本仓方法论的 skills 映射

三层工具栈的中间层——用本仓已有的评估/优化方法论改造 skills（全部可落地）：

| 本仓资产 | skills 场景的用法 |
|---|---|
| prompt 手册 11 章六步闭环（造卷→摸底→归因→调参→验收→上岗） | skill 的 body 优化直接套用：黄金集=trigger eval+任务 eval 双集；归因=03 章路由失败四象限；调参=skill-creator 循环或 GEPA |
| McNemar/配对检验（A/B 实验方法论卡） | with-skill vs baseline 的显著性判定（skill-creator 的盲评只给偏好，不给 p 值——可加） |
| dummy 下界探针（实践阶梯） | "skill 带来的提升"必须显著超"仅 description 提示效应"——对照组：只给 description 不给 body |
| E4 军备竞赛（性能优化 Agent） | skill 系统的红队：恶意 skill 投毒/触发劫持的攻防测试 |
| 六步闭环的"metric 是新的 prompt"警告 | eval 集定义权=优化方向——skill-creator 让人审 eval 集的原因完全同构 |

### 一个可直接跑的最小闭环（本站协议）

```
1. 造卷: 20 trigger query(含 near-miss) + 10 任务样本(带可判输出)
2. 摸底: E1 协议跑触发率; 任务样本跑 with/without skill 双条件
3. 归因: 触发失败→改 description; 执行失败→改 body/scripts
4. 调参: 手动或让模型按失败样本重写(单亲版 MCE)
5. 验收: held-out 重跑, McNemar 定显著性
6. 上岗: git 版本化 skill 目录, CI 跑 E3 合规 + 触发回归
```

## ✍️ 练习

1. 为你某个 skill 的 description 设计一个 5 轮手动 run_loop：每轮改写 → E1 协议测 10 query → 记录 near-miss 变化。第 5 轮与第 1 轮差在哪？
2. （思考）MCE 的 agentic crossover 需要"skill 的执行历史"。你的 skill 使用日志里现在有什么？缺什么？（大多数用户缺执行日志本身——这提示 skill 的 telemetry 是进化的前提设施）
3. 对照第 1 节五旋钮表：你最有信心让机器优化哪个、最不敢放手哪个？为什么？

---

**下一篇**：[08 — 研究前沿：2025-2026 论文地图](08-研究前沿-2025-2026论文地图.md)
