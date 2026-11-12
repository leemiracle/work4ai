# 讲透 torch-harmonics（NVIDIA org · understand 全链 2026-11-11）

NVIDIA torch-harmonics 球谐函数（Spherical Harmonic Transform）库——服务全球网格模型（SFNO 球面傅里叶神经算子/风乌式天气预报/S2Transformer）的 PyTorch 原生底座：SHT+Legendre+求积数学核、DISCO 分布式球面卷积（稠密/CSR/kpacked 三形态，sm90 WGMMA 与 sm100 tcgen05 双代 CUDA 内核）、球面 attention（含 2212 行 ring 注意力反向内核）与 polar/azimuth 双进程组分布式层。

## 全链状态表

| 阶段 | 状态 | 数据 |
|---|---|---|
| deepwiki | ✅ 10-26 | 45/45 结构页 TRUE_100（`deepwiki/`，_coverage-check.md 实证；此前"52 页"口径有误已勘正） |
| prepare/批分析 | ✅ 11-11 | 208 代码文件，批阶段甄别笔记 44 条（NOTES-DIGEST.md）；C++/CUDA scanner 盲区签名手扫补齐 |
| merge | ✅ | **625 节点 / 1206 边**（contains 417/exports 417/imports 289/documents 20/related 19/inherits 17/tested_by 14/depends_on 8/triggers 3/deploys 1/configures 1） |
| layers/tour | ✅ | 10 层（L01 工程门面→L10 测试文档）/ 12 步导览 |
| finalize | ✅ | validator 0 issues/0 warnings，fingerprints 208 文件@c66375cf |
| onboarding | ✅ | 8 节 10732 字符（不计空格），68 个 path:line 锚全源码核实（basename 消歧终验 0 坏） |
| explain | ✅ 11-11 | 4 篇 11981 字符（不计空格，单篇 2988-2999），64 个全路径锚+11 个文内短锚；主会话独立终验 0 坏（basename 歧义逐条归位核实） |

## explain 索引

- [01-sht 与求积](explain/01-sht与求积.md) — SHT=Legendre×FFT 分解、四层 nn.Module 体系、预计算缓存
- [02-disco 全栈](explain/02-disco全栈.md) — 卷积张量三形态+sm90 WGMMA/sm100 tcgen05 双代内核
- [03-attention-cuda 双代](explain/03-attention-cuda双代.md) — 三层架构+ring 前反向内核+online softmax 三段式
- [04-分布式与示例模型](explain/04-分布式与示例模型.md) — autograd 原语三件套+polar/azimuth 正交组+SFNO 模型族

图谱在仓内 `/usr-data/data2/repos/agent-repos/NVIDIA/torch-harmonics/.understand-anything/knowledge-graph.json`。

## 源码级勘误清单（批分析+onboarding 甄别汇总）

1. **notebook 镜像实为 13 对非 12**：notebooks/ 与 docs/tutorials/ 逐对 cmp 实测 13/13 全部逐字节 identical（tutorials 侧仅多 index.md）；图谱 layer 摘要写"12 对"是漏数——双份维护无自动同步机制，改一侧必漂移
2. **CUDA/模板 scanner 双盲（工具链勘误）**：scan-result importMap 中 38 个 C++/CUDA 文件 20 个空（52.6%）、94 个 py 文件 18 个空；tree-sitter 对 .cu 内核签名与纯模板声明头提取为空（kernels_cpu/attention_cpu_fwd.h L63 起手扫、disco_helpers.h L37/L103 手扫，NOTES-DIGEST 多条实证）——图谱 C++ 符号可信度靠批阶段人工甄别支撑
3. **writer 残留 tmp/（流水线勘误）**：.understand-anything/tmp/ 残留 36 个 ua-file-analyzer-input-*.json 派发输入未被 finalize 清理（只清 intermediate/；TE 仓 110 个同理），后续仓收官须手工清
4. **SpectralConvS2 同名两套实现**：examples/models/_layers.py:379 是旧版独立实现（FNO 风格 per-mode 权重），与主库 spectral_convolution.py:43 同名不同物；SFNO 实际用 _layers 版（sfno.py:37 import 实证）——追实现必须看清 import 来源
5. **私有 API 复制**：distributed/_amp_utils.py:67 `_cast` 逐字镜像 torch.amp.autocast_mode._cast，注释自认 "which is private, hence the copy"——torch 版本升级断点区
6. **wheel 静默掉 CUDA 的历史事故**：.github/workflows/build_wheels.yml:267-270 注释自述 CUDA-labelled wheel 不含内核时"silently falls back to torch-native paths, survived several releases unnoticed"，:270 起因此加 .nv_fatbin/__cudaRegisterFatBinary 存在性断言——本地 wheel 装上却没跑原生内核不报错即此机制
7. **编译扩展顶层命名**：attention.py:38 `from attention_helpers import ...` 是裸顶层模块名——setup.py:157 把扩展编成顶层 attention_helpers 而非包内路径，与常规 torch 扩展惯例相反；import 失败=没装编译产物而非路径问题
8. **布局显式转换是硬设计**：attention/optimized/attention_interface.cpp:71-77 与 _layout.py:38-42——退化维度（H*W==1）下 stride 推断不可区分 NCHW/NHWC，全栈禁止 stride 推断、统一模块边界显式转换；"contiguous 即 NCHW"的默认假设在本仓不成立
9. **基准回归守卫**：benchmarks/run.py:106 `_is_regression` 对照仓内 reference_results.csv（H100/GB200/GB300 三机×dtype 矩阵）按架构+dtype 匹配检 speedup——优化内核的隐性性能契约
10. **plotting 延迟导入**：plotting.py:36-43 matplotlib/cartopy 全 try-import 守卫——core 包不强依赖可视化栈，裸环境可用

台账：`/usr-data/data2/repos/agent-repos/deepwiki-batch/understand-nv-a-layer.md`
