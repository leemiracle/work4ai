# 五 · 应用：从 FlashAttention 到国产栈

## 5.1 FlashAttention 系：融合范式三次跃迁

- **FA1/FA2**（[讲透3FS 精读](../../04-研/讲透3FS/README.md) 的姊妹篇锚点 arXiv:2205.14135/2307.08691）：online softmax 把注意力从 $O(s^2)$ HBM 访存压到 $O(s)$——02.4 节数学的产业兑现，长上下文从此可算；
- **FA3**（Hopper 世代）：warp specialization+TMA 异步化，把屋脊点右侧的实跑曲线再往上推；
- **MLA 世代**（[讲透FlashMLA](../../02-透/讲透FlashMLA/README.md)）：注意力 kernel 开始"懂模型结构"——KV 协议 656B→528B→FP4 288B token-interleaved 排布随代演进，sm90 与 Ascend 950 双后端同仓——**kernel 生态从"通用算子库"变"模型专属基础设施"**。

## 5.2 GEMM 的极致：FP8 与分组

- **DeepGEMM**（[讲透DeepGEMM](../../02-透/讲透DeepGEMM/README.md)）：FP8 分组 GEMM 服务 MoE 形状（运行时才知道每组 token 数）；per-128 缩放贯穿 dispatch/GEMM/KV/量化四层（DeepSeek 设计哲学：**一次设计 vs 组件拼装**的可证伪判据）；
- **TileKernels+mHC**（[讲透TileKernels](../../02-透/讲透TileKernels/README.md)）：论文公式 100% 落地的样板（φ GEMM 移交 DeepGEMM 的分工），Tile 级抽象让 kernel 开发向库工程靠拢。

## 5.3 推理侧的 kernel 经济学

[讲透推理服务](../讲透推理服务/README.md) 02.3 证明了 decode 强度恒 1.0——kernel 层的全部对策：

- **权重侧**：W4A8/W4A16 量化让分母（字节）缩 4 倍，强度提到 ~4——量化本质是 roofline 操作（[讲透llm-awq](../../03-查/讲透llm-awq/deepwiki/INDEX.md)/[讲透smoothquant](../../03-查/讲透smoothquant/deepwiki/INDEX.md) 两条主流路线）；
- **融合侧**：把 norm/激活/掩码挂进 decode kernel（消灭中间落地）；
- **投机侧**：一次读权重验证 k 个 token（[讲透推理服务](../讲透推理服务/05-应用-服务的真实战场.md) 5.3 节）。

## 5.4 编译层：Triton/TVM 与"kernel 民主化"

- **Triton**（[讲透Triton](../../02-透/讲透Triton/README.md)）：block 级抽象让研究者写得出能看的 kernel——FA2 官方实现就是 Triton；autotune 把 4.2 节的平台特异性部分自动化；
- **TVM/xla/onnx**（查区原料仓）：编译路线的野心是彻底跳过手写——现实是"编译器榨 80%、热点手写最后 20%"的分层稳态；
- **tile/lang 新生代**（[讲透slang](../../03-查/讲透slang/deepwiki/INDEX.md)、[讲透helion](../../03-查/讲透helion/deepwiki/INDEX.md)）：tile-first DSL 把 02.3 节的重用数学直接做成语言原语。

## 5.5 国产栈：镜像世界的机会与代价

[讲透TIRx](../../02-透/讲透TIRx/README.md)（沐曦 kernel 库，本仓 understand 图谱金标准首例）与 CUDA-Stack 逆向报告（[讲透CUDA-Stack-RE](../../03-查/讲透CUDA-Stack-RE/REPORT.md)：三工具线解包 CUDA 栈）展示了同一个事实：**CUDA 生态的护城河不在驱动而在十几年的 kernel 资产**。国产路线要么重写全套（TIRx 模式）、要么门面适配（KCCL 模式，见 [讲透集合通信](../讲透集合通信/05-应用-真实训练中的集合通信.md) 5.4）——kernel 层是所有路线里最贵的学费。

## 5.6 单元闭环：一条屋脊曲线的三种读法

五幕脉络：算子边界=HBM 边界是隐形税（01）→ 屋脊与重用给出"把强度推过屋脊点"的全部数学（02）→ 模拟器逐位对账（03）→ 但数值一致性/平台特异性/调试黑盒是持续学费（04）→ 产业从 FA 融合、FP8 GEMM、量化到国产栈都在这条曲线上找自己的位置（05）。

**一条 roofline 曲线，三种读法**：算法工程师读它找融合机会（AI 推过屋脊）、系统工程师读它选量化策略（分母打折）、架构师读它判产业分工（谁该手写谁该编译）。

✍️ 结业练习：挑一个你常用的模型算子组合（如 QKV+RoPE+attention），列出每个算子的 AI 值与屋脊判定，指出融合收益最大的切割点；再对照 Triton 官方教程里对应 fused kernel 的写法验证你的判断。
