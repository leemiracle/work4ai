# VecEnv 抽象基座 base_vec_env.py：算法只与"批"对话

## 一、角色定位

SB3 所有算法从不直接面对 gym.Env，训练循环只认 VecEnv。base_vec_env.py（502行）是这份向量化契约的唯一定义处：批量 step/reset 的节拍、gym 5 元组到 SB3 4 元组的折叠边界、wrapper 委托链协议、支撑多进程的 CloudpickleWrapper。DummyVecEnv 与 SubprocVecEnv 是两个参考实现，VecNormalize/VecMonitor 等十来个包装器全以 VecEnvWrapper 为基。"算法层永远只见批"由此成立：policy 一次前向出 n_envs 个动作、buffer 第 0 维永远是 env 索引；代价是 episode 边界与 terminated/truncated 之别须折叠进返回值——这份折叠规范是本文最重要的阅读点。

## 二、内部结构

开头是类型别名（base_vec_env.py:L15-21）：`VecEnvObs`（ndarray/dict/tuple）与契约核心 `VecEnvStepReturn = (obs, 奖励 ndarray, done ndarray, list[dict])`——**4 元组**，非 gym 的 5 元组。

`VecEnv` ABC（base_vec_env.py:L50）构造器持有 num_envs、spaces、`reset_infos` 与延迟生效的 `_seeds/_options`（base_vec_env.py:L65），并断言各子环境 render_mode 一致（base_vec_env.py:L75）。抽象方法八个：reset/step_async/step_wait/close 与 get_attr/set_attr/env_method/env_is_wrapped（定义于 base_vec_env.py:L109、L123、L135、L144、L166、L177、L189、L202）。具体方法：step = step_async + step_wait 连打（base_vec_env.py:L214）；render（base_vec_env.py:L230）兼容"构造期定 render_mode"，rgb_array 下借 OpenCV 伪装 human（base_vec_env.py:L269）；seed 只填 `[seed+idx]`（base_vec_env.py:L292、L308）；set_options 用 deepcopy 防共享可变状态（base_vec_env.py:L311-323）；另有 `unwrapped`/`_get_indices` 等工具（base_vec_env.py:L327、L346）。

`VecEnvWrapper`（base_vec_env.py:L360）持 `self.venv`（base_vec_env.py:L375），几乎全部方法一行转发（base_vec_env.py:L384-423），reset/step_wait 反而留抽象；`class_attributes` 构造时快照反射（base_vec_env.py:L382）。魔法在 `__getattr__`（base_vec_env.py:L425）：找不到的属性沿 venv 链递归下钻（base_vec_env.py:L450），双向 `getattr_depth_check`（base_vec_env.py:L468）检测同名属性被两层 wrapper 遮蔽的歧义，命中即抛带定位的 AttributeError（base_vec_env.py:L430）。`CloudpickleWrapper`（base_vec_env.py:L487）换 cloudpickle 序列化（base_vec_env.py:L497），让 lambda 能进子进程。

## 三、外部连接

两个实现分踞进程模型两极：`DummyVecEnv`（dummy_vec_env.py:L15）同进程顺序执行，构造时检测"env 函数返回同一实例"（dummy_vec_env.py:L32）；`SubprocVecEnv`（subproc_vec_env.py:L79）每 env 一进程，`_worker`（subproc_vec_env.py:L20）跑命令循环，父侧经 `mp.Pipe` 通信（subproc_vec_env.py:L116），默认 forkserver（subproc_vec_env.py:L112，线程安全见 issue #217），daemon=True 防孤儿挂死（subproc_vec_env.py:L121），构造尾握手取 space（subproc_vec_env.py:L126）。

wrapper 子孙：vec_normalize/vec_monitor/vec_frame_stack 等，全沿 self.venv 委托、可任意叠层。消费方：collect_rollouts 每步 `env.step(actions)` 喂整批动作，off_policy 同构；两个实现都 import patch_gym 兼容旧 gym（subproc_vec_env.py:L17）。

## 四、数据流

step 全链路：算法交出 (n_envs, action_dim) 动作 → step_async（Subproc 逐 pipe 发 step 命令，subproc_vec_env.py:L131；Dummy 仅存引用，dummy_vec_env.py:L53）→ step_wait 收齐（Subproc 逐 remote.recv 后 np.stack，subproc_vec_env.py:L136；Dummy 顺序执行，dummy_vec_env.py:L56）。**gym→SB3 折叠**两侧同构：5 元组 → done = terminated or truncated（dummy_vec_env.py:L63 / subproc_vec_env.py:L37）；`info["TimeLimit.truncated"] = truncated and not terminated`（dummy_vec_env.py:L66 / subproc_vec_env.py:L38）保住 bootstrap 的"真终止 vs 截断"之别；done 时 `info["terminal_observation"]` 存终帧并自动 reset（dummy_vec_env.py:L70-71 / subproc_vec_env.py:L41-42）。VecEnv 由此没有 episode 边界。

堆叠契约：obs 由 `_stack_obs`（subproc_vec_env.py:L230）按 space 类型分派——Dict 逐 key、Tuple 逐位、普通直接 `np.stack`（subproc_vec_env.py:L245-253），env 索引进第 0 轴；rewards/dones 是 `(num_envs,)` 数组；**infos 保持 list[dict] 不并成数组**。Dummy 侧常驻 buffer、返回时 copy 防别名（dummy_vec_env.py:L47、L73）。

seed/options 延迟语义：`seed()` 当场只写 _seeds，注入在下一次 reset（dummy_vec_env.py:L78 / subproc_vec_env.py:L144 发 `(seed, options)`，worker 在 subproc_vec_env.py:L46 才调 `env.reset(seed=...)`），用完即清空（base_vec_env.py:L96）——base_vec_env.py:L296 的 WARNING 注释明示这是 gym 0.26 语义迁移。set_options 同构（dummy_vec_env.py:L77）。

## 五、设计决策

**权衡一：step_async/step_wait 拆分。** 为真异步预留：SubprocVecEnv 先全 send 再全 recv，理论上 worker 计算可与父进程重叠；但 DummyVecEnv 里是假异步（只存动作，dummy_vec_env.py:L53），SB3 核心的 step 模板也只是连打（base_vec_env.py:L214-222），重叠收益从未被核心利用。代价：裸调 step_wait 拿脏数据，wrapper 须同时转发两个半步（base_vec_env.py:L384）。这是"为可能的并行性支付永久的 API 复杂性"。

**权衡二：自动 reset 折叠 episode 语义。** 换来"无限流"接口——主循环零 done 分支、buffer 永不空转；代价是语义稀释：off-policy 必须记得从 info 捞 `terminal_observation` 存 replay buffer（HER/QR-DQN 必答），漏掉即静默错误；TimeLimit.truncated 同为 bootstrap 正确性暗线。

**权衡三：__getattr__ 魔法委托。** 动态转发让任意属性跨任意层 wrapper 可达，省几十个样板转发；代价是属性遮蔽难排查——对策是 depth_check 双向发现即报 ambiguous、报错带 module.class 定位（base_vec_env.py:L430），构造时快照 class_attributes 免得每次都反射（base_vec_env.py:L382）。

**权衡四：#2284 文件句柄修复（subproc_vec_env.py:L162）。** close() 在 join 子进程后补 `remote.close()` 关父侧 pipe（subproc_vec_env.py:L166）——此前依赖 GC 回收，超参搜索这类长循环反复建/删 SubprocVecEnv 时 fd 泄漏撞上 `Too many open files`。修复仅 6 行，2026-09 合入（commit 7cfb4dd）。教训：显式关闭别指望 GC。

**权衡五：Dummy vs Subproc 进程模型。** 判据在 SubprocVecEnv docstring（subproc_vec_env.py:L84）：env 非 IO 密集时 n_envs 不应超逻辑核数；轻环境用 Dummy——每步 pickle 往返的 IPC 开销反超并行收益。forkserver/spawn 线程安全但要求 `if __name__ == "__main__"`（subproc_vec_env.py:L87），fork 免此约束但与线程不安全库冲突——默认选前者。

## 六、新人提示

step 返回 4 元组：terminated/truncated 已折叠进 done，要区分读 info["TimeLimit.truncated"]。done 后同一步返回的 obs 已是下个 episode 首帧，终帧在 info["terminal_observation"]。infos 是逐 env 的 list[dict]，别按数组批处理。`make_vec_env(lambda: env)` 复用同一实例直接 ValueError（dummy_vec_env.py:L32），构造函数须每次 new。seed 在 reset 前调、只生效一次。长循环反复建 SubprocVecEnv 务必 close()——修复后 pipe 才真关闭。跨 wrapper 取属性优先 get_attr/env_method，unwrapped（base_vec_env.py:L327）一键到底。

> 元数据：非空格字符 4800 ｜ 锚 60 组/去重 70 个（主 base_vec_env.py，交叉 dummy_vec_env.py、subproc_vec_env.py）｜ 六节齐/5 组权衡 ｜ @master(b2878f4)
