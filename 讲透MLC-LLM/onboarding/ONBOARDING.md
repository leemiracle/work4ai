# MLC-LLM 新人上手指南（ONBOARDING）

> 基于知识图谱自动生成：1950 节点 / 4011 边 / 14 架构层 / 15 步导览 · git commit `9fa644f`
> 配套：`../deepwiki/`（28 页）· `../explain/`（5 篇精讲）

## 1. 项目总览

MLC-LLM 是**基于机器学习编译（MLC）的通用 LLM 部署引擎**，解决一个问题：同一份大模型如何高效跑在所有设备上——CUDA 服务器、手机 Vulkan/Metal GPU、浏览器 WebGPU，全吃同一套编译产物。技术核心是 **Apache TVM 统一编译流**：

```
HuggingFace 权重 ──gen_config──▶ mlc-chat-config.json
              ──convert_weight──▶ MLC 量化权重
              ──compile──▶ Relax IR ──编译pass──▶ 平台原生库(.so/.wasm)
```

编译期 Python（`python/mlc_llm/`）完成，运行时核心 C++（`cpp/serve/`）实现，经 JSON FFI 桥接到 Python/REST/Android/iOS/WebLLM。一句话定位：**编译器视角的 llama.cpp**——不手写各平台 kernel，让 TVM 流水线自动生成，用 FlashInfer/Triton/CUTLASS 补足最后一公里。

## 2. 架构分层（14 层）

```
┌───────────────── 用户接口 ─────────────────┐
│ python-cli(45) python-serve(32)           │
│ docs-build(90) testing(60)                │
└──────┬───────────────────────┬────────────┘
 编译期  │              运行时    │
┌───────▼──────────┐ ┌─────────▼────────────┐
│ model-arch(140)   │ │ cpp-serve(50)       │
│  40+架构成对model/ │ │  ThreadedEngine→    │
│  loader           │ │  EngineImpl+17动作  │
│ compiler-pass(35) │ │ cpp-ffi(31)         │
│ op-nn(17)         │ └─────────┬───────────┘
│ conv-template(34) │           │ FFI
│ py-support(17)    │ ┌─────────▼──────────┐
└───────────────────┘ │ android(61)        │
                      │ ios(47) web-wasm(4)│
                      └────────────────────┘
```

| 层 | 规模 | 职责 |
|---|---|---|
| python-cli-interface | 45 | CLI 总入口：9 个子命令，「CLI→Args→interface」三层转发 |
| model-arch-matrix | 140 | **最大层**：40+ 架构的 `*_model.py`+`*_loader.py` 成对 |
| compiler-quantization | 35 | TVM 编译 pass + group/awq/fp8/block_scale 量化 |
| op-nn-primitives | 17 | `op/` extern 算子（attention/triton/moe）+ `nn/` PyTorch 风格原语 |
| conversation-template | 34 | ConvTemplate 注册表 + tokenizers FFI |
| python-support | 17 | logging（fan-in 77）/auto_target/tensor_parallel 地基 |
| python-serve | 32 | asyncio 异步引擎 + OpenAI REST + radix_tree |
| cpp-serve-engine | 50 | **推理引擎本体**：EngineImpl、17 动作、radix_tree |
| cpp-support-ffi | 31 | support/ 公共库 + json_ffi 跨语言引擎 |
| web-wasm | 4 | emcc→WASM→WebGPU（WebLLM 消费） |
| android | 61 | MLCChat 应用 + mlc4j JNI 绑定 |
| ios-swift | 47 | MLCChat iOS + MLCSwift 包（Metal） |
| docs-build-infra | 90 | docs/ + CI + cmake/pyproject |
| testing | 60 | pytest，78 条 tested_by 边锚定回归 |

## 3. 核心模块

1. **模型加载器矩阵**：`model.py` 全仓扇出第一（126 import），MODELS 字典 47 条目；每个 Model 元数据含 config/model/source/quantize 四要素。
2. **compiler_pass 流水线**：`pipeline.py` 以 `@register_pipeline("mlc_llm")` 挂进 TVM，5 Phase 编排约 40 个 pass。
3. **TVM op 算子**：attention.py（FlashInfer/cuDNN）、triton.py、moe_matmul.py、cutlass.py。
4. **Python async serve 引擎**：AsyncMLCEngine 提供 OpenAI 风格异步接口；engine_base 拉起 C++ 双后台线程；回调经 `call_soon_threadsafe` 回事件循环。
5. **C++ serve 引擎**：`EngineImpl::Step()` 每步只执行一个动作；threaded_engine 包成线程安全指令队列。
6. **对话模板**：registry.py 按 mlc_chat_config 字符串索引 30+ 族模板。
7. **FFI 协议**：json_ffi_engine.cc 实现「JSON 进 JSON 出」，Kotlin/Swift/JS 零绑定接入。
8. **移动端**：Android（mlc4j/Vulkan）、iOS（MLCSwift/Metal）、Web（WebGPU）共享编译产物。

## 4. 关键概念（14 个）

| 概念 | 解释 |
|---|---|
| MLC 编译流 | gen_config→convert_weight→compile 三步出平台库 |
| 量化预设注册 | make_quantization_functions 工厂按模型类装配 awq/fp8/group 开关 |
| PagedKVCache | 分页 KV cache 抽象，create_paged_kv_cache 按页分配 |
| fuse_tir_ops | Phase 1/3 算子融合：dequantize+matmul+ewise 消除显式反量化 |
| dispatch 系 pass | 按目标分派 KV cache（TIR/FlashInfer）、Triton kernel、BLAS |
| cutlass fusion | op/cutlass.py 接入 CUTLASS GEMM epilogue 融合 |
| ConvTemplate | 每族模型的消息格式（角色前后缀+停止词） |
| 投机解码 | draft/verify 双模型：batch_draft→batch_verify；另有 EAGLE 树形验证 |
| radix tree prefix cache | token 级前缀树复用 KV cache（Python 154 行壳，C++ 845 行本体） |
| threaded_engine | C++ 线程化外壳：指令队列+双后台循环 |
| JSONFFI | 请求响应全 JSON 字符串的跨语言协议 |
| tensor_parallel | TP 分片注解 + Disco 进程池 + NCCL/RCCL |
| WebGPU/WASM | web/ emcc 打包，浏览器跑编译产物（WebLLM） |
| engine mode | local/interactive/server 三档，决定容量推断 |

## 5. 推荐学习路径（15 步）

1. README：建立「编译部署引擎」心智模型
2. `__main__.py`→`cli/compile.py`：CLI→Args→interface 约定
3. `model.py`：Model 四要素与 47 条目
4. `nn/__init__.py`+`loader/`：「PyTorch 语法产出 TVM IRModule」词汇表
5. `quantization/model_quantization.py`：编译期量化装配
6. `interface/compile.py`+`pipeline.py`：5 Phase 全景
7. `op/attention.py`/`triton.py`：extern 算子
8. `conversation_template/registry.py`+`tokenizers.py`：模板与分词
9. `serve/engine.py`+`engine_base.py`+`radix_tree.py`：asyncio 与 C++ 边界
10. `entrypoints/openai_entrypoints.py`：REST 装配
11. `cpp/serve/engine.cc`：EngineImpl 与 Step 循环
12. `engine_actions/`：17 动作+radix_tree.h+sampler
13. `support/module_vtable.h`+`json_ffi/`：跨语言桥
14. web/+android/mlc4j+ios/MLCSwift：三平台共享产物
15. `tests/python/serve/`：改引擎前先看行为快照

## 6. 文件地图（按层 44 条）

**编译链（python）**：`model/model.py`（注册中心）、`model/llama/llama_model.py`（参考实现）、`model/deepseek_v2/deepseek_v2_model.py`（MLA+MoE，873 行）、`loader/{loader,huggingface_loader,standard_loader}.py`、`quantization/{model_quantization,group_quantization}.py`、`compiler_pass/{pipeline,dispatch_kv_cache_creation,fuse_dequantize_matmul_ewise,low_batch_specialization}.py`、`op/{attention,triton,moe_matmul}.py`、`nn/kv_cache.py`、`interface/{compile,serve,jit}.py`、`support/{auto_target,tensor_parallel}.py`、`conversation_template/registry.py`、`tokenizers/tokenizers.py`

**运行时（python serve）**：`serve/engine.py`（AsyncMLCEngine）、`serve/engine_base.py`（基座+回调）、`serve/radix_tree.py`（前缀缓存壳）、`serve/entrypoints/openai_entrypoints.py`、`protocol/openai_api_protocol.py`、`json_ffi/engine.py`

**运行时（cpp）**：`serve/engine.cc`（EngineImpl）、`serve/threaded_engine.cc`（线程外壳）、`serve/engine_state.cc`（双队列）、`serve/engine_actions/{action.h,batch_prefill_base.cc,batch_decode.cc,eagle_batch_draft.cc,eagle_batch_verify.cc}`、`serve/radix_tree.cc`（845 行本体）、`serve/sampler/{gpu_sampler,cpu_sampler}.cc`、`serve/logit_processor.cc`、`serve/config.cc`（显存估算）、`serve/function_table.cc`（TVM 函数表+Disco）、`json_ffi/json_ffi_engine.cc`、`metadata/model.cc`、`support/json_parser.h`、`tokenizers/tokenizers.cc`

**端侧与守护**：`web/emcc/mlc_wasm_runtime.cc`、`android/mlc4j/.../MLCEngine.kt`、`ios/MLCSwift/Sources/Swift/LLMEngine.swift`、`tests/python/serve/`（引擎与 prefix cache 行为快照）

## 7. 复杂度热点

- **serve/engine.py（1946 行）+engine_base.py（1278 行）**：Python 侧最大，asyncio 回调与流式状态机交织
- **cpp/serve/engine.cc（1102 行）**：Create 装配流水线+Step 内嵌 disagg 与 Disco 分支
- **deepseek_v2（model 873+loader 258 行）**：MLA（q/kv_lora+absorb）+MoE 权重映射全仓最烧脑
- **batch_prefill_base.cc**：四 prefill 变体共享骨架，分块+prefix 匹配+状态更新耦合
- **eagle_batch_draft/verify.cc**：tree attention 候选树管理
- **pipeline.py**：pass 顺序即语义

## 8. 与生态关系

| 项目 | 关系 |
|---|---|
| TVM | 基座：Relax/TIR/Dlight/VM 全来自 TVM |
| vLLM | 服务端竞品；vLLM 只做 CUDA，MLC 用编译换全平台 |
| llama.cpp | 端侧竞品；手写 kernel+GGUF vs 编译器生成+自有量化 |
| WebLLM | 消费方：web/ WASM 产物+JSON FFI 是其运行时底座 |
| FlashInfer/Triton/CUTLASS/xgrammar | extern 算子与结构化输出上游 |

定位：**TVM 是编译器内核，MLC-LLM 是 LLM 发行版，移动 App/WebLLM 是预装系统**。

---
*2026-09-05 · understand-onboard 流水线 · 图谱 commit 9fa644f*
