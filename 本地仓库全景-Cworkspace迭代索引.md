---
card_id: WS-PANORAMA
title: "本地仓库全景：C:\\workspace 21 仓迭代索引"
universe: 元理论
burke:
  scene: "C:\\workspace 除了 work4ai 还有 20+ 个仓库——它们是同一双手在 2026 年 6-8 月用 AI 批量生产的知识生态"
  agent: "把整个 workspace 当复杂系统治理的架构师"
  agency: "research 流水线（outline/fields/分批agent）+ 用例卡方法"
  act: "20 仓深读 → 结构化用例卡 → 横断结论 + 合并清单"
  purpose: "盘点姊妹库资产、建立互链网络、识别风险（未提交/虚标/腐烂）"
  tension: "资产已存在，缺的是边——More Is Different，网络价值在连接"
  arc: [总表, 横断结论, 合并清单, 风险, 复现]
  status: done
  refs:
    - "数据: .research/workspace-repos/{outline.yaml, fields.yaml, results/*.json × 20}"
    - "方法: dr-research 流水线（research → research-deep 分批 agent）"
    - "姊妹篇: 复杂系统迭代work4ai.md（网络治理理论）、用例库/（GitHub 279 仓）、Agent框架案例/deepseek-harness插件化框架（今日已并）"
    - "今日增补: 透视GitHub-DeepSeek开源全景.md + 讲透DeepSeek/（org:deepseek-ai 36 仓全量深读；本地克隆在 work4ai/.tools/deepseek-repos/，gitignored）"
updated: 2026-08-15
---

# 🗺 本地仓库全景：C:\workspace 21 仓迭代索引

> **2026-08-15 全量深读完成**：A 层（自有 AI 项目）5 + B 层（自有知识库）8 + C 层（外部参考库）7 = 20 仓，每仓一张结构化用例卡（七大类字段 + 证据锚点），另加今日已合并的 deepseek-harness 共 21 仓。
> 原始卡片：`.research/workspace-repos/results/*.json`（本文件是唯一入库入口，孤儿率为零）。

## 0. 一句话总纲

**C:\workspace 不是 20 个孤立文件夹，是一个"AI 辅助知识生产实验室"的化石层**：几乎每个库都是 1-4 天单日冲刺的爆发产物，work4ai 是其中被显式依赖的方法论 hub——资产已经存在，缺的是边。

## 1. 总表（20 仓 × 本质 × 动作）

| 层 | 仓库 | 一句话本质 | 建议动作 |
|---|---|---|---|
| A | **neo-os** | 把 work4ai"讲透"方法论**运行时化**的可解释性基础设施（四层栈 + Lean4 sorry=0 + trace 可证伪实证） | 桥接互链 + 用例库收录（其 03-methodology 已单向引用 work4ai，应回链成双向） |
| A | **world-ai4sci-math** | 133 万字、1152 arXiv 一手核实、118 可运行实验的世界模型×AI4Sci×AI4Math 全景调研卷 | 桥接互链 + 精选合并（top-20-insights / ten-lessons 两篇直接入库） |
| A | **ai-atlas** | 三天 AI 批量生成的广度型 AI 全景"总入口"姊妹库（实测 447 md，README 统计口径混乱） | 部分合并 + 互链（选型/职业/术语/技能图谱是 work4ai 缺位组件） |
| A | **ai-os-dd** | 单日成型的 AI×OS 尽调深潜：78 创新点矩阵 + FormalLinux(30 lean) + llmkv 跨进程 KV Cache daemon | 桥接互链 + 精选单篇合并（M14/M18 → 讲透KV Cache 等） |
| A | **math-expert-pro** | 时间主轴×概念横切×双透镜（16 数学家轴+55 从业者角色）三维数学训练矩阵，35 个可跑脚本 | 桥接互链 + 精选合并（AI-for-Math 卡 → 讲透Lean4数学） |
| B | **essence** | 以哲学为根、四科学部为干、48 条"调用思想家"洞察为货币的跨学科本质追问系统 | 桥接互链 + 精选合并（entropy 跨学科卡 → 软件即熵治理） |
| B | **growth-hub** | 以"可验证+反幻觉"为设计原则的第二大脑（曾整体吞并 csdiy 库） | 桥接互链 + 治理借鉴（L1-L4 可验证架构、AI笔记≠内化） |
| B | **gongwen-mastery** | "本质→操作→实战"三层架构的百万字公文库（实测 121 万字 < 宣称 163 万，词表 150-190 对 < 宣称 1000） | 仅索引 + 互链（AI 辅助写作边界两处互链，引用以实测数为准） |
| B | **master-equivalent** | 考试倒逼的备考军火库 + PaddleOCR 全书解析→闪卡/模拟卷自动生成流水线 | 仅索引 + 考古参考（知识加工流水线方法卡一条） |
| B | **agi-venture** | 以变现为终的 AGI 战略操作手册骨架（决策框架精，但 28 分钟生成后 17 天零迭代） | 桥接互链 + 精选合并（agent-patterns → 讲透Agent；市场数据需校准） |
| B | **social-laws** | 五段式规律卡（历史→直觉→数学→Python→批判）的社会科学规律实验室，21 篇 CSSCI 双轨校准 | 桥接互链 + 精选合并（体例 → 讲透复杂系统借鉴） |
| B | **economy** | 极小档案壳：远端本体（30 commits/v1.27）的完整索引，内容文件全缺 | 考古参考 + 仅索引（7 轮撞车核查方法论提炼一篇入 notes/economics） |
| B | **ai-lab-landscape** | CSRankings 数据 + 三档 delegate prompt 单日量产 155 篇实验室档案的"批量调研工厂" | 桥接互链 + 数据定点合并（4 份 CSV → 前沿与媒体/13 学术圈） |
| C | **Foundations-of-LLMs** | 浙大 2024 中文《大模型基础》六章教材快照 + 987 行章节对齐论文列表 | 仅索引（第 5 章模型编辑是 work4ai 空白主题，留作引用源） |
| C | **Machine-Learning-Interviews** | MLSD 9 步公式 + 18 场景模板 + 公司系统一手链接库的面试五模块指南（2023 止，无 LLM 题） | 仅索引 |
| C | **cracking-the-data-science-interview** | 2019-2020 DS 求职现场：76 道规范题卡 + 九成体积的第三方书代码快照 | 仅索引 + 考古参考（书代码直引上游，不搬） |
| C | **CNTK** | 微软第一代 DL 框架完整"败者标本"（C++ 双引擎/BrainScript/1BitSGD，16117 commits） | 考古参考 + 仅索引（摘 5 处证据入讲透PyTorch 后，552MB 可降级冷数据） |
| C | **earthly** | "Dockerfile 和 Makefile 生了个孩子"：target 复用编译到 BuildKit LLB 层缓存 | 仅索引 + 考古参考（51MB 留本地，工程化手册库建桥接页） |
| C | **mips-sim** | **C 层中的 A 级遗珠**：63 章自著 CPU 教材（2.2 万行）+ 100 视角库 + gpu-mode 交叉表 | ⚠ 先 git 提交保护增量（约 2/3 未提交），再桥接 + 选择性合并 |
| C | **csdiy** | 活的公共课程索引 + 死的 22GB 离线快照 + 自建 L1-L5 精加工层三合一（git 实际仅 6.2MB） | 仅索引 + 选择性摘录（课程卡五要素范式、LLM 精读互链清单） |

## 2. 横断结论（跨 20 仓综合）

1. **单日冲刺生态**：12/20 仓是 1-4 天集中冲刺产物（mips-sim 7/4、ai-atlas 7/12-14、essence 7/12、growth-hub 7/12-16、social-laws 7/17、ai-os-dd 7/22、neo-os 8/5、agi-venture 28 分钟……）——这是《复杂系统迭代》"探索期高 T 爆发"的实证：workspace 的温度曲线是脉冲式的，且多数库冲刺后进入冻结（无负反馈固化阶段）。
2. **work4ai 是方法论 hub**：neo-os 显式建契约层引用（03-methodology/from-work4ai.md 六类映射）、world-ai4sci-math 与 6+ 讲透单元同题、ai-atlas 是降级候选、mips-sim 视角库同源——按网络科学语言：**入边已形成，出边缺失**（work4ai 侧无回链）→ 当前是"孤儿引用"状态，本文件即是补边。
3. **三大风险**：①**未提交资产**（mips-sim 约 2/3 高价值内容、world-ai4sci-math 59 文件未入 git、economy 本体在远端）②**宣传虚标**（gongwen-mastery 字数/词表虚高 3-5 成）③**快照腐烂**（csdiy 停 2026-02、Foundations 停 2025-01、CNTK 停 2022）。
4. **动作分布**：桥接互链 14 / 部分合并 6 / 仅索引 8 / 考古 4（组合计数）——大部分价值在**网络连接**而非内容搬运，恰是《复杂系统迭代》"补桥"优先于"搬内容"的治理建议。

## 3. 高优先级合并清单（Top 10，源 → 目标）

| # | 动作 | 源 | 目标 |
|---|---|---|---|
| 1 | mips-sim 未提交内容 git add+commit（数据安全，立即） | C:\workspace\mips-sim（Perspectives/GPU_MODE_*） | 该库自身 git |
| 2 | neo-os 双向回链 + 用例库立卡 | neo-os 03-methodology | work4ai 主 README / 用例库 |
| 3 | top-20-insights + ten-lessons 两篇 | world-ai4sci-math/04-synthesis | 前沿与媒体/ |
| 4 | 选型成本/职业路线/术语/技能图谱 | ai-atlas 08-11 | work4ai 缺位组件（新建或并入前沿与媒体） |
| 5 | M14/M18/M12 讲透型单篇 | ai-os-dd/deep-dive | 讲透KV Cache / 讲透形式化验证 |
| 6 | 五段式规律卡体例借鉴 | social-laws 任意规律卡 | 讲透复杂系统/群体智能 |
| 7 | L1-L4 可验证架构 + AI笔记≠内化 | growth-hub 06-insights | 元理论旁证（互链即可） |
| 8 | entropy 跨学科卡 | essence | 软件即熵治理 / 讲透信息论 |
| 9 | agent-patterns 精选 | agi-venture/phase-4 | 讲透Agent |
| 10 | 4 份 CSRankings CSV + 99-executive-summary | ai-lab-landscape/data | 前沿与媒体/13 学术圈数据附录 |

（执行细节含源路径与理由见 results/*.json 的"与work4ai关系.可合并资产"字段。）

## 4. 网络治理呼应

本索引是《[复杂系统迭代work4ai.md](./复杂系统迭代work4ai.md)》可证伪预测的第一次系统实践：
- **补桥**：本文件 + 用例库映射行，把 5 个"孤儿引用"姊妹库接入 work4ai 网络；
- **温度诊断**：workspace 整体处于"高 T 探索后未降温"态，建议进入固化期（执行合并清单、补回链、提交未入库资产）；
- **hub 检查**：work4ai 入度来源已从"内部讲透系列互引"扩展为"外部项目方法论依赖"——hub 地位成立，单点风险可控（方法论已外化为 neo-os 契约层副本）。

## 5. 数据与复现

```
.work in: C:\workspace\work4ai\.research\workspace-repos\
  outline.yaml   # 21 items + 5 批执行计划
  fields.yaml    # 七大类字段定义
  results\*.json # 20 张用例卡（每张含 uncertain 数组）
方法: /research 建纲 → /research-deep 批4仓×2agent 分批深读 → validate_json.py 验证 20/20 通过
```

📌 **下一步**：执行合并清单 Top10（建议顺序：1 数据安全 → 2/5 桥接 → 3/4/10 内容合并 → 6/7/8/9 借鉴互链）
