# 精讲：compiler_pass/ — LLM 编译流水线

> 位置：`python/mlc_llm/compiler_pass/`（22 个 pass 文件）· 编排核心 `pipeline.py` 209 行 · 扇出 25
> 图谱：TVM IRModule 上的编译 pass 集合，pipeline.py 统一编排

## 角色定位

compiler_pass 是 MLC「编译换性能」的主战场。模型架构产出的是**高层计算图**（TVM Relax IRModule）——语义正确但性能平庸：反量化是显式 kernel、KV cache 只有接口没有实现、采样在 host 端。本目录把它按目标平台改写成**可直接部署的高效代码**。

注册方式：`@register_pipeline("mlc_llm")`——MLC 的流水线是 **TVM 官方 pipeline 机制的扩展包**，与 TVM 内置 zero pipeline 共享基础设施（LegalizeOps/FuseOps/Dlight）。

## 内部结构

`pipeline.py` 把约 40 个 pass 编排成 5 个 Phase：

- **Phase 0 · attach/dispatch（13 个）**：不优化只「装零件」——`DispatchKVCacheCreation` 把 KV cache 创建调用改写为具体实现（TIR paged 或 FlashInfer）；`AttachGPUSamplingFunc`/`AttachLogitProcessFunc` 挂采样与 logit 处理；`AttachSpecDecodeAuxFuncs` 补投机解码辅助函数；另有 VariableBounds/CUDAGraph 提示等约束附加。
- **Phase 1 · 高层图优化**：`DispatchTritonKernel`、`FuseFTDequantizeEpilogue`（FT GEMM epilogue 融合）、`FuseDequantizeTranspose`、`BLASDispatch`（可选 cuBLAS）、`FuseAddRMSNorm`（非 llvm）、`FuseTransposeMatmul`。
- **Phase 2 · 降级到 TIR**：复用 TVM Relax 官方管线 LegalizeOps→FuseOps→FuseTIR。
- **Phase 3 · TIR 级融合**：`FuseDequantizeMatmulEwise`（反量化+矩阵乘+逐元素三元融合，低比特推理性能命门）、`FuseDequantizeTake`、DCE。
- **Phase 4+5 · 低层与收尾**：`LowBatchGemvSpecialize`（batch=1 GEMV 特化）+ Dlight 默认调度（GPU 五种/CPU 一种）→ StaticPlanBlockMemory 内存静态规划 → 内存估算挂元数据 → CUDA graph 重写 → VM 字节码 → AttachExternModules。

辅助件：`_LogProgress`（空 pass 打日志）、`_DebugDump`（dump 中间 IR 为 debug-phaseN.py）——调试第一工具。

## 外部连接

- **上游**：`interface/compile.py` 发起编译；各 pass import `support/logging`
- **下游**：产出交 TVM codegen 出平台库；内存估算供运行时显存预算
- **横向**：`quantization/` 决定要融合的反量化形态；`op/triton.py` 由 DispatchTritonKernel 调度；`nn/kv_cache.py` 由 DispatchKVCacheCreation 落地

## 数据流

一条量化 matmul 的编译命运：

```
架构定义: w_int4 --dequantize--> w_f16 --matmul(x)--> out(+bias/act)
Phase 0: KV cache 接口→具体实现；采样函数挂载
Phase 1: 检测 dequantize→transpose / FT epilogue 模式融合
Phase 2: LegalizeOps 落成 TIR matmul PrimFunc
Phase 3: FuseDequantizeMatmulEwise 模式匹配（查 GlobalVar
         名前缀 dequantize*/matmul*）三元合一
Phase 4: 按 variable_bounds 克隆 batch=1 特化版
Phase 5: 显存规划 → VM 字节码 → .so
```

`fuse_dequantize_matmul_ewise.py` 的典型手法：枚举 aux tensor 数（0-4）×ewise 数（0-3,6）组合，每种注册一组 `FuseOpsByPattern`——**用组合爆炸换覆盖率**。

## 设计决策

1. **pass 顺序即语义**：fuse 在 LegalizeOps 前后各一次、Dlight 必须在 TIR 生成后——顺序是正确性问题，pipeline.py 用顺序列表显式表达。
2. **attach 而非侵入**：采样/logit/KV cache 全用挂载而非改模型定义——模型代码纯净，运行时职责编译期注入。
3. **按 target 条件启用**：`FuseAddRMSNorm`/`LiftTIRGlobalBufferAlloc` 判 `!= "llvm"`、`ForceNarrowIndexToInt32` 判 `!= "cuda"`——CPU/GPU/WASM 分叉藏在条件里。
4. **_DebugDump 门设计**：null 时零开销直通，需要时逐 Phase 落盘 IR。

## 新人提示

- **调试编译第一动作**：`compile --debug-dump <dir>`，对比 phase0-5 找问题引入点。
- **加新 pass**：实现 `transform_module(mod, ctx)`，module_pass 装饰，插进 pipeline 合适位置（fuse 类放 Phase 1/3）。
- **测试锚点**：`tests/python/compiler_pass/` 逐 pass 回归。
- **别在 Phase 0 找优化**：那里全是信息附加，图变换从 Phase 1 开始。
