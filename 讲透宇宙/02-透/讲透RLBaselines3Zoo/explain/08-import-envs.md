# 08 · 可选依赖的动态注册：rl_zoo3/import_envs.py 与 --gym-packages 联动

## ① 角色定位

`rl_zoo3/import_envs.py` 全文仅 73 行，却是 zoo「一包支持几十种环境」的关键设计。核心张力：zoo 想开箱支持 pybullet / Atari / highway-env / minigrid / panda-gym 等一堆环境后端，但这些包个个重（物理引擎、ROM、mujoco 依赖），绝不可能全部进 `install_requires`。这个文件是解法的前半——**内置白名单 best-effort 注册**：模块顶层 8 个 `try/except ImportError` 块逐个尝试 import，装了就借 import 副作用完成 gymnasium 注册，没装就静默跳过，zoo 本体照常工作。后半是 `--gym-packages` CLI 参数，把注册面开放给用户运行时注入任意第三方环境包。

文件里唯一**无条件执行**的注册逻辑在末尾：为 6 个经典控制环境注册 `*NoVel` 变体（速度信息置零的部分可观测版本），专门服务 RecurrentPPO（ppo_lstm）调参。

## ② 内部结构

**头部导入**（`rl_zoo3/import_envs.py:1-7`）：`register`/`register_envs` 来自 `gymnasium.envs.registration`（`rl_zoo3/import_envs.py:5`），`MaskVelocityWrapper` 来自 `rl_zoo3.wrappers`（`rl_zoo3/import_envs.py:7`）。

**8 个可选包的 try/except 块**（每个 3-9 行）：

| 包 | 行号 | 备注 |
|---|---|---|
| `pybullet_envs_gymnasium` | `rl_zoo3/import_envs.py:9-12` | 纯 import，注册在包自身 `__init__` 里完成 |
| `ale_py` | `rl_zoo3/import_envs.py:14-20` | 唯一显式调 `gym.register_envs(ale_py)`（`rl_zoo3/import_envs.py:18`），源码注释 `# no-op`（`rl_zoo3/import_envs.py:17`）——当前 import 已自动注册，显式调用是 Gymnasium 1.x 推荐写法的前向兼容防御 |
| `highway_env` | `rl_zoo3/import_envs.py:22-30` | 唯一带 `else` 分支：import 成功后执行 numpy 热修 `np.float = np.float32`（`rl_zoo3/import_envs.py:26-30`）——numpy 1.24 移除了 `np.float` 别名，highway_env 仍引用，不补这行 import 即崩 |
| `custom_envs` | `rl_zoo3/import_envs.py:32-35` | |
| `gym_donkeycar` | `rl_zoo3/import_envs.py:37-40` | |
| `panda_gym` | `rl_zoo3/import_envs.py:42-45` | |
| `rocket_lander_gym` | `rl_zoo3/import_envs.py:47-50` | |
| `minigrid` | `rl_zoo3/import_envs.py:52-55` | |

两种写法值得注意：纯 `except ImportError: pass`（如 `rl_zoo3/import_envs.py:11-12`）与 `pass` + `else:` 热修（`rl_zoo3/import_envs.py:26-30`）——else 分支保证 numpy 只在 highway_env 确实存在时才被 import。**只捕 ImportError**：装了但损坏（如 numpy ABI 冲突抛其他异常）不会被静默吞掉，而是如实崩溃，这是有意的取舍。

**NoVel 注册**（`rl_zoo3/import_envs.py:58-73`）：

- 工厂 `create_no_vel_env(env_id)`（`rl_zoo3/import_envs.py:59-65`）返回闭包 `make_env(render_mode=None)`：`gym.make(env_id)` 后立即包 `MaskVelocityWrapper`（`rl_zoo3/import_envs.py:61-63`）；
- 注册循环遍历 `MaskVelocityWrapper.velocity_indices` 的全部键（`rl_zoo3/import_envs.py:68`），`env_id.split("-v")` 拆名字与版本（`rl_zoo3/import_envs.py:69`），`register(id=f"{name}NoVel-v{version}", entry_point=...)` 注册派生 id（`rl_zoo3/import_envs.py:70-72`）；
- 数据源是 `rl_zoo3/wrappers.py:309-316` 的 `velocity_indices` 类字典，硬编码 6 个环境及其观测中速度分量下标：CartPole-v1（`[1,3]`）、MountainCar-v0 / MountainCarContinuous-v0（`[1]`）、Pendulum-v1（`[2]`）、LunarLander-v3 / LunarLanderContinuous-v3（`[2,3,5]`）。

## ③ 外部连接

**被谁 import（清一色副作用导入）**：`rl_zoo3/train.py:16`、`rl_zoo3/enjoy.py:13`、`rl_zoo3/exp_manager.py:51`、`rl_zoo3/push_to_hub.py:22`——全部带 `# noqa: F401`，import 即执行注册，不引用任何符号。入口 `rl_zoo3/__init__.py:3` 先于一切执行 `import rl_zoo3.gym_patches`（TimeLimit 补丁，docstring 自述「notably TimeLimit wrapper and Pybullet envs」，`rl_zoo3/gym_patches.py:1-4`），再导入 utils——补丁先行，注册在后，次序有讲究。

**`--gym-packages` 联动链**（grep 实证）：

- `rl_zoo3/train.py:115-120` 定义参数（`nargs="+"`，help 明言 "Additional external Gym environment package modules to import"）；
- `rl_zoo3/train.py:171-172` 主流程开头逐个 `importlib.import_module(env_module)`——用户包借自身 import 副作用注册；
- `rl_zoo3/enjoy.py:57-62` 定义、`rl_zoo3/enjoy.py:79-80` 同构循环；
- 注册完成后 `rl_zoo3/train.py:175-183` 查 `gym.envs.registry`，未命中用 `difflib.get_close_matches` 给出「你是不是想打 XXX」的纠错提示（`rl_zoo3/train.py:180`）；
- 与 utils 的耦合点：`create_test_env` 在父进程先 `gym.spec(env_id)` 落定 spec、再以 `make_env` 闭包传给子进程（`rl_zoo3/utils.py:249-255`，注释明言 "when the registry was modified with `--gym-packages`"，引 imitation PR 160）；训练侧同构代码在 `rl_zoo3/exp_manager.py:687-695`。原因：`--gym-packages` 的注册发生在运行时，子进程（尤其 spawn 模式）不会重放这段逻辑，捕获 spec 对象而非事后查表即可免疫。

**安装面**（pyproject.toml 实证）：8 个包里只有 2 个真在 extras 里——`pybullet_envs_gymnasium>=0.6.0`（`pyproject.toml:61`）与 tests extra 的 `highway-env`（`pyproject.toml:56`）；`panda-gym~=3.0.1` 被注释掉，备注 "need to upgrade to gymnasium"（`pyproject.toml:69`）；`custom_envs` / `gym_donkeycar` / `rocket_lander_gym` 不属于任何 extra，纯用户自装。注册尝试零成本，装了就用。

**NoVel 消费者**：`hyperparams/ppo_lstm.yml` 六个键——`PendulumNoVel-v1`（`hyperparams/ppo_lstm.yml:26`）、`CartPoleNoVel-v1`（`:49`）、`MountainCarNoVel-v0`（`:71`）、`MountainCarContinuousNoVel-v0`（`:83`）、`LunarLanderNoVel-v2`（`:163`）、`LunarLanderContinuousNoVel-v2`（`:182`）。

## ④ 数据流

**全链示例**：`rl_zoo3 train --algo ppo_lstm --env PendulumNoVel-v1 -f logs/`

1. import `rl_zoo3` → `rl_zoo3/__init__.py:3` 先打 gym_patches（TimeLimit 行为回退）；import `rl_zoo3.train` → `rl_zoo3/train.py:16` 触发 `import_envs`：8 个 try/except 按本机安装情况尽力注册 + 6 个 NoVel id 写入 `gym.envs.registry`；
2. `parse_args` 后若有 `--gym-packages my_envs`，`rl_zoo3/train.py:171-172` import 用户模块，注册表再扩；
3. `rl_zoo3/train.py:175-183` 校验 `PendulumNoVel-v1` 在表中（其 entry_point 是 `create_no_vel_env("Pendulum-v1")` 生成的闭包）；
4. `ExperimentManager` → `gym.spec` 解析出该闭包（父进程落定，`rl_zoo3/exp_manager.py:687-695`）→ `make_vec_env` 每个子环境调 `gym.make("Pendulum-v1")` 再包 `MaskVelocityWrapper`（`rl_zoo3/import_envs.py:61-63`）；
5. wrapper 按查表结果把观测第 2 维（角速度）置 0：`self.mask[velocity_indices[env_id]] = 0.0`（`rl_zoo3/wrappers.py:327`），`observation * mask`（`rl_zoo3/wrappers.py:332`）——环境从 MDP 变 POMDP，策略被迫靠记忆（LSTM）估计速度，这正是 RecurrentPPO 的调参场景；
6. 未查到的 env id 抛 `NotImplementedError`（`rl_zoo3/wrappers.py:328-329`）——即 MaskVelocityWrapper 只服务表内 6 环境，NoVel 注册循环与能力表严格同源，不会产生裸注册。

**静默降级路径**：没装 pybullet 时 `import pybullet_envs_gymnasium` 抛 ImportError → `pass`（`rl_zoo3/import_envs.py:11-12`）→ 用户跑 pybullet 环境 id 时才在 `rl_zoo3/train.py:176-183` 收到 "not found in gym registry, you maybe meant ..."——错误从 import 期推迟到使用期，且带着拼写纠错。

## ⑤ 设计决策

1. **静默降级而非硬依赖**：`except ImportError: pass` 让 `pip install rl_zoo3` 保持轻量；代价是「没装」与「拼错名字」同症，全靠 `rl_zoo3/train.py:180` 的 difflib 纠错兜底——把失败推迟到信息最充分的时刻（用户点名要某个 env 时）才报。
2. **顺着 gym 生态惯例**：环境包在自身 `__init__` 里调 `register` 是 gym/gymnasium 的标准副作用模式，zoo 只需 best-effort import 白名单即可白嫖全部注册逻辑；ale_py 块额外显式 `register_envs`（`rl_zoo3/import_envs.py:18`）是对新式显式注册 API 的对冲（源码注释 `no-op` 自证当前冗余）。
3. **热修隔离在 else 分支**（`rl_zoo3/import_envs.py:26-30`）：`np.float` 别名只补在 highway_env 确实存在时，不污染无 highway_env 机器的 numpy 命名空间；`np.float = np.float32` 而非 `float` 是贴近旧语义（np.float 曾是内置 float 的别名，但 highway_env 上下文里 float32 是安全选择）。
4. **NoVel 用 callable entry_point 而非字符串**：`"module:attr"` 字符串无法表达「按 env_id 参数化的包装」，工厂+闭包（`rl_zoo3/import_envs.py:59-65`）是唯一自然写法；配合 spec 父进程捕获（`rl_zoo3/utils.py:249`），在 Linux fork 的 SubprocVecEnv 下安全。
5. **能力表单一事实源**：`velocity_indices`（`rl_zoo3/wrappers.py:309`）同时驱动「wrapper 能掩哪些环境」与「注册哪些 NoVel id」（`rl_zoo3/import_envs.py:68`），加新环境只改一处、两处能力自动同步——但注意 yml 不在此列（见⑥）。
6. **panda_gym 注册保留、依赖注释**（`rl_zoo3/import_envs.py:42-45` vs `pyproject.toml:69`）：try/except 的语义就是「装了就用，没装不碍事」，与 extras 是否安装彻底解耦。

## ⑥ 新人提示

- **读码入口**：本文件 5 分钟可读完，先看 8 个 try/except 感受模式，再细读 `create_no_vel_env` 工厂与注册循环（`rl_zoo3/import_envs.py:59-73`），最后跳去 `rl_zoo3/wrappers.py:300-333` 看 MaskVelocityWrapper 本体。
- **新增环境包三步**：加一个 try/except 块 → （可选）在 pyproject.toml extras 加依赖 → 在 hyperparams yml 写调参块。别忘了 README 的环境列表也要同步。
- **版本漂移坑（本仓实证）**：`rl_zoo3/wrappers.py:314-315` 已升到 `LunarLander-v3`/`LunarLanderContinuous-v3`，注册循环因此只会注册 `LunarLanderNoVel-v3`；但 `ppo_lstm.yml:163,182` 仍写着 `LunarLanderNoVel-v2`/`LunarLanderContinuousNoVel-v2`——这两个键现在跑 `rl_zoo3 train --env LunarLanderNoVel-v2` 会在 `rl_zoo3/train.py:183` 直接 not found（difflib 大概会建议 v3）。教训：改 `velocity_indices` 的 env id 时，`import_envs.py` 自动跟随，**hyperparams yml 必须手动同步**。
- **排查「env not found」**：先跑 `python -c "import rl_zoo3.import_envs, gymnasium as gym; print([k for k in gym.envs.registry if 'NoVel' in k])"` 看注册表实际内容，再查包是否装对（`pip show pybullet_envs_gymnasium`）。自定义环境走 `--gym-packages your.pkg.module`，模块 import 时必须触发注册。
- **只捕 ImportError 是特性**：环境包装了但 import 半路抛非 ImportError（版本冲突、缺 so 文件）会让 zoo 直接崩——这是刻意设计，静默吞掉真 bug 比崩溃更糟；排查这类崩溃先看 traceback 是不是来自 try 块内部。
- **平台注意**：callable entry_point + 闭包 make_env 在 spawn 启动方式（Windows/macOS 的 subprocess 默认）下可能 pickle 失败；zoo 主力场景是 Linux（fork），遇跨平台问题优先检查 vec_env 启动方式。

<!-- chars(no-space): 7247, anchors: 66 -->
