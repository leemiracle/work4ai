# 快速开始指南

## 第一次使用

### 1. 了解项目
阅读项目总览：
```bash
cd /mnt/c/Users/mirac/Documents/personal-capability-system
```

依次阅读：
1. `README.md` - 了解项目目标和能力框架
2. `models/human-capability-panorama.md` - 理解能力本质，评估自己的能力分布 ⭐⭐
3. `models/30-day-cognitive-training.md` - 30天认知升级训练计划（推荐从这里开始）⭐
4. `models/cognitive-methods.md` - 了解系统级认知方法（5大系统）⭐
5. `ROADMAP.md` - 了解执行者→判断者转型路径
6. `models/cognitive-methods-for-technical-scenarios.md` - 技术人专项（可选）

### 2. 初始化能力评分
打开 `metrics/` 目录，对所有9个能力进行自我评估：

**【核心能力 ⭐】(最优先)**
1. `problem-definition.md` - 问题定义与选择能力 ⭐⭐⭐
2. `judgment.md` - 判断与取舍能力 ⭐⭐⭐
3. `resource-integration.md` - 资源整合能力 ⭐⭐
4. `influence.md` - 影响力与沟通能力 ⭐⭐

**【进阶能力】**
5. `abstract-modeling.md` - 抽象建模能力
6. `systems-thinking.md` - 系统级思维
7. `decision-making.md` - 不确定性决策能力
8. `technical-depth.md` - 技术底层理解
9. `migration.md` - 快速迁移能力

填写每个文件的"当前得分"部分。

### 3. 了解能力框架
阅读每个指标文件，了解：
- 评估维度和打分标准
- 提升路径 (Level 1-10)
- 练习方法

---

## 日常使用

### 开始30天认知训练（推荐新人）

每日10-15分钟，系统提升认知能力：

```bash
cp learning-log/daily-cognitive-training.md learning-log/daily/Day-01.md
```

填写每日训练模板，完成五层认知练习：
1. 拆解（信息理解）
2. 推演（逻辑推理）
3. 量化（决策优化）
4. 画反馈（系统思维）
5. 复盘（元认知）

详细计划参考：`models/30-day-cognitive-training.md`

---

### 开始专项能力练习

```bash
./start.sh
```

选择你要练习的能力，系统会自动创建练习记录文件。

### 练习步骤
1. 从练习方法中选择一个
2. 填写练习记录
3. 记录过程中的思考
4. 完成后更新指标

### 记录学习
学习新知识时：
```bash
cp learning-log/template.md learning-log/YYYY-MM-DD-topic.md
```
记录学习内容、深度思考和行动计划。

---

## 周期性任务

### 每日
- [ ] 完成每日认知训练（10-15分钟）
- [ ] 或进行至少一个专项练习（30-90分钟）
- [ ] 记录关键发现
- [ ] 标记待验证假设

### 每周
- [ ] 回顾本周练习
- [ ] 识别模式
- [ ] 调整下周重点

### 每月
- [ ] 复制 `reviews/monthly/template.md`
- [ ] 更新所有9个能力评分
- [ ] 填写月度复盘
- [ ] 制定下月计划

### 每季度
- [ ] 复制 `reviews/quarterly/template.md`
- [ ] 进行深度复盘
- [ ] 调整长期目标
- [ ] 评估转型进度

---

## 文件组织

```
personal-capability-system/
├── README.md                      # 项目总览
├── QUICKSTART.md                  # 本文件
├── ROADMAP.md                     # 执行者→判断者转型路线图 ⭐
├── start.sh                       # 每日练习启动脚本
├── metrics/                       # 能力量化指标 (每月更新)
│   ├── problem-definition.md      # ⭐ 问题定义与选择能力
│   ├── judgment.md                # ⭐ 判断与取舍能力
│   ├── resource-integration.md    # ⭐ 资源整合能力
│   ├── influence.md               # ⭐ 影响力与沟通能力
│   ├── abstract-modeling.md       # 抽象建模能力
│   ├── systems-thinking.md        # 系统级思维
│   ├── decision-making.md         # 不确定性决策能力
│   ├── technical-depth.md         # 技术底层理解
│   └── migration.md               # 快速迁移能力
├── practices/                     # 日常练习记录
│   ├── template.md                # 练习记录模板
│   ├── example-*.md               # 6个练习示例（含认知方法组合示例）
│   ├── problem-definition/        # 问题定义练习
│   ├── judgment/                  # 判断力练习
│   ├── resource-integration/      # 资源整合练习
│   ├── influence/                 # 影响力练习
│   ├── abstract-modeling/         # 抽象建模练习
│   ├── systems-thinking/          # 系统思维练习
│   ├── decision-making/           # 决策能力练习
│   ├── technical-depth/           # 技术深度练习
│   └── migration/                 # 迁移能力练习
├── reviews/                       # 月度/季度复盘
│   ├── monthly/
│   │   └── template.md            # 月度复盘模板
│   └── quarterly/
│       └── template.md            # 季度复盘模板
├── projects/                      # 实战项目追踪
│   └── template.md                # 项目模板
├── learning-log/                  # 学习日志
│   ├── template.md                # 学习日志模板
│   └── daily-cognitive-training.md # 每日认知训练模板（10-15分钟）⭐
└── models/                        # 个人建立的抽象模型库
    ├── human-capability-panorama.md # 人类能力全景图（六大能力系统）⭐⭐
    ├── cognitive-methods.md       # 系统级认知方法图谱（5大系统）⭐
    ├── 30-day-cognitive-training.md # 30天认知升级训练计划 ⭐
    ├── cognitive-methods-for-technical-scenarios.md # 技术场景应用指南 ⭐
    ├── ai-question-generation.md  # AI自主生成问题分析
    └── talent-polarization.md     # 能力两极分化推演
```

---

## 快速参考

### 【核心能力 ⭐】(最优先练习)

#### 1. 问题定义与选择能力 ⭐⭐⭐
**核心**: 质疑框架、定义价值、选择真正值得解决的问题
**AI能**: 生成框架内问题
**AI不能**: 质疑框架、定义价值
**练习**: 假设质疑练习、问题重构练习
**时长**: 30-60分钟
**示例**: `practices/example-problem-definition.md`

#### 2. 判断与取舍能力 ⭐⭐⭐
**核心**: 复杂条件下的判断、长期vs短期权衡、风险承受
**AI能**: 提供方案和数据
**AI不能**: 做最终选择、承担责任
**练习**: 决策矩阵、事前验尸
**时长**: 30-60分钟
**示例**: `practices/example-judgment.md`

#### 3. 资源整合能力 ⭐⭐
**核心**: 整合人+AI工具+专家，设计工作流
**AI能**: 执行具体任务
**AI不能**: 设计流程、协调资源
**练习**: 工具组合、流程设计、资源映射
**时长**: 60-90分钟
**示例**: `practices/example-resource-integration.md`

#### 4. 影响力与沟通能力 ⭐⭐
**核心**: 建立信任、协调利益、推动落地
**AI能**: 生成内容
**AI不能**: 建立信任、说服他人
**练习**: 结构化表达、说服练习、冲突处理
**时长**: 30-60分钟

### 【进阶能力】

#### 5. 抽象建模能力
**核心**: 把复杂现实变成结构化模型
**练习**: 每天用5Why拆解一个现象
**时长**: 30-60分钟
**示例**: `practices/example-abstract-modeling.md`

#### 6. 系统级思维
**核心**: 理解全局约束和跨维度影响
**练习**: 画出一个系统的完整图景
**时长**: 60-90分钟

#### 7. 不确定性决策能力
**核心**: 在信息不完整时做决策并承担责任
**练习**: 事前验尸分析
**时长**: 30-60分钟

#### 8. 技术底层理解
**核心**: 深入理解系统瓶颈、性能边界、架构权衡
**练习**: 阅读一篇经典论文并实现核心算法
**时长**: 90-180分钟

#### 9. 快速迁移能力
**核心**: 学习速度 × 跨领域应用
**练习**: T型快速迁移挑战
**时长**: 30-60天

---

## 常见问题

### Q: 练习需要多长时间？
A: 每天至少30分钟，建议1-2小时。根据练习类型调整。

### Q: 如何选择今天练习什么？
A:
1. 如果不确定，从"问题定义与选择能力"开始
2. 优先练习得分最低的能力
3. 结合当前工作/学习需求
4. 按照ROADMAP.md的转型阶段

### Q: 如何知道是否有进步？
A:
- 每月复盘时对比得分变化
- 记录实际应用能力的场景
- 观察AI工具使用效率的提升
- 观察决策质量的改善

### Q: 能力之间可以交叉练习吗？
A: 非常鼓励。实际中很多问题需要多个能力综合解决。

### Q: 如何从执行者转型为判断者？
A:
1. 阅读 `ROADMAP.md` 了解转型路径
2. 按照4个阶段推进 (觉醒→学习→实践→成长)
3. 优先练习4个核心能力
4. 在真实项目中应用新能力

### Q: AI工具很多，怎么选择？
A:
1. 评估工具是否解决你的核心问题
2. 考虑学习成本vs收益
3. 看社区活跃度和生态
4. 小规模试用再决定

### Q: 转型失败了怎么办？
A:
1. 失败是学习的一部分
2. 用季度复盘模板深度分析原因
3. 调整策略，继续前进
4. 判断力的提升需要时间积累

---

## 下一步

### 今天
1. 阅读 `README.md` 和 `ROADMAP.md`
2. 运行 `./start.sh` 开始第一次练习
3. 从"问题定义与选择能力"开始

### 本周
1. 阅读 `metrics/` 下的所有指标文件
2. 完成至少3次练习
3. 阅读所有练习示例

### 本月
1. 完成月度复盘
2. 更新能力得分
3. 制定下月计划

---

## 核心原则

1. **判断力是区分判断者和执行者的核心**
2. **AI是工具，不是竞争者**
3. **转型需要时间，不要急于求成**
4. **小决策积累成大判断力**
5. **持续记录，持续反思，持续改进**

---

**记住**:
- AI放大执行力，人类价值转向判断力
- 现在是转型判断者的最佳时机
- 时间窗口有限，越早开始越好
- 判断力是练习出来的，不是天赋
