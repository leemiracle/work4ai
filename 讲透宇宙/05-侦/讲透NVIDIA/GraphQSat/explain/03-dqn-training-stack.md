# 03 · Python Q-learning 训练栈 —— gqsat 包与 dqn.py 主循环

> 对象：`dqn.py`（327 行，仓库根）、`gqsat/agents.py`、`gqsat/models.py`、`gqsat/buffer.py`、`gqsat/learners.py`、`gqsat/utils.py`、`evaluate.py`、`add_metadata.py`
> 一句话：一个把训练主循环整个写在 `if __name__ == "__main__"` 里的科学脚本，配上"图网络出 Q 值、变长动作空间上取 max"的 DQN 变体——agent 的每个动作是"给某个变量赋真/假"，Q 网络在二部图（变量节点×子句节点）上做消息传递后对每个变量节点输出两个 Q 值。

## 一、角色定位

C++ 侧（前两篇）提供的是一个"每步停一次、等一个 ±var 决策"的 SAT 求解环境；本篇的 Python 栈是消费它的 RL 训练系统。分层很清楚：

- `dqn.py`（仓库根，非 gqsat 包内）：训练入口脚本。全部三个函数（`dqn.py:33` 的 `save_training_state`、`dqn.py:76` 的 `get_annealed_eps`、`dqn.py:88` 的 `arg2activation`）都是主循环的辅助件，真正的训练流程是 `dqn.py:99` 起的 `if __name__ == "__main__":` 直线脚本，约 230 行，无任何 `train()` 封装——典型的"论文实验脚本"风格：牺牲复用性换取流程一目了然。
- `gqsat/`：四个可复用件——`agents.py` 决策者、`models.py` 图网络、`buffer.py` 回放缓冲、`learners.py` 学习器；`utils.py` 承担参数解析/环境构造/图批处理/评估四职（`gqsat/utils.py:130` 的 `build_argparser`、`gqsat/utils.py:435` 的 `make_env`、`gqsat/utils.py:381` 的 `batch_graphs`、`gqsat/utils.py:456` 的 `evaluate`）。
- `evaluate.py`/`add_metadata.py`：评估线两个入口，后者专门生成"MiniSat 基线步数表"。

注意目录事实：`dqn.py`、`evaluate.py`、`add_metadata.py` 都在仓库根而非 `gqsat/` 内（README 的训练命令是 `python dqn.py ...`），gqsat 是被它们 import 的库包。

## 二、内部结构

### 2.1 dqn.py：__main__ 直线脚本

脚本分两臂：**续训臂**（`dqn.py:108-152`，`args.status_dict_path` 非空时）从 `status.yaml` 恢复全部训练状态——模型（`dqn.py:119-122` 的 `SatModel.load_from_yaml` + `load_state_dict`）、target 网（`dqn.py:124-127`）、回放缓冲 pickle（`dqn.py:130-131`）、优化器与调度器（`dqn.py:135-142` 连类对象都序列化了：`optimizer_class`/`scheduler_class` 存的是类型本身，恢复时重新构造再灌 state_dict）；**从头臂**（`dqn.py:154-212`）创建 `SummaryWriter` 并把 `writer.logdir` 就地用作输出目录（`dqn.py:156-157`），构造网络、deepcopy 出 target 网（`dqn.py:204`）。

主循环双层：外层 `while learner.step_ctr < args.batch_updates`（`dqn.py:217`）以**学习器更新次数**（而非 episode 数或环境步数）为终止条件；每 episode `env.reset(args.train_time_max_decisions_allowed)`（`dqn.py:220`）——这个 cap 传入后，超过它的决策会由环境自动回落 VSIDS（第 1 篇的 `max_decision_cap` 机制）。内层 `while not done`（`dqn.py:234`）：`agent.act(hist_buffer, eps=annealed_eps)` → `env.step(action)` → `buffer.add_transition`（`dqn.py:236-238`）。学习触发的门控在 `dqn.py:244-247`：每 `step_freq` 个环境步、且缓冲量超过 `max(init_exploration_steps, bsize+1)` 时调一次 `learner.step()`。评估触发的门控在 `dqn.py:269`：`args.env_name == "sat-v0" and not learner.step_ctr % args.eval_freq`——用字符串字面量比对 gym 注册 id，是脚本与环境注册体系（第 2 篇）的又一处弱耦合。

`history_len > 1` 直接 `raise NotImplementedError`（`dqn.py:223-226`）：图观测下历史堆叠未实现，`hist_buffer` 实际恒为单帧。

### 2.2 agents.py：三类决策者

- `Agent` 基类（`gqsat/agents.py:20-25`）：抽象 `act`/`__str__`；
- `MiniSATAgent`（`gqsat/agents.py:28-35`）：`act` 恒返回 `-1`——环境侧（`minisat/minisat/gym/MiniSATEnv.py:281-282`）把负决策翻译成 32767 哨兵，即"永远让 VSIDS 决策"的基线臂；
- `RandomAgent`（`gqsat/agents.py:38-49`）：均匀采样动作空间；
- `GraphAgent`（`gqsat/agents.py:52`）：**独立类，不继承 Agent**（签名无括号）——它多拿了 `net/args` 构造参数且 `act` 带 `eps` 形参，与基类协议不兼容，作者索性不装样子。`forward`（`gqsat/agents.py:60-73`）跑网络后用 `vdata[:, VAR_ID_IDX] == 1` 过滤出变量节点的输出（第 2 篇的跨包常量契约在此消费）；`act`（`gqsat/agents.py:75-82`）按 ε 随机选未赋值变量的 2i/2i+1，否则 `choose_actions` 取展平 Q 的 argmax（`gqsat/agents.py:84-85`）。

### 2.3 models.py：图网络与 inspect 魔法

文件头声明拷贝改写自 PyTorch Geometric 的 MetaLayer 文档源码（`gqsat/models.py:1-2`）。三层结构：

- `ModifiedMetaLayer`（`gqsat/models.py:35-50`）：给 MetaLayer 加了 `v_indices/e_indices` 透传——为了让批内多图的聚合算子知道每个节点/边属于哪张图；
- `GraphNet`（`gqsat/models.py:112-233`）：单次消息传递块。edge_model/src-dest 拼接、node_model/scatter 聚合（sum 或 mean，`gqsat/learners.py` 之外的选择在 `gqsat/models.py:208-211`）、global_model/scatter_mean，三个闭包在 `gqsat/models.py:191-228` 定义后组装进 `ModifiedMetaLayer`；
- `EncoderCoreDecoder`（`gqsat/models.py:236-367`）：encode-process-decode 三段式。core 循环 `for st in range(self.steps)` 把 latent 与 encoder 输出 latent0 拼接后反复消息传递（`gqsat/models.py:337-345`）——`core_steps` 是网络深度（评估时可在 `evaluate.py:49-51` 用 `-1` 之外的值覆盖，等价于免重训改深度做消融）。

最有味道的是 `SatModel.save_to_yaml`（`gqsat/models.py:59-76`）：构造函数里传了 `save_name` 就自动把**构造实参**序列化成 yaml。实现靠 `inspect.stack()[len(cls.mro()) - 2]`（`gqsat/models.py:64-66`）回溯到叶子类 `__init__` 的栈帧，再用 `inspect.getargvalues` 抓局部变量。为什么取这一层？`SatModel.__init__` 里调 `save_to_yaml` 时，栈顶往上第 `len(mro())-2` 帧恰好是叶子类构造器（跳过 nn.Module 和 object）。注释自认局限："this WILL NOT work with multiple inheritance of the leaf children"（`gqsat/models.py:63`）——多重继承会打破 mro 深度与栈深度的对应。配套的 `load_from_yaml`（`gqsat/models.py:78-82`）用 `getattr(sys.modules[__name__], class_name)(**call_args)` 反射重建，实现模型结构随 checkpoint 自描述。这是把"超参与结构重建"问题 solved 在序列化层的巧解，代价是依赖解释器栈布局。

注意 `dqn.py:177-202` 构造网络时 `out_dims=(2, None, None)`（`dqn.py:184`）——只有变量节点有输出头，每变量恰好 2 个 Q 值（赋真/赋假），这正是动作空间"每变量二选一"在网络侧的形状表达。另有两处小节：u 维度没有独立超参，直接复用 e 的（`dqn.py:182` 的 `core_e_out_size` 第三次出现传给 u 槽位，`dqn.py:189`/`dqn.py:194` 同款）；全局观测 `global_in_size=1` 且输入恒零（`minisat/minisat/gym/MiniSATEnv.py:100`/`201`），u 通道基本是摆设。

### 2.4 buffer.py：环形缓冲与 idx+1 技巧

`ReplayGraphBuffer`（`gqsat/buffer.py:20-31`）用四个平行数组存转移：dones/rewards/actions 是 torch 张量，观测是 `np.zeros((size, 4), dtype=object)`（`gqsat/buffer.py:31`）——object dtype 让每个槽位存四个任意形状的 numpy 数组（vertex/edge/connectivity/global）。

采样（`gqsat/buffer.py:48-58`）的巧劲在**不存 next_state**：`self.batch(self.observations[idx + 1])`（`gqsat/buffer.py:56`）直接取下一槽位当后继状态。前提是转移严格按时间顺序写入环形数组（`add_transition` 的 `ctr` 递增，`gqsat/buffer.py:33-46`），相邻即后继。代价有三处补丁：(1) `curr_size = self.ctr - 1`（`gqsat/buffer.py:50`）防止取到未填充槽；(2) `dones` 初始化为全 1（`gqsat/buffer.py:27`）——空槽被当作终止态，即使误采也不会外推 Q 值；(3) episode 边界处 idx+1 可能跨到下一 episode 的首帧，靠 done 掩码（`gqsat/buffer.py:57` 的 `1.0 - self.dones[idx]`）把 target 压回纯奖励。省一半观测内存的设计，正确性完全依赖"顺序写入+掩码"两条纪律。

### 2.5 learners.py：变长动作空间上的 DQN 更新

`GraphLearner`（`gqsat/learners.py:22-47`）：Adam + StepLR + mse/huber 二选一（`gqsat/learners.py:28-38`），target 网常驻 eval 态（`gqsat/learners.py:26`）。

`step()`（`gqsat/learners.py:71-108`）是标准 DQN 目标在变长动作空间上的改造：

1. **target 侧**（`gqsat/learners.py:75-86`）：`no_grad` 下对 s_next 前向，得到每变量 2 个 Q；`idx_for_scatter` 按 `variable_nodes_sizes` 给每张图的每个变量节点铺 2 个重复图号（`gqsat/learners.py:77-84`），`scatter_max` 后每图一个 max-Q——这就是"max over actions"在"每图动作数=2×该图变量数"下的实现；TD 目标 `r + nonterminals * gamma * max_q`（`gqsat/learners.py:86`）。注意这是**vanilla DQN**（target 网自己取 max），不是 Double DQN；
2. **online 侧**（`gqsat/learners.py:88-94`）：`gather_idx = (var_vertex_sizes * qs.shape[1]).cumsum(0).roll(1)`、首元素归零后 `qs.flatten()[gather_idx + a]`——把全局动作 id `a`（展平 Q 向量下标）换算进当前 batch 的展平布局。`cumsum+roll(1)` 手法与 `batch_graphs` 的 `conn_adjuster`（`gqsat/utils.py:399-400`）同款，都是"变长段拼接后的段内偏移"问题；
3. 损失→裁剪梯度（`gqsat/learners.py:98-103`）→ 每 `target_update_freq` 步硬拷贝 target（`gqsat/learners.py:105-106`）→ `step_ctr` 自增并返回 loss/grad_norm/lr/average_q 字典（`gqsat/learners.py:108-120`）。`gqsat/learners.py:112` 的 `get_lr()` 在新 PyTorch 已废弃，老版本复现者留意。

`get_qs`（`gqsat/learners.py:49-58`）与 agent 的 forward 同样按 `VAR_ID_IDX` 过滤变量节点（`gqsat/learners.py:58`），并同时返回 `states[3]`——`batch_graphs` 七元组里的 `variable_nodes_sizes`（`gqsat/utils.py:388-392`/`421-429`），供 scatter 分段。

### 2.6 评估线

- `evaluate.py:28-55`：读 `status.yaml` 拿训练期 args，逐项被命令行覆盖（`evaluate.py:36-37` 的 `setattr` 循环），再 `load_from_yaml` 重建网络、`strict=False` 加载权重（`evaluate.py:53-55`，容忍 core_steps 改动导致的形状差异）；
- `add_metadata.py:24-55`：给问题目录生成 `METADATA` 基线——对同一批 CNF 分别以 `with_restarts=False/True` 两臂跑 `MiniSATAgent`（恒弃权决策，`add_metadata.py:30-38`），rollout 用 `env.step(action, dummy=True)`（`add_metadata.py:46`，dummy 路径只推进不重建观测，省掉图构造开销），把两种模式下的 MiniSat 步数写进文件（`add_metadata.py:62-68`）。环境侧的 `normalized_score = 基线步数 / agent 步数`（`minisat/minisat/gym/MiniSATEnv.py:324-330`）消费这份表——>1 即胜过 MiniSat 基线。这是全仓唯一"训练之前必须先跑"的数据准备步骤。

## 三、外部连接

- **向下**：`gqsat/utils.py:432` 的 `import gym, minisat`（副作用注册，第 2 篇）→ `make_env`（`gqsat/utils.py:435-453`）`gym.make(args.env_name, ...)` 把 `max_cap_fill_buffer/penalty_size/with_restarts` 等训练超参直通环境构造；
- **奖励语义**：Python 侧自算 `step_reward`——正常步 `-penalty_size`（默认 0.0001，`minisat/minisat/gym/MiniSATEnv.py:77`）、解出为 0（`MiniSATEnv.py:306-311`）；每步小罚 + 终点免罚 = 最小化决策数的密集信号。C++ 的 `env_reward` 不参与（第 1 篇）；
- **向上**：TensorBoardX 的 `SummaryWriter` 记录曲线（`dqn.py:156`、`dqn.py:285-304`）；`save_training_state`（`dqn.py:33-73`）在 `save_freq` 与 episode 末双 checkpoint（`dqn.py:255-267`/`dqn.py:317-327`），后者注释点明动机：episode 末的 buffer pickle 与被评估的模型在转移上保持一致；
- **CLI 对偶**：整条 Python 训练栈的地位，等价于 `minisat/minisat/simp/Main.cc:141-148` 那个 `while (S.env_hold)` 循环的"智能版"——CLI 用 VSIDS 填 agent_decision，这里用 Q 网络填。

## 四、数据流

一个训练步的完整旅程：`env.step` 返回图观测四元组 → `buffer.add_transition` 存槽位 ctr → 学习触发时 `sample` 出 batch → `batch_graphs`（`gqsat/utils.py:381-429`）把 batch 拼成一个"多连通分量的巨型图"：顶点/边/全局各自 concat，connectivity 用 `conn_adjuster` 平移段偏移（`gqsat/utils.py:398-408`），并预计算每图的变量节点数与节点/边归属表（`gqsat/utils.py:388-392`/`410-419`）→ 网络前向 → Q 值按变量节点过滤 → argmax/ε-随机得全局动作 id → `MiniSATEnv.step` 经 `decision_to_var_mapping`（观测压缩后局部行号→原始变量号，`minisat/minisat/gym/MiniSATEnv.py:144-147`/`233`）→ ±(var+1) 编码进 C++。

动作 id 的三段编码变换是这条栈最容易踩坑的地方：`GraphAgent` 产出的 2i/2i+1 是**压缩后变量行号**的编码，环境把它映射回原始变量，再转 DIMACS ±码——三个命名空间（batch 展平下标/局部变量行号/DIMACS 变量号）靠两次映射衔接，任何一次观测压缩（vars_remapping）变化都会牵动全部三处。

## 五、设计决策

**为什么主循环不封装成函数？** 科学脚本取舍：断点续训靠"全量状态转储"（`dqn.py:33-73` 连 optimizer/scheduler 的类对象都进了 yaml）而非框架 checkpoint；流程改动直接改脚本；代价是无法被别处 import 复用、单测只能整跑。同类项目里 RLlib 等框架的抽象成本被明确拒绝了。

**ε-退火按转移数而非 episode**（`dqn.py:76-85`）：SAT 问题的 episode 长度方差极大（几十到上万步），按 episode 退火会让探索率与问题规模耦合；按转移数对齐了"经验量"这一真实进度量。

**图批处理用拼图而非 PackedBatch**（`gqsat/utils.py:382-383` 注释 "we treat a batch of graphs as one mega graph"）：把 N 张图当 N 个连通分量拼成大图，一次前向出全部 Q——这是 PyG `Batch` 的手工前身，省掉了逐图循环的开销，代价是 scatter 系列全部需要显式归属表。

**target 网硬更新**（`gqsat/learners.py:105-106`）而非软更新：与 DQN 原文一致的保守选择；结合每图 max 的 target 计算，整个学习器是"结构适配"而非"算法改良"——GraphQ-SAT 的贡献重心在环境与表示（前两篇），学习算法保持最朴素基线。

## 六、新人提示

1. **跑训练前的依赖顺序**：先 `add_metadata.py` 生成各问题目录的 `METADATA`（否则 `normalized_score` 报错/环境打不出相对分），再 `dqn.py`；两者都要求工作目录能 import 到根目录的包。
2. **读 `dqn.py` 别找 train 函数**——它不存在。从 `dqn.py:99` 顺读即可；两个分支（resume/scratch）只在前 60 行分叉，之后是同一段主循环。
3. **调 `max_decision_cap` 族参数**时记住语义分工：`reset(max_decisions_cap)`（环境 Python 侧计步）与 C++ 侧 `decisions > max_decision_cap`（观测截断）是同一个值的两侧，但 Python 的 `step_ctr` 在超限后走"自动弃权"路径（`minisat/minisat/gym/MiniSATEnv.py:257-267`），`max_cap_fill_buffer` 决定超限后是否还收集转移——训评估行为不同全在这两个开关。
4. **报错先查版本**：这套栈钉在 2019-2020 生态（`Dockerfile:23` 的 python3.6 一路贯到 gym 旧 API、`np.int/np.long` 已废除的别名仍在 `MiniSATEnv.py:169`/`338` 使用、`yaml.load` 无 Loader 的老调用在 `gqsat/models.py:81`、`get_lr` 废弃在 `gqsat/learners.py:112`）——在新环境里这些会先于任何逻辑问题爆出来。
5. **理解 Q→decision 只需盯三行**：`gqsat/agents.py:69`（过滤变量节点）、`gqsat/agents.py:84-85`（展平 argmax）、`minisat/minisat/gym/MiniSATEnv.py:283-288`（2i/2i+1 → ±(i+1)）。想换策略（如采样而非 argmax、加 mask）只动这三处，网络与环境都不用改。
