# 04 · CartPole 精讲：范本级环境的标准写法

> 源码版本：main @ 8b22ad4；文件 `gymnasium/envs/classic_control/cartpole.py`（614 行）
> 行号锚格式 `cartpole.py:L行号`，全部从当前源码核实；交叉文件锚单独标明文件名。

## 一、角色定位

`cartpole.py` 是 Gymnasium 的**门面环境**：`gym.make("CartPole-v1")` 是文档第一行示例、CI 教程常客，更是官方文档"如何写自定义环境"一节让读者直接抄的模板。它实现 Barto, Sutton, Anderson 1983 年论文中的倒立摆问题（cartpole.py:L25-26）——一根杆无驱动地铰接在小车上，靠左右推力维持平衡。文件头（cartpole.py:L1-5）注明血统：代码直接移植自 Rich Sutton 的 pole.c 并附 permalink，这让 CartPole 成为 RL 史上被复现次数最多的环境。

它在知识图谱中位于"经典控制与 Phys2D 环境族"层（layer-7），是 tour step-5 的主角。全文件 614 行包含两个类：`CartPoleEnv`（cartpole.py:L21）——纯 NumPy 标量环境，只依赖 `math/numpy/pygame`，无任何物理引擎；以及 `CartPoleVectorEnv`（cartpole.py:L356）——同一物理内核的原生向量化实现，走 `gym.make_vec` 的 `vector_entry_point` 通道（envs/\_\_init\_\_.py:21,29）。同一个文件示范了"标准 Env + 原生 VectorEnv"两种写法，这是其他环境族少有的完备度。

它作为范本的深层理由是**契约完备且零外部依赖**：metadata 声明、空间构造、seed 协议、terminated/truncated 二分、渲染惰性化、越界步警告，一个不缺；而物理只是四行手推微分方程。学环境开发的心智负担被压到最低——所有复杂性都在 API 形状上，而不在领域知识上。

## 二、内部结构

### 类头与 metadata

`CartPoleEnv(gym.Env[np.ndarray, int | np.ndarray])`（cartpole.py:L21）用泛型标注了"观测是 ndarray、动作是 int 或 ndarray"——后者兼容向量化形态。`metadata`（cartpole.py:L115-118）声明 `"render_modes": ["human", "rgb_array"]` 与 `"render_fps": 50`。这两个数字有隐含耦合：物理步长 `tau = 0.02` 秒（cartpole.py:L132），1/0.02 = 50，即**渲染帧率严格对应仿真时钟**，human 模式下动画以真实速度播放。

### `__init__`：物理常数与空间构造

构造参数只有两个（cartpole.py:L120-122）：`sutton_barto_reward`（切原始奖励形式，见第五节）与 `render_mode`。物理常数区（cartpole.py:L125-133）是清一色裸属性：`gravity=9.8`、`masscart=1.0`、`masspole=0.1`、`length=0.5`（注释明言"actually half the pole's length"，cartpole.py:L129——是半杆长，因为杆质心在半长处）、`force_mag=10.0`、`tau=0.02`、`kinematics_integrator="euler"`。**没有 super().__init__() 调用、没有随机性初始化**——随机性全部延迟到 reset，这是刻意设计（见第五节）。

失败阈值区（cartpole.py:L136-137）：`theta_threshold_radians = 12 * 2 * math.pi / 360`（即 ±12° ≈ ±0.2095 rad，注意这行写法是"12×2π/360"，用周角换算度数）与 `x_threshold = 2.4`。随后是全文件最值得抄的一段——**观测空间边界推导**（cartpole.py:L139-152）：

```python
high = np.array([self.x_threshold * 2, np.inf,
                 self.theta_threshold_radians * 2, np.inf], dtype=np.float32)
self.action_space = spaces.Discrete(2)
self.observation_space = spaces.Box(-high, high, dtype=np.float32)
```

为什么是阈值的 **2 倍**（±4.8 与 ±0.418）？注释（cartpole.py:L139-140）给出答案：terminated 在积分**之后**判定（cartpole.py:L199-204），失败那一步的观测可能已越过阈值；若 Box 边界恰好设成阈值，`obs in observation_space` 就会变成 False，PassiveEnvChecker 会当场报警。2 倍冗余保证"失败观测仍在界内"。速度两维无物理界，直接 `np.inf`。动作空间 `Discrete(2)`（左/右推，cartpole.py:L36-37 的 docstring 表）。

收尾（cartpole.py:L154-163）把 `render_mode` 存为实例属性，`screen/clock` 初始化为 None（渲染惰性化伏笔），`state=None`（强制先 reset），`steps_beyond_terminated=None`（越界步计数哨兵）。

### `step`：动力学推进的完整闭环

`step`（cartpole.py:L165-227）是范本中的范本。入口两个 assert（cartpole.py:L166-169）：动作必须在 action_space 内、必须先 reset。随后是**倒立摆动力学**（cartpole.py:L175-184，注释引用 Florian 2005 推导论文 coneural.org/florian/papers/05_cart_pole.pdf）：

$$\text{temp} = \frac{F + m_p l \dot\theta^2 \sin\theta}{m_c + m_p}, \qquad \ddot\theta = \frac{g\sin\theta - \cos\theta \cdot \text{temp}}{l\left(\frac{4}{3} - \frac{m_p \cos^2\theta}{m_c + m_p}\right)}, \qquad \ddot{x} = \text{temp} - \frac{m_p l \ddot\theta \cos\theta}{m_c + m_p}$$

这是牛顿-欧拉法对"小车+均质杆"系统的闭式解（杆转动惯量 \(I = \frac{4}{3} m_p l^2\) 体现在 4/3 因子里）。然后是**积分器分派**（cartpole.py:L186-195）：默认显式 Euler——位置用**旧**速度更新、角度用**旧**角速度更新；else 分支是 semi-implicit（symplectic）Euler——先更新速度再用**新**速度更新位置。注意判据是字符串等于 `"euler"`，把实例属性 `kinematics_integrator` 改成任何别的值就切换积分器。

状态以 **float64** 重建（cartpole.py:L197）保积分精度，返回时才降 float32（cartpole.py:L227）与 Box dtype 对齐。terminated 四连判（cartpole.py:L199-204）：|x| > 2.4 或 |θ| > 12°，纯 bool。奖励三分支（cartpole.py:L206-221）：未终止 +1；**刚倒下**（`steps_beyond_terminated is None`）仍 +1 并置计数器（cartpole.py:L208-212）；倒下后继续 step 则发一次性 `logger.warn` 警告（cartpole.py:L214-218）且奖励归零——"undefined behavior 但不静默"。最后 `render_mode == "human"` 时自动渲染一帧（cartpole.py:L223-224），并返回五元组，其中 **truncated 恒为 False**（cartpole.py:L226-227），行内注释直说原因：时间上限由 `make` 时外挂的 TimeLimit wrapper 管。

### `reset`：seed 协议与随机化

`reset`（cartpole.py:L229-248）只有三件事：`super().reset(seed=seed)`（cartpole.py:L235）——Env.reset 在 seed 非 None 时重建 `self._np_random`（core.py:169-171，seed=None 则复用已有 RNG 流，即官方"make 后 seed 一次、之后不再 seed"范式）；经 `utils.maybe_parse_reset_bounds`（cartpole.py:L238-242，实现于 classic_control/utils.py:17）解析 options 里的自定义 low/high（默认 ±0.05）；然后 `self.np_random.uniform(low, high, size=(4,))`（cartpole.py:L243）对**四维状态全部均匀随机**初始化——注释（cartpole.py:L236-237）提醒自定义边界可能产生界外观测。收尾清零越界计数器、human 模式渲染、返回 `(float32 obs, {})`（cartpole.py:L244-248）。

### `render` 与 `close`

`render`（cartpole.py:L250-345）先处理 `render_mode=None` 的裸调用——只警告不炸（cartpole.py:L251-258）；随后**延迟导入 pygame**（cartpole.py:L260-266），ImportError 转成 `DependencyNotInstalled` 并提示 `pip install "gymnasium[classic-control]"`。屏幕惰性初始化分两路（cartpole.py:L268-275）：human 走 `pygame.display.set_mode` 开真窗口，rgb_array 只建离屏 `Surface`。绘制部分（cartpole.py:L279-333）用 `gfxdraw` 画小车矩形、以 `Vector2.rotate_rad(-x[2])` 绕轴销旋转的杆（cartpole.py:L312）、轴销圆与地线；坐标细节如 `cartx = x[0]*scale + screen_width/2`（cartpole.py:L296）完成世界系到屏幕系的映射（world_width 恰为 2×x_threshold=4.8，cartpole.py:L279）。收尾两分支（cartpole.py:L337-345）：human 走 `event.pump + clock.tick(render_fps) + display.flip`——`tick(50)` 把吞吐节流到真实时间；rgb_array 用 `pygame.surfarray.pixels3d` 取零拷贝像素视图再 transpose 成 `(H, W, 3)`。`close`（cartpole.py:L347-353）quit pygame 显示子系统。

### `CartPoleVectorEnv`

第二类（cartpole.py:L356-613）继承 VectorEnv，metadata 额外声明 `autoreset_mode: NEXT_STEP`（cartpole.py:L362），构造参数多出 `max_episode_steps=500`（cartpole.py:L368）。空间用 `batch_space` 合成批量版（cartpole.py:L412-415）。step 把标量物理整体向量化：`force = np.sign(action - 0.5) * force_mag`（cartpole.py:L439）一个表达式同时处理批内左右推；terminated 变逐元素布尔数组（cartpole.py:L467-472）；**truncated 由自身判定** `self.steps >= self.max_episode_steps`（cartpole.py:L474-476）；autoreset 逻辑用 `prev_done` 掩码（cartpole.py:L483-492）——上一步 done 的子环境在本步开始前就地重置，reward/terminated/truncated 清零后返回新鲜观测，这正是 NEXT_STEP 语义。渲染（cartpole.py:L516-607）为每个子环境建独立 Surface，返回帧列表。

## 三、外部连接

上游依赖极薄：`gymnasium.spaces`（Discrete/Box）、`gymnasium.logger`、`classic_control.utils`（reset bounds 解析）、`gymnasium.error.DependencyNotInstalled`、`gymnasium.vector`（AutoresetMode/VectorEnv/batch_space，cartpole.py:L13-18）——pygame 只在 render 内延迟导入，**核心 step/reset 路径零渲染依赖**。

注册侧：envs/\_\_init\_\_.py:18-24 注册 `CartPole-v0`（`max_episode_steps=200`，`reward_threshold=195`），envs/\_\_init\_\_.py:26-33 注册 `CartPole-v1`（500/475），两者的 `entry_point` 与 `vector_entry_point` 分别指向本文件两个类。`gym.make` 解析 spec 后自动套三层 wrapper——docstring 里印着结果栈 `<TimeLimit<OrderEnforcing<PassiveEnvChecker<CartPoleEnv>>>>`（cartpole.py:L84）。其中 TimeLimit（wrappers/common.py:43）在 step 后检查 `elapsed >= max_episode_steps` 就把 truncated 置 True（wrappers/common.py:130-137）——这就是 cartpole.py:L226 注释所说的"外部管截断"。

下游辐射三条线：其一是文档与教程（几乎每篇 how-to 都以 CartPole 为例）；其二是 tests/envs 的横向回归（test_envs 会遍历所有注册环境跑 API 一致性检查，CartPole 是最常被命中的路径）；其三是同仓 phys2d/cartpole.py——同一物理的 JAX 函数式重写（layer-11 的 FuncEnv 体系），参数可域随机化，可视为本文件的"纯函数化镜像"。

**关于 EzPickle 的诚实澄清**：一个流传甚广的印象是"CartPole 继承 EzPickle"，实测不成立——`CartPoleEnv.__mro__` 只有 `CartPoleEnv → Env → Generic → object`。EzPickle 定义于 utils/ezpickle.py:6，机制是 `__getstate__` 只存构造参数、`__setstate__` 用参数重建实例，专治**包裹不可 pickle 底层句柄的环境**（MuJoCo/Box2D 全族，以及本仓的 phys2d/cartpole.py 也继承了它）。CartPoleEnv 走默认 `__dict__` pickle：实测 reset 后可以正常 dumps/loads；但 render 之后 pickle 报 `TypeError: cannot pickle 'pygame.surface.Surface'`——screen/clock 活对象挡路。对照之下，`gym.make` 返回的 wrapper 套娃可以 pickle（Wrapper 系走 RecordConstructorArgs 路径，core.py:302），所以训练代码通常 pickle 外层而绕开此坑。

## 四、数据流

一次完整 episode 的数据流：

1. **make**：`gym.make("CartPole-v1")` → registry 查 spec → 套 TimeLimit/OrderEnforcing/PassiveEnvChecker → 底层 `CartPoleEnv(render_mode=None)`，此刻 state=None、screen=None，没有任何资源被占用。
2. **reset(seed=42)**（cartpole.py:L229-248）：seed 经 Env.reset 装配 `np_random`（PCG64 Generator）→ 四维状态各自 `uniform(-0.05, 0.05)` → 返回 float32 观测 + 空 info。此后 seed=None 的后续 reset 复用同一条随机流，保证"一个 seed 决定整条训练轨迹"。
3. **step(action)**（cartpole.py:L165-227）：动作 0/1 → force=±10N（cartpole.py:L171）→ 闭式方程算 θ̈/ẍ（cartpole.py:L177-184）→ Euler 前进 τ=0.02s（cartpole.py:L186-190）→ float64 存内部态（cartpole.py:L197）→ 阈值四连判得 terminated（cartpole.py:L199-204）→ 奖励分支（cartpole.py:L206-221）→ 观测降级 float32 返回（cartpole.py:L227）。观测是**新数组**而非内部态引用——L227 的 `np.array(self.state, dtype=np.float32)` 做了显式拷贝转换，满足 Env 契约"返回新数据"的要求（core.py:161-163 的 Note）。
4. **truncation 分叉**：环境返回的 truncated=False 一路穿透到 TimeLimit（wrappers/common.py:130-137），后者数步数、到 500 步改写 truncated=True。学习者拿到的 `(500 步, terminated=False, truncated=True)` 里，截断信号完全来自 wrapper 层。
5. **渲染旁路**：rgb_array 模式下训练循环按需调 `env.render()`，拿到 `(400, 600, 3)` uint8 帧喂给 RecordVideo；human 模式下渲染内嵌在 step 里（cartpole.py:L223-224），`clock.tick(50)` 同步节流。
6. **向量化路径**：`gym.make_vec("CartPole-v1", num_envs=3, vectorization_mode="vector_entry_point")`（cartpole.py:L100 示例）直接构造 CartPoleVectorEnv，step 收 `(3,)` 动作数组、批内各自积分（cartpole.py:L438-465）、done 子环境就地重置（cartpole.py:L484-490）、返回 `(3,4)` float32 观测批——没有 wrapper 逐层转发的开销，这是它存在的全部理由。

## 五、设计决策

**（1）terminated 与 truncated 的职责二分**。倒下是 MDP 的真实吸收态（terminated），到时上限是人为截断（truncated），二者在 bootstrap 值估计时语义完全不同——截断态的后续价值仍应被估计。CartPole 把后者彻底外包给 TimeLimit（cartpole.py:L226-227），环境自身零步数计数。好处：同一环境类可被套不同 max_episode_steps 复用成 v0/v1 两个 spec（envs/\_\_init\_\_.py:18-33 里 200/500 只差注册参数）。反例恰在同一文件：CartPoleVectorEnv 必须自管 truncated（cartpole.py:L474-476），因为 vector_entry_point 绕过了 make 的 wrapper 套娃——设计随执行路径而变，不是教条。

**（2）显式 Euler 而非 RK4**。tau=0.02s 下显式 Euler 已稳定，且 v0/v1 的历史基准数字（reward_threshold 195/475）都建立在 Sutton 原版 pole.c 的这套积分上——换积分器会改变动力学轨迹，等于悄悄换了环境。同族 Acrobot 用 RK4 是因为欠驱动双连杆需要更高精度。另注意分支判据是字符串 `"euler"`（cartpole.py:L186），semi-implicit 是 else 兜底而非显式枚举，改属性值即可切换但无校验。

**（3）Box 边界取 2 倍阈值的防御性**（cartpole.py:L139-149）：保证"触发 terminated 的那一步观测仍 contains=True"。这解决了时序上的鸡生蛋问题——观测必须先于（且包含）失败态，校验链才不断裂。速度维用 inf 则承认物理上无界，PassiveEnvChecker 对 Box 的 finite 检查会照常放行。

**（4）惰性初始化的全面贯彻**。随机性延迟到 reset（\_\_init\_\_ 不建 RNG，cartpole.py:L161-163）、pygame 延迟到 render（cartpole.py:L260-266）、screen/clock 延迟到首帧（cartpole.py:L268-277）。`gym.make` 千次不渲染就千次零渲染开销；无头服务器上跑纯训练连 pygame 都不必安装。代价是 render 后不可 pickle（见第三节实测），EzPickle 型"参数重建"本可解此坑，但 classic_control 选择了简单。

**（5）越界步的宽容处理**（cartpole.py:L208-221）：terminated 后继续 step 不抛异常，首次给 logger.warn、奖励归零、计数器累加。RL 训练循环里"忘 reset"是高频 bug，范本选择"响亮警告 + 定义良好但无意义的返回值"而非崩溃，兼顾调试友好与鲁棒。

**（6）sutton_barto_reward 兼容开关**（cartpole.py:L61-63, L92）：默认每步 +1（含终止步）；开关打开后回到原版 0/-1 形式。一个布尔参数维护了四十年前的语义兼容（v1 于 Gymnasium 1.0.0a2 加入，cartpole.py:L111），示范了"奖励函数变更要走参数而非新版本"的轻量路线——但代价是 docstring 里两套 reward_threshold 并存（475 vs 0），新人容易看混。

**（7）渲染双模式的性能取舍**。human 的 `clock.tick(50)`（cartpole.py:L339）意味着挂 human 训练吞吐被钉死在 50 FPS；rgb_array 不节流、离屏渲染、按需调用，是录像与训练的标准姿势。`render_mode` 在构造时一次性固定（cartpole.py:L154）而非旧 gym 的 `render(mode=...)` 运行时切换——API 简化的代价是灵活性，Gymnasium 在这里选择了契约清晰。

## 六、新人提示

- **抄它，但从正确的地方抄**：\_\_init\_\_ 的空间声明（L139-152）、step 的 assert 与五元组返回（L165-227）、reset 的 `super().reset(seed=seed)` 首行（L235）、metadata 与惰性渲染——这四块是模板的全部骨架。物理方程换成你自己的领域模型即可。
- **`length = 0.5` 是半杆长**（cartpole.py:L129），全杆长 1.0；推公式时用错长度是最常见的复现错误。4/3 因子来自均质杆绕质心转动惯量，不是魔法常数。
- **12° 是终止角，24° 是观测角**（cartpole.py:L55-58 的 docstring 表）：两套角度勿混。同理 2.4 是终止边界，4.8 是观测边界。
- **reset 的 options 边界**：`options={"low": -0.1, "high": 0.1}` 可以放宽初始随机化（cartpole.py:L85 示例），但注释（cartpole.py:L236-237）警告可能产生 observation_space 界外的首观测，PassiveEnvChecker 会报警。
- **别在训练时挂 render_mode="human"**：50 FPS 节流 + 每步自动渲染（cartpole.py:L223-224）会把训练拖慢一个数量级；要用 human 看效果就用 `gym.wrappers.HumanRendering` 事后包装，或仅在评估脚本里开。
- **pickle 时机**：render 前可 pickle、render 后报 Surface TypeError；需要序列化 checkpoint 时保存 wrapper 层或 `render_mode=None` 重建。
- **向量化优先走 vector_entry_point**：`gym.make_vec(..., vectorization_mode="vector_entry_point")` 用本文件的原生 CartPoleVectorEnv，比 `sync` 模式（逐个调用单环境 step，cartpole.py:L103-105 示例）快数倍——但注意其 autoreset 是 NEXT_STEP 语义（done 后下一步即返回新回合观测，cartpole.py:L483-492），训练循环的 bootstrap 逻辑要与之匹配。
- **对照阅读**：phys2d/cartpole.py 是同一物理的 JAX 函数式重写（且继承了 EzPickle），两文件对读能立刻看清"有状态 Env 类"与"纯函数 transition"两种环境建模范式的全部差异——这恰是理解 Gymnasium 未来演化方向（functional API）的捷径。
