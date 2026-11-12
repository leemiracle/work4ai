# 05 · frozen_lake.py — 表格型 MDP 的教科书范本

> 源码：`gymnasium/envs/toy_text/frozen_lake.py`（507 行）· 图谱定位：第 6 层「玩具文本与表格环境族」代表节点（fanIn 3/fanOut 14）

## 一、角色定位

FrozenLake（冰湖）是 Gymnasium 最经典的**表格型 MDP（tabular MDP）参考实现**：n×n 格世界里，agent 从左上角 `S` 出发绕开冰孔 `H`、走到右下角 `G`。MDP 全要素——状态、动作、转移概率、奖励、终止——浓缩在 500 行纯 Python+numpy 中，并**把转移概率显式物化为一张表 `P[s][a]`**，这在全仓独一份（控制类环境只有动力学方程）。正因这张表，它是 value/policy iteration 等 model-based 方法的标准试验场——算法直接读 `P` 做 Bellman backup，无需采样估计转移；官方 Q-learning 教程与 GIF 脚本（`gen_frozen_lake_gif.py:9`）以它为载体。注册表提供两个变体（`gymnasium/envs/__init__.py:140-155`）：`FrozenLake-v1`（4x4/100 步/阈值 0.70）与 `FrozenLake8x8-v1`（8x8/200 步/0.85）。**零第三方渲染依赖、确定性、毫秒级单步开销**，使其成为 CI 回归与教学的首选。

## 二、内部结构

文件按「模块级资产 → 类」组织。**模块级（frozen_lake.py:L15-80）**：① 动作常量 `LEFT/DOWN/RIGHT/UP=0..3`（L15-18）——顺序构成顺时针动作环，滑移扰动因此能用 `(a±1)%4` 表达；② `MAPS`（L20-32）预置 `"4x4"`/`"8x8"` 地图，字符语义 `S`=起点、`F`=冰面、`H`=冰孔（落入即终局）、`G`=终点；③ `is_valid`（L36-53）用 DFS 验证存在到 `G` 的通路；④ `generate_random_map(size=8, p=0.8, seed)`（L56-80）拒绝采样生成地图：按 `p` 撒 `F`，钉死左上 `S`/右下 `G`（L77-78），`is_valid` 验收不过重来。

**`FrozenLakeEnv(Env)` 类（L83）**：`metadata`（L226-229）声明三种 `render_modes` 与 `render_fps=4`。`__init__`（L231-322）参数优先级：`desc` 显式地图 > `map_name` 预置 > 皆空时随机 8x8（L240-243）；地图转 `dtype="c"` 字节矩阵（L244），格子判断即 `b"S"`/`b"H"` 比较。核心是**构造期一次性预计算整张转移表**：`self.P={s:{a:[]}}` 嵌套字典（L255），三重循环 `row/col/action` 填充（L283-301）。动作空间 `Discrete(4)`、观察空间 `Discrete(nrow*ncol)`（L303-304）；pygame 槽位惰性置 `None`（L309-322）。`render`（L350-363）分派：`ansi` 走 `_render_text`（L486-500），`human`/`rgb_array` 走 `_render_gui`（L365-475）——tile 整格铺底、overlay 按 64px 比例叠加（L398-407），裂纹用位置哈希 `(x*3+y*5)%7` 散布（L449-453），agent 精灵居中、落 `H` 被孔洞贴图遮盖（L462-466）；`_render_text` 用 StringIO 拼网格、`colorize` 标红当前位置（L492）。

## 三、外部连接

**向内依赖**（fanOut 14 去向）：`toy_text/utils.py` 的 `categorical_sample`（utils.py:L4-8）是全家族共享采样原语，frozen_lake/taxi/cliffwalking 共用；另有 `spaces.Discrete`、`seeding.np_random`（支撑 `reset(seed=)` 契约）、`utils.colorize` 与 `DependencyNotInstalled`。**向外被依赖**：注册体系经 entry_point 挂载两个 id；`make` 依 `max_episode_steps` 自动包 `TimeLimit`——这解释了 `step` 恒返回 `truncation=False`（L333-334 注释明言时间限制外包给 wrapper）。

**与 JAX tabular 版的共享资产关系（batch 5 图谱实证）**：`gymnasium/envs/tabular/` 仅有 Blackjack/CliffWalking 两个 JAX FuncEnv（FrozenLake 尚无 JAX 版），其复用模式是本家族的直接延伸——`tabular/blackjack.py:14` 显式 `from gymnasium.envs.toy_text.blackjack import SCREEN_SIZE, draw_table`（渲染借用 numpy 版画桌函数），`tabular/cliffwalking.py:12-16` 导入 toy_text 的 `AGENT_OFFSET/ART_CELL_SIZE/FLAG_OFFSET/LETTER_OFFSET` 精灵偏移常量。即 **numpy toy_text 是「资产源」，JAX tabular 是「逻辑重写 + 渲染资产复用」的消费方**；未来补 JAX 版时 `MAPS` 与格子语义必然同样被导出。

## 四、数据流

**构造期（一次性）**：`desc` 字符串列表 → bytes 矩阵 → 三张派生数据。① 初始分布：`np.array(desc==b"S")` 展平归一化（L252-253），支持多起点。② 转移表 `P` 由三个内嵌函数支撑：`to_s(row,col)=row*ncol+col` 压成一维状态号（L259-260）；`inc` 执行移动并 **clamp 在边界内**（L262-271），撞墙即原地不动；`update_probability_matrix` 返回 `(new_state, reward, terminated)`（L273-281），奖励按 `b"GHF".index(letter)` 查 `reward_schedule` 三元组，`terminated` 即落入 GH。填表分两支（L283-301）：当前格为 `G/H` 时写入吸收态自环 `(1.0, s, 0, True)`（L289-290）；`is_slippery=True` 时对动作环邻居 `[(a-1)%4, a, (a+1)%4]`（L293）各生成一条转移，概率为 `fail_rate/success_rate/fail_rate`，`fail_rate=(1-success_rate)/2`（L257）——顺时针环邻居恰是两个**垂直方向**，与 docstring 的 1/3-1/3-1/3 算例一致；`is_slippery=False` 则单条 `(1.0,...)` 确定性转移（L301）。

**运行期**：`reset` 先 `super().reset(seed=seed)` 初始化 `self.np_random`，再 `categorical_sample(initial_state_distrib,...)` 抽起点，返回 `(int(self.s), {"prob":1})`（L342-348）。`step(a)` 取 `self.P[self.s][a]`，逆 CDF 采样选出实际发生的一条（L325-327）——**环境随机性全部集中在这一个采样点**——更新 `self.s` 后返回五元组，info 里的 `prob` 是该转移概率，供重要性采样使用。状态仅一个整数，观察=状态。

**渲染期**：`human` 下 `step`/`reset` 自动 `render()`（L331-332）；`rgb_array` 取 `surfarray.pixels3d` 后 `transpose(axes=(1,0,2))` 转 (H,W,3)（L472-475）；`ansi` 零 pygame 依赖。

## 五、设计决策

**1. 预计算 P 表而非即时模拟**。`__init__` 把全部 nS×nA×3 条转移算好，`step` 退化为查表+采样。代价是构造期 O(nS·nA)（4x4 仅 48 条），换来 `step` 常数极小、DP 可直接消费 `P`、转移结构**可打印透明**三重收益。这是 toy_text 与物理引擎类环境的分野：前者 MDP 是「声明」出来的，后者是「涌现」出来的。

**2. 滑移在动作环上取邻居**。`(a±1)%4` 而非手写方向表，依赖 L15-18 常量恰好顺时针排列——改动常量顺序会静默破坏滑移语义。新版把 `success_rate` 参数化（docstring 版本史注明 v1.3），打破旧硬编码 1/3。

**3. 边界 clamp 而非弹回**。撞墙转移落在原地，配合滑移意味着贴墙走时打滑概率**汇聚到原地不动**——P 表中同一 `s'` 可有多条未合并条目，采样照常，但手写 DP 假设「每 (s,a) 的 s' 互异」会出错。

**4. 终止与截断职责分离**。环境只报 `terminated`，`truncation` 恒 False，时间截断交给 `TimeLimit`——裸环境是无限期 MDP，符合「语义最小化、策略性限制放 wrapper」分层原则。

**5. 零依赖分层渲染**。核心仅依赖 numpy；`ansi` 兜底，`human`/`rgb_array` 才惰性导入 pygame，缺失时抛 `DependencyNotInstalled`（L366-371）；裂纹位置哈希（L451）保证渲染跨帧稳定。

**6. 随机地图的拒绝采样**。不做智能构造，就是「生成-验证-重来」，靠 `p=0.8` 高冻结率让拒绝率可控；`seed` 使地图可复现。

## 六、新人提示

1. **阅读路径**：docstring（L84-224）→ 模块级四件套 → `__init__` 填表循环 → `step`/`reset` → 渲染两路。P 表读懂，环境即读懂。
2. **直接看 P**：`env.unwrapped.P[0][LEFT]`（`make` 返回 checker 包装，须 `.unwrapped`）；slippery 默认下 3 条 `(1/3, s', r, t)`——左手往左/上/下各 1/3。
3. **bytes 陷阱**：`desc` 是 `dtype="c"` 矩阵，格子值是 `b"S"` 不是 `"S"`；混用 str/bytes 是最常见报错源。
4. **采样原语细节**：`categorical_sample`（utils.py:L4-8）的 `argmax(cumsum(p) > random())` 用严格大于，零概率项永不选中；三邻居概率和恒为 1。
5. **自定义 desc 无校验**：`is_valid` 只在 `generate_random_map` 内调用，传不连通或无 `G` 的地图不报错、只表现为永不成功；多 `S` 合法。DP 迭代应在 `terminated=True` 处截断，否则 `G/H` 自环算成无限期停留。
6. **新参数测试薄**：`success_rate`/`reward_schedule` 未被单测覆盖，用前按 docstring L210-218 算例手验 `P` 表。
7. **写自己的环境**：frozen_lake 是「离散观察+离散动作+可枚举转移」类的最佳模板；转移不可枚举时学 CartPole 的即时计算路线。
