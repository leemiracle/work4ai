# DeepWiki 相关生态仓清单（related/）

> 选仓标准：与 SGLang 存在直接代码依赖、架构借力或强对比关系的仓库。
> 抓取日期：2026-09-03（各仓 DeepWiki 主页 overview 单页，截断至 ~18KB）

| 文件 | 仓库 | 关联角色 | 状态 |
|------|------|---------|------|
| [flashinfer.md](flashinfer.md) | flashinfer-ai/flashinfer | **核心内核依赖**：SGLang 的 attention（FlashInfer backend）/MoE（fused MoE）/sampling 大量调用其 JIT 内核 | ✅ 已抓 |
| [nixl.md](nixl.md) | ai-dynamo/nixl | **PD 分离传输层**：SGLang prefill-decode disaggregation 的跨节点 KV 传输底座 | ✅ 已抓 |
| [xgrammar.md](xgrammar.md) | mlc-ai/xgrammar | **结构化输出引擎**：SGLang 约束解码（19.2 章）的 grammar 后端 | ✅ 已抓 |
| [vllm.md](vllm.md) | vllm-project/vllm | **同类竞品**：PagedAttention/连续批处理路线对比；深度资料见 `work4ai/讲透vLLM/` | ✅ 已抓（概要） |
| [tensorrt-llm.md](tensorrt-llm.md) | NVIDIA/TensorRT-LLM | **性能对标**：NVIDIA 官方推理引擎 | ✅ 已抓 |
| [tgi.md](tgi.md) | huggingface/text-generation-inference | **同类框架**：HF 官方 serving | ✅ 已抓 |
| [sgl-router.md](sgl-router.md) | sgl-project/sgl-router | 官方姊妹仓（Rust router）——**DeepWiki 无 wiki**，功能已并入主仓 sgl-model-gateway，说明文件指向主 wiki 20/21 章 | ⚠️ 占位说明 |
| [speculative-decoding.md](speculative-decoding.md) | sgl-project/speculative-decoding | EAGLE 论文官方仓——**DeepWiki 无 wiki**，说明文件指向主 wiki 12 章 | ⚠️ 占位说明 |

## 选仓逻辑说明

1. **上下游依赖优先**：flashinfer（算子）、nixl（传输）、xgrammar（约束输出）是 SGLang 运行时真实 import 的三大外部项目，读懂它们才能读懂 SGLang 的能力边界。
2. **竞品对比**：vLLM 与 TensorRT-LLM 是唯二需要正面对比的推理引擎；TGI 作为同类补充。vLLM 的 110 页级深度资料已在 `work4ai/讲透vLLM/` 沉淀，此处仅保留 overview 以便横向引用。
3. **官方系谱**：sgl-project org 下仅 sglang 主仓有完整 wiki；sgl-router 与 speculative-decoding 两个子仓经探测（HTTP 200 但无 `div.prose-custom` 正文容器，仅 ~31KB 壳页面）确认 DeepWiki 未生成内容，如实记录而非编造。
