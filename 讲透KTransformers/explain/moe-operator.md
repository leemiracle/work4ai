# MoE 算子精讲：operators/experts.py

> 仓库无 operators/moe/ 子目录，MoE 主实现即 archive/ktransformers/operators/experts.py（2096 行，目录最大），router 在同目录 gate.py。经典框架虽已进 archive，"attention 在 GPU、experts 在 CPU"的思想全在此。

## 1. 角色定位

13 层架构的 layer:operator（算子层），MoE 侧最重文件：20+ 类，三种专家后端 × 七个模型家族。对照 attention.py（MLA 永远 GPU）——异构分界线画在两文件间：attention+KV cache 留 GPU；占参数 95%+ 却稀疏激活的 routed experts 放 CPU，权重经 mmap 不必进 RSS。

## 2. 内部结构

- 后端执行器：KExpertsBase（L68）定 forward/load/unload 契约与 load_weights（L88，解析 ffn_gate/up/down_exps 三张量）。KExpertsCPU（L143）主角；KExpertsMarlin（L437）GPU INT4；KExpertsTorch（L562）纯 torch 对照。注册进 EXPERTS_MAP（L680），键即 YAML 的 generate_op；generate_cuda_graphs（L50）生成 CUDA graph 捕获 batch 列表。
- 两阶段容器：KTransformersExperts（L686）同时构造 generate_experts（KExpertsCPU@cpu）与 prefill_experts（KExpertsTorch@cuda）（L700）；load(mode)（L712）按 InferenceState.GENERATE/PREFILL/UNLOAD 换边——先 unload 一侧再 load 另一侧；forward（L739）按 self.mode 分派。
- 模型家族块（L770-2096）：KDeepseekV2MoE(L874)、KDeepseekV3MoE(L972)、KQwen2MoeSparseMoeBlock(L770)、KMistralSparseMoEBlock(L1074) 及 Qwen3/GLM4/Smallthinker 等 V2（多透传 bsz_tensor/cuda_graph_idx，L1273）。各继承 models/modeling_*.py 原始 MoE Block 只重写 forward，保留 moe_kexperts/moe_infer_simple/moe_infer 三路径。

gate.py：KMoEGate（L91）forward 委托 orig_module（L107）即原版 grouped topk，load（L110）把 router 权重搬上 GPU。

## 3. 外部连接

依赖（图谱 edges）：cpuinfer.py（CPUInfer 线程池，submit_with_cuda_stream 桥接 CUDA 流）、custom_loader.py（get_mmap_tensor）；C++ 侧经 cpuinfer_ext.moe 的 MOEConfig/MOE（L26）。被依赖：optimize_rules/*.yaml 以类名字符串引用、operators/models.py 的 load_layer_to（L443）调 set_inference_mode 逐层搬运、ascend/ 的 NPU 变体继承。基类 BaseInjectedModule 用 __getattr__/__setattr__ 重定向让注入类冒充原模块。

## 4. 数据流：一次 decode 的 MoE 前向

DeepSeek-V3 单 token（KDeepseekV3MoE.forward，L974）：
1. router（GPU）：self.gate(hidden_states) 得 topk_idx/topk_weight（L879 同构）。
2. 异步下发：seq_len==1 走 submit_for_one_decode（L882；实现 L293）——copy_ 进类级 pinned buffer（L144，每 graph 形状一份），再 submit_with_cuda_stream(当前流, self.moe.forward(...data_ptr()...))，七个裸指针交 C++ 线程池。
3. 重叠：CPU 算 experts 同时 GPU 跑 shared_experts（L884）。
4. 同步：sync_for_one_decode（L310）等 C++ 完，output_cpu 拷进 output_gpu_map[out_device] 返回 GPU 张量。
5. merge：y += 共享专家输出，resize_ 回原形（L887）。

DISK 层在加载期：load_weights（L367）用 get_mmap_tensor（custom_loader.py:405）拿 mmap 切片——量化字节留 page cache，不反量化不拷贝；load（L169）以 ctypes.addressof（L183）取裸地址传 MOEConfig（llamafile 后端 L201；AMX 后端 L220）。prefill 相反：moe_kexperts（L915）进 GPU torch，长序列选 moe_infer（L939，按专家分组批算）或 moe_infer_simple（L921 双循环）。

## 5. 设计决策

- 双执行器：prefill compute-bound（大批 token，GPU 批 matmul 赢）；decode memory-bound（每 token 只激活 topk 专家却要摸全部权重，CPU 大内存赢）。换边而非并存，省显存。
- 类级静态 buffer：61 层共享一组 pinned buffer（L144），CUDA graph 捕获期地址必须稳定。
- 裸指针：绕过 dispatcher，C++ 直读 mmap 量化字节——"CPU/DISK 分层"本质是 page cache 当最后一级 cache；submit/sync 拆两步即为第 3 步的重叠。

## 6. 新人提示

- 切入：先读 DeepSeek-V3-Chat.yaml 看类名引用，再从 KDeepseekV3MoE.forward → moe_kexperts → KTransformersExperts.forward → KExpertsCPU.forward 打通一线。
- KExpertsCPU.forward（L320）三分支：graph 捕获中/XPU/通用同步；调试走通用路径（真拷贝），性能与生产不同。
- gate.py L167 潜伏 bug：logits 未定义即被使用；EXPERTS_MAP 键是 YAML 字符串，改名不同步要到 inject 时才报错。
