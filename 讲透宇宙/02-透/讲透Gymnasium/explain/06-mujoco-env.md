# 06 · MujocoEnv 精讲：MuJoCo 全族的公共骨架

> 源码版本：main @ 8b22ad4；主文件 `gymnasium/envs/mujoco/mujoco_env.py`（229 行），兼及 `mujoco_rendering.py`（848 行）与子类样例 `ant_v5.py`/`reacher_v5.py`。
> 行号锚格式 `mujoco_env.py:L行号`，交叉文件锚单独标明文件名，全部从当前源码核实。

## 一、角色定位

MuJoCo 是 Gymnasium 最大的环境家族：`envs/mujoco/` 下 9 个环境各出 v4/v5 两代共 18 个实现文件，外加 `assets/` 里 14 个 MJCF XML 模型。这 18 个文件没有一个是"从零写的环境"——它们全部继承同一个基类 `MujocoEnv`（mujoco_env.py:L35）。这个 229 行的抽象基类把 MuJoCo 物理引擎的完整生命周期（模型加载、状态重置、步进仿真、渲染委托）收拢为公共骨架，子类只负责填领域语义：奖励怎么算、怎样算健康、观测挑哪些维度。

架构上是教科书级的**模板方法模式**（Template Method）：`reset()`（mujoco_env.py:L172-187）在基类里定死流程——`mj_resetData` 清场、调子类 `reset_model()` 撒噪声、`_get_reset_info()` 组 info——子类只覆盖中间的钩子；而 `step()`（mujoco_env.py:L213-216）干脆 `raise NotImplementedError`，因为各环境的奖励与终止语义差异太大，无法提炼公共模板。在知识图谱中，本文件是 tour "MuJoCo 基础设施"步的核心节点，与 `mujoco_rendering.py`、`utils.py`、`assets/*.xml` 共同构成"MuJoCo 基础设施与模型资产"层。

目录里还有一个 0 字节的 `mujoco_py_env.py`——纯粹的历史化石：`-v2` 时代的 MuJoCo 环境依赖已停止维护的 `mujoco-py` 绑定，Gymnasium 收编时把这批环境迁去了 gymnasium-robotics 仓，`envs/__init__.py:L195-204` 把 `Reacher-v2` 等 id 注册到 `_raise_mujoco_py_error` 报错函数上，占位文件只是让旧 import 路径不炸。今天 `gym.make("Reacher-v2")` 得到的不是环境而是一条迁移指引异常。

## 二、内部结构

### `__init__`：11 参数的配置范式

签名（mujoco_env.py:L38-51）三个必选参数加八个渲染相关可选参数：`model_path`（XML 路径）、`frame_skip`（每次 `step()` 对应的仿真帧数）、`observation_space`（可为 None，见第五节），以及 `render_mode/width/height/camera_id/camera_name/default_camera_config/max_geom/visual_options`。这份参数表就是 v5 全族的构造范式——子类把 `xml_file`、`frame_skip`、`default_camera_config` 透传上来，用户经 `gym.make("Ant-v5", frame_skip=10)` 即可换仿真节拍。`default_camera_config` 是 v5 新增的相机参数字典（如 Ant 的 `{"distance": 4.0}`，ant_v5.py:L9-11），最终由 `MujocoRenderer._set_cam_config` 逐属性 setattr 到 MjvCamera 上（mujoco_rendering.py:L835-843）——自备第三方模型时不必改 XML 就能摆好机位。

### 资产路径解析：expand_model_path

`expand_model_path`（mujoco_env.py:L21-32）三分支：以 `.` 或 `/` 开头按原样、`~` 展开 user 目录、**其余一律拼到 `envs/mujoco/assets/` 下**（mujoco_env.py:L28），不存在则抛 OSError。这解释了子类默认值 `"ant.xml"` 这类裸文件名为何能命中资产——解析基准是包内 assets 目录而非工作目录。14 个 XML 的映射：ant/half_cheetah/hopper/humanoid/humanoidstandup/inverted_pendulum/inverted_double_pendulum/reacher/swimmer 一一对应 9 个环境；**pusher 与 walker2d 在 v5 换用了修正版模型**（`pusher_v5.xml`、`walker2d_v5.xml` 与 v4 旧版并存于 assets）；`point.xml` 在主仓无任何 Python 引用——它是预留给下游 gymnasium-robotics PointMaze 系环境的公共资产。

### 引擎初始化与状态快照

`_initialize_simulation`（mujoco_env.py:L118-130）三步：`mujoco.MjModel.from_xml_path` 编译 XML 得模型；把离屏 framebuffer `offwidth/offheight` **只增不减**地扩到用户请求的宽高（mujoco_env.py:L127-128，XML 声明更大时尊重 XML）；`mujoco.MjData(model)` 分配仿真数据区。随后立刻快照 `init_qpos/init_qvel`（mujoco_env.py:L81-82，`ravel().copy()` 展平防引用泄漏）——XML 里的 `keyframe/qpos0` 初值从此成为 reset 噪声的基准点。

两个状态辅助方法自带"诚实警告"：`set_state`（mujoco_env.py:L132-142）断言 qpos/qvel 形状后写入并 `mj_forward` 正演一次刷新派生量，若模型无 actuator state（na==0）则把 `data.act` 置 None（mujoco_env.py:L140-141）；`state_vector`（mujoco_env.py:L204-209）拼接 qpos/qvel 返回，但 docstring 明确提醒二者**不构成完整物理态**——MuJoCo 的 full physics state 还包含 act 激活与仿真时间等（mjtState 文档）。这就是 utils.py 另备一套基于 `mjSTATE_FULLPHYSICS` 的 get_state/set_state 的原因：基类快照够训练用，严格复现校验须走完整态。

### 空间推导与 dt

`_set_action_space`（mujoco_env.py:L112-116）直接从 `model.actuator_ctrlrange` 转置出 Box 上下界——**动作空间形状完全由 XML 的 actuator 声明决定**，改模型即改动作空间，零代码。`dt` 是 property（mujoco_env.py:L189-191）：`model.opt.timestep * frame_skip`。Ant 默认 0.01×5=0.05 秒。构造时还有一道一致性断言（mujoco_env.py:L86-89）：若子类 metadata 已带 `render_fps`，必须等于 `round(1/dt)`——帧率与仿真时钟的耦合在基类强制校验。

### do_simulation：步进主循环

`do_simulation`（mujoco_env.py:L193-202）先校验动作维度必须等于 `model.nu`（actuator 数），再进 `_step_mujoco_simulation`（mujoco_env.py:L144-155）：写 `data.ctrl` → **单次调用** `mujoco.mj_step(model, data, nstep=n_frames)` 批量步进 → 补一刀 `mj_rnePostConstraint`。最后一行是历史兼容：MuJoCo 2.0 起若无 force sensor，`cacc/cfrc_ext` 等力量量不计算（openai/gym#1541），而 Ant 类环境的 contact_cost 依赖 `cfrc_ext`，故手动触发逆动力学后处理。

### reset 与渲染委托

`reset`（mujoco_env.py:L172-187）：`super().reset(seed=seed)` 装配 np_random → `mj_resetData` 清空物理态 → 子类 `reset_model()` → `_get_reset_info()` → human 模式自动渲一帧。`render()`（mujoco_env.py:L157-161）只有一行——委托给构造时创建的 `MujocoRenderer`（mujoco_env.py:L98-110，**函数内延迟导入**，step/reset 路径完全不触碰渲染模块）。待覆盖方法集中在文件尾注释区（mujoco_env.py:L211-227）：`step`/`reset_model` 必须实现，`_get_reset_info` 默认返回空 dict。

## 三、外部连接

上游依赖刻意单薄：`mujoco` 包用 try/except 守卫（mujoco_env.py:L10-15），ImportError 转成 `error.DependencyNotInstalled` 并提示 `pip install "gymnasium[mujoco]"`——与 pyproject 的 extras 分发策略一致，未装引擎的用户 import 即得可读错误而非裸 traceback。其余只有 numpy 与 `gymnasium.spaces`。

向下游辐射三路。其一是 **18 个子类**，全部以 `class AntEnv(MujocoEnv, utils.EzPickle)` 双继承形式出现（ant_v5.py:L14）。EzPickle 的必要性正是 MuJoCo 族的特点：`MjModel/MjData` 是 C 结构体包装，不可 pickle，`__getstate__` 只存构造参数、恢复时重开引擎（utils/ezpickle.py:6）。对照 04 篇已实证的 `CartPoleEnv` 不继承 EzPickle（MRO 里没有它，纯 NumPy 状态走默认 `__dict__` 序列化）——"环境是否继承 EzPickle"成了"有无不可序列化引擎句柄"的指示灯。04 篇还实证了后者的另一面：CartPoleEnv 在 render 之后 pickle 直接炸在 pygame Surface 活对象上，而 MuJoCo 族走参数重建路径完全绕开活句柄——训练代码想做环境 checkpoint 时，两类环境的可保存边界截然不同。其二是**渲染器** `mujoco_rendering.py` 的 `MujocoRenderer`（L701）：持 `_viewers` 字典按 render_mode 惰性建上下文（L796-827），`camera_id/camera_name` 互斥校验（L745-749），两者都不给时默认 `camera_name="track"`（L751-753），且若模型里真有叫 track 的相机则强制改回 FREE 相机 id=-1（L755-768）——否则 FIXED 相机会吞掉 `default_camera_config` 的 distance/elevation 等参数。底层 `BaseRender`（L43）派生 `WindowViewer`（human，glfw 窗口）与 `OffScreenViewer`（rgb_array/depth_array/rgbd_tuple），GL 后端经 `_ALL_RENDERERS` 工厂按需选 glfw/egl/osmesa（L36-40），并按 MuJoCo 3.2.0/3.11.0 版本线切换 marker 与 camera API（L14-15）。两条渲染路径细节迥异：OffScreenViewer.render（L238-331）每帧把 marker/overlay 画进 MjvScene，经 `mjr_readPixels` 分别读 RGB 与深度缓冲，按 render_mode 分派返回（L323-328）；WindowViewer（L335）则要跑 glfw 事件泵、处理键鼠交互、按 render_fps 真实时间节流。其三是**测试工具** `utils.py` 的 `get_state/set_state`（基于 `mjtState.mjSTATE_FULLPHYSICS`，注释明言训练用默认、验证用 `mjSTATE_INTEGRATION`）。

注册侧：`envs/__init__.py` 为每个环境注册 v4/v5 两条 entry_point（如 reacher L208/L215），`max_episode_steps=50`（Reacher）到 1000（Ant 等）各异——截断统一由 TimeLimit wrapper 外挂，子类 step 里 truncated 恒 False 并留注释（ant_v5.py:L370-371）。

## 四、数据流

以 `gym.make("Ant-v5")` 的一次 episode 为例：

1. **构造**：AntEnv.\_\_init\_\_ 先行 `utils.EzPickle.__init__` 把全部 14 个构造参数按序登记（ant_v5.py:L246-263），再调 `MujocoEnv.__init__(xml_file="ant.xml", frame_skip=5, observation_space=None, ...)`（ant_v5.py:L284-291）。基类加载 ant.xml 得 model/data，快照 15 维 init_qpos（7 维 free joint 四元数 + 8 维 hinge）与 14 维 init_qvel，从 8 个 actuator 的 ctrlrange 推出 `Box(-1,1,(8,),float32)` 动作空间。返回子类后补算观测空间：`obs_size = qpos.size + qvel.size - 2×exclude + cfrc_ext[1:].size×include`（ant_v5.py:L303-309）得默认 105 维，并重建 metadata 补 `render_fps=round(1/dt)=20`（ant_v5.py:L293-301）。
2. **reset(seed=42)**：基类装配 np_random → `mj_resetData` → `reset_model()`（ant_v5.py:L406-421）：`qpos = init_qpos + uniform(-0.1, 0.1, nq)`（位置均匀噪声）、`qvel = init_qvel + 0.1×standard_normal(nv)`（速度正态噪声）→ `set_state` 写回并 `mj_forward` 正演一次刷新派生量（mujoco_env.py:L142）→ `_get_obs` 返回首观测，`_get_reset_info` 附 x/y_position（ant_v5.py:L423-428）。
3. **step(action)**（ant_v5.py:L348-371）：记录 main_body 的 xpos → `do_simulation(action, frame_skip=5)` 内 `mj_step(nstep=5)` 推进 0.05 秒 → 差分算速度得 forward_reward → `_get_rew` 合成 reward 与分量字典 → `terminated = (not is_healthy) and terminate_when_unhealthy` → truncated=False 交 TimeLimit → info 携 x_position/x_velocity/reward_forward 等。观测由 `_get_obs`（ant_v5.py:L393-404）拼装：qpos 切掉前两维（xy 位置不进观测，inductive bias）、qvel 全量、cfrc_ext 切掉 worldbody 行后 clip 到 [-1,1]。
4. **渲染旁路**：rgb_array 模式下训练循环按需 `env.render()`，`MujocoRenderer.render` 断言宽高非 None 后分派给缓存的 OffScreenViewer（mujoco_rendering.py:L784-792）；human 模式则内嵌在 step/reset 尾部自动渲帧（ant_v5.py:L368-369）。

## 五、设计决策

**observation_space=None 的两段式构造**是 v5 最典型的范式。基类允许 observation_space 为 None（mujoco_env.py:L90-91），Ant 等"全量派"先调基类、后按 `data.qpos/qvel/cfrc_ext` 实测维度自算 Box；Reacher 等"精选派"则先算好定长 Box 再传入（reacher_v5.py:L170-176）。观测本就两套口径：全量派直接暴露物理态（Ant 105 维 = 11 qpos + 14 qvel + 80 cfrc_ext），精选派做任务化特征工程——reacher_v5.py:L238-248 只出 10 维：关节角取 cos/sin（解周期性）、跳过 root、末两维是**指尖-目标的 xy 差值**（任务相对量，比裸坐标利于学习）。哪套好取决于算法：无模型 RL 爱全量可复现，课程/模仿学习常精选。v5 还给全量派配了工程补丁——`env.observation_structure` 字典（ant_v5.py:L311-317）把 skipped_qpos/qpos/qvel/cfrc_ext 各段长度显式公布，wrapper 与工具链从此不必解码语义即可切片观测。

**frame_skip 语义**设计成"一次 step = n 帧仿真"而非"循环调 step"：`mj_step(nstep=n)` 在 C 层批量积分（mujoco_env.py:L150），避免 Python 循环开销，也保证 dt 是物理上有意义的动作保持时长——动作空间因此是 torque 而非逐帧微调。v5 把 frame_skip 提升为构造参数（ant_v5.py:L201 的 Version History），但改它必须同步 metadata render_fps，否则撞上 mujoco_env.py:L86-89 的断言。

**v4→v5 的子类职责收敛**在 ant_v5.py:L195-216 的 Version History 里写得像一份变更日志范本：healthy_reward 修复为只在健康时发放（旧版躺着也给，issue #526）；contact_cost 恒计入奖励（v4 由 use_contact_forces=False 整体关闭，现以 contact_cost_weight=0 表达）；cfrc_ext 排除恒为 0 的 worldbody 行（issue #204，训练还更快）；x_position/info 改用 qpos 修掉 xpos 滞后一帧的偏差（issue #521/#539）；reset 必返回非空 info。健康判定本身则收敛为 `is_healthy` property（有限性 + z 区间双判，ant_v5.py:L341-346），terminate 开关 `terminate_when_unhealthy` 让用户可关掉 termination 只留 reward 信号。对照 v4 的 hopper 可见收敛幅度：其 `is_healthy` 要同时判状态有限、z 区间、关节角区间三连（hopper_v4.py:L112），healthy_reward 里还藏着 `float(self.is_healthy or self._terminate_when_unhealthy)` 这种费解表达式（hopper_v4.py:L91）—— termination 被关掉时健康与否都发存活奖励，语义要读三遍；v5 把 terminated 的判定显式写进 step 主流程（ant_v5.py:L358），奖励与终止彻底解耦。另一条更底层的实质变化：v5 起 `xml_file` 支持完全自定义/第三方模型（ant_v5.py:L197），v4 只允许对既有模型做有限替换——v5 把"环境类只是默认配置、模型即配置"的定位坐实，这是 Gymnasium 从环境集合走向环境框架的关键一步。

**渲染与物理的彻底解耦**：基类只在构造末尾建 renderer、`render()` 单行委托（mujoco_env.py:L157-161），viewer 按模式惰性创建且 `_viewers` 缓存互不干扰（同时要 rgb_array 和 human 时自动 `make_context_current` 切换，mujoco_rendering.py:L829-831）。four 种 render_mode（human/rgb_array/depth_array/rgbd_tuple，ant_v5.py:L220-225）共享同一模型-数据对，离屏宽高在模型层只增不减（mujoco_env.py:L127-128）。

## 六、新人提示

写自定义 MuJoCo 环境的**最小清单**：继承 `(MujocoEnv, utils.EzPickle)`；`MujocoEnv.__init__` 传 xml_file/frame_skip（observation_space 二选一范式）；必实现 `reset_model` 与 `step`；`EzPickle.__init__` 必须把**全部**构造参数按原顺序登记（ant_v5.py:L246-263 是标准姿势），漏一个 pickle 后参数漂移；metadata 的 render_fps 等于 `round(1/dt)`。

三个易踩的坑：其一，`xml_file` 裸文件名是相对 **assets 目录**解析的（mujoco_env.py:L28），自备模型要么给 `./`、`/`、`~` 开头的完整路径，要么把文件放进 assets；其二，`do_simulation` 对 ctrl 是**裸写入不裁剪**（mujoco_env.py:L148）——超界动作会被 MuJoCo 引擎内部 clamp 到 ctrlrange，不报错也不警告，复现实验时别指望它在 info 里留痕；其三，场景几何体超 `max_geom=1000` 时渲染直接 RuntimeError（mujoco_rendering.py:L97-98），复杂模型记得调大。其四，`set_state` 断言 qpos/qvel 必须精确等于 `(nq, nv)`（mujoco_env.py:L137）——带 free joint 的模型 root 块是 7 维四元数，手工构造状态少一维就是 AssertionError，别拿观测维度去凑物理维度（Ant 观测 105 维但 nq+nv 只有 29）。

两个必做的动手练习：一是给 Ant 换 `frame_skip=10` 跑通并观察 metadata 断言如何逼你同步 render_fps；二是读 reacher_v5.py:L222-236 的 reset_model——目标点采样用 `while True` 重抽直到离原点足够远（L226-229），这是"reset 随机化不只是加噪声"的最佳示例。顺带一算：Ant 观测 105 维对物理态 29 维的巨大落差，正是第五节两套观测口径之争的量化注脚——观测从来是工程产物，不是物理镜像。

下一步可读 ant_v4.py 与 ant_v5.py 的 diff 亲证第五节的迁移清单，再深入 mujoco_rendering.py:L238-331 的 OffScreenViewer.render 看 rgb/depth 双缓冲读取的实现细节。
