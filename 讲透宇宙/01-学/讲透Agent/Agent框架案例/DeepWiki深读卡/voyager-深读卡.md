# voyager 深读卡 —— LLM 驱动的 Minecraft 终身学习 Agent，"代码即技能"库开山之作

> **定位**：NVIDIA/Caltech 出品的 GPT-4 具身终身学习 Agent（NeurIPS 2023 spotlight），在 Minecraft 中无人干预地自动探索、写代码、攒技能。核心差异化 = 自动课程 + 可执行代码技能库 + 迭代提示机制三件套，不微调、纯上下文学习即可无限累积能力。
> **本地**：`repos/voyager`（MineDojo/Voyager）｜**深读**：deepwiki 16 子页归档 `deepwiki/voyager/full.md`（2026-08-21）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| 编排层 | 中央调度器：终身学习循环与任务分解 | `Voyager`（voyager.py：`learn/rollout/step/inference`） |
| 课程层 | 自动课程：提议难度递增任务、跟踪进度 | `CurriculumAgent`（agents/curriculum.py） |
| 执行层 | GPT-4 生成可执行 JS 代码完成当前任务 | `ActionAgent`（agents/action.py，含 chest memory） |
| 评估层 | GPT 自验证任务成败并给出 critique | `CriticAgent`（agents/critic.py） |
| 技能层 | 技能=代码：Chroma 向量检索 + 持久存储 | `SkillManager`（agents/skill.py，ckpt/skill/） |
| 环境层 | Python↔Node 桥：注入代码、回收游戏事件 | `VoyagerEnv`（env/bridge.py ↔ Mineflayer） |
| 基元层 | 技能可调用的 JS 原子动作库 | `control_primitives/*.js`（craftItem/mineBlock/useChest…） |

## 二、核心机制

1. **自动课程**（Curriculum Agent 页）：GPT-4 综合当前状态、背包、附近方块实体、已完成/失败任务清单，提议"下一步最合适的任务"，难度随进度递增。**创新点**：没有奖励模型也没有人工课程表，用 LLM 当课程规划器驱动开放式探索——后来所有 "agent 自己给自己定目标" 的设计都源于此。
2. **代码即技能**（Skill Manager / Skill System 页）：任务成功后，实现代码被存为 `.js`，LLM 再生成功能描述并 embedding 入 Chroma 库；新任务按语义检索 top-5 相关技能注入 prompt，技能可无限组合复用。**创新点**：能力增长不靠梯度而靠"可检索的程序性记忆"，skill library 概念的开山实现；技能库可 checkpoint、可社区共享换机续训。
3. **迭代提示机制**（Action Agent 页）：GPT-4 生成代码 → 环境执行 → 执行报错/游戏事件回填 prompt → 重新生成，直到 Critic 验证通过。**创新点**：环境反馈 + JS 执行器报错 + GPT 自验证三重反馈闭环，替代人工调试，是后来 agent "self-debug / self-verification" 范式的雏形。
4. **学习/推理双模式**（Usage and Examples 页）：`learn()` 开放式终身学习 vs `decompose_task()+inference()` 复用既有技能库执行指定任务（如 "craft a diamond pickaxe" 自动分解为子目标链）。

## 三、与讲透系列的对位

| Voyager 概念 | 讲透系列对应概念 |
|---|---|
| CurriculumAgent 自主提议任务 | 讲透学习型Agent · 自进化（自主目标设定/课程） |
| Skill Library（Chroma+JS 代码） | 记忆机制 · 程序性长期记忆 + 向量检索 |
| 迭代提示+执行报错回填 | ReAct 循环 + 上下文工程（反馈进上下文重试） |
| ActionAgent 生成 JS 组合基元 | 工具调用（代码即 action space） |
| Mineflayer 受控进程内执行 JS | 安全沙盒（代码执行隔离在游戏进程） |

## 四、关键入口

```python
voyager/voyager.py                       # 主类+学习循环 learn()/rollout()/inference()，读懂全局先读它
voyager/agents/curriculum.py             # 自动课程：propose_next_task/update_exploration_progress
voyager/agents/action.py                 # GPT-4→JS 代码生成 + chest memory 背包状态管理
voyager/agents/critic.py                 # check_task_success 自验证关卡
voyager/agents/skill.py                  # SkillManager：add_new_skill/retrieve_skills + Chroma
voyager/control_primitives/craftItem.js  # 控制基元示例：技能赖以组合的原子动作
voyager/env/bridge.py                    # VoyagerEnv↔Mineflayer 桥：代码注入+事件观察
skill_library/                           # 官方/社区技能库，可下载直接续训
```

## 五、深读子页地图（16 页精选 6）

1. **Core Architecture**（L1029）— 五组件关系 + 学习循环时序图，全局最清晰的总览页
2. **Curriculum Agent**（L1532）— 自动课程全实现：任务提议、进度管理、QA 缓存、warm-up 机制
3. **Action Agent**（L1860）— 迭代提示机制与错误处理的第一现场
4. **Skill Manager**（L2302）— "代码即技能"的存取/描述生成/向量检索全流程
5. **Control Primitives**（L3108）— JS 基元与技能的组合语法，看懂 action space 设计
6. **Environment Integration**（L3352）— Python↔Node 桥与观察系统，具身落地的工程细节

## 六、与"我们"的关系（一句话）

学 Agent 想真正理解"skill library/自进化"从哪来，必须读这个源头仓库——它示范了不微调、纯靠"检索式程序性记忆"就能终身累积能力的完整闭环。

---
生成：2026-08-21 · deepwiki 16 页全归档
