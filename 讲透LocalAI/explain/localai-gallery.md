# core/gallery/models.go + resolve_variant.go — 模型画廊：安装编排与变体选择器

> 源文件：`core/gallery/models.go`（1010 行）+ `core/gallery/resolve_variant.go`（435 行）
> 知识图谱归属：gallery 层（模型分发与安装子系统的核心）

## 一、角色定位

gallery 包是 LocalAI 的"应用商店"：把远端画廊 YAML 目录里的模型条目变成磁盘上可加载的 `<name>.yaml` 配置+权重文件。这两个文件分工明确——

- **models.go 是编排层**：负责安装全流程（拉目录→解析条目→探显存→下载校验→落盘）、卸载（交叉引用去重后删文件）、安全扫描，以及构建"宿主画像"（`HostResolveEnv`）和"集群画像"（`ClusterResolveEnv`，L956）供选择器消费。
- **resolve_variant.go 是纯函数选择器**：`SelectVariant`（L286）只做一件事——给定候选列表+宿主环境，选出该装哪个变体。它不碰网络、不碰目录、不读磁盘，所有事实（内存、兼容性、偏好、探针）都通过 `ResolveEnv` 结构体注入（L70-132），这正是它可以在任意硬件形状上离线测试的原因。

变体（variants）机制是这套代码的存在理由：一个画廊条目可声明多个"同一权重的不同构建"（如 GGUF 量化版引用 MLX 原生版、vLLM 版），LocalAI 按当前硬件自动选最合适的装，用户始终用条目的稳定名字访问。

上游调用方：`core/http` 的安装/删除端点、`pkg/mcp/localaitools` 的 MCP 工具（REST 与 MCP 必须同步）、分布式控制器（走 `ClusterResolveEnv`）。下游依赖：`pkg/downloader`（下载+HuggingFace 安全扫描）、`pkg/vram`（显存估算）、`pkg/system`（硬件能力三张词表）、`pkg/xsysinfo`（cgroup 感知的 RAM 读取）、`lconfig`（配置校验与推理默认值）。

## 二、内部结构

**数据模型**（models.go L57-84）：`ModelConfig` 是画廊 YAML 的内部结构（description/license/urls/name/config_file/files/prompt_templates），L70-72 新增三个变体解析记录字段 `EntryName/ResolvedVariant/PinnedVariant`——记录"这个稳定名字背后实际装的是哪个变体、是否被钉住"，供重装/升级时保持同样的选择。

**候选构建** `variantOptions`（L93-130）：把条目声明的每个变体在活动画廊目录里解引用（`FindGalleryElement`），取出**被引用条目**的 backend 与 tags 拼成 `VariantOption`（因为"能不能跑"是目标构建的属性，不是声明者的）；两层防呆：引用不存在报错（L101）、引用的条目自己还带变体也报错（L104，解析是单趟的，嵌套会被静默忽略）。最后把条目自身作为 base 追加为普通候选（L120-129）——追加而非特判，保证只有一条选择路径。

**显存探针** `probeEntryMemory`（L158-178）：调 `pkg/vram.EstimateModelMultiContext`，按 GGUF header range-fetch 估算→HTTP HEAD content-length→声明的 `size:` 三级回落；刻意不用 HF 仓库列表求和（量化条目的 urls 常指向基模型仓库，会严重高估）。`probeTimeout`=5s（L142）——一个条目多个变体逐个探，不可达的宿主必须快速放弃：探不到只损失排名，卡住则损失整个安装。返回 0 语义是"未知"而非"零需求"。

**宿主画像** `HostResolveEnv`（L269-298）+ `availableModelMemory`（L321-331）：有可用 GPU 用 VRAM；否则用 `xsysinfo` 读系统 RAM（cgroup 感知——K8s 里容器的 limit 才是真预算）；检测到 GPU 但 VRAM 读 0（arm64 Mac 统一内存的正常形态）回落 RAM 而非 0，否则 Mac 永远被钉死在 base。RAM 也读不到→0→淘汰一切已知大小的变体、只装 base（宁可小下载，不劝未知主机下大文件）。

**选择算法** `SelectVariant`（resolve_variant.go L286-392），六步：
1. 显式 pin 直接赢（L287-294），fit 与否都装——运维覆盖就该覆盖；
2. backend 不可跑的变体丢弃（L316）；
3. 已知内存超预算的丢弃（L320）；未知大小的**存活**——没有证据证明装不下就不能拒；
4. base 免双闸无条件存活（L315），但参与排名；
5. 幸存者四键排序（L371-382）：fit 档位→引擎偏好→服务特性→内存（大到小）；
6. 全灭且无 base 才报 `ErrNoVariantMatch`（L336）。

fit 三档（L397-422）：`rankProvenFit`（实测装得下）< `rankBase`（base 未证实时仍高于未知变体——base 是保证能装的载荷，未知变体是猜测）< `rankUnknownFit`。

**改写与分离** `ResolveVariant`（models.go L196-261）：选出后浅拷贝 `*source`，做"元数据分裂"——payload（url/files/config_file/overrides）来自被选变体，presentation（name/description/icon/license）来自声明条目，`Variants` 置 nil 防二次解析（L239）；然后 `deepCopyStringMap` 深拷贝 Overrides/ConfigFile、`slices.Clone` 切片（L254-258）——安装路径的 mergo 会原地改写嵌套 map，不深拷贝就会把用户请求写进画廊目录、跨安装泄漏。

**安装编排** `InstallModelFromGallery`（L373-562）：无变体条目直接装（此时请求 variant 会按名拒绝 L498）；有变体时 pin 优先级=本次请求 > 磁盘召回（`._gallery_<installName>.yaml` 的 `PinnedVariant`，L519-528，**按安装名而非条目名键控**——自定义命名的安装读错键会静默重选）；召回的 stale pin 触发 `ErrPinNotFound` 时降级重选+警告（L543-548），本次请求的 pin 则致命——一次画廊编辑不能把模型变成永久不可修复。`applyModel`（L382-479）三分支构建 config：远程 URL 拉取 / ConfigFile 重 yaml / 纯 overrides（必须 `installsSomething` 否则拒绝 L424），mergo 合并请求 overrides 后调 `InstallModel`，可选连带装后端（L470-476）。

**落盘** `InstallModel`（L564-775）：`VerifyPath` 防路径逃逸→config_file 与 overrides 合并成 map→`ApplyInferenceDefaults` 补家族默认采样参数（只填缺，L625-654）→`Validate` 类型校验→无 files 时走 `PrimaryArtifactSpec` 绑定 HF artifact（enforceScan 时先探 `.gitattributes`，L665-674）→FileTask 批量下载（SHA256+`HuggingFaceScan`）→prompt templates 写 `.tmpl`→`writeModelConfigAtomic` 原子写 `<name>.yaml`（L758）→最后写 `._gallery_<name>.yaml` 安装记录（L766-774）。

**卸载** `DeleteModelFromSystem`（L859-914）：列出该模型全部文件（配置 yaml+gallery 记录的 files+`ModelFileName`/`MMProjFileName` 推断），再枚举目录里**所有其他模型**的文件清单做交叉引用去重（L867-897）——共享文件不删，最后删配置 yaml。

**集群画像** `ClusterResolveEnv`（L956-1010）：控制器通常是无 GPU 的 pod，拿它选型会让 A100 集群只装最小 CPU 构建。取集群最大单节点内存覆盖、按 capability 各建一个 `NewCapabilityState`（控制器自身检测不泄漏进 worker 判决）做兼容性**并集**（变体只需在某处能跑）、引擎偏好去重并集；所有降级路径都落回单机行为。

## 三、外部连接

| 方向 | 对象 | 交互 |
|------|------|------|
| 上游 | core/http 端点 / MCP localaitools | 安装、删除、列出、pin 请求的入口 |
| 上游 | 分布式控制器 | `ClusterResolveEnv`（集群级选型） |
| 下游 | pkg/downloader | FileTask 下载、SHA256、HuggingFaceScan（ClamAV+危险 pickle） |
| 下游 | pkg/vram | GGUF header range-fetch 显存估算（带缓存） |
| 下游 | pkg/system/capabilities.go | 三张词表：engineNamePreferenceRules / backendBuildTagPreferenceRules / ServingFeaturePreferenceTokens |
| 下游 | lconfig | ApplyInferenceDefaults、Validate、ModelConfig 持久化 |
| 同包 | gallery.go 等 | AvailableGalleryModels / FindGalleryElement / GalleryModel 定义 |

## 四、数据流

以"安装一个带变体的模型"为例：请求（name+可选 variant）→拉取/缓存画廊目录→`FindGalleryElement` 找到条目→`HostResolveEnv`（或集群版）构建环境→`variantOptions` 逐变体解引用+探显存（每个≤5s）→`SelectVariant` 四键排序→`ResolveVariant` 元数据分裂+深拷贝→`InstallModel`：合并配置→补默认→校验→下载（进度回调 `downloadStatus` 驱动 UI）→写 .tmpl→原子写 `<name>.yaml` 与 `._gallery_<name>.yaml`（记录三元组）→（可选）连带装后端。重装时从 `._gallery_` 召回 pin，升级/画廊变更后 stale pin 自动降级重选。卸载走反方向：列文件→全目录交叉引用→安全删除。

## 五、设计决策

1. **选择器纯函数化**：所有硬件事实经 `ResolveEnv` 注入（连探针都是 func 字段，L131），测试可 pin 精确大小或精确失败，零网络依赖。
2. **base 是候选不是兜底**：免过滤（老条目在新版本必须仍可装）但不免排名——大量化 base 必须能赢过未知大小的变体（L274-277 注释）。
3. **三张词表严格分离**：引擎名（`backend:` 值）匹配 EnginePreference；build tag（cuda/rocm）属于已安装构建别名解析；服务特性（dflash/mtp）匹配**显式 tags**。接错词表不报错、静默退化成按大小选——resolve_variant.go L87-93 专门警告别把 BackendPreferenceTokens 接进来。
4. **未知≠零**：探不到大小只降排名不淘汰；网络故障不能静默改变安装内容（L44-45、L272-273）。
5. **tags 是唯一服务特性信号**：条目名里的 marker 不是契约，作者没写的特性不算数（L46-56）——静默降级到 plain build 可恢复，凭名字 marker 晋级不可见。
6. **排序键顺序即设计**：fit>引擎>特性>大小。引擎压大小（Mac 选 MLX 而非更大 GGUF，L348-351 "Do NOT move this below size"）；引擎压特性（dflash 在便携引擎上不赢正确引擎上的 plain build——错引擎损失整块 GPU，L356-362）；同引擎同特性下大小取胜（更大=更高质量量化，L363-367）。
7. **pin 语义分两级**：请求 pin 致命、磁盘召回 pin 可过期——运维意图要硬，画廊演化要软。
8. **引用别名防御**：struct 浅拷贝后 Overrides 等引用字段仍指向画廊目录自身，安装路径会原地改写它们，必须深拷贝到底（L241-253 的注释把 mergo 递归改写嵌套 map 的机制讲透了）。
9. **统一内存回落**：GPU 检测到但 VRAM=0 回落 RAM——写错这一行，所有 Mac 永远只能装 base（L310-316）。

## 六、新人提示

- **阅读顺序**：先读 resolve_variant.go（435 行纯逻辑，注释即论文），再读 models.go 的编排。两文件的注释密度是全仓标杆，几乎每个"为什么"都写在代码旁。
- **加新引擎/新特性永远不改 resolve_variant.go**：引擎进 `engineNamePreferenceRules`，服务特性进 `ServingFeaturePreferenceTokens`，选择器不命名任何引擎（L144-146）——这是词表驱动设计的核心契约。
- **给画廊条目加 tags 要谨慎**：tags 是服务特性的唯一声明渠道，规则见 `.agents/adding-gallery-models.md`；写错 tag 等于放弃该特性的排名优势。
- **调试"为什么装了这个变体"**：看日志 `Resolved model to variant`（L553）与 `Reasons`（每个被拒变体一行人话）；fallback-to-base 会显式 Warn（L208）。
- **`._gallery_<name>.yaml` 是安装记录**：pin 召回、变体追溯都靠它；删除模型会连带清理，手删等于重置 pin。
- **分布式模式选型必走 ClusterResolveEnv**：控制器硬件不可当裁判，这是 L942-955 注释用一整段讲的教训。
- **测试选择器**：`ResolveEnv.ProbeMemory` 注入固定值即可覆盖"探针失败/超时/未知大小"全部分支，不需要 mock 网络。
