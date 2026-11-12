# code-annotated —— 逐行中文教学注释版（全仓 45 文件）

> 2026-10-14 生成。原仓 `/usr-data/data1/workspace/rl/DRL-robot-navigation-IR-SIM` @31e1a4d 保持只读零改动（终验 git status=0）；本目录是完整镜像结构的注释副本。
>
> **验证结论（三重，全过）**：31 个有效文件 `ast.dump` 与原文件**完全等价**（代码+docstring 语义零改动的最硬证据）、全部可编译、空行零净减；每个非空代码行均带中文注释（docstring 内部行按"逐字符不变"硬约束豁免，其教学职责由 def/class 上方块注释覆盖）。验证器 `_verify.py` 可复跑。

## 注释密度与口径

- 原仓 8126 行 → 注释版 ~9367 行，纯增 ~1240 行注释（行尾+块注释）
- 每行代码：做什么（基础档）+ 关键行为什么（教学档：twin Q 取 min 防 Q 高估、polyak 软更新、GAE 偏差-方差对照、tanh squash 雅可比修正等）
- 张量操作标注 shape 流转；RL/MARL/pytest 术语首现展开 1-2 句通俗解释
- `__init__.py` ×14 为包角色一行说明（原文件为空）

## 文件地图

| 路径 | 行数(原→注) | 内容 |
|---|---|---|
| `robot_nav/models/TD3/TD3.py` | 451→496 | TD3 主算法（twin critic/延迟更新/目标平滑） |
| `robot_nav/models/DDPG/DDPG.py` | 429→477 | DDPG（该仓实现已含平滑+延迟，唯缺孪生 critic） |
| `robot_nav/models/CNNTD3/CNNTD3.py` | 494→536 | CNN 吃 185 维单帧（180 激光束+5 导航量）的 TD3 |
| `robot_nav/models/RCPG/RCPG.py` | 517→565 | TD3 式 DPG + CNN-GRU 编码 10 帧历史 |
| `robot_nav/models/PPO/PPO.py` | 501→554 | PPO（注意：MC 回报优势，非 GAE；整批更新） |
| `robot_nav/models/SAC/SAC.py` | 407→443 | SAC 主算法（最大熵/α 自动调/rsample） |
| `robot_nav/models/SAC/SAC_{actor,critic,utils}.py` | 199+65+138→247+84+170 | tanh squash 雅可比修正/数值稳定式/软更新 |
| `robot_nav/models/HCM/hardcoded_model.py` | 199→238 | 硬编码对照基线（故意次优，采碰撞样本供预训练） |
| `robot_nav/models/MARL/marlTD3/marlTD3.py` | 633→696 | 多智能体 TD3：逐 agent 配对 Q+共享 twin-Q+双注意力 |
| `robot_nav/models/MARL/Attention/{iga,g2anet}.py` | 421+268→478+305 | 硬门控稀疏图+PyG 消息传递 / 稠密双阶段 Gumbel×点积 |
| `robot_nav/SIM_ENV/{sim,marl_sim,sim_env}.py` | 143+363+35→195+421+76 | 单机/多机仿真：reward 全拆解+观测构造 |
| `robot_nav/{replay_buffer,utils}.py` | 221+253→274+292 | 环形 buffer+预训练加载+Max Upper Bound 上界计算 |
| `robot_nav/{marl,rnn,rl}_train.py` | 176+173+145→195+187+160 | 三条训练线（MARL/RCPG/CNNTD3） |
| `robot_nav/{marl_test_single,marl_test_random}.py` | 461+241→510+262 | MARL 测试：固定圆环 100 局 vs 随机持续 1000 局 |
| `robot_nav/{rnn_test,rl_test,rl_test_random}.py` | 97+88+160→106+97+168 | 单智能体测试线 |
| `robot_nav/rvo_test_{single,random}.py` | 238+289→298+348 | RVO 经典避障对照组 |
| `tests/test_{model,utils,sim}.py` | 150+111+60→206+159+121 | 冒烟/分发/运动学三套测试 |

## 实证勘误清单（源码级，注释中均已就地标注）

1. **TD3.py Critic Kaiming 误初始化**：Q2 入层初始化对象仍是 `layer_1`，`layer_4` 保持默认初始化
2. **forward 中 `weight.data` 赋值**使 `layer_2_s/a` 权重脱离计算图（遗留调用行）
3. **PPO 非 GAE**：MC 回报减 V 做优势；整批更新非 minibatch（`batch_size` 为接口占位未用）
4. **marl_train.py 默认 `attention="iga"` 起不来**：构造器合法值仅 igs/g2anet，按原样 ValueError；测试脚本用的 `"igs"` 才是 iga.py Attention 类注册键
5. **marl_sim.step 画边 NameError 预留位**：`combined_weights=None` 时 `weight` 未定义（原作者注释掉的 `else: weight=1` 即预留修复位）
6. **G2ANet 索引越界风险**：实测输出 `(5,4)`，`j` 循环到 `N−1` 时 `i_weights[N-1]` 越界；`i_weights` possibly unbound（marl_test_single.py:178）
7. **marl_sim.reset 多机分支**：`robot_state` 入参被随机采样无条件覆盖；固定 `robot_goal` 只写 0 号机器人
8. **g2anet 是简化版**：软打分非论文原版 ESL+CSL+GLU；iga 外层 q/k/v 为残留死权重、加性打分无 √d
9. **RVO 对照组配置陷阱**：RVO 控制器由 world YAML `behavior` 激活——`circle_world.yaml` 中该行**被注释**、`multi_robot_world.yaml` 干脆没有；圆周对穿目标由 irsim `object_factory` 自动覆盖 YAML 的 `goal`
10. **tests 两处恒真断言疑似笔误**（`robot_state[1]` 自比较，单机/多机各一处）
11. **观测口径并存**：rl 线训练 CNNTD3 用 185 维全扫描，测试 TD3/SAC 用 25 维分箱压缩（5 扇区）
12. Max Upper Bound Loss 上界实证：`max_bound = r + (1−done)·[−ω·γ^⌊N⌋ − γ^(⌊N⌋+1)·frac + goal·γ^(⌈Nlin⌉+⌊N⌋+1) + Σ v·γ^k]`，TD3.py:303 以 `relu(Q−bound)²` 惩罚

## 生成方式

12 批 general 子代理（4 并发，并发红线内）+ 主会话手写 14 个 `__init__.py`；派发模板见上级目录 `_annotator-template.md`。修复记录：rnn_train.py/CNNTD3.py 各补回 1 个被块注释吞掉的 PEP8 空行（主会话终验抓出）；g2anet.py 空行仅位置变化零净减，判合格。
