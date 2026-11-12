# 11 · 测试张量工厂：`tests/utils/tensors.py`

## 1. 角色定位

43 行（wc 实测），全测试体系的"地基中的地基"：把 12 个 torch 张量构造函数按 `DEVICE`/`DTYPE` 柯里化成带下划线后缀的便捷版本（`randn_`/`ones_`/`eye_`...），并提供 `make_inputs_and_targets` 一站式造输入/标签对。图谱实测 fan-in 62（61 条 imports 入边 + 1 条 documents）——全库 fan-in 之冠，从 scalarization 的 12 个 test 文件到 profiler 脚本全部引用它。它的存在回答一个工程问题：**如何让全测试套件在 CI 矩阵（cpu/cuda:0 × float32/float64）间无缝切换，又不污染被测代码的设备语义**——答案见文件头 3 行注释（:11-13）里那句关键自白：只为 tests 里的代码固定 device/dtype，"while not affecting code written in src"。

## 2. 内部结构：函数地图

| 行号 | 成员 | 职责 |
|---|---|---|
| :1-9 | imports | `functools.partial`（:1）是全部魔法的引擎；`from settings import DEVICE, DTYPE`（:4）；`torch.utils._pytree` 的 `PyTree, tree_map`（:6）；`get_in_out_shapes`（:8）；`fork_rng`（:9） |
| :11-13 | 设计注释 | 解释为何用柯里化而非 `torch.set_default_device` 或超大 `with torch.device(...)` 上下文——后两者会波及 src 侧代码 |
| :16-18 | 整型族 | `arange_`/`randint_`/`randperm_`——只固定 device（注释 :15 "Default device is most likely int"：这三个默认产整型，不动 dtype） |
| :20-27 | 浮点族 | `empty_`/`eye_`/`ones_`/`rand_`/`randn_`/`tensor_`/`zeros_`——同时固定 device+dtype（:20 注释 "Set it to the right kind of float"） |
| :30-36 | `make_inputs_and_targets(model, batch_size)` | 从模型架构反推输入/输出形状（:31 `get_in_out_shapes(model)`，实现在 `tests/utils/architectures.py:47`），`fork_rng(seed=0)`（:32）内分别造 inputs/targets（:33-34） |
| :39-43 | `_make_tensors` | 私有助手：`is_leaf` 判"形状元组"（:40-41），`tree_map(lambda s: randn_((batch_size, *s)), tensor_shapes, is_leaf=is_leaf)`（:43）——**PyTree 感知**，嵌套 tuple/dict 的多输入架构（Transformer 的 attention mask 等）也能逐叶造张量 |

上游 `tests/settings.py` 的机制（9 行文件之外的 35 行）：`_POSSIBLE_TEST_DEVICES = {"cpu", "cuda:0"}`（:5）与 `_POSSIBLE_TEST_DTYPES = {"float32", "float64"}`（6）圈定合法值；`os.environ["PYTEST_TORCH_DEVICE"]`（:9）读环境变量、非法值直接 ValueError（:13-17）、要 cuda 但不可用也炸（:19-20）；`DEVICE = torch.device(_device_str)`（:22）、`DTYPE = getattr(torch, _dtype_str)`（:35）。CI 矩阵的 float64 组与 GPU 组就是从这两个环境变量注入（`checks.yml` 的 include 项）。

## 3. 外部连接

**61 个 imports 消费者**（图谱）按层分布：`tests/unit/scalarization/` 全部 14 文件（test_random/test_stch/test_sum/test_uw/_inputs/test_constant/test_cosmos/test_dwa/test_famo/test_geometric_mean/test_imtl_l/test_mean/test_pbi…）、`tests/unit/aggregation/` 与 `autojac/` 大部、`tests/profiler/run_profiler.py`、`tests/plots/`、`tests/trajectories/` 等——**改任何一个函数签名等于触碰全测试面**。出边 3 条（图谱）：`tests/settings.py`、`tests/utils/architectures.py`、`tests/utils/contexts.py`——恰好是测试基建铁三角（配置/架构/随机性）。

**配套件的分工**：`tests/conftest.py` 的 autouse fixture `fix_randomness`（:22）固定 `rand.seed(0)`/`torch.manual_seed(0)`（:23-24），且 CPU 上强制确定性算法（:31 `torch.use_deterministic_algorithms(True)`，注释 :26-30 说明 GPU 跑 benchmark 时放行非确定性换速度）；`fork_rng`（`contexts.py:12`）在造数据时 fork 出独立 RNG 再 `torch.manual_seed(seed)`（:15）——与 fixture 的全局种子互补，保证"不同测试用不同数据、同一测试可复现"。`make_inputs_and_targets` 的随机性全部收在 `fork_rng(seed=0)` 门内（:32），同架构多次调用产出可复现的同批数据。

## 4. 数据流：一个聚合器测试的造数走读

以 `tests/unit/aggregation/test_values.py` 风格的用例为例（数值对拍类）：

1. **矩阵构造**：`randn_((m, n))`——:25 的 `partial(torch.randn, device=DEVICE, dtype=DTYPE)` 把 CI 注入的 float64/cpu（或 float32/cuda:0）烙进每个张量；测试代码里从此不再出现 device/dtype 字样，矩阵连读性极高；
2. **PyTree 路线**（模型级测试）：`make_inputs_and_targets(model, batch_size=8)`（:30）→ `get_in_out_shapes(model)`（:31，从 `architectures.py` 的 `INPUT_SHAPES`/`OUTPUT_SHAPES` 声明取 PyTree 结构）→ `_make_tensors`（:39）的 `tree_map`（:43）逐叶展开 `randn_((batch_size, *shape))`——嵌套形状树变成嵌套张量树；
3. **随机性闭环**：fixture 已播全局种子（conftest :23-24）；`fork_rng`（:32）再 fork 一次并重播 seed=0——即使测试中段有人改了全局 RNG，本函数产出不变；
4. **消费**：`model(*inputs)` 前向 → `backward(losses)` → 断言——产出的张量 dtype 与 src 侧参数一致（src 侧模型由测试另建、`.to(DEVICE)`），全链路无 dtype 漂移。

这条流的关键不变量：**src 代码看到的 device/dtype 全部来自显式参数（模型、数据都被 .to 过），而非全局默认**——`torch.set_default_device` 这类全局开关被有意回避（:12-13 注释点名批评），保证被测行为与生产环境一致。

## 5. 设计决策（含批判视角）

- **partial 柯里化 vs 全局默认**：三方案对比写在 :11-13——`torch.set_default_device` 影响面失控（src 里未显式设 device 的代码全被波及）、大 `with torch.device(...)` 上下文要求所有造数集中一处（测试做不到）；partial 把"设备正确的构造器"做成一等值传播，是最小侵入解；
- **下划线后缀命名**（`randn_`）：表明"这是 randn 的本地变体"而非新语义；与 numpy 的就地操作后缀（`arr.fill_`）撞名但语境无歧义；
- **PyTree 感知只在 `_make_tensors`**（:39-43）：单张量构造器不管树，树逻辑集中在模型数据入口——复杂度没有扩散；
- 批判视角一：62 fan-in（图谱）使本文件成为**事实上的测试公共 API**，却没有任何 deprecation 保护——删改一个函数名会一次性砸红几十个文件的 import，且 pytest 的报错是一片 import error 海而非单点失败；理想形态是像 src 一样维护 `__all__` 与弃用期，但测试代码通常不值得这套仪式；
- 批判视角二：`:16-18` 与 `:21-27` 两族的 dtype 处理差异（不带/带）依赖 torch 各构造器的默认 dtype 惯例（arange 默认 int64、randn 默认 float32），:15/:20 两行注释只是暗示——若某 torch 版本改默认值，两族划分会静默错位；
- 批判视角三：`make_inputs_and_targets` 只会造 `randn` 输入（:43 lambda 硬编码），图像/序列等需要特殊分布的测试还得自己造——通用性止步于"数值形状正确"。

## 6. 新人提示

1. 写新测试的造数纪律：tests 里一律 `randn_`/`tensor_` 等带下划线版本，**永远不要**裸调 `torch.randn`（会落到默认 device/dtype，在 CI 的 cuda/float64 组上变成隐性失败或精度不足）；
2. 跑局部矩阵：`PYTEST_TORCH_DTYPE=float64 uv run pytest tests/unit/aggregation -x`——双精度能抓 float32 掩盖的数值问题（聚合器测试尤其依赖）；GPU 组同理换 `PYTEST_TORCH_DEVICE=cuda:0`；
3. 多输入模型（PyTree 输入）的测试直接用 `make_inputs_and_targets`，配合 `tests/utils/architectures.py` 里现成的 54 个顶层架构类（含 ResNet18/Transformer）——新架构先进 architectures.py 声明 `INPUT_SHAPES`/`OUTPUT_SHAPES`，`test_engine.py` 与 mtl 测试就自动获得覆盖；
4. 随机数据断言数值时记得 fixture 种子（conftest :23-24）使同进程内多次造数**不同**（RNG 在推进）——需要固定对比就自己包 `fork_rng(seed=...)`（`contexts.py:12`）。
