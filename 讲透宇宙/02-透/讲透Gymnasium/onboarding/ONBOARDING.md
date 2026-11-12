# Gymnasium 新人上手文档（ONBOARDING）

> 基于知识图谱（1153 节点 / 2819 边 / 16 层 / 16 步导览，commit `8b22ad4a`，v1.4.0）自动生成，全部行号锚经源码核实。
> 仓库：`/usr-data/data1/workspace/rl/Gymnasium`（Farama-Foundation/Gymnasium）

## 1. 项目定位与一句话理解

**一句话**：Gymnasium 是强化学习（RL）算法与环境之间的标准通信 API 库——它不实现任何学习算法，只定义"环境长什么样"的契约，并附带一批符合该契约的标准环境。

README 第一段即钉明身份（`README.md:15`）：这是 OpenAI Gym 的维护者分支（fork）——OpenAI 数年前将 Gym 移交外部团队维护，Gymnasium 就是官方指定的后续演进地，也是"今后维护发生的地方"。配套论文 arXiv:2407.17032（NeurIPS 2025）将这套 API 学术化钉版。

生态地位的三点事实：① Stable-Baselines3、CleanRL、Tianshou 等主流 RL 训练库全部以 `gymnasium.Env` 为环境接口，事实标准；② 它是纯 Python 库，核心依赖仅 `numpy` 与 `cloudpickle`（`pyproject.toml:26-28`），物理引擎（Box2D/MuJoCo/JAX）全部走可选依赖组按需安装；③ 门面 `gymnasium/__init__.py:5` 汇出全部公开符号，版本号 1.4.0（`gymnasium/__init__.py:61`），Python >= 3.11（`pyproject.toml:11`）。

历史脉络值得一分钟：OpenAI Gym（2016）开创了"环境 API"范式但自 v0.21 后维护迟滞，2022 年维护团队接手分叉出 Gymnasium，由 Farama 基金会（一个专做 RL 开源基础设施的非营利组织）承接，姊妹项目还有多智能体环境的 PettingZoo 与离线数据集 Minari——三者共享同一套设计哲学：API 严格版本化、行为变更写进迁移文档、旧接口用兼容层缓冲而非静默更改。理解这条时间线就理解了 Gymnasium 的偏执：它对 API 稳定性的执着（每个 docstring 都标 `versionchanged`）源于亲历过 Gym 生态断裂的痛。

对新人最关键的心智模型：**这不是一个"框架"，而是一份契约 + 一座环境仓库**。读懂 `core.py` 与 `spaces/` 就读懂了 80% 的 Gymnasium，其余都是契约的实现者（环境）与装饰者（wrapper）。

## 2. 五分钟上手

```bash
pip install gymnasium          # 核心安装，零重依赖
```

```python
import gymnasium as gym

env = gym.make("CartPole-v1")  # 注册表查找 + 自动包装
observation, info = env.reset(seed=42)

for t in range(1000):
    action = env.action_space.sample()          # 随机策略
    observation, reward, terminated, truncated, info = env.step(action)

    if terminated or truncated:
        observation, info = env.reset()          # 回合结束必须 reset

env.close()
```

要点：① `reset` 只在开局与回合结束时调用，首次带 `seed` 定随机性；② `step` 返回五元组（第 4 节详解）；③ CartPole-v1 的注册项声明了 `max_episode_steps=500` 与 `reward_threshold=475.0`（`gymnasium/envs/__init__.py:27-32`），所以 500 步必触发 `truncated`。想看画面传 `gym.make("CartPole-v1", render_mode="human")`；想批量化用 `gym.make_vec("CartPole-v1", num_envs=8)`；想列出全部可用环境用 `gym.pprint_registry()`，或查单个环境规格 `gym.spec("CartPole-v1")`。上手机会成本极低是刻意设计：五个调用（make/reset/step/sample/render）覆盖 90% 使用场景，其余都是进阶件。

## 3. 架构总览（按 16 层图谱）

知识图谱把仓库切成 16 层，从工程地基到对外门面。逐层速览（层号即图谱层号）：

**L1 工程配置与社区治理**：`pyproject.toml` 定义包元数据、可选依赖组与 `ty` 类型检查配置；`.pre-commit-config.yaml` 挂风格钩子；`.github/workflows/` 下 8 条流水线（pytest 矩阵、三线文档构建、链接检查、pre-commit、教程运行、PyPI 发布）加上 issue/PR 模板与 dependabot，构成社区治理面。

**L2 核心契约与测试夹具**：`gymnasium/core.py` 是全仓心脏（Env 与 Wrapper 两大抽象基类），`error.py` 是以 `Error(Exception)` 为根的 20 个异常类层次，`logger.py` 是统一告警出口；`tests/testing_env.py` 的 `GenericTestEnv`（注入回调的可编程假环境）被全仓测试复用。

**L3 Spaces 体系**：`spaces/space.py:18` 的 `Space` 抽象基类派生 `Box`（`box.py:64`）、`Discrete`（`discrete.py:27`）、MultiBinary、MultiDiscrete 四大基础空间，加 Dict/Tuple/Graph/Sequence/Text/OneOf 组合空间；`spaces/utils.py:101,182,356` 的 `flatdim/flatten/unflatten` 用 singledispatch 按空间类型分发展平逻辑。

**L4 通用工具与校验**：`utils/` 横切工具箱——env_checker/passive_env_checker 校验环境合规，`step_api_compatibility.py` 兼容旧版四元组 step 返回，`seeding.py` 管随机性，`play.py` 支持键盘交互游玩，`save_video.py` 录像，`env_match.py` 环境对拍；`EzPickle`（`utils/ezpickle.py:6`）与 `RecordConstructorArgs`（`utils/record_constructor.py:9`）两个 mixin 支撑环境的 pickle 重建。

**L5 环境注册与发现**：`envs/registration.py` 实现 EnvSpec/WrapperSpec 与全局 registry，提供 register/make/make_vec/spec/pprint_registry（第 5 节深潜）；`envs/__init__.py` 以 63 个 `register()` 调用构成内置环境总目录——查"某 id 对应哪个文件"从这里入手。

**L6 玩具文本与表格环境**：toy_text 含 FrozenLake/Taxi/Blackjack/CliffWalking 四大经典 MDP（显式转移概率表+categorical_sample 采样），tabular 子包用 numpy 数组重写 Blackjack/CliffWalking 做表格法对照。零第三方依赖，教学与回归测试首选。

**L7 经典控制与 Phys2D**：classic_control 五将 CartPole/Pendulum/MountainCar（离散/连续）/Acrobot，pygame 渲染；phys2d 用纯 numpy 重写 CartPole/Pendulum 的函数式版本（state/reward 函数分离），为 JAX 实验线提供物理内核。

**L8 Box2D 物理环境**：LunarLander（`lunar_lander.py:79`，含连续动作版与风力扰动）、BipedalWalker（含 Hardcore 模式）、CarRacing 及独立的 car_dynamics 车辆动力学模型。需要 `pip install gymnasium[box2d]`。

**L9 MuJoCo 基础设施**：`mujoco_env.py:35` 的 `MujocoEnv` 基类统一 XML 加载、frame_skip 步进、从 actuator_ctrlrange 推导动作空间；`mujoco_rendering.py` 分离 OffScreen/Window 双渲染后端；`assets/` 下的 MJCF XML 模型是环境的"肉体"。

**L10 MuJoCo 环境实现**：11 个机器人环境各有 v4/v5 双代共 22 个文件（Ant/HalfCheetah/Hopper/Humanoid/Walker2d 等），演进范式高度一致（第 6 节详解）。

**L11 JAX functional 实验线**：`experimental/functional.py:21` 的 FuncEnv 把环境表达为纯函数集合，面向 jit/vmap 硬件加速；`envs/functional_jax_env.py:21` 适配回 gym.Env 契约。

**L12 变换类 Wrappers**：无状态、语义透明的数据改写——transform_observation 的 11 类（Filter/Flatten/Grayscale/Resize/Reshape/Rescale/Dtype/AddRender/Discretize 等）、transform_action（Clip/Rescale/Discretize）、transform_reward（Clip），像素管线积木。

**L13 有状态与生命周期 Wrappers**：`wrappers/common.py` 五大高频件（TimeLimit/Autoreset/PassiveEnvChecker/OrderEnforcing/RecordEpisodeStatistics）+ stateful_observation（Delay/TimeAware/FrameStack/Normalize/MaxAndSkip）+ stateful_action（StickyAction）+ rendering 录制线。

**L14 向量化执行**：`vector_env.py:49` 的 VectorEnv 契约与 `AutoresetMode` 枚举（:41，NEXT_STEP/SAME_STEP/DISABLED 三态）；`sync_vector_env.py:27` 串行版、`async_vector_env.py:56` 多进程管道并行版（含异常穿透）；`vector/utils/space_utils.py:51` 的 batch_space 把单环境空间批量升维。

**L15 向量化 Wrappers**：`wrappers/vector/` 下 14 个文件镜像普通 wrapper——VectorizeTransformObservation（:104）把单环境 wrapper 逐 sub-env 复用，array_conversion/jax_to_numpy/numpy_to_torch 做批量张量框架转换，common.py 的 RecordEpisodeStatistics（:23）跨 sub-env 追踪回合统计。

**L16 门面**：`gymnasium/__init__.py` 汇出一切（依赖图顶点，度 161 枢纽），`py.typed` 标记 PEP 561 类型随包分发，`wrappers/__init__.py:165` 用 PEP 562 `__getattr__` 对依赖 jax/torch 的转换类做懒加载。

纵观 16 层的依赖方向：L16 门面在最顶，L2 契约与 L3 空间被中间所有层引用，环境家族（L6-L10）依赖注册（L5）与契约（L2），wrapper 双体系（L12-L15）横切在契约之上——层次即依赖图的自然分层，没有循环。

一个必须钉版的勘误：图谱摘要把 `functional_jax_env.py` 归在 experimental/ 下，实际它在 `gymnasium/envs/functional_jax_env.py`；phys2d 与 tabular 也都在 `envs/` 子包内（`gymnasium/envs/phys2d/cartpole.py:13` 的 import 语句可证）。看代码时以文件系统为准。

## 4. 核心概念深潜

### 4.1 Env 契约：一个类规定整个生命周期

`core.py:28` 定义 `Env(Generic[ObsType, ActType])`，核心就四个方法与一组属性：

- **`step(action) -> (obs, reward, terminated, truncated, info)`**（`core.py:79-81`）：五元组是全库最核心的数据契约。`terminated` 指 MDP 意义上的终止态（进岩浆/达目标），`truncated` 指超出 MDP 范畴的截断（典型是时限）；二者语义分离正是为了 bootstrap 类算法能正确计算价值——若回合被截断，目标值应从价值函数 bootstrap 而非记为终态零。
- **`reset(*, seed=None, options=None) -> (obs, info)`**（`core.py:124-129`）：关键字限定传参。自定义环境 reset 首行必须 `super().reset(seed=seed)`（`core.py:139` 文档明确要求），它会在 `core.py:171` 调 `seeding.np_random(seed)` 完成播种。
- **`render()`/`close()`**：渲染由构造时的 `render_mode` 决定（None/human/rgb_array/ansi 及 `_list` 变体），`metadata["render_modes"]` 声明支持项；`render_fps` 约束与 dt 的一致性在 MuJoCo 基类里还有专门校验。
- **`np_random`**：惰性 PRNG，未播种时回退熵源初始化（`utils/seeding.py:10` 的 `np_random` 把整数 seed 规范化为 `(np.random.Generator, seed)` 元组）。播种语义很讲究：环境已有 PRNG 且 `seed=None` 时不重播——典型用法是"初始化后播一次，之后永不再播"。

契约违规有专属异常信号：`error.py` 的 20 个类覆盖 `ResetNeeded`（未 reset 就 step）、`InvalidAction`、`UnregisteredEnv` 三细分及异步向量的 `AlreadyPendingCallError` 等。异常类型如此细分不是炫技，而是让 wrapper 与上层库能程序化区分"用户用法错"与"环境实现错"。

### 4.2 Spaces：观测与动作的数学描述

每个 Env 携带 `observation_space` 与 `action_space`，二者都是 `Space`（`spaces/space.py:18`）实例。Space 的契约：`sample()` 采样、`contains(x)` 判属、`seed()` 播种、`shape/dtype` 元数据，另有 `to_jsonable/from_jsonable` 序列化接口与旧版 pickle 状态迁移。两大基石：`Box(low, high, shape)` 表示 R^n 闭区间笛卡尔积，连续动作/观测的主力（CartPole 的 4 维观测 [-4.8,4.8]×... 与 Pendulum 的 [-2,2] 扭矩动作都是它）；`Discrete(n)` 表示有限整数集，支持 `mask` 动作屏蔽采样与 `start` 偏移（`discrete.py:37,40`，如 `Discrete(3, start=-1)` 表示 {-1,0,1}），给非法动作约束留了原生口子。组合空间允许结构化观测：Dict（命名观测拼盘）、Tuple、Sequence（变长，适配 RNN）、Graph（图结构）、Text（LLM 类环境）、OneOf（异构动作空间并存）。`flatten`（`spaces/utils.py:182`）把任意空间元素压成一维向量喂给 MLP，`flatdim`（:101）算维度、`unflatten`（:356）逆变换——神经网络的输入输出形状全部由 Spaces 推导，这是该子系统存在的根本理由：**空间即环境与算法之间的类型系统**。

### 4.3 Wrapper：装饰器模式的环境流水线

`core.py:302` 的 `Wrapper` 继承 `Env` 并持有 `self.env`，默认全透传（step/reset/render/close 见 :338-344），子类按需覆写；`action_space/observation_space` 走"setter 缓存+未设则透传"模式，保证包装器局部改写不污染底层；`spec` property 会 deepcopy 并合并底层 spec，保证 `env.spec` 永远如实描述整条链。三个特化基类把覆写点收敛到单一方法：`ObservationWrapper.observation()`（`core.py:546`）、`RewardWrapper.reward()`（`core.py:590`）、`ActionWrapper.action()`（`core.py:625`）——写一个像素灰度化 wrapper 只需三行。全仓 30+ 个 wrapper 分两类：无状态变换（Grayscale/Resize/ClipReward 等）与有状态（`wrappers/common.py` 的 TimeLimit:43、Autoreset:174、PassiveEnvChecker:225、OrderEnforcing:371、RecordEpisodeStatistics:468；FrameStackObservation 在 `stateful_observation.py:305`；NormalizeReward 在 `stateful_reward.py:20`，其统计核 `RunningMeanStd` 在 `wrappers/utils.py:33`）。包装链可无限嵌套，`env.unwrapped` 一路剥到底。工程细节：继承 `RecordConstructorArgs` 的 wrapper 能把构造参数记进 spec、pickle 时可精确重建（这是 make 能校验 additional_wrappers 的前提）；环境侧则配 `EzPickle`（`utils/ezpickle.py:6`）按构造参数序列化，AsyncVectorEnv 跨进程传环境全靠这对组合。

### 4.4 注册体系：id 字符串如何变成类实例

`envs/registration.py` 维护全局 `registry`：`register()`（:563）把 id 与 `EnvSpec`（:72，dataclass 含 entry_point/max_episode_steps/order_enforce 等 19 个字段，`order_enforce=True`/`disable_env_checker=False` 两个默认值见 :99-100）绑定；`ENV_ID_RE`（:24）解析 `[namespace/](name)[-v(version)]` 格式；查不到时用 `difflib.get_close_matches` 给出 "Did you mean" 拼写建议（:342，namespace 打错也有单独建议 :339）；版本号省略时走候选匹配挑最新版。`env_spec.make(**kwargs)`（:120）给已持有 spec 的场景复用；`register_envs`（:548）支持整模块批量注册，第三方环境包的推荐姿势。惰性加载是关键设计：注册只存字符串 `entry_point="gymnasium.envs.classic_control.cartpole:CartPoleEnv"`，import 发生在 make 时——所以装了核心包不装 MuJoCo 也不会在 `import gymnasium` 时炸；id 里还能带未加载模块前缀（`"module:Env-v0"`），make 时才 importlib 拉起（:496）。

## 5. 一条数据的完整旅程：gym.make("CartPole-v1") 背后

1. **注册期**（import gymnasium 时）：`envs/__init__.py:27-32` 执行 `register(id="CartPole-v1", entry_point="gymnasium.envs.classic_control.cartpole:CartPoleEnv", vector_entry_point="...:CartPoleVectorEnv", max_episode_steps=500, reward_threshold=475.0)`，registry 里只存描述不 import cartpole 模块。
2. **查 spec**：`make()`（`registration.py:640`）拿字符串 id 调 `_find_spec`（:488），用 `ENV_ID_RE` 解析 name+version 精确匹配 registry；未带版本号会走候选查找。
3. **解析 creator**：`load_env_creator`（:533）把 `"module:Class"` 拆开，`importlib.import_module`（:543）真加载模块并 getattr 拿类。
4. **实例化**：`env = env_creator(**env_spec_kwargs)`（:738）——make 传的 kwargs 覆盖 spec 默认 kwargs。随后 :754 校验实例确为 `gymnasium.Env` 子类（还专门识别旧 gym 类给出迁移报错），并在 :770 给 `env.unwrapped.spec` 回填一个最小 spec。渲染模式有一段贴心分支：请求的 `render_mode` 不在环境声明列表里时（:712-735），`human` 请求会自动改用 rgb_array 并补挂 HumanRendering wrapper，`xxx_list` 请求会补挂 RenderCollection。
5. **默认包装链（由内向外三层）**：
   - `PassiveEnvChecker(env)`（:805）——除非 `disable_env_checker=True`，逐调用被动校验返回值与声明 space 一致；
   - `OrderEnforcing(env)`（:809）——`order_enforce` 默认 True（`EnvSpec` 字段默认值见 :99-100），保证 reset 先于 step；
   - `TimeLimit(env, 500)`（:812-816）——`max_episode_steps` 非 -1/None 时套上，spec 里的 500 生效。
   所以你拿到的 `env` 实为 `TimeLimit(OrderEnforcing(PassiveEnvChecker(CartPoleEnv)))` 套娃。此外 :818-824 还会按 `additional_wrappers` 把用户预先套过的 wrapper 用记录的构造参数逐一重建——spec 描述与实际链的一致性由此闭环。
6. **step 的五元组产生**：动作沿包装链向内透传到 `CartPoleEnv.step`（`cartpole.py:165`）——欧拉积分推物理、算 reward、`terminated = bool(...)` 判杆倒（:199）；返回途中被 TimeLimit 拦截：`_elapsed_steps >= _max_episode_steps` 时强置 `truncated = True`（`wrappers/common.py:133-134`）。OrderEnforcing 与 PassiveEnvChecker 各自完成秩序校验与数据形状检查后，五元组最终回到用户手上。回合结束后由用户手动 reset（单环境）——自动重置职责移到了 vector 侧的 AutoresetMode，普通环境可用 Autoreset wrapper（`common.py:174`）显式补上。
7. **向量化入口**：`make_vec`（`registration.py:835`）同链路，但优先用 `vector_entry_point`（CartPole 有原生向量化实现 `CartPoleVectorEnv`，免去 N 份 Python 对象），否则按 `VectorizeMode`（:245，sync/async/vector_entry_point 三态）用 Sync/AsyncVectorEnv 包 N 份副本。

## 6. 设计决策与取舍

**terminated/truncated 分离替代 done**：OpenAI Gym <v26 用单一 `done` + `info["TimeLimit.truncated"]` 补丁区分两种结束，语义含混导致 bootstrap 错误频发。Gymnasium v0.26 起拆为两个布尔（`core.py:87-91` 的 versionchanged 记载动机："critical for reinforcement learning bootstrapping algorithms"）。代价是五元组比四元组长一点、旧代码要迁移（`utils/step_api_compatibility.py` 提供兼容层），换来的是 off-policy 价值估计的正确性不再依赖用户读文档细心。

**v4→v5 演进逻辑**（MuJoCo 族范式）：奖励重构为 `_get_rew` 返回结构化分量字典（info 里可查 reward_forward/reward_ctrl 等，总分=sum）、新增 xml_file/frame_skip/default_camera_config 可配项、reset 噪声可调、v5 默认启用 contact 修正。这套演进的深层动机是可解释与可复现：奖励分解进 info 后，训练曲线异常时能逐分量归因，而不是对着一个标量黑盒猜。`tests/envs/mujoco/test_mujoco_v5.py` 把"分量求和=总分""v4→v5 行为差异逐项核对"做成回归测试，`utils/env_match.py:9` 的 `check_environments_match`（同 seed 同动作序列比对两环境）正是这类版本演进的验收器。

**vector 与普通 wrapper 双体系**：`VectorEnv`（`vector/vector_env.py:49`）与 `Env` 是平行契约而非继承——批量观测是 `(num_envs, *space.shape)` 的堆叠数组，属性分 `single_observation_space`（子环境）与 `observation_space`（批空间）两层。于是 `wrappers/` 与 `wrappers/vector/` 镜像两套：普通版 TransformObservation 与向量版 VectorizeTransformObservation（`wrappers/vector/vectorize_observation.py:104`，内部用假环境逐 sub-env 复用单环境 wrapper）。双体系的代价是维护翻倍，收益是单环境语义可无损升维到批量轴。

**JAX functional 实验线**：`experimental/functional.py:21` 的 `FuncEnv` 把环境重新表达为纯函数集合（initial/transition/observation/reward/terminal，:55-82），状态作为显式参数传入传出，天然适配 `jax.jit/vmap` 硬件加速。`envs/functional_jax_env.py:21` 的 `FunctionalJaxEnv` 负责把函数式后端适配回 `gym.Env` 契约（:103 再加向量化版）。样板是三层：flax 参数集（可域随机化）+ FuncEnv 纯函数 + JaxEnv 包装（`envs/phys2d/cartpole.py:49`）。放在 experimental/ 而非正式 API，明示这是试错田。

**API 版本演进的节奏感**：v1.0 是分水岭——`make` 的 `autoreset` 与 `apply_api_compatibility` 参数被移除（`registration.py:596,667` 的 versionchanged 记载），自动重置收口到 vector 体系的 AutoresetMode，旧 gym 四元组兼容收口到独立工具函数；此后每个行为变更都走"文档标注+兼容层缓冲+大版本号递进"三件套。另一条暗线是双 numpy 兼容：CI 同时跑 numpy 1.x 与 2.x 矩阵（`run-pytest.yml:14`），源码里随处可见的 `np.integer[Any]` 泛型标注就是为此付出的代价。渲染 API 也换代过：渲染模式从"step 后调 render(mode=...)"改为构造期 `render_mode` 参数决定，人机渲染与 rgb 阵列渲染分流，这解释了为什么 make 里要有一整段 render_mode 修补分支。

**收束边界**：`CONTRIBUTING.md:10` 明言不再接受新环境贡献——库定位从"环境大合集"收束为"API 标准+精选环境集"，新环境应去独立仓库（Farama 生态）发展。核心依赖极简（numpy/cloudpickle）配合 entry_point 惰性导入，保证 `pip install gymnasium` 秒装且不拖物理引擎。

## 7. 测试与质量闸

**三道 checker 防线**：① `utils/env_checker.py:406` 的 `check_env`（源自 Stable Baselines3）——侵入式串联 reset/step 检查确定性、seed 后 RNG 状态一致、返回数据不复用（防 buffer 别名 bug，契约见 `core.py:118-120` Note）等，自定义环境对接 Gymnasium 的标准验收工具；② `utils/passive_env_checker.py`——被动路线，不改数据逐调用校验（`check_obs` 分发器在 :131），正是 make 默认挂载那层 wrapper 的内核；③ `utils/env_match.py:9`——环境对拍，版本演进验收专用。

**测试规模**：全仓 266 个 Python 文件中 `tests/` 占 125 个，约 383 个测试函数，与源码文件数（121）基本 1:1。基础设施高度复用：`tests/testing_env.py` 的 `GenericTestEnv`（注入回调的可编程假环境）与 `tests/spaces/utils.py` 的 23 个基础空间+组合空间测试矩阵，被 20+ 个测试文件参数化共享。

**CI 矩阵**：`run-pytest.yml:13-14` 用 Docker 跑 Python 3.11/3.12/3.13/3.14 × numpy 1.x/2.x 全量测试（排除不可行组合），numpy>=2.1 还加跑 doctest——docstring 里的示例代码本身是可执行测试；另有链接检查、三线文档构建（开发版/发布版/手册）、pre-commit、教程运行与 PyPI 发布共 8 条流水线。pre-commit 挂四组钩子（通用检查、codespell 拼写、ruff 检查+格式化、`ty` 类型检查，见 `.pre-commit-config.yaml:4-51`），配合 `py.typed` 标记的类型分发，静态质量与运行时质量双轨并行。质量闸外化到工具而非口头约定，是本仓最值得借鉴的工程习惯。

## 8. 深入路线图（按 16 步导览给三条路径）

16 步 tour 的顺序本身是官方推荐的阅读线：门面(1)→核心契约(2)→Spaces(3)→注册(4)→classic_control(5)→toy_text(6)→Box2D(7)→MuJoCo 地基(8)→MuJoCo 实现(9)→JAX functional(10)→变换 wrapper(11)→有状态 wrapper(12)→vector 引擎(13)→vector wrapper(14)→质量闸(15)→工程 CI(16)。按角色裁剪：

**算法工程师路径（用环境）**：1→2→3→4 打底（契约与注册），5→6 挑 CartPole/FrozenLake 读懂 obs/reward 语义，12（TimeLimit/RecordEpisodeStatistics/NormalizeReward 直接影响训练正确性）、13（Sync/AsyncVectorEnv 决定采样吞吐）。重点文件：`core.py`、`wrappers/common.py`、`vector/sync_vector_env.py:27`（最易读的向量化参考实现，`envs = [env_fn() for env_fn in env_fns]` 在 :112）。练手任务：给 CartPole 套 `TimeLimit + RecordEpisodeStatistics + NormalizeObservation` 三层链，打印回合回报曲线；再用 `gym.make_vec` 起八环境对比 Sync/Async 吞吐差异，你会直观撞上 `_add_info`（`vector_env.py:284`）的批量 info 聚合问题。

**环境开发者路径（写环境）**：2→3（契约与空间必考），5 精读 `cartpole.py`（一个标准 Env 的完整范本：物理积分、reset 随机化、terminated 判定、原生向量化），6 看 toy_text 的"显式转移概率表+采样"写法，8→9 学 `MujocoEnv` 基类（`mujoco_env.py:35`：XML 加载、frame_skip、actuator_ctrlrange 推导动作空间）与 v5 范式，15 用 `check_env` 自验。Box2D 线的 `lunar_lander.py:79` 附带 heuristic 专家策略（:791）可做 sanity check。练手任务：实现一个 GridWorld 环境，规定好 observation_space/action_space/metadata，reset 首行 `super().reset(seed=seed)`，跑 `check_env` 拿到全绿——这一套走通，你的环境就能被整个 RL 生态直接消费。

**贡献者路径（改库本身）**：1→16 先看工程面（依赖策略、CI 矩阵、贡献边界），2 读 `core.py` 全文与 `error.py` 异常层次，11→12→13→14 把双 wrapper 体系与 vector 引擎吃透（这是 PR 高发区），15 理解质量闸如何守护 API 演进。注意 `CONTRIBUTING.md` 的边界：bug 修复、wrapper 增强、文档欢迎，新环境不收。练手任务：从给 `tests/` 补一个 wrapper 边界用例起步（`tests/wrappers/utils.py` 的记录型回调夹具现成可用），再读一个历史 PR 体会"行为变更必须带 versionchanged 标注"的库规。

三条路径殊途同归的终点都是第 2 步的 `core.py`——Gymnasium 的一切设计，都是为了让这份几百行的契约被整个 RL 生态无条件信任。新人最常见的两个坑也顺便钉版：一是回合结束忘记 reset 就继续 step，会被 OrderEnforcing 抛 `ResetNeeded` 拦下（这是保护不是故障）；二是把 `terminated` 当成"回合结束"单条件用，漏掉 truncated 导致 off-policy 目标值算错——五元组里两个布尔一个都不能省。

---
*生成于 2026-10-14，知识图谱 commit 8b22ad4a（v1.4.0）。*
