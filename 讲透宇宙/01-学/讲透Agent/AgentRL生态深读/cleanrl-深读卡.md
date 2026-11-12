# cleanrl 深读卡 —— 单文件实现的 DRL 算法博物馆（可读性压倒一切）

> **定位**：Shengyi "Costa" Huang（vwxyzjn）等 7 人的 DRL 参考实现库（JMLR 2022, 23(274)），每个算法变体 = 一个自包含 .py：`ppo.py` 312 行装下 PPO 全部。官方自认"**not meant to be imported**"（README.md:40）——它是被阅读/被魔改的，不是被 import 的。AgentRL 生态里唯一以"可读性"为第一目标的库。
> **本地**：`~/ai/cleanrl`（180M 浅克隆@fe8d8a0，2026-04-20；cleanrl/ 37 个 .py = 33 顶层 + ppo_trxl/3 + isaacgym/1，其中 JAX 版 9 个；docs/rl-algorithms 15 md · benchmark 20 sh · tests 15 py——全实测）
> **深读**：deepwiki 33 子页（索引 2026-07-27 标 fe8d8a，与本地 commit **完全一致**）——行号基本直对，但抽查抓到 **2 处陈旧锚点/失实断言**（见 §四注）

## 一、组件栈（deepwiki §1 蒸馏 + 本地实测）

| 层 | 职责 | 关键实体 |
|---|---|---|
| 单文件脚本范式 | 全部算法逻辑，零继承 | cleanrl/ 37 脚本：Args dataclass（ppo.py:17）→ tyro CLI（:130）→ make_env（:81）→ Agent/QNetwork（:100）→ 训练循环 |
| 共享工具 | 全库唯一"抽象豁免区" | cleanrl_utils/ 18 模块：buffers.py:250 ReplayBuffer / atari_wrappers.py 五包装器 / tuner.py / benchmark.py / huggingface.py / enjoy.py + evals/ 11 |
| 基准编排 | 多环境×多种子×SLURM | benchmark/ 20 个 .sh + slurm 模板（benchmark.py:27-33） |
| 复现与调参 | 断点续跑/超参搜索 | reproduce.py / resume.py / tuner.py（Optuna） |
| 云基建 | 千级并行实验 | cloud/ Terraform 六机型明码标价（cloud/main.tf:21-27，$0.034/h ARM→$1.204/h T4）+ submit_exp.py:91-119 boto3 提交 |
| 文档站 | benchmark.cleanrl.dev | mkdocs + docs/rl-algorithms/ 15 md（"37 细节"谱系树） |
| 质量门 | CI | tests/ 15 文件全 subprocess 烟测 + tests.yaml:13 Python 3.8/3.9/3.10 矩阵 |

## 二、核心哲学：单文件实现

- **为什么"无抽象"反而成就它**（README.md:19-22,40）：①可读——论文公式到代码零跳转，`ppo_atari.py` 一个文件讲完 PPO×Atari（README 自述 340 行，实测 329 行）；②可改——原型新特性不动全局，官方明说比模块库"少 subclassing"；③可复现——seeding + `torch_deterministic` + wandb `save_code`（上传训练脚本本体）。代价自认：**duplicate code**。
- **标准文件布局是第二发明**：37 个脚本同构（Args→make_env→Agent→循环→SummaryWriter），于是 **diff 两个脚本 = 算法差异本身**——`ddpg→td3` 的 diff 就是 TD3 论文三改进（双 Q 取 min td3:241 / 目标平滑 :232-233 / 延迟更新 :255）；30+ 脚本可横向对照全靠这个约定。
- **"37 细节"血统**：ICLR 2022 博客 *The 37 Implementation Details of PPO* 是 docs/rl-algorithms/ppo.md:19 的纲领，按变体拆档注入——ppo.py=13 核心细节（ppo.md:83）、ppo_atari=9 Atari 细节（:172）、ppo_atari_lstm=5 LSTM 细节（:443）。每个超参都有出处注释，这是它当"参考实现"的硬通货。
- **与 torchrl 组件化路线的根本对立**：torchrl 用 TensorDict/EnvBase/module 组合教"组装算法"，cleanrl 删光抽象教"读懂算法"。本目录隔壁 `torchrl/` 深读即另一极——两卡对照 = 2026 RL 库设计的光谱两端；生态位也互补：研究者读 cleanrl、工程团队上 torchrl/verl。

## 三、与本项目知识的对位

| cleanrl 脚本/概念 | 讲透RL 对应 | rl_agent toy / 实验对照 |
|---|---|---|
| ppo.py（clip 目标 :265-267，GAE 递推 :221-230，优势归一 :262） | 02 策略梯度与PPO | exp_grpo 乘法 clip 近似（toy 版） |
| dqn.py（回放+target 网+软更新 :214-218，截断处理 :184-187） | 01 Q-Learning与DQN | 讲透RL experiments/08_bellman_and_deadly_triad.py 的姊妹实证素材 |
| ddpg→td3→sac（td3:241/:255；sac 自动熵调 :204-207, :292，tanh 修正 :148） | 08 Actor-Critic-SAC（DDPG→TD3→SAC 严格推导的**参考答案**） | ——（toy 无 off-policy） |
| c51/rainbow（分布值函数） | 01/08 分布 RL | —— |
| ppo_rnd_envpool（RND 内在奖励） | 00 两大流派·探索 | —— |
| ppo 全家有 critic | 03 GRPO 去 critic = LLM 时代反向变形（工业版见 verl 卡） | exp_grpo 组内归一 (r−mean)/(std+ε) |
| tyro Args dataclass | ——（harness 配置层的最小样板） | rl_agent harness 配置对照 |

姊妹关系：讲透RL experiments 追求"纯标准库几秒跑通"，cleanrl 是同一哲学的社区正统（JMLR 收录）；toy 与它同属"自包含可跑"谱系，toy 是教学前置层、cleanrl 是标准参考层、verl 是工业层。

## 四、关键入口（本地验证 file:line）

```
cleanrl/ppo.py                        # 教学标杆 312 行=完整 PPO（Args:17/make_env:81/Agent:100/tyro:130/GAE:221-230/clip:265-267/价值裁剪:272-282）
cleanrl/dqn.py                        # 248 行 DQN（final_observation:184-187 / TD loss:196-201 / 软更新:214-218；ReplayBuffer import 自 cleanrl_utils/buffers.py:250）
cleanrl/ppo_atari_envpool_xla_jax_scan.py  # 吞吐天花板 522 行：整条 rollout 进 XLA 图（XLA_MEM:23 / AgentParams:171 / lax.scan GAE:345）
cleanrl/sac_continuous_action.py      # 熵自动调优（target_entropy:204 / alpha_loss:292 / tanh log-prob 修正:148）
cleanrl/td3_continuous_action.py      # 对照 dqn/ddpg 读：TD3 三改进（min 双Q:241 / 噪声平滑:232-233 / 延迟更新:255）
cleanrl_utils/tuner.py                # Optuna Tuner:24（sqlite:36 / 跨环境归一化聚合:51-54）
cleanrl_utils/huggingface.py          # push_to_hub:15（@retry 10 次:14 / replay.mp4:10）
docs/rl-algorithms/ppo.md             # 37 细节谱系树（:19 纲领 / 13+9+5 拆档 :83/:172/:443）
```

> ⚠️ deepwiki 同 commit 仍有 2 处失实（抽核实锤）：①§3.2 引 atari_wrappers 行号陈旧——称 NoopResetEnv:12/MaxAndSkipEnv:97/ClipRewardEnv:125，实测 **:62/:168/:213**（§5.2 同页系行号反而正确，deepwiki 子页索引快照不一致）；②§3.1 称 ppo_atari_multigpu 用 DDP 包装 agent（:218），实测**无 DDP**，改手写 `dist.all_reduce(all_grads)`（:367）。

## 五、深读子页地图（33 页归类 + 精选 10）

**归类**：入门 5（§1/2/2.1/2.2/2.3）·核心算法 6（§3/3.1-3.5）·JAX 3（§4/4.1/4.2）·环境 7（§5/5.1-5.6）·EnvPool 1（§6）·基准评测 4（§7/7.1-7.3）·云部署 3（§8/8.1/8.2）·工程治理 4（§9-12）。

- **§3.1 PPO**：7 变体矩阵（标准/Atari/连续/LSTM/多GPU/EnvPool/RPO）+ 超参全带行号出处——与 docs/ppo.md 的 37 细节档位互为索引。
- **§3.2 DQN**：4 变体对照（PyTorch/JAX×classic/Atari）+ "与原论文差异"节（Adam 替 RMSprop、target 更新 1k 替 10k）；⚠陈旧锚点页（见 §四注）。
- **§3.5 进阶算法**：六件套一页看全——PPG 双相训练/C51 分布投影/RPO 均匀噪声注入/QDagger 蒸馏/RND 内在奖励/PQN 去 target 网络用 LayerNorm+Q(λ)（pqn.py:95/:204）。
- **§4.2 EnvPool XLA**：全库性能天花板——环境步进进 XLA 计算图，`jax.lax.scan` 替 Python 循环，GAE 用 reverse scan（与 ppo.py:221 的 for 循环互为教学对照）。
- **§5.5 多智能体**：Conv2d(6,32)（:91）=4 帧堆叠+2 个 agent 指示通道，选择性归一化只除前 4 通道（:106）——共享策略区分玩家的最小技巧。
- **§5.6 Isaac Gym**：GPU 物理仿真 4096 并行 env（:73）+ num_steps=16（:75）→ 有效 batch 65,536；统计量全留 GPU 的 RecordEpisodeStatisticsTorch（:115）。
- **§7.3 Optuna**：设计哲学"一套超参管一类任务"（非逐任务过拟合）——target_scores 区间归一化跨环境聚合（tuner.py:51-54）。
- **§8.1 AWS Batch**：Terraform 六机型带时薪注释（main.tf:21-27），submit_exp 一条命令展开多种子作业——单人跑千实验的基建范本。
- **§9 测试**：测试即 subprocess 烟测（test_classic_control.py:4-9，256 步跑通即过）× 3 Python 版本×7 job=21 并行 CI——与"单文件无单测对象"哲学自洽。
- **§12 Glossary**：Single-file/Args/SPS 等术语表，新人第一站。

## 六、与"我们"的关系（一句话）

讲透RL 00→01→02→08 章每条公式的"标准答案脚本"就在 cleanrl——它与讲透实验同守"几秒跑通"哲学，是从 toy 直达文献级参考实现的最短跳板（rl_agent 想标准化时抄它的文件布局，而不是引入框架）。

---
生成：2026-08-20 · deepwiki 索引 2026-07-27（fe8d8a）+ 本地 180M 克隆@fe8d8a0 逐条 grep 实测（file:line 锚点 40+，纠 deepwiki 失实 2 处）
