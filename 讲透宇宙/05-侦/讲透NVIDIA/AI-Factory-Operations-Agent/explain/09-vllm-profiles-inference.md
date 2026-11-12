# 09 · vLLM profiles 与 afoa-inference 子 chart：推理面的两套部署拓扑

> 仓库：NVIDIA/AI-Factory-Operations-Agent（AFOA，Mosaic 栈的 OpenClaw 运维 agent）
> 主文件：`helm/mosaic-stack/profiles/vllm-super-1gpu.yaml`（38 行）、`profiles/vllm-ultra-4gpu.yaml`（42 行）、`helm/afoa-inference/`（独立子 chart，9+52+125+32 行）
> 协同文件：`helm/mosaic-stack/templates/vllm.yaml`（172 行，in-cluster 推理模板）、`templates/_helpers.tpl`（llm URL/模型 helper）

## 一、角色定位

AFOA 的 LLM 有三种来法：in-cluster vLLM（两个 profile 二选一）、外部推理端点（`llm.mode=external`）、以及**跨集群独立部署**——`afoa-inference` 子 chart 专为"GPU 不在 agent 集群"的场景准备（`Chart.yaml:6` 自述 "Example standalone vLLM inference for a separate GPU cluster"）。两个 profile 文件是 overlay 式 values 片段，不是模板：`helm upgrade -f profiles/vllm-ultra-4gpu.yaml` 整体替换 `llm.*` 子树，把默认的单卡 Super 配置翻成四卡 Ultra。

两套拓扑的关系由 `_helpers.tpl` 的 URL helper 串起来：vllm 模式下 `llmBaseUrl` 指向 in-cluster Service（`_helpers.tpl:104-110`），external 模式直接用装机方给的 `llm.external.baseUrl`——afoa-inference 部署完后，主 chart 以 external 模式+该 Service 的跨集群地址接入。第三种兼容形态是 `llm.requestCompatibility.enabled` 时的 ExternalName Service（`vllm.yaml:155-172`），给旧客户端保留稳定 DNS。

## 二、内部结构

### super-1gpu：单卡 NVFP4 视觉语言模型

`vllm-super-1gpu.yaml` 的关键值逐项读：

- **模型**：`nvidia/Nemotron-3.5-Super-VL-120B-A12B-NVFP4`（`:12`）——120B 总参/A12B 激活的**视觉语言 MoE**，权重 NVFP4 量化，因此单张 GPU 放得下（`gpuCount: 1`、`tensorParallelSize: 1`，`:14-15`）。镜像 digest 钉死 `sha256:cb9bc64f...`（`:9`）。
- **Mamba 混合架构适配**：`--mamba-backend=flashinfer`（`:28`）、`--mamba-ssm-cache-dtype=float16`（`:29`）、`--enable-mamba-cache-stochastic-rounding` + `--mamba-cache-philox-rounds=5`（`:30-31`）——Nemotron 3.5 是 hybrid SSM/attention 结构，这三条是 Mamba 状态缓存的数值稳定配置（float16 状态+随机舍入防漂移）。
- **长上下文**：`--max-model-len=262144`（`:33`）=256K token 窗口；`--max-num-seqs=16`（`:32`）限制并发序列，运维 agent 的负载是少而长的会话，不是高并发短请求。
- **agent 契约**：`--reasoning-parser=nemotron_v3`（`:27`）+ `--enable-auto-tool-choice --tool-call-parser qwen3_coder`（`:36-38`）——推理链剥离与工具调用解析都在 vLLM 服务端做，OpenClaw 侧拿到的是规整后的输出。
- **资源**：8/16 核 CPU、64/128Gi 内存（`:18-24`），500Gi 模型缓存 PVC（`:16-17`）。revision 钉 `8a115b9d...`（`vllm-super-1gpu.yaml:26`）——HF 仓库的精确快照，配合 digest 双重可复现。

### ultra-4gpu：四卡 TP4 的 550B

`vllm-ultra-4gpu.yaml` 换模型换并行不改骨架：

- **模型**：`NVIDIA-Nemotron-3-Ultra-550B-A55B-NVFP4`（`:12`）——550B/A55B 纯文本 MoE，同样 NVFP4 权重，但需要 `gpuCount: 4` + `tensorParallelSize: 4`（`:14-15`），2Ti 缓存（`:17`）、64/128 核、512Gi/1Ti 内存（`:19-24`）。
- **与 Super 的六处差异**：`--kv-cache-dtype=fp8`（`:26`）——**FP8 是 KV cache 精度，不是权重精度**（权重仍是 NVFP4），在 256K 窗口下把 KV 显存砍半；`--disable-custom-all-reduce`（`:30`）+ `--enforce-eager`（`:31`）——多卡环境下放弃自定义 all-reduce 与 CUDA graph，属稳定性优先的保守档；`--max-num-batched-tokens=32768`（`:32`）抬高单步批 token 数喂饱大模型 prefill；`--enable-expert-parallel`（`:33`）开 MoE 专家并行——TP4 切的是注意力与流水，专家并行再把 550B 的专家池分布到四卡；`--model-loader-extra-config '{"enable_multithread_load":true}'`（`:37-38`）多线程加载 2Ti 权重。VL 特有的 stochastic rounding 三条在 Ultra 上没有（Ultra 同属 Nemotron 3 混合架构，mamba backend/float16 两条仍在 `:34-35`，去掉的只是随机舍入与 philox 两条）。

### templates/vllm.yaml：模板侧的硬约束

StatefulSet 三件套值得注意的细节：`podManagementPolicy: Parallel`（`vllm.yaml:16`）多副本时同时起不等序；`VLLM_WORKER_MULTIPROC_METHOD=spawn`（`:69-70`）+ `NCCL_NVLS_ENABLE=0`（`:71-72`）+ `VLLM_ALLREDUCE_USE_SYMMEM=0`（`:73-74`）三条环境变量是多卡 TP 的已知兼容组合；`startupProbe` 的 `failureThreshold: 480` × `periodSeconds: 30`（`:82-84`）= **4 小时的模型加载预算**——首次从 HF 拉 2Ti 权重真实需要这个量级；dshm 用 Memory 型 emptyDir 且尺寸可配（`:104-108`），NCCL 共享内存不经此会崩；`volumeClaimTemplates` 让每副本自带缓存卷（`:109-120`）。TP 注入走 helper `mosaic-stack.vllmTensorParallelSize`（`_helpers.tpl:128-130`），其"缺省回落 gpuCount"的行为被 `validation.yaml:76-78` 的"必须相等"条款锁死——helper 与校验双保险。

### afoa-inference：独立 GPU 集群的极简 chart

125 行模板 + 52 行 values，与主 chart 完全解耦（无 mosaic-stack helpers 依赖）。`templates/vllm.yaml` 是同样的 StatefulSet+Service 骨架，但有三处独立设计：

1. **认证分离**：`VLLM_API_KEY` 从装机方预建的 Secret 注入（`afoa-inference/templates/vllm.yaml:51-55`，values 注释 `:13-15` 明示"安装前先建"）；HF 下载凭据 `modelToken` 是**另一条独立通道**（`:56-62`）——推理鉴权与模型仓库下载权分开，轮换互不影响。主 chart 默认 `VLLM_API_KEY=local-vllm` 明文（`openclaw.yaml:551-559`），跨集群后必须真 token。
2. **Ingress 只暴露 /v1**：`path: /v1` + `pathType: Prefix`（`afoa-inference/templates/ingress.yaml:25-26`），host 与 tlsSecretName 用 `required` 强制（`:19-20`）——跨集群流量必须过受信 TLS 的内部 ingress，注释 `:46` 写明设计意图。dashboard/metrics 端口不出集群。
3. **默认 values 即 Super profile 的镜像**：同 digest、同模型、同 extraArgs 全套（`afoa-inference/values.yaml:4-45` 与 `vllm-super-1gpu.yaml:6-38` 逐行对照仅键路径不同）——跨集群部署默认拿到与 in-cluster 完全一致的推理行为，避免"同一 agent 两个集群两种回答质量"。

## 三、外部连接

- **OpenClaw 侧**：`openclaw.yaml:551-561` 注入 `VLLM_API_KEY` 与 `OPENCLAW_VLLM_BASE_URL`（helper 产出）；`NODE_EXTRA_CA_CERTS` + llm-ca 卷（`:562-565`、`:689-693`）支持自签 CA 的外部端点。
- **validation.yaml**：profile 枚举（`:64-66`）、TP=gpuCount（`:76-78`）、distributed 移除（`:73-75`）三条款直接约束这两个 profile 文件。
- **nemoclaw.json**：`"primary": "llm/{{ include "mosaic-stack.llmModel" . }}"`（`nemoclaw.json:65`）把 servedModelName 接进 agent 主模型声明——两套 profile 的 `servedModelName`（nemotron-3.5-super-vl / nemotron-ultra-550b）就是 agent 看到的模型名。
- **afoa-inference 自己的渲染测试**（`afoa-inference/tests/chart-render.test.mjs`，59 行 4 用例）：默认只出 GPU 负载+Service、凭据/存储/站点硬件可独立配置、ingress 只路由 API 且引用站点 TLS、缺认证或缺 TLS 直接 fail——子 chart 自带行为契约（第 12 篇详述主 chart 版）。

## 四、数据流

in-cluster 形态：OpenClaw gateway → `http://<vllm-name>:<port>/v1`（`_helpers.tpl:105-106`）→ StatefulSet Service → vLLM pod（首启 startupProbe 窗口内从 HF/缓存卷加载权重）→ OpenAI 兼容流。跨集群形态：OpenClaw → `llm.external.baseUrl`（指向 afoa-inference 的 ingress，TLS）→ /v1 Prefix 路由 → 独立集群的 StatefulSet。模型缓存在两种形态下都是 PVC 本地缓存——跨集群时 2Ti 权重走 HF 直拉或预灌，不经 agent 集群。

## 五、设计决策

- **profile 是 values overlay 而非模板分支**：`llm.vllm.profile` 值只用于校验枚举（`validation.yaml:64-66`），模板对两种 profile 完全无感知——加第三个 profile 只需新 values 文件+一条枚举值，模板零改动。
- **并发 16、上下文 256K 的取向**：运维诊断会话要吞下日志/监控大盘/文档，长窗优先于吞吐；`max-num-seqs=16` 同时是显存护栏。
- **digest+revision 双钉**：镜像 digest 保证 vLLM 引擎行为，HF revision 保证权重快照——两者任一漂移都可能让 mamba/stochastic-rounding 这类精细配置失配。
- **afoa-inference 刻意不复用主 chart**：独立发版节奏、独立 values 域、"Example"定位——它是参考实现而非产品承诺，复制它比抽象共享层更诚实。

## 六、新人提示

- 切 profile 是 `helm upgrade -f profiles/vllm-ultra-4gpu.yaml ...`，**不是**改 `llm.vllm.profile` 单值——两个 profile 文件对资源的整体覆盖才是切换动作本身。
- Ultra 首次拉模型前确认 PVC（默认 2Ti）与节点盘；startupProbe 4 小时预算内 Pod 一直 `0/1` 是正常加载，不是死锁——`kubectl logs` 看到 vLLM 下载进度再判断。
- `--enforce-eager` 牺牲 decode 吞吐换稳定，若压测发现 Ultra 吞吐不足，先测关掉它的收益再动其它参数（记得那是稳定性保守项，见 `vllm-ultra-4gpu.yaml:31`）。
- ⚠️ 甄别记录：任务简报"Super VL 120B 单卡 NVFP4 / Ultra 550B 4 卡 TP4 FP8 KV+专家并行"与源码吻合，但需钉口径——**FP8 只修饰 KV cache dtype**（`vllm-ultra-4gpu.yaml:26` `--kv-cache-dtype=fp8`），两个模型的权重都是 NVFP4；另 Ultra 同样有 mamba 配置两条（`:34-35`），缺的只是 stochastic-rounding/philox 两条。图谱 summary 与源码一致。

（行号锚基于当前工作树源码逐条核实。）
