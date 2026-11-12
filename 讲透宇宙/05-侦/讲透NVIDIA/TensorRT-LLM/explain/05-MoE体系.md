# 05 · MoE 专家体系：类型化谈判语言与 12 后端 × 双 provider 的解析网

## 角色定位

`tensorrt_llm/_torch/moe/`（图谱 211 节点）是全部 MoE 模型的算力层。独特之处不是某个 kernel，而是把"**选哪个后端**"做成类型化谈判语言：Problem/Environment/Deployment/Eligibility/ResolutionReport 五个 frozen dataclass 描述需求与裁决、identity 注册表发身份证，resolver 在 23 个后端里跑资格筛选并输出带拒绝轨迹的报告。

## 内部结构

**契约谈判语言（impl_contract.py，657 行）**：`MoEProblem`（impl_contract.py:98，量化/形状/路由需求）、`MoEEnvironment`（impl_contract.py:232，依赖）、`MoEDeployment`（impl_contract.py:267，并行拓扑）、`MoEEligibility`（impl_contract.py:341）、裁决侧 `MoERejection`（impl_contract.py:436）与 `MoEResolutionReport`（impl_contract.py:452，selected+备选+拒绝链）。全部 frozen——谈判输入不可变。

**身份与注册（impl_identity.py，298 行）**：`MoEImplId`（impl_identity.py:57）是身份证，`MoEImplQuery`（impl_identity.py:93）支持通配，`MoEImplRegistry`（impl_identity.py:166）做 token 不相交校验，`register_moe_impl`（impl_identity.py:292）装饰器入口。token 形如 trtllm.trtllm_gen.fused_moe.nvfp4——provider.家族.能力三段式。

**解析器与工厂**：`resolve_moe_impl`（moe_resolution.py:525）按偏好+能力解析：`build_moe_problem`（moe_resolution.py:274）/`build_moe_deployment`（moe_resolution.py:351）组装谈判输入，逐候选问询，未知 literal 直接 ValueError。`create_moe_backend`（create_moe.py:43）/`create_moe`（create_moe.py:268）是门面——执行单元只能作 backend 构造，独立层请求被 TypeError 拒绝。

**层装配**：`MoE` 主类（interface.py:196）多继承 mixin；`ConfigurableMoE`（configurable_moe.py:75，907 行）是统一门面；执行基座 `MoEImplBase`（impl_base.py）。

**路由方法（routing.py，1778 行）**：`BaseMoeRoutingMethod`（routing.py:257）之下 13 家方法类——Default(routing.py:309)/DeepSeekV3(routing.py:472)/DeepSeekV4(routing.py:524)/MiniMaxM2(routing.py:619)/MiniMaxM3(routing.py:697)/Llama4Renorm(routing.py:839)/SparseMixer(routing.py:883) 等；其上是 perfect router 双 planner（routing.py:1106/1294）做离线最优路由。口径勘误：图谱摘要"15+ 家"，按源码类计数是 13 家方法类+双 planner+1 实现类（Deepseekv3RoutingImpl routing.py:348）。

**量化方法全集（quantization.py，7835 行，wc -l 实证）**：`FusedMoEMethodBase`（quantization.py:320）ABC 之下按"后端×量化"矩阵展开——Unquantized(quantization.py:801)/DeepSeekFP8BlockScales(quantization.py:1202)/NVFP4(quantization.py:2300)/NVFP4CuteDsl(quantization.py:3654)…，覆盖 permute 缓存、host pageout 与 EPLB。

**trtllm-gen 双 provider 叶族（trtllm_gen/）**：同一 TRTLLM-Gen kernel 家族有 **trtllm 本尊与 flashinfer 两个 provider**——flashinfer 侧 5 叶（trtllm_gen/__init__.py:55-59），trtllm 侧对应 5 叶（trtllm_nvfp4.py 等）。资格门 eligibility.py 细到 provider/shard 对齐/激活常数；fp8_block_scale.py 让 DeepSeek 式 1x128 块尺度双 provider 共用。

## 外部连接

- **上行**：五家新世代模型（02 篇）的 MoE 层全部汇到 ConfigurableMoE/TRTLLMGenFusedMoE；Kimi K3 断言必须开启（modeling_kimi_linear.py:1202）。
- **通信策略族（communication/）**：`Communication` ABC（communication/base.py:56，固化 pre/post-quant dispatch 时序）+`CommunicationFactory`（communication_factory.py:71）在 AllGather 兜底/DeepEP/NVLink/NCCL-EP 间择优。
- **下行算子**：fused_moe_cute_dsl.py（2138 行）、fused_moe_deepgemm.py（DeepSeek FP8 块尺度）、mega_moe/（DeepGEMM+CuTe DSL 双 MegaMoE，TRT-LLM 反向服务 DeepSeek 的汇流件）；旁路 weight_owner.py 的 `is_moe_weight_owner` 是权重改名（gate/up/down→w1/w3/w2）唯一判定闸。

## 数据流

前向：router logits → RoutingMethod 出 top-k 专家+权重 → MoEScheduler（moe_scheduler.py 双策略）dispatch token 到专家 rank → MoEImplBase.run_moe（按 ResolutionReport 选 kernel：FC1→激活（activation.py 四类）→FC2）→ combine 归约 → 共享专家融合（fused_shared_expert.py）。启动时：defaults → create_moe → resolve_moe_impl 谈判 → 报告落日志。

## 设计决策

1. **选择即报告**：拒绝必须留轨迹（gate 名+原因），部署排障不必复现谈判；frozen dataclass 防中途篡改。
2. **执行单元与完整层分离**：MoEImplBase 只作 backend、TritonFusedMoE/VanillaMoE 是完整层——构造期 TypeError 而非运行期崩。
3. **双 provider 同 kernel 家族**：trtllm 与 flashinfer 共享资格门与量化基类，kernel 升级与包依赖解耦；量化知识集中单文件，模型层零量化逻辑。

## 新人提示

- 必读 MOE_DEVELOPER_GUIDE.md；读码顺序 impl_contract.py:98 → impl_identity.py:166 → moe_resolution.py:525 → routing.py:257。
- 新后端清单：三段式 token → register_moe_impl → can_implement 资格门 → 量化 Method 类 → 薄叶文件（trtllm_gen/ 内薄叶是模板范本）。
- 调选择问题先看 ResolutionReport 拒绝链；collect_moe_environment 有缓存，测试用 override 重置。
