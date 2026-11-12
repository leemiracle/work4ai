# Stable-Baselines3（SB3）新人 Onboarding

> 仓库：`/usr-data/data1/workspace/rl/stable-baselines3`（DLR-RM/stable-baselines3@b2878f4，v2.9.2a0）。包内路径相对 `stable_baselines3/`，docs/tests 等相对仓库根；`file:line` 锚均经 grep 核实。

## ① 这个项目是什么 / 为什么存在

SB3 是 PyTorch 强化学习算法的"可靠实现集"（JMLR 2021 论文对应库）。RL 论文代码长期难复现，SB3 用**统一、经测试、文档齐全**的实现消灭之，API 是 sklearn 风格三段式：

```python
model = PPO("MlpPolicy", "CartPole-v1").learn(10_000)
action, _ = model.predict(obs)
```

主仓六大算法——on-policy A2C/PPO、off-policy DQN/TD3/DDPG/SAC——外加 HER（`her/`）。生态：RL Zoo 训练/调参、SB3-Contrib 实验算法、SBX 是 Jax 版。SB3 刻意只做算法库。

## ② 全景架构：12 层地图

图谱（634 节点/1681 边）分 12 层，主线：**用户 API→算法→基类骨架→网络/Buffer→运行时→VecEnv→工程**。

| # | 层 | 文件 | 职责 |
|---|---|---|---|
| 1 | 算法实现层 | 24 | a2c/ppo/dqn/td3/ddpg/sac/her 七包+顶层 `__init__.py` |
| 2 | 基类与缓冲区 | 5 | base_class、on/off_policy_algorithm、buffers、save_util |
| 3 | 策略网络与分布 | 5 | policies、torch_layers、distributions、noise 等 |
| 4 | 运行时支撑 | 10 | callbacks、logger、monitor、utils、sb2_compat 等 |
| 5 | 环境工具 | 7 | env_util、env_checker、atari_wrappers、envs/ |
| 6 | 向量化环境 | 15 | vec_env/（Dummy/Subproc 后端+8 种 wrapper） |
| 7-9 | 文档三层 | 51 | guide 22、API 18、docs 基建 11 |
| 10 | 测试套件 | 31 | tests/ 30 个 test_*.py |
| 11 | CI/CD 与容器 | 16 | ci.yml、Makefile、Dockerfile、scripts/ |
| 12 | 项目治理 | 8 | README、pyproject.toml、setup.py 等 |

**算法类只填"损失+超参"两个洞：骨架来自第 2 层、构件第 3 层，环境交互必经第 6 层 VecEnv**；余为横切与工程层。

## ③ 核心抽象

四条脊柱：

1. **算法脊柱**：`BaseAlgorithm`（`common/base_class.py:67`）统一 learn/predict/save/load，派生两支：`OnPolicyAlgorithm`（`common/on_policy_algorithm.py:21`，rollout 采集→整批更新）与 `OffPolicyAlgorithm`（`common/off_policy_algorithm.py:27`，train_freq 定交互/更新频率+replay buffer 生命周期）。算法类很薄：`PPO.train()` 在 `ppo/ppo.py:184`。
2. **策略脊柱**：`BaseModel(nn.Module)`（`common/policies.py:39`）管序列化/设备，`BasePolicy`（:280）定义 predict，`ActorCriticPolicy`（:416）组装"特征提取器+`MlpExtractor` 双流+分布头"。提取器在 `common/torch_layers.py`（`MlpExtractor:184`、Dict 观测用 `CombinedExtractor:264`）。SB3 的"policy"实指含 actor/critic/target 网络与 optimizer 的容器。
3. **VecEnv 家族**：`VecEnv`（`common/vec_env/base_vec_env.py:50`）定义 step_async/step_wait 协议；`DummyVecEnv`（`common/vec_env/dummy_vec_env.py:15`）串行、`SubprocVecEnv`（`common/vec_env/subproc_vec_env.py:79`）每环境一 worker；`VecEnvWrapper`（:360）之上叠 VecNormalize 等四种 wrapper。**关键心智：SB3 内部一切环境都是 VecEnv，obs 永远带 batch 维**。
4. **Buffer 家族**（`common/buffers.py`）：`BaseBuffer:27`→on-policy 用 `RolloutBuffer:343`（GAE 在 `compute_returns_and_advantage:403`）；off-policy 用 `ReplayBuffer:158` 及 `DictReplayBuffer:525`。HER 的 `HerReplayBuffer`（`her/her_replay_buffer.py:15`）是 DictReplayBuffer 子类——不是算法。

## ④ 一次训练的生命周期（learn() 数据流）

以 `PPO(...).learn(10_000)` 为例：

1. **构造**：`_setup_model()`（`ppo/ppo.py:173`）建 RolloutBuffer 与 ActorCriticPolicy。
2. **learn 入口**：`BaseAlgorithm.learn`（`common/base_class.py:512`）→`_setup_learn()`（:383）把 gym.Env 自动包成 Monitor+DummyVecEnv，初始化 callback/logger。
3. **采样**：`collect_rollouts`（`common/on_policy_algorithm.py:162`）推进 n_steps：policy.forward 出动作/价值/log_prob→buffer.add 写入；回调 `_on_step()` 可返回 False 终止。
4. **GAE**：`compute_returns_and_advantage`（`common/buffers.py:403`）用 value 残差递推优势与回报。
5. **更新**：`PPO.train()`（`ppo/ppo.py:184`）按 epoch×minibatch：ratio→clipped surrogate loss→clip_grad_norm→step；approx_kl 超 target_kl 早停。回到 3 循环，dump_logs 输出 ep_rew_mean（来自 Monitor）。

Off-policy 变体：采样换 `collect_rollouts`（`common/off_policy_algorithm.py:526`），每步经 `_store_transition`（:461）入库；更新按 train_freq 触发 `train()`（learn 在 :324），采样+polyak 软更新 target 网络。探索：DQN 用 LinearSchedule 做 epsilon 衰减（`dqn/dqn.py:155`），TD3/DDPG 靠外部噪声（`common/noise.py:28/:50`），SAC 靠分布采样。

## ⑤ 目录导航（按需找文件）

- **改/加算法**：对应算法包（算法类+policies.py 两文件）；A2C/PPO 策略实为 `common/policies.py` 的 ActorCritic 系，TD3/SAC 才自带。改骨架去 on/off_policy_algorithm.py。
- **改网络**：`common/torch_layers.py`+`docs/guide/custom_policy.md`；分布头→`common/distributions.py`（`make_proba_distribution:670` 按动作空间选型）。
- **改环境**：`make_vec_env`（`common/env_util.py:40`）一行建环境；自定义环境先过 `check_env`（`common/env_checker.py:467`）；归一化→vec_env/vec_normalize.py。
- **加 callback**：继承 `BaseCallback`（`common/callbacks.py:31`）覆写 `_on_step`；现成的 `CheckpointCallback:245`、`EvalCallback:342`；文档 `docs/guide/callbacks.md`。
- **改保存格式**：`common/save_util.py`。**查默认签名**：`docs/modules/` autodoc。

## ⑥ 测试与质量体系

tests/ 31 个文件五道防线：①端到端冒烟——`test_run.py`、`test_identity.py`；②行为回归——`test_deterministic.py`（同 seed 两次训练奖励序列逐元素一致）、`test_train_eval_mode.py`；③持久化——`test_save_load.py`（924 行）；④数值——`test_distributions.py`（KL 解析值对拍）、`test_gae.py`、`test_n_step_replay.py`；⑤子系统矩阵——`test_vec_envs.py`、`test_her.py`。CI（`.github/workflows/ci.yml`，Python 3.10-3.13）跑 lint/type/pytest；配置在 `pyproject.toml`，本地入口 `scripts/run_tests.sh`。改核心代码前先读对应 test——API 契约的可执行规约。

## ⑦ 深水区预警（已勘误的坑）

1. **HER 是 buffer 不是算法**：`from stable_baselines3 import HER` 抛 ImportError（shim 在 `stable_baselines3/__init__.py:18`）；正确用法 `replay_buffer_class=HerReplayBuffer` 配 off-policy 算法+MultiInputPolicy，环境须实现 GoalEnv 协议（compute_reward+三键 Dict 观测），模型加载必须带环境（`set_env:124` 要求 VecNormalize 反归一化）。重标注在 `sample:186`：real+virtual 拼接，把 desired_goal 换成实际达成的 goal 重算奖励（`_get_virtual_samples:287`）；续训前须 `truncate_last_trajectory:386`。
2. **DDPG 是 TD3 特例**：`class DDPG(TD3)`（`ddpg/ddpg.py:14`），训练循环全复用。精确措辞：不是 `target_policy_noise=0`（TD3 校验要求 >0），而是 `target_noise_clip=0.0`（:108）使噪声失效+`policy_delay=1`（:107）+`n_critics=1`（:114）。
3. **save/load 的 excluded_save_params**：`common/base_class.py:303` 把 policy/device/env/replay_buffer/_vec_normalize_env/_logger 从 JSON 剔除——经 torch.save 存 pth 或重建；replay buffer 默认不保存，须单独 `save_replay_buffer`（`common/off_policy_algorithm.py:229`）。
4. **VecNormalize 的 pickle 工作流**：`__getstate__`（`common/vec_env/vec_normalize.py:128`）剥离 venv，加载必须 `VecNormalize.load(path, venv)`（:311）重挂环境；评估前须 `sync_envs_normalization`（`common/vec_env/__init__.py:56`）同步统计，否则评估有偏。
5. **sb2_compat 兼容层**：PyTorch 与 TF 的 RMSprop 数值行为不同（epsilon 位置等），SB2 老模型续训须换 `RMSpropTFLike`（`common/sb2_compat/rmsprop_tf_like.py:8`）。
6. **其他坑**：off-policy 的 timeout 处理依赖 `handle_timeout_termination`（`common/off_policy_algorithm.py:258`，自定义 buffer 缺此属性会静默置 False）；图像 uint8 [0,255] 由 CNN 自动归一化，通道序靠 VecTransposeImage 兜底；ep_rew_mean 无 Monitor 时不出。

## ⑧ 上手路线：3 天计划（按 16 步 tour）

**Day 1（会用）**：步 1-2——`README.md`+`docs/guide/quickstart.md` 跑通 CartPole，啃 `common/base_class.py` 与 `docs/guide/developer.md`。动手：换 SAC/TD3 跑 PyBullet。

**Day 2（懂内部）**：步 3-8 顺序读源码：on-policy 数据流→A2C/PPO→DQN→TD3/SAC/DDPG→网络结构→分布与噪声，对比三个 train() 差异。动手：写 callback 打印梯度范数。

**Day 3（能扩展）**：步 9-16——VecEnv 协议与 wrapper、监控闭环、save/导出、HER 深水区、env_checker、测试与 CI。动手：自定义环境过 check_env→接 HER 训练→save/eval/ONNX 全链。下一步指向 RL Zoo。

---

<!-- metadata: chars_no_space=6000; file:line_anchors=27; repo=stable-baselines3@b2878f4 v2.9.2a0; graph=634n/1681e/12L/16tour; generated=2026-10-14 -->
