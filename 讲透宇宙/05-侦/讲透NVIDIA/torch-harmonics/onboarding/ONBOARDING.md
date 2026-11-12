# torch-harmonics 新人导航（ONBOARDING）

> 知识图谱版（commit c66375cf，625 节点/1206 边/10 层/12 步 tour，2026-11-11）；行号锚均经源码核实。

## 一、一图看懂

NVIDIA 的球谐函数（Spherical Harmonic Transform, SHT）库：给全球网格模型（SFNO 球面傅里叶神经算子、风乌式天气预报、S2Transformer）提供 PyTorch 原生的谱变换、DISCO 球面卷积、球面注意力与分布式底座。仓根自带 SKILL.md:1 技能索引与 .skills/ 两个 agent 技能（disco-kernel-dev、test-writing）——NVIDIA 也按 agent 协作开发维护本仓。结构上是三个世界：纯 PyTorch 数学核（L02）→ 原生 CPU/CUDA 内核（L03-L06）→ 分布式封装（L07）。10 层：

| 层 | 职责 | 代表文件 |
|---|---|---|
| L01 工程门面·CI·基准 | 仓根文档/CI/agent skill/benchmarks | setup.py、.github/workflows/build_wheels.yml |
| L02 球谐核心数学库 | SHT/Legendre/求积/谱卷积/重采样/随机场 | torch_harmonics/sht.py |
| L03 DISCO 分布式卷积 | 离散-连续卷积三形态+原生内核双代 | torch_harmonics/disco/convolution.py |
| L04 Attention Python 层 | 球面全局/邻域注意力封装 | torch_harmonics/attention/attention.py |
| L05 Attention CPU 内核 | CPU 前反向 C++（含 upsample 变体） | attention/optimized/kernels_cpu/ |
| L06 Attention CUDA 内核 | ring 注意力 sm90/sm100 双代路径 | kernels_cuda/attention_cuda_bwd_ring.cu（2212 行） |
| L07 分布式层 | polar/azimuth 进程组+逐层分布式化 | torch_harmonics/distributed/primitives.py |
| L08 示例模型与数据集 | SFNO/S2Transformer/S2UNet/S2Segformer/LSNO+PDE/SWE | examples/models/sfno.py |
| L09 Notebooks 教程镜像 | 13 篇教程（与 docs/tutorials 逐字节镜像） | notebooks/ |
| L10 测试与文档 | 24 个测试文件+Sphinx docs | tests/test_sht.py |

依赖方向：L02 是地基（quadrature.py fanIn 25 全仓第一，SHT/卷积/attention/损失全都消费它的求积权重）→ L03/L04 站其上并共享 ψ 邻域结构 → L05/L06 是 L04 的内核后端（L03 自带同构内核）→ L07 把 L02-L04 逐层包成并行版 → L08 消费一切；L01/L09/L10 是外围。

## 二、五分钟路线（12 步 tour→5 里程碑）

**M1 门面与技能（步1）**：README.md、SKILL.md:1（技能索引）、.skills/disco-kernel-dev/SKILL.md 与 .skills/test-writing/SKILL.md——内核开发全流程 checklist 与测试规范，是 agent 协作开发的实证。**M2 数学核（步2-5）**：先看 torch_harmonics/__init__.py:40 导出面分清五条线（SHT/谱卷积/求积/重采样/attention+disco）；torch_harmonics/sht.py:42 RealSHT 是心脏，legendre.py:183 预计算表+cache.py:38 自制 lru_cache 是数值底座；quadrature.py:508 QuadratureS2 与四种纬度权重（:320/:356/:387/:450）；spectral_convolution.py:43 SpectralConvS2、random_fields.py:37 GaussianRandomFieldS2。**M3 DISCO（步6-7）**：disco/convolution.py:484 主层 → optimized/disco_optimized.py:74 按 SM_90a/SM_100a 选 kpacked 内核 → kernels_cuda/ 双代 .cu 与 kernels_torch 参考实现。**M4 Attention（步8-10）**：torch_harmonics/attention/attention.py:253 NeighborhoodAttentionS2（DISCO 的注意力对偶）→ _layout.py:139 布局真源 → kernels_cuda/attention_cuda_bwd_ring.cu 2212 行最重内核 → kernels_cpu/ 无 GPU 正确性基准。**M5 分布式+模型+测试（步11-12）**：distributed/utils.py:83 init 建 polar/azimuth 正交组 → primitives.py:304 通信原语 → examples/models/sfno.py:174 SFNO 装配 → tests/test_convolution.py:68 稠密参考实现收尾。

## 三、核心子系统深读

### 3.1 SHT 与数值底座（sht/legendre/quadrature/truncation/cache/utils）
sht.py:42 RealSHT 的 forward（sht.py:148）只有两步：经度 rfft（sht.py:169）+ 纬度与预计算 Legendre 表的 einsum 收缩（sht.py:178，`...mk,mlk->...lm`）。2π 尺度因子在构造期折进求积权重（sht.py:136），省掉每次 forward 对复数张量的点乘——一次预计算换千次运行。四类变换：RealSHT:42、InverseRealSHT:187、RealVectorSHT:330、InverseRealVectorSHT:488（向量版服务梯度/旋度等谱运算）。数值底座三层：legendre.py:183 `_precompute_legpoly` 用 `@lru_cache(typed=True, copy=True)` 按 (mmax,lmax,nlat,grid,norm,csphase) 缓存（:367 是第二个缓存入口）；cache.py:38 是自制 lru_cache——copy=True 深拷贝出参，防止调用方改动污染缓存表；quadrature.py 提供梯形(:320)/Legendre-Gauss(:356)/Lobatto(:387)/Clenshaw-Curtis(:450) 四种权重与 precompute_latitudes(:110)（网格点+权重一体缓存）；truncation.py:93 truncate_sht 决定 lmax/mmax 组合保证正逆可逆。torch_harmonics/utils.py:122 `_EnsureContiguous` autograd Function 在实空间做 copy（:103）——绕过 Inductor 无法生成读写 complex buffer 的 Triton 内核这一限制的关键技巧。

### 3.2 DISCO 全栈：三形态卷积张量+双代 tensor core 内核
disco/convolution.py:414 DiscreteContinuousConv ABC → :484 DiscreteContinuousConvS2 → :852 转置卷积。卷积张量 Ψ 三形态：稠密参考（tests/test_convolution.py:177 `_precompute_convolution_tensor_dense`，纯 Python）→ CSR 稀疏（层内 psi_idx/psi_vals，convolution.py:661 `_get_psi`）→ kpacked 紧凑 kernel 布局（disco_optimized.py:92 `_maybe_kpack_psi`：blocked-CSR，每个邻居携带全部 K_pad 值成一个块——正是这个块布局让 tensor core 收缩成为可能；注释还记录了 NBR_PAD 填充从半分辨率 ~33MB/高分辨率 ~274MB 到紧凑化的内存修复史）。内核双代：`_kpacked_supported_on_device`（disco_optimized.py:74）按 compute capability 分发——9.x → WGMMA 路径（kernels_cuda/disco_cuda_fwd_dense_kpacked_sm90.cu，529 行）、10.x → tcgen05 路径（sm100.cu，392 行），设备不匹配则回退 CSR 路径"correct everywhere"。disco_cuda.cuh:52 起的 gather helper 注释详述半字布局 word 偏移推导（P=1 需 5 个 word、P=2 需 8 个，替代 8 次标量 2 字节加载）；disco_cuda_ptx.cuh 同一套 cp_async_16B helper 按 __CUDA_ARCH__ 条件编译，是双代共享底座。kernels_torch/disco_torch.py:51 是纯 PyTorch 参考实现，永远可用。

### 3.3 Attention 三层：Python/CPU/CUDA 与 ring 双代
attention/attention.py 两个入口：AttentionS2:49（全局 O(N²)）与 NeighborhoodAttentionS2:253（测地盘邻域 O(kN)，与 DISCO 共用 ψ 邻域结构——attention.py:44 直接 import `_precompute_convolution_tensor_s2`，ψ 即 DISCO 零阶核的支撑集）。分发在构造期一次完成：attention.py:348 探测 optimized 内核可用性，attention.py:464 起 attention_handle 二选一（optimized/torch），forward 里 :568 直接调用零分支。NHWC 化是本子系统最值得读的设计：_layout.py:139 to_nhwc/:164 to_nchw 是唯一转换点；attention_interface.cpp:71-77 注释明言"布局在模块边界显式转换而非 stride 推断——退化维度下两种布局 stride 不可区分"（H*W==1 时 contiguous NCHW 的 stride(1)==1 与 NHWC 无法区分，_layout.py:38 同款规则）；attention.py:511 起的 forward 注释解释了为什么全程 NHWC（1×1 投影变成纯 GEMM、head split 变 free view、反向转换由 autograd 自动生成）。kernels_torch/attention_torch.py:467 用 `@torch.library.register_fake` 注册 PT2 compile 的 meta 内核。CPU 内核（optimized/kernels_cpu/：fwd 154 行/bwd 146 行/permute/upsample 变体，bwd_upsample.cpp 365 行最大）保证无 GPU 环境的正确性基准；CUDA 侧 kernels_cuda/attention_cuda_bwd_ring.cu 2212 行是仓内最重内核，同文件含 sm90 WGMMA 与 sm100 tcgen05 双路径，两遍式反向（pass1 重算 softmax 权重与统计量、pass2 按 ψ 行累计 dq/dk/dv）；fwd_ring.cu 1198 行是 online softmax max-rescale-finalize 三段式的 ring 版实现。

### 3.4 分布式层与示例模型
distributed/utils.py:83 init 显式接收两个进程组：polar 组（:73，纬度分片）与 azimuth 组（:78，经度分片），两组正交使 collectives 互不干扰；_DistributedConfig:43 单例持有全局状态。primitives.py 中每个通信原语都是 torch.autograd.Function+setup_context+backward 三件套（如 :304 _DistributeTransposeAzimuth、:340 _DistributeTransposePolar，symbolic 节点支持 torch.export），:396 _reduce 等 84 个 fanOut 的原语面是全仓最大。逐层分布式化：distributed_sht.py:51/251/432/614 四类 Distributed SHT、distributed_spectral_convolution.py:46、distributed_convolution.py:225/597、distributed_attention.py:878 DistributedNeighborhoodAttentionS2（局部 ψ 取代基类全局 ψ 的注释链很值得一读）、distributed_resample.py:45。注意 distributed/_amp_utils.py:67 `_cast` 逐字复制了 torch.amp.autocast_mode._cast 私有 API——torch 升级断点区。示例模型：examples/models/sfno.py:174 SphericalFourierNeuralOperator（:340-343 构造上/下采样与内部网格四个 SHT 句柄）、s2transformer.py:365 SphericalTransformer、s2unet.py:404 SphericalUNet、s2segformer.py 与 lsno.py，全部站在 examples/models/_layers.py 共享层库上；examples/shallow_water_equations.py:43 ShallowWaterSolver 是谱方法浅水方程求解器（训练数据源）；examples/losses.py 是按球面求积权重积分的损失模板基类族。

## 四、数据流走查：SFNO 一层的一生 + DISCO 卷积前向

1. **网格到谱**：物理空间信号 (B,C,nlat,nlon) 进入 examples/models/sfno.py:340 构造的 RealSHT → sht.py:148 forward：rfft 经度（sht.py:169）→ 转置使 nlat 落快轴（sht.py:172）→ 与折入权重的 Legendre 表 einsum（sht.py:178）→ 复系数 (…,lmax,mmax)。
2. **谱域乘法**：spectral_convolution.py:43 SpectralConvS2 在 (l,m) 模式上乘可学习权重（FNO/SFNO 的核心算子）；SFNO 块内用的则是 _layers.py:379 的旧版同名实现（见第六节坑 1）。
3. **谱回网格**：InverseRealSHT（sht.py:187）Legendre 综合+逆 FFT 回物理空间；再过 MLP/位置嵌入（examples/models/_layers.py）完成一个 SFNO block。
4. **DISCO 卷积支路**：convolution.py:484 forward 用 CSR ψ 做稀疏收缩；disco_optimized.py:74 判定设备支持后先 :92 `_maybe_kpack_psi` 转 blocked-CSR，再进 sm90/sm100 dense kernel（WGMMA/tcgen05）；不支持回 CSR 内核，无编译扩展时回 disco_torch.py:51 纯 torch 路径——四层降级链层层保正确性。
5. **分布式版**：DistributedRealSHT 在进程组内做局部变换+all-to-all 转置完成全局变换；DISCO 把卷积核沿经度带切成可并行的 distrunc 段，每个 azimuth rank 持有一段；梯度经 primitives.py 的逆向 collective 自动回传。
6. **测试兜底**：tests/test_convolution.py:177 稠密参考实现是所有优化内核正确性的 ground truth。

## 五、依赖地图（枢纽 top10，按 fanIn）

| 枢纽文件 | fanIn | fanOut | 角色 |
|---|---|---|---|
| torch_harmonics/__init__.py | 27 | 9 | 顶层 barrel：五条线的公共 API 面 |
| torch_harmonics/quadrature.py | 25 | 24 | 求积中枢：权重被 SHT/卷积/attention/损失全消费 |
| tests/testutils.py | 18 | 27 | 测试共享：分布式上下文/种子/张量比较 |
| torch_harmonics/utils.py | 10 | 10 | 杂项：连续性保证/MOLA 火星高程加载 |
| torch_harmonics/distributed/utils.py | 10 | 6 | polar/azimuth 进程组管理与单例 |
| disco/optimized/disco.h | 10 | 0 | DISCO C++ 子系统 include 根（张量校验宏） |
| distributed/primitives.py | 9 | 84 | 通信原语库（1404 行，fanOut 全仓最大） |
| attention/optimized/kernels_cuda/attention_cuda.cuh | 9 | 0 | 六个 CUDA 算子的签名声明头 |
| attention/optimized/kernels_cuda/attention_cuda_utils.cuh | 9 | 2 | attn_params_t 参数结构体与调试设施 |
| attention/optimized/kernels_cuda/cudamacro.h | 9 | 0 | CHECK_CUDA 错误检查宏 |

规律：数学核（quadrature）与分布式原语（primitives fanOut 84）是两大引力中心；disco 与 attention 的 .h/.cuh 声明头 fanIn 高但 fanOut=0，是典型的"include 根"型枢纽——改它们等于全量重编；examples/models/_layers.py（fanIn 8/fanOut 28）是五个示例模型的共享地基。

## 六、坑与勘误（源码级发现）

1. **同名类两套实现**：examples/models/_layers.py:379 SpectralConvS2 与主库 spectral_convolution.py:43 SpectralConvS2 同名但为旧版独立实现（FNO 风格 per-mode 权重）；SFNO 实际用的是 _layers 版（sfno.py:37 import 实证）——读码极易混淆，追实现必须看清 import 来源。
2. **私有 API 复制**：distributed/_amp_utils.py:67 `_cast` 逐字镜像 torch.amp.autocast_mode._cast，注释自认 "which is private, hence the copy"——torch 版本升级的断点区。
3. **布局陷阱是设计出来的**：attention_interface.cpp:71-77 与 _layout.py:38——退化维度下 stride 推断无法区分 NCHW/NHWC，全栈强制模块边界显式转换；读 attention 代码时不要假设 contiguous 即 NCHW。
4. **scanner 双盲（工具链勘误）**：scan-result importMap 中 38 个 C++/CUDA 文件 20 个空（52.6%）、94 个 py 文件 18 个空；tree-sitter 对 .cu 内核签名与纯模板声明头全盲（attention_cpu_fwd.h L63 起、disco_helpers.h L37 起均手扫补充）——图谱内 C++ 符号的可信度靠批阶段人工甄别支撑。
5. **notebook 双份维护**：notebooks/ 13 篇与 docs/tutorials/ 13 篇逐字节 identical（cmp 实测 13/13 全 identical，tutorials 侧仅多一个 index.md）——图谱 layer 摘要写"12 对"是漏数；改一侧不改另一侧必然漂移，当前无自动同步机制。
6. **wheel 静默掉 CUDA 的历史事故**：.github/workflows/build_wheels.yml:267-270 注释自述 "it does not crash, it silently falls back to torch-native paths, so it survived several releases unnoticed"——CUDA-labelled wheel 不含 CUDA 内核时不报错；:270 起因此加了 .nv_fatbin/__cudaRegisterFatBinary 存在性断言。本地装了 wheel 却没跑原生内核时不报错，就是这个机制。
7. **writer 残留（流水线勘误）**：.understand-anything/tmp/ 残留 36 个 ua-file-analyzer-input-*.json 派发输入——finalize 清 intermediate/ 但不清 tmp/（TE 仓 110 个同理），后续仓收官须手工清。
8. **plotting 延迟导入**：plotting.py:36-43 matplotlib/cartopy 全部 try-import 守卫，缺失时给安装提示——core 包不强依赖可视化栈，裸环境 import torch_harmonics 不需要 cartopy。
9. **编译扩展的顶层导入**：attention.py:38 `from attention_helpers import ...` 是裸顶层模块名（setup.py:157 把扩展编译成顶层 attention_helpers 而非包内路径）；import 失败通常意味着没装编译产物而非路径问题，与常规 torch 扩展放包内的惯例相反。

## 七、如何跑起来

**安装三形态**（setup.py:112 get_ext_modules）：纯 Python（pip install，无扩展时自动回退 torch 路径）；CPU+OpenMP（`TORCH_HARMONICS_ENABLE_OPENMP=1`，setup.py:44）；CUDA（`TORCH_HARMONICS_BUILD_CUDA_EXTENSION=1` 或检测到 CUDA_HOME 可用，setup.py:129；编出 torch_harmonics.disco._C（setup.py:187）与 torch_harmonics.attention._C（setup.py:217）两个扩展，kpacked 内核需 TORCH_CUDA_ARCH_LIST 含 9.0a/10.0a）。**容器**：Dockerfile:41 `TORCH_CUDA_ARCH_LIST="8.0 8.6 8.7 9.0a 10.0a+PTX"` 覆盖 Ampere→Blackwell；:43 NVCC_THREADS=4 MAX_JOBS=8 控编译并行。**测试**：tests/run_tests.sh 先串行 pytest（test_convolution+test_sht），--distributed 时 ngpu=grid_lat×grid_lon（run_tests.sh:60）与库内 polar/azimuth 进程组一一对应；无多卡时 distributed 测试用 gloo 单进程多进程组模拟多 rank（tests/testutils.py:110 setup_distributed_context）。**基准**：benchmarks/bench.py 注册表模式+run.py 驱动，对照仓内 reference_results.csv（H100/GB200/GB300 三机矩阵）按架构+dtype 检 speedup 回归（run.py:106 _is_regression）。**环境**：requires-python>=3.10（pyproject.toml:31）、torch>=2.6.0（pyproject.toml:40）。

## 八、延伸阅读

- docs/guide/ 五篇：spherical_harmonic_transforms.ipynb（SHT 数学推导与归一化约定）、spectral_convolutions.ipynb、disco_convolutions.ipynb、spherical_attention.ipynb、distributed.md。
- notebooks/ 13 篇教程：getting_started 起步、train_spherical_neural_operator 训 SFNO、shallow_water_equations 数据集、stanford_2d3ds_dataset 球面分割、equivariance_test 等价性检验。
- DeepWiki 45 页全量镜像：~/ai/work4ai/讲透NVIDIA/torch-harmonics/deepwiki/（2026-10-26 抓取，结构 45/45 全命中）。
- agent 协作资产：SKILL.md 索引 + .skills/disco-kernel-dev（内核开发全流程 checklist）与 .skills/test-writing（测试规范）。
- 图谱资产：12 步 tour 与 30 枢纽见 .understand-anything/onboard-input.json，完整 knowledge-graph.json 可下钻；批阶段 44 条甄别笔记在 NOTES-DIGEST.md。

---
*行号随上游演进可能漂移，以语义定位为准。*
