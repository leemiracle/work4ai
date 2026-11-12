# 12 · 配置 Schema 与 Serving 体系（仓级 9 schema / managed-inference 目录 / HF revision 钉扎）

## 一、角色定位

NemoClaw 有两张"配置契约网"：**仓级 `schemas/`**（9 个 JSON Schema、合计 2717 行）约束仓内自有配置（blueprint、CLI 配置、网络策略、onboarding、插件、preset、路由池、沙箱策略、系统就绪）；**`managed-inference/`**（4 schema + 9 models + 22 recipes + 27 presets）则是"本地大模型服务目录"——用 Kubernetes 风格的 `apiVersion/kind` 声明每一条可服务模型链路，从 HF 权重 revision 到运行时镜像 digest 全部钉死。前者管"NemoClaw 自己怎么配置"，后者管"NemoClaw 能替你跑哪些模型、凭什么相信这条链路"。

## 二、内部结构

**仓级 9 schema**（行数实测）：`network-policy.schema.json` 966 行最大（策略 DSL 全量枚举），`nemoclaw-config-v1.schema.json` 833 行次之（用户可见配置面），`blueprint.schema.json` 360 行（镜像/组件编排）、`system-readiness` 209、`onboard-config` 118、`openclaw-plugin` 76、`sandbox-policy` 68、`router-pool-config` 48、`policy-preset` 39。消费面：`src/lib/config/model.ts` 运行时引用，`test/onboarding/validate-config-schemas.test.ts` 等测试门保证 schema 与样例永远同步——schema 是被测试执行的合同而非文档装饰。

**managed-inference 数据模型**：单一 `apiVersion: nemoclaw.nvidia.com/managed-inference/v1`（`src/lib/inference/serving/catalog.ts:31` 同款常量）下三种 kind——`ServingModel`（模型身份）、`ServingRecipe`（一条可执行部署链）、`ServingPreset`（用户可选档位）。三个 schema 的 `$id` 直接指向 GitHub 路径（`catalog.ts:37-41`），`CATALOG_SOURCE_PATTERN`（`:42`）限定目录来源只能是 `managed-inference/{models,recipes,presets}/*.ya?ml`。

**ServingModel 的 revision 钉扎**：`model.schema.json:21-24` 规定 `id` 必须是 `owner/name` 形态、**`revision` 只接受 40 位 hex（git commit）、64 位 hex 或 `sha256:` 前缀 64 位**三种形态——mutable tag 在类型层面即非法。9 个模型文件全部合规实证：`vllm.deepseek-r1-distill-llama-70b.v1.yaml:11` 钉 `b1c0b44b…` 40 位 commit，`:17` 声明 `gated: true`（需 HF_TOKEN），`:19-20` `preparation.ref: none/v1`（无需制备）；而 `vllm.deepseek-v4-flash-0731.v1.yaml` 用最重的制备合同 `snapshot-copy-and-exact-text-replacement/v1`——快照拷贝带逐文件 sha256 digest + 精确文本替换带 `expectedText` 全文锚（改一个字符即失败）。spec 还要求 `menuOrder/downloadSizeBytes/probePolicyRef/capabilities`（chatCompletions/streaming/toolCalls/reasoning/multimodal 五布尔）——目录即 UI 菜单与能力声明的单一事实源。

**ServingRecipe（1744 行 schema、22 个实例）**：以 `llama-cpp.muse-glimmer-30b.spark-single.v1.yaml` 为例，三层 revision/digest 钉扎：llama.cpp 源码仓库 commit（`:19`）、HF 模型 commit（`:23`）+ 逐 GGUF 文件 sha256 与字节数（`:27`）、下载器镜像 `nvcr.io/nvidia/vllm@sha256:…`（`:34`）、运行时镜像 `ghcr.io/nvidia/nemoclaw/llama-cpp-server@sha256:…`（`:46`）；再叠加 acquisition（`hugging-face-exact-file/v1` + HF_TOKEN 可选鉴权）与 cache 策略（`hugging-face-shared-cache/v1`、host-user 共享、preserve 清理）。schema `$defs` 里 `stableId/imageDigest/sha256/sourceRevision/topologyBinding` 等命名原语被三种 kind 复用。

**ServingPreset（27 个）**：`vllm.linux-amd64-nvidia.single.nemotron-3-nano-4b-fp8.yaml` 展示三块——readiness 需求树（`scope: everyNode` 的 capability 检查：host.platform.supported、host.docker.available…）、`validation.level: hardware` + `evidence: preexisting-supported-profile-v0.0.109`（硬件级验证要挂证据指针）、`recipeRef`（`:101`）跨文件引用到具体 recipe；`priority: 300` 与 `selection: automatic` 支撑多档位自动择优。

**目录完整性**：`catalog-integrity.ts:9-27` 的 `canonicalize` 递归排序键、拒绝 undefined 与非有限数、把 `-0` 归一为 `0`——`catalog.ts:107-112` 在其上做 `canonicalServingCatalogJson` 与 sha256 摘要，使"目录内容"有稳定指纹，可跨版本比对与缓存（批阶段甄别笔记：canonicalServingCatalogJson 键排序归一化使摘要跨版本稳定复现）。

## 三、外部连接

`catalog-loader.ts:137` 的 `loadServingCatalog()` 是统一装载入口（`:156,160` 按 id 取 preset/recipe）；下游 `host-local-vllm-selection/materialization`、`managed-cluster-*`（发现/安装/拓扑/执行/生命周期 13 个模块）把 recipe 落成真实容器；`hugging-face-model-verification.ts` 在下载时兑现 revision/digest 承诺，`profile-provenance.ts`/`runtime-auth-fingerprint.ts` 把"跑的是什么"回写成可审计凭据。命名约定横跨硬件档：spark(dgx-spark-gb10)/station(dgx-station-gb300)/n1x/linux-amd64/linux-arm64 与 single/dual 拓扑组合成 recipe 文件名语法。上游 27 presets 中还含 `local-model-profile.vllm.spark.v1.yaml` 这类 profile 型条目。

## 四、数据流

新增可服务模型的完整链：models/ 加 ServingModel（钉 revision）→ recipes/ 加部署配方（钉源码+权重+双镜像 digest）→ presets/ 加档位（挂 readiness 树+硬件证据+recipeRef）→ `loadServingCatalog` 编译 → 选择器按 readiness/priority 定档 → 下载器按 acquisition 合同取权重并逐 digest 验证 → 运行时按 recipe 拉镜像 → readiness/probe（`probePolicyRef` 如 `nvidia.endpoint-validation.standard/v1`）→ 目录 canonical sha256 进凭据。全程无一处 mutable 引用。

## 五、设计决策

1. **revision 三形态正则**是"供应链钉扎进类型系统"的最小完备集：commit、裸 sha256、带前缀 sha256 覆盖 HF 全部不可变寻址方式。
2. **Model/Recipe/Preset 三分**对应三个变化轴（权重/链路/档位），跨文件 ref 替代巨型单文件，27×22×9 的组合空间保持可维护。
3. **验证级别要挂证据**：`validation.evidence` 强制硬件档位注明凭据来源，"supported"不是自称。
4. **canonical JSON 指纹**让目录变更可被 diff/sha 追踪——配置目录获得类似二进制的完整性语义。
5. 仓级 schema 与 serving schema 分居两处是有意的：前者随 CLI 发版演进，后者是数据目录可独立增长。

## 六、新人提示

加模型先读 `recipe.schema.json` 的 `$defs` 原语再写 YAML，多数约束已有命名定义；写完跑 catalog 装载测试（`catalog-loader.test.ts`）。检查 digest 时注意 HF revision 是 40 位 commit 而文件级是 sha256: 前缀，别混。preset 的 readiness id 拼错会在选择期静默不匹配——用 `profile-list`/`requested-profile-model` 相关测试兜底。图谱提示：YAML 实例多为 config 节点，真正的逻辑锚在 `src/lib/inference/serving/` 31 个 TS 模块，跨表查询走 `recipeRef`/`API_VERSION` 这类字符串常量边。
