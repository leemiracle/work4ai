# 12 · env_checker 与 passive_env_checker：RL 环境的合规审查官

> 精讲对象：`gymnasium/utils/env_checker.py`（主动版）、`gymnasium/utils/passive_env_checker.py`（只读版）、`gymnasium/wrappers/common.py` 的 PassiveEnvChecker、`gymnasium/envs/registration.py` 的 disable_env_checker 开关。版本 Gymnasium 1.4.0，行号以当前 main 为准。

## 一、角色定位

一个自定义环境写得对不对——reset 是否吃 seed、obs 是否真落在 `observation_space` 里、step 是否确定性——单靠人眼审查既不可靠也不可扩展。Gymnasium 把这道验收工序固化成了两套互补的检查器，这也是它作为"RL 环境标准 API 库"的立身之本：API 标准不仅是文档，还附带可执行的合规判据。

两套检查器同源而分工。`env_checker.py` 的 `check_env`（env_checker.py:L406）是**侵入式全量体检**：它会真实地驱动环境跑多轮 seeded reset/step、抽查 RNG 状态、逐个 render_mode 实例化新环境，凡违反协议一律 `AssertionError` 拦下，面向**环境作者**——写完环境、提 PR 之前的验收关卡。`passive_env_checker.py` 则是**只读旁观体检**：只在数据流经时核对返回值的类型与空间一致性，违规走 `logger.warn` 提醒而非报错，面向**普通用户**——由 `gym.make` 默认自动挂载，零成本兜底。文件头注释（env_checker.py:L1-14）交代了血统：源自 Stable Baselines3（Antonin Raffin）并借鉴 PettingZoo 的断言，由 Mark Towers 拆分为"invasive / passive"两文件，从此两套受众、两种强度正式分档。

值得先纠正一个常见误解：现版本的 `check_env` 并不"主动修复"环境的属性（详见第五节的勘误）。它的"主动"体现在**侵入式执行协议**——真实跑环境、硬断言拦截，而不是替作者改代码。

## 二、内部结构

### check_env 的完整检查清单

`check_env(env, warn=None, skip_render_check=False, skip_close_check=False)`（env_checker.py:L406-426）按固定顺序串联：

1. **前置甄别**：非 `gymnasium.Env` 子类直接 `TypeError`（L430-443），其中还特判了基类是 `gym.core.Env`/`gym.core.Wrapper` 的旧 Gym 环境（L432-434 用字符串比对基类名）；`env.unwrapped is not env` 时警告建议用裸环境来检查（L444-447）。若 metadata 声明 `jax`/`torch`，自动把 env 重绑定为 `JaxToNumpy`/`TorchToNumpy` 包装（L449-452）。
2. **空间检查**：先 `hasattr` 断言两个空间存在（L455-465），再委托 passive 版的 `check_action_space`/`check_observation_space`（L459/L466），外加主动版独有的 `check_space_limit`（L460/L467）——Box 空间含 ±inf 界时警告（L371-378），一维 Box 动作空间非对称/非归一化时建议 `[-1,1]` 或 `[0,1]` 并链去 SB3 的 RL tips（L381-397）；Tuple/Dict 递归下钻（L398-403）。
3. **reset 协议**：`check_seed_deprecation`（env 上还挂旧版 `seed()` 方法则警告，L327-340）、`check_reset_return_info_deprecation`（L310-324）、`check_reset_return_type`（裸 tuple/二元/obs in space/info 是 dict，L343-365）、`check_reset_seed_determinism`（下节详述）、`check_reset_options`（签名含 `options`/`**kwargs` 且真能跑 `env.reset(options={})`，L176-201）。
4. **返回值检查**：调用 passive 版 `env_reset_passive_checker` 与 `env_step_passive_checker`（L477-478）。
5. **step 确定性与数据不复用**：`check_step_determinism`（L204-270）与 `check_returned_data_not_reused`（L273-307）。
6. **render 与 close**：对 `env.spec.metadata["render_modes"]` 里的每个模式 `spec.make(render_mode=...)` 新建环境实测（L489-494）；close 幂等性靠"连关两次"验证（L500-508）。

`check_reset_seed_determinism`（L79-173）是协议核心，五连 reset：`reset(seed=123)` → `reset()` → `reset(seed=123)` → `reset()` → `reset(seed=456)`，中途每次都断言 obs 在空间内（L99/L109/L114/L120/L147）。它用 `inspect.signature` 检查 reset 是否接受 `seed` 或 `**kwargs`（L89-93），签名没有则直接抛 `gym.error.Error`（L170-173）。核心验证有四层：(a) `spec.nondeterministic` 为 False 时（L124），同 seed 两次 reset 的 obs 必须 `data_equivalence`（L125-130），仅"相似但不严格相等"（`np.allclose` 容差 1e-5）降级为警告（L131-138）；(b) **RNG 状态指纹**——deepcopy 保存 `env.unwrapped._np_random`（L105/L117），断言两次 seed=123 的 `bit_generator.state` 完全一致（L140-144），这比比 obs 更根本，专抓"reset 没调 `super().reset(seed=seed)`"（L102-104 的断言消息明说）；(c) seed=456 必须**产生不同的** RNG 状态（L150-155）；(d) seed 参数默认值必须是 None，否则环境默认就是确定性的（L163-169）。

`check_step_determinism`（L204）同理：`env.action_space.seed(123)` 采样动作（L217-218），同 seed reset 后 step 两次，比对 obs/reward/info 等价性、terminated 严格相等、truncated 必须为 False（"一步就截断，肯定出了大问题"，L259-261），并验证 step 后 `_np_random` 与 reset 时快照的 RNG 状态一致（L226-238）。`check_returned_data_not_reused`（L273）则收集 reset+两次 step+再 reset 的全部 (obs, info)，两两 `combinations` 配对断言 `data_shares_objects` 为假（L295-307）——环境不得复用内部缓冲返回数据，否则用户的 replay buffer 会被原地改写。

### passive_env_checker 的 partial 伪函数与一次性体检

passive 模块的公开面只有五个符号（passive_env_checker.py:L13-19）。空间检查的骨架是通用递归函数 `check_space(space, space_type, check_box_space_fn)`（L61-106）：先验空间继承自 `gymnasium.spaces.Space`（L65-73，还特判旧 `gym.spaces`），再按 Box/Discrete/MultiDiscrete/MultiBinary/Tuple/Dict 分派，Tuple/Dict 非空且递归（L95-106）。关键的工程手法在 L109-116：

```python
check_observation_space: Callable[[Space], None] = partial(
    check_space, space_type="observation", check_box_space_fn=_check_box_observation_space)
check_action_space: Callable[[Space], None] = partial(
    check_space, space_type="action", check_box_space_fn=_check_box_action_space)
```

`check_action_space`/`check_observation_space` **不是 def 出来的函数，而是 `functools.partial` 赋值出的伪函数**——把差异点（space_type 标签、Box 专项检查回调）做成参数注入同一骨架，observation 版多查"high < low"倒挂（L38-41），action 版只查 low==high（L57-59）。类型注解显式写 `Callable[[Space], None]` 保住签名可读性。这也是本图谱 batch 分析时确认的结构事实：模块内没有一个重复的 space 检查分支。

运行时体检由三个 `env_*_passive_checker` 承担。`env_reset_passive_checker`（L250-290）检查签名含 seed/options（缺失走 `logger.deprecation`，L256/L269），调用真 reset 后核对二元 tuple、obs（经 `check_obs`）、info 类型，**原样返回数据**。`check_obs`（L131-176）按空间类型核对 obs 的类型/dtype/长度/键集，最后 `obs in observation_space` 用 try/except 包住——`contains` 抛异常也算"不在空间内"警告（L172-176）。`check_obs` 前面还排着三个 `@overload` 桩（L119-130），分别针对 Discrete 的 int、Box 的 ndarray 与泛型空间——运行时逻辑只有一份，重载纯粹是给类型检查器看的窄化签名。`env_step_passive_checker`（L293-350）兼容旧四元组（done 合并版，走 deprecation，L302-312）与新五元组，核对 terminated/truncated 是 bool、reward 是数值且非 NaN/inf（L332-344）。`env_render_passive_checker`（L405-457）核对 metadata 的 `render_modes`/`render_fps` 声明、`render_mode` 合法性，再实际调用 render 并交给 `_check_render_return`（L353-402）按模式核对返回类型——`rgb_array` 必须 uint8 三维且末轴为 3，`*_list` 模式递归核对每个元素（L392-402）。

这些函数被 `PassiveEnvChecker`（wrappers/common.py:L225）包装成运行时守护：构造时立刻查 env 类型与两个空间（L253-275），然后设四个标志位 `checked_reset`/`checked_step`/`checked_render`/`checked_data_reuse`（L277-285）。**首 reset** 走 `env_reset_passive_checker` 并把结果存进 `_previous_data`（L319-324）；**首 step** 走 `env_step_passive_checker`，顺手用 `_previous_data` 做一次 reset→step 的数据复用比对（L291-301）；**第二 step** 再做一次 step→step 复用比对后置位 `checked_data_reuse`（L305-311）；**首 render** 走 render 检查（L330-334）。之后所有调用直通底层——一次性体检，检查开销只付一次。

## 三、外部连接

**与 make 默认链的咬合**是 passive 检查器的生命线。`make()` 的 `disable_env_checker: bool = False`（registration.py:L570）与 `register()` 的 `disable_env_checker: bool | None = None`（L643）两级开关汇合于 L802-805：显式 False 或"未指定且 EnvSpec 字段也是 False"（EnvSpec 默认即 False，L100）就挂上 `PassiveEnvChecker`。注释点明它是**最低层 wrapper**（L801）——先于 OrderEnforcing 和 TimeLimit 包裹，因此 `gym.make("CartPole-v1")` 的栈是 `TimeLimit<OrderEnforcing<PassiveEnvChecker<CartPoleEnv>>>`，检查器看到的是最接近裸环境的行为。注意 registration.py:L770-784 在实例化后会把 `env.unwrapped.spec` 重写为带 `disable_env_checker=True` 的 minimal spec（L777）——这是 make 链里罕见的**直接属性写**，目的是阻止检查器被二次叠加；而 PassiveEnvChecker 自己的 `spec` property（common.py:L336-355）又会 deepcopy 出一份把 `disable_env_checker` 改回 False 的 spec，让 `env.spec.make()` 重建环境时检查器仍然生效。两处一收一放，配合得相当精巧。

**上游依赖**：`inspect`（签名协议检查）、`numpy`（allclose/shares_memory）、`deepcopy`（RNG/obs 快照，对抗环境复用内部缓冲）；核心侧依赖 `gym.Env` 的 `_np_random`/`unwrapped`/`spec`/`metadata` 契约与 `spaces` 家族的 `contains`。**输出协议**统一走 `gym.logger`（logger.py）：`warn` 前缀 `WARN:` 黄色、`deprecation` 归入 DeprecationWarning 且经 L13 的 filterwarnings 每处只弹一次、`error` 前缀 `ERROR:` 红色；颜色由 `utils/colorize.py:L23` 的 ANSI 着色实现，`min_level=30`（logger.py:L7-9）控制开关。

**消费方**：全仓测试 `tests/envs/test_envs.py:L39` 对每个注册环境跑 `check_env(env, skip_render_check=True)`；`tests/utils/test_env_checker.py` 用刻意构造的缺陷环境（漏调 super().reset(seed)、复用观测缓冲等）逐项验证各断言能精确命中预期错误消息；官方文档 create_custom_env.md:L377-381 把 `check_env` 写进自定义环境教学。检查器自己也被测试镜像约束——passive 版的每个警告在 `tests/utils/test_passive_env_checker.py` 里都有参数化用例。

## 四、数据流

以用户 `gym.make("CartPole-v1")` 后的首个 episode 为例。**构造期**：make 实例化 CartPoleEnv → 写 minimal spec → 包 PassiveEnvChecker → 包 OrderEnforcing → 包 TimeLimit。PassiveEnvChecker.__init__ 立即执行空间检查，此刻数据流还没开始，纯粹是结构审查。**首 reset**：调用穿过 TimeLimit/OrderEnforcing 到达 PassiveEnvChecker.reset，标志位翻转，`env_reset_passive_checker` 真调底层 reset，返回值在原地被检查（签名、tuple 形状、obs 对空间、info 类型）后**原封不动**上抛，同时 `(obs, info)` 存入 `_previous_data`。**首 step**：同样穿过检查（五元组、bool、reward NaN/inf、obs），再与 `_previous_data` 做 `data_shares_objects` 比对——该函数（passive_env_checker.py:L179-218）比较的是**身份而非值**：dict 按键下钻、tuple 元素递归、ndarray 用 `np.shares_memory`（L214，连 `buffer[:]` 这种视图复用都能抓到）、object 数组逐元素递归，不可变对象一律放行（L215-218，避免 int 驻留造成的假阳性）。第二 step 再比对一次后体检结束，后续成千上万次 step 走直通分支，零额外开销。

`check_env` 的数据流则是**主动编排的实验序列**而非旁观：五连 reset 反复改写 `_np_random`，deepcopy 在每个关键点拍快照防环境原地改 obs（env_checker.py:L98/L108/L224 注释明言这是对抗内部观测缓冲复用）；step 确定性检查里 `seeded_rng` 快照与 step 后的 RNG 做 state 级比对（L226-238）。数据复用检查把 3-5 次 (obs, info) 调用结果两两配对断言。render 检查的数据流是**分叉**的——对原环境只测当前 render_mode，对每种模式则 `spec.make(render_mode=...)` 另起炉灶全新实例（L491），测完即 close，完全不污染主环境状态。两条数据流的对照即两版检查器的本质区别：passive 是"顺路安检"，invasive 是"考试划重点做实验"。

## 五、设计决策

**受众分档、强度分档**。同一套协议，作者侧用 assert（错即失败，逼你修），用户侧用 warn（错也放行，只提醒）——因为用户拿到的第三方环境改不了源码，硬断言只会让库不可用；而作者在 CI 里需要的就是一票否决。`check_env` 里同为"obs 不在空间内"，passive 路径是 logger.warn（passive_env_checker.py:L172-176），主动路径是硬 assert（env_checker.py:L99）。`spec.nondeterministic` 则提供了诚实的出口：真随机的环境（如物理噪声）声明后跳过确定性断言（env_checker.py:L214-215），协议检查不逼迫自然规律。

**勘误：check_env 并不改 env 属性**。社区常说 check_env 会"自动修复"环境，但在 1.4.0 源码里它**没有任何一处对 env 属性的直接赋值**。它对环境状态的改变只有三类：把局部变量 env 重绑定为 JaxToNumpy/TorchToNumpy 包装（env_checker.py:L449-452，包装而非改写）；通过 `action_space.seed()`（L217/L283）和多次 seeded reset 驱动环境自身状态机；以及经 spec.make 造新实例。真正"直接写属性"的动画发生在 make 链（registration.py:L770-784 的 `env.unwrapped.spec = ...`）和 PassiveEnvChecker 的 spec 副本（common.py:L343-344，写在 deepcopy 上）。老版 gym 确实干过替环境补属性的勾当，Gymnasium 的哲学已转向"只判定、不代改"。

**partial 骨架复用**（passive_env_checker.py:L109-116）把六种空间类型的检查收敛为一个递归函数加两个注入点，消除了 observation/action 两套近乎全同的分支——后续新增检查项只改一处。**一次性标志位**（common.py:L277-285）是典型的摊销设计：检查成本集中在前两次调用，长训练里可忽略。**`data_equivalence` 的双档容差**（env_checker.py:L36/L66-70）是个务实的折衷：数值环境常有浮点顺序差异，`np.allclose(1e-5)` 判"等价"（过审），`exact=True` 判"严格相等"（不等只警告），既不冤枉作者也不放过真不确定性。**deepcopy 快照**贯穿两个确定性检查，防的是环境把 obs 数组原地复用导致比对的其实是同一对象——这类环境缺陷在真实第三方环境里高频出现，测试文件专门为其造了用例。

**三级输出协议**也是刻意分级：`logger.warn`（黄色 `WARN:`，logger.py:L17-35）面向"不合规但不致命"，`logger.deprecation` 归入 DeprecationWarning 且每处只弹一次（L13 的 filterwarnings，避免刷屏）面向"旧 API 债"，`logger.error`（红色 `ERROR:`，L44-47）与 assert 面向"必须修"。`min_level` 全局闸门（L9，默认 30）允许下游库整体静音。检查消息本身写得像诊断文档——断言串里直接给出修复指引和文档链接，这是把"检查器"当"教学工具"用的设计自觉。

## 六、新人提示

**新环境开发工作流**（贡献约定）：写环境 → `from gymnasium.utils.env_checker import check_env; check_env(env)` → 全绿再提 PR。仓库自己的每个环境都在 CI 里过这道关（tests/envs/test_envs.py:L39），第三方环境作者理应对齐。三个签名开关要认识：`warn` 参数已废弃、传了只提示"now ignored"（env_checker.py:L427-428）；`skip_render_check=True` 在无显示器的 CI 里常用；`skip_close_check` 跳过双 close 检查。

**实用排障口诀**：断言消息本身就是诊断书——"random number generator not generated" 意味着 reset 里忘了 `super().reset(seed=seed)`（L102-104）；"share an object" 意味着返回了内部缓冲的引用，去 obs 里加 `.copy()`；"truncates after 1 step" 多半是 TimeLimit 或截断条件写反。想屏蔽 make 自带的被动检查，用 `gym.make(id, disable_env_checker=True)` 或注册时声明；被动检查的警告不会终止程序，但如果你的训练日志里它反复弹（DeprecationWarning 每处只弹一次，logger.py:L13），说明环境有 API 旧债。最后注意 `check_env` 跑完环境状态已被彻底搅动（多次 reset、RNG 换种子），**不要指望检查过的 env 还能接着跑实验**——开新实例，或者把 check_env 只留在 CI 里。向量环境侧没有 PassiveEnvChecker 的 vector 版（common.py:L231 明言 "No vector version of the wrapper exists"），SyncVectorEnv 等只在单环境层各自把关，这也是贡献向量环境时更要手动跑 `check_env` 的原因。这也是文档反复强调"constructed 后调用"的隐含语义：它是一次性验收，不是可叠加的运行时服务。
