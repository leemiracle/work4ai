# 02 · QEC 核心库两码族：surface_code 与 color_code

## 一、角色定位

`code/qec/` 是域知识基座：把码结构、含噪记忆电路、探测器错误模型（DEM）、同调等价（HE）沉淀为可复用对象，供 data/ 与 training/ 消费。子包 `surface_code/` 与 `color_code/` 平行展开，根级共享 noise_model.py（892 行，25 参数）、dem_sampling.py（380 行，GPU 采样）与 precompute_dem.py（2242 行，augmented-DEM 预计算）。两码族各有一套 memory_circuit/homological_equivalence/data_mapping/detector_input 四件套镜像加 `_torch` 加速版——平行复制而非抽象共用。

## 二、内部结构

**surface 侧** surface_code/memory_circuit.py（1499 行）三层积木：`SurfaceCode`（memory_circuit.py:28，3 方法）生成旋转面码结构；`Circuit`（memory_circuit.py:332，20 方法）是电路指令集；`MemoryCircuit(Circuit)`（memory_circuit.py:794）组装记忆实验：`_add_stabilizer_round`（memory_circuit.py:1107）逐轮稳定子测量。**模块级函数 `triangular_color_code_circuit(d)`（memory_circuit.py:1236）是 color code 电路构建器却住在 surface_code/ 目录**——color_code/memory_circuit.py:26 注释称其为 legacy reference implementation，目录语义错位的活化石。

**color 侧** color_code/memory_circuit.py（1773 行）自成一套且更胖：`Circuit`（L424）**23 个方法**、`MemoryCircuit(Circuit)`（L949）**10 个方法**（surface 版 20/4）。图谱摘要所记"23 方法/10 方法"实为 color 版数字；继承链也有两条，并非全仓唯一。color_code/color_code.py（787 行）的 `ColorCode`（color_code.py:74）实现矩形网格嵌入的三角 color code：`_generate_plaquettes`（color_code.py:180）铺三色 plaquette，`superdense_plaquette`（color_code.py:637）供 superdense 映射。reference_superdense_noise.py（596 行）的 `Si1000ReferenceNoiseSpec`（reference_superdense_noise.py:108）走窄路：电路骨架与 detector 布局不动，仅逐操作重注噪声指令以对齐论文 Si1000 语义。

**共享件**：`NoiseModel`（noise_model.py:169）是 25 参数电路级噪声契约——2 prep + 2 meas + 3 idle_cnot + 3 idle_spam + 15 cnot Pauli，与 config_public.yaml 的 noise_model 节一一对应；normalize 族（noise_model.py:91 起）归一 family/semantics/mode 三轴。`dem_sampling`（dem_sampling.py:195）从 DEM 的 (H, p) 批量采样错误帧：cuQuantum cuStabilizer `BitMatrixSampler`（dem_sampling.py:220；模块级 try 探测 dem_sampling.py:36）+ cupy 数组桥；`_touch_sampler_entry`（dem_sampling.py:102）做采样器缓存——同 H 复用、同 seed 可重放、stale 逐出。

**HE 四件**：surface 版 homological_equivalence.py（1275 行）实现论文 Section II.D 的 canonical 代表固定（docstring 署名 Muyuan Li）；color 版（1497 行）在 homological_equivalence.py:116 自署"AI Assistant (based on surface code HE)"——AI 辅助移植的内部自白。torch 版 surface 3362 行（**全仓最大单文件**）、color 800 行。

## 三、外部连接

- 上游：Stim（电路表示/采样）、cuQuantum cuStabilizer、cupy、torch。
- 下游：训练侧 data/generator_torch*.py 消费 augmented-DEM；推理侧 datapipe_stim.py:101 用 `compile_sampler().sample()`；training/evaluation 经 data_mapping 拿张量布局。torch 快速路径 memory_circuit_torch.py 两版（surface L56 `MemoryCircuitTorch` / color L63 `ColorMemoryCircuitTorch`）被 generator_torch_color 直接引用。
- precompute_dem.py:2189-2191 函数体内延迟 import `data.precompute_frames._load_noise_model`，注释明示"avoid a circular dependency"。

## 四、数据流

训练数据核心链：**Stim 电路 → DEM → GPU 采样 → 同调等价 → 训练张量**。NoiseModel 注入 MemoryCircuit 生成含噪电路 → 提取 DEM 得 incidence 矩阵 H 与概率向量 p → `dem_sampling(H, p, batch)` 在 GPU 出 detector outcome 帧 → HE 把同一陪集的等价错误固定为 canonical 代表 → data_mapping 展开成 (4, T, D, D) 四通道张量。augmented-DEM 预计算把 H/p/A 离线固化，取代 legacy frame 预计算——data/precompute_frames.py:18 docstring 明说"has been replaced by the Torch augmented-DEM pipeline"，残留的只是 25p 噪声配置加载 helper。

## 五、设计决策

1. **平行复制而非抽象基类**：Circuit 两码族各一份、方法集不重合——共享抽象收益抵不过电路语义差异，宁 duplication 不 wrong abstraction。
2. **延迟 import 断环**（precompute_dem.py:2189）：qec↔data 环依赖靠运行时 import 解开，代价是静态 import 图不完整。
3. **采样器缓存换吞吐**：采样器构建贵，以 H 为键缓存、LRU 逐出、同 seed 免重建。
4. **25 参数噪声模型当公共契约**：一个 dataclass 锚定配置、电路注入、DEM 提取三端，参数语义（"AB"= A 在 control、B 在 target）入 docstring 防歧义。
5. **reference noise 窄目标**：只换噪声指令不动骨架（头部自述 keep schedule fixed），把"对齐论文"与"重构电路"两风险解耦。

## 六、新人提示

- 先读 surface 三层（SurfaceCode→Circuit→MemoryCircuit）再看 color 版：色码版是加强重复非新范式。
- 找 color 电路构建别只搜 color_code/，legacy 版在 surface_code/memory_circuit.py:1236。
- HE 四件同名易混：surface 是原始实现（Muyuan Li）、color 是移植（homological_equivalence.py:116 自署 AI Assistant），出 bug 先对照 surface 语义。
- 无 cuquantum 环境 import 不炸：dem_sampling.py:36 try/except 兜底。
- surface 版 HE torch 3362 行是全仓最大单文件，按 X/Z 基分半读。

`字数|锚数`：3496|28（不计空格字符；行号锚=全锚24+缩写4）
