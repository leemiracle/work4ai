# 11 · th_op 与 tf_op：一套引擎的两个宿主

## 角色定位

th_op/tf_op 是 FT 引擎的两条绑带：算力全在 `models/` 与 `layers/`，它们把宿主张量翻译成 `ft::Tensor` 并托管权重/NCCL/cublas——零计算胶水层，却决定权重驻留与 API 面貌。图谱 L12（75 节点）与 L13（20 节点）之差即历史裁决：TF 是 2020 初代主力，PyTorch 随后接管所有新模型——fp8/NeoX/Swin/ViT/BART/Longformer/多卡 GPT/int4 工具族均仅 th_op。

## 内部结构

th_op 的心脏是 `th_op/th_utils.h`：`get_ptr` 直取 `data_ptr()` 裸指针即零拷贝（`th_op/th_utils.h:57`），`convert_tensor` 按 `is_cuda()` 推断内存归属，`CHECK_INPUT` 宏三连校验 device/连续性/dtype（`th_op/th_utils.h:35`）。导出分两类：有状态模型注册成 TorchScript custom class（`th_op/multi_gpu_gpt/ParallelGptOp.cc:212`），构造一次反复调 forward；无状态权重预处理走 `torch::RegisterOperators`——`GptOps.cc` 只注册一个 `find_context_duplications` 工具（`th_op/common/GptOps.cc:69`，文件名复数是误导），`WeightOnlyQuantOps.cc` 注册 9 个量化工具且全部强制 CPU（`th_op/common/WeightOnlyQuantOps.cc:338`）。tf_op 是 7 个模型目录加 `tf_op/BaseOp.h`：`BaseOp<T>` 继承 `tf::OpKernel`，构造期建 cublas 句柄与互斥锁（`tf_op/BaseOp.h:47`），输入按索引取自 OpKernelContext；`convert_tensor` 硬编码 `MEMORY_GPU` 且按编译期模板 T 分派三型，无 CPU 路径（`tf_op/BaseOp.h:99`），模型算子靠 REGISTER_OP+REGISTER_KERNEL_BUILDER 注册。

## 外部连接

th_op 向上接 torch 张量与当前 stream，向下借 `Allocator<TH>` 分配 buffer；tf_op 的 stream 取自 `eigen_device`，allocator 换 `AllocatorType::TF`（`tf_op/gpt/GptOp.cc:159`）。两处归位：`DynamicDecodeOp` 放 common 因其构造只收 vocab_size 与并行度、零权重，forward 吃 logits 吐 token ids（`th_op/common/DynamicDecodeOp.cc:294`），属通用解码层；`FusedSelfAttentionOp.cc` 放 decoder 因其直调 `DecoderSelfAttentionLayer.h` 的单 kernel 调度函数 `fusedQKV_masked_attention_dispatch`（`tf_op/decoder/FusedSelfAttentionOp.cc:146`）——包装的并非 FusedAttentionLayer 类（双目录零引用），th_op 无对应物，KV cache 由外部张量托管。

## 数据流

以 ParallelGptOp 为例：Python 构造 `torch.classes.FasterTransformer.ParallelGptOp(head_num, ..., weights, ...)`，按 `weights[0]` dtype 分派 `FTGpt<half>`。FTGpt 构造期：`ftNcclInitialize` 建 tensor/pipeline 两级 communicator（`th_op/multi_gpu_gpt/ParallelGptOp.h:96`）；逐层把 weights 裸指针绑进 `gpt_weights_` 十二组槽位；成员向量持有 torch 张量防指针失效（`th_op/multi_gpu_gpt/ParallelGptOp.h:484`）。每次 forward：`torch::empty` 预分配输出，FTGpt 取 torch stream、栈上构造轻量 `ft::ParallelGpt` 配置对象（`th_op/multi_gpu_gpt/ParallelGptOp.h:321`，权重从不搬家），包成 `map<string, ft::Tensor>` 交 `gpt.forward` 写回预分配张量。

## 设计决策

一，零拷贝即所有权反转：转换不搬数据只换描述——th 侧靠成员向量保活，TF 侧权重是图常量输入、图生命周期兜底：tf_op 并不用 resource 机制（全目录零命中），每次 Compute 重取指针、栈上重建 `ParallelGptWeight` 逐槽绑定（`tf_op/gpt/GptOp.cc:182`，变量名 gpt_weidghts 是上游 typo）。二，校验与转换分离：`convert_tensor` 自身不查 dtype，错配会被 reinterpret 静默算出垃圾，CHECK_INPUT 宏是唯一防线，故每个 op 显式重复调用。三，TF 超参写死图 Attr、换参重建图；torch 构造参数运行时自由传。四，精度分叉：tf_op 仅 fp32/fp16（bf16 靠编译期开关），th_op 另有 gpt_fp8 与 FP8 权重校准量化 op（`th_op/multi_gpu_gpt/WeightTransposeCalibrateQuantizeOp.cc:91`）。

## 新人提示

第一，th_op 下没有 `PYBIND11_MODULE`——绑定面全是 `torch::jit::class_` 与 `torch::RegisterOperators`，Python 侧对应 `torch.classes` 与 `torch.ops.fastertransformer`。第二，TF 侧读 REGISTER_OP 先数输入：Gpt 断言 `num_inputs == num_layer*12+7`（`tf_op/gpt/GptOp.cc:152`）即权重布局协议，BERT 是 16 组 N*T，排错先对索引。第三，tf_op 的 CMake 分 BUILD_TF（五目录）与 BUILD_TF2（t5/deberta）两档，别假设全可用。第四，文件名会撒谎：`FusedSelfAttentionOp.cc` 注册的 op 叫 `FusedQkvMultiHeadAttention`（`tf_op/decoder/FusedSelfAttentionOp.cc:51`），按注册名检索。第五，数值错乱先查 dtype 过没过 CHECK_INPUT、TF 输入在不在 GPU（`convert_tensor` 硬编码 `MEMORY_GPU`）。
