# 06 · pina/_src/domain/cartesian_domain.py —— 盒几何基元：区间字典驱动与四种采样

## ① 角色定位

`CartesianDomain`（pina/_src/domain/cartesian_domain.py:10）实现轴对齐超盒——一维区间的笛卡尔积，是域层最常用的几何基元：图谱给它的 imports 入边 9 全部来自 problem zoo（poisson/burgers/helmholtz/advection/allen_cahn/acoustic_wave/diffusion_reaction/inverse_poisson 加域桶）。它的全部语义由一个 key→区间或定点值的字典驱动（`{"x": [0, 1], "y": [0, 1]}` 或 `{"t": 0.0}`），支持四种采样模式，并且是唯一实现全部模式的几何——Ellipsoid/Simplex 只支持 random，这正是 base_problem.py docstring warning（L110-120）所述限制的几何侧根源。

## ② 内部结构

| 成员 | 行号 | 职责 |
|---|---|---|
| `__init__` | pina/_src/domain/cartesian_domain.py:21 | 调基类解析字典；注册 `_sample_modes` 五个模式名（L38，lh/latin 同义） |
| `is_inside` | pina/_src/domain/cartesian_domain.py:40 | 内外判定：定点维精确比对 + 区间维开/闭不等式（L62-86） |
| `sample` | pina/_src/domain/cartesian_domain.py:88 | 主入口：分流 range/fixed、joint/per-variable 采样、拼 LabelTensor |
| `_sample_range` | pina/_src/domain/cartesian_domain.py:189 | 采样内核：[0,1] 上布点后线性重标定到 bounds（L200-214） |
| `partial` | pina/_src/domain/cartesian_domain.py:216 | 边界构造：每个区间维生成上下两面（L229/232），返回 `Union`（L236） |

字典解析不在本文件而在基类 `BaseDomain`（pina/_src/domain/base_domain.py:9）：`__init__` 把每个值分进两只桶 `_fixed`/`_range`（L37-38）——标量进定点桶（L62-66），二元 list/tuple 进区间桶且 `low >= high` 直接拒绝（L69-76）；`variables` 属性返回排序后的全部键（L176-183）；另有跨域更新 `update`（L86）与采样参数校验 `_validate_sampling`（L122，被 sample 的 L141 调用）。

## ③ 外部连接

imports 出边 4（pina/_src/domain/cartesian_domain.py:4-7）：base_domain（继承）、union（partial 的返回类型）、core/utils（采样算法）、label_tensor（返回载体）。采样算法全部下沉塔基：`torch_lhs`（pina/_src/core/utils.py:182）供 lh/latin，`chebyshev_roots`（pina/_src/core/utils.py:235）供 chebyshev——域层不实现数值算法，只做几何语义，这是"金字塔依赖向 core 汇聚"的典型样本。`Union`（pina/_src/domain/union.py:9，`BaseOperation` 子类）承接 partial 的面列表并按集合运算分发采样（pina/_src/domain/union.py:49）。tested_by 出边 1 指向 tests/test_domain/test_cartesian_domain.py（163 行）。

## ④ 数据流

从 pina/_src/problem/zoo/poisson_problem.py:70 的 `CartesianDomain({"x": [0, 1], "y": [0, 1]})` 到边界采样点的全链：

1. BaseDomain 解析得 `_range={"x":(0,1),"y":(0,1)}`、`_fixed={}`；
2. 问题里 `"boundary": spatial_domain.partial()`（pina/_src/problem/zoo/poisson_problem.py:74）触发 partial：对每个区间维 v 构造把 v 钉死在下/上界的两个盒（pina/_src/domain/cartesian_domain.py:229/232），2D 共 4 面，`Union(faces)` 返回（L236）；
3. `problem.discretise_domain(n, "grid", domains=["boundary"])` 落到 `sample(n, mode)`（L88）：`_validate_sampling` 先行（L141），再分离 range 与 fixed 维（L144-145）；若全是定点维则提前返回常量列（L148-153）；
4. grid/chebyshev 分支逐维采样再外积（L163-170）：每维 `_sample_range` 内 `torch.linspace(0,1,n)`（L206）重标定后 `torch.cartesian_prod` 合成 n^d 点阵（L170）；random/lh/latin 则联合采样、总量恒为 n（L159-160，`torch_lhs` 在 [0,1]^d 内一次布点）；
5. 定点维用 `torch.full` 拼列（L173-178），结果 `as_subclass(LabelTensor)` 并贴标签（L184-185），最后按标签字母序重排列（L187）上交问题层。

`_sample_range` 的重标定公式 `pts * (hi - lo) + lo`（L214）是所有模式共享的出口——四种策略只差 samplers 字典（L200-209）里 [0,1] 上的布点方式：random 用 `torch.rand`（L201）、chebyshev 用 `chebyshev_roots(n).mul(0.5).add(0.5)`（L202-205）、grid 用 `torch.linspace`（L206）、lh/latin 共用 `torch_lhs`（L207-208）。

## ⑤ 设计决策（含批判视角）

- **统一"先采样后重标定"**：五种模式收敛到一个字典加一行线性映射，新增模式只需加一个 lambda；代价是端点语义不齐——grid 的 linspace 闭区间保证采到极值，random 的 `torch.rand` 理论上取不到 0/1。docstring warning 明言只有 grid 模式采到极值（L118-120），意味着 Dirichlet 边界配点靠 random 是不完整的。
- **joint 与 per-variable 的语义分裂**：random/lh 输出 n 点，grid/chebyshev 输出 n^d 点（note L110-116 写明）。换模式不换 n，点数静默幂次化，是新手配点数失控的头号来源。
- **定点维 int64 陷阱**：定点值直接进 `torch.full`（L149、L175），传 Python int（`{"t": 0}`）会产出 int64 张量，直到 autograd 求导才报错。仓内 AI 技能规则 .opencode/skills/RULES.md:59-63 明文规定定点变量必须写 float——类型系统漏洞由技能文档兜底，这是可验证的坏味道。
- **is_inside 的开闭语义**：默认严格不等式（L82），`check_border=True` 才含边界（L71-77）；而 grid 采样恰好产出边界点——对 grid 点集用默认 is_inside 会判 False，语义坑被参数化而非消除。
- **partial 不去重**：2D 边界 4 面的角点、3D 各面的共享棱都会重复出现；random 采样取不到面边缘时问题被掩盖，grid 采边界时重复点直接双倍计数，无显式去重也无文档警示。
- **字母序输出**（L187）：列序与字典书写顺序解耦，保证 LabelTensor 列与方程标签对齐的稳定性——好的决定，代价是调试打印顺序与声明顺序不一致。

## ⑥ 新人提示

- 定点维永远写 float：`CartesianDomain({"t": 0.0})`；`{"t": 0}` 会埋 int64 雷（.opencode/skills/RULES.md:59-63）。
- `grid`/`chebyshev` 的 n 是**每维**点数、总量 n^d；`random`/`lh`/`latin` 的 n 才是总量。
- `lh` 与 `latin` 是同一实现的两个名字（L207-208），tutorial 里混用不是笔误。
- 边界条件标准写法是 `spatial_domain.partial()` 得到 Union 再挂给 Condition 的 domain；内部域直接用原 domain 对象。
- 要往已采样域加点走 `BaseProblem.add_points`（pina/_src/problem/base_problem.py:178），重复 discretise_domain 会整体覆盖。
- 验证几何判定时记得 `is_inside` 默认开区间，测边界点要传 `check_border=True`（pina/_src/domain/cartesian_domain.py:71-84）。

*自报：不计空格字符 4036；行号锚 58 处（file:line 锚 19 + 同文件 L 式行引用 39），均经 grep 对 commit 60ea474a 核实。*
