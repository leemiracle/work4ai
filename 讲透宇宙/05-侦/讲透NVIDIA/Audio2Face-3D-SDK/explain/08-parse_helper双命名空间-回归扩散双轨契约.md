# 08 · parse_helper 双命名空间——回归/扩散双轨模型契约与同名类消歧

## 角色定位

`parse_helper.h` 是**模型资产装载契约**。audio2face 的版本（`audio2face-sdk/include/audio2face/parse_helper.h`）用两个命名空间 `IRegressionModel`（parse_helper.h:31）与 `IDiffusionModel`（parse_helper.h:109）把**回归与扩散两代网络的装载契约并排放在同一头文件里**——同名类成对出现，靠命名空间隔离。audio2emotion 侧是同构设计（`IClassifierModel`/`IPostProcessModel`，audio2emotion/parse_helper.h:30,89）。看到 `IRegressionModel::` 前缀即知走的是哪条模型轨。

## 内部结构

**公共契约层**（audio2face/parse_helper.h）每轨四接口：`INetworkInfo`（回归版 parse_helper.h:34-52 / 扩散版 112-132）、`IAnimatorData`（55-68 / 135-144）、`IGeometryModelInfo`（71-91 / 147-167）、`IBlendshapeSolveModelInfo`（94-105 / 170-182）；命名空间外还有轨无关的 `IBlendshapeSolverConfig`（parse_helper.h:187）、`IBlendshapeSolverData`（201）与 Bundle 聚合接口 `IGeometryExecutorBundle`（215-242）、`IBlendshapeExecutorBundle`（246-273）。

两轨契约**刻意不对称**：扩散版 `INetworkInfo` 多出 `GetIdentityLength/GetIdentityName(index)`（parse_helper.h:123-125，回归版只有单 identity 版 parse_helper.h:45）；扩散版 `GetAnimatorData/GetAnimatorParams` 按 identityIndex 取指针（parse_helper.h:152-154），回归版无参引用（76-78）；扩散版 `GetExecutorCreationParameters` 额外吃 `identityIndex+constantNoise`（parse_helper.h:157-161）。扩散版 `IAnimatorData` 也薄——没有回归版的两个 PCA reconstruction 读取（parse_helper.h:60-62）。

**实现层**（`internal/parse_helper.h`）是 Owner 类族：`NetworkInfoOwner/AnimatorDataOwner/ModelInfoOwner` 两命名空间各一份（internal/parse_helper.h:42,61,82 回归 vs 125,145,161 扩散），`BlendshapeSolveModelInfoOwner` 在文件后部第二次开命名空间再放一对（internal/parse_helper.h:236-263 回归 / 266-298 扩散）；轨无关的 `BlendshapeSolverConfigOwner/BlendshapeSolverDataOwner`（internal/parse_helper.h:202,220）。两个 Bundle 实现 `GeometryExecutorBundle`（internal/parse_helper.h:301-341）与 `BlendshapeSolveExecutorBundle`（internal/parse_helper.h:343-392）各持 `nva2x::CudaStream`+累积器 vector+执行器（internal/parse_helper.h:337-340），并提供 `InitRegression/InitDiffusion` 双入口（internal/parse_helper.h:317-332）。

## 外部连接

audio2emotion 版示范契约复用：`IPostProcessModel` 直接 `using INetworkInfo = IClassifierModel::INetworkInfo`（audio2emotion/parse_helper.h:92-95），实现层同样 `using IClassifierModel::NetworkInfoOwner`（internal/parse_helper.h:102-103）——后处理模型复用分类器的网络元信息，只重定义 `IEmotionModelInfo`。文件尾 16 个 `Read*ModelInfo_INTERNAL/Read*Bundle_INTERNAL` 声明（internal/parse_helper.h:395-475）被 DLL 门面逐一转发。数据侧 nlohmann_json（core CMakeLists PRIVATE）解析 model.json。

## 数据流

单文件路径：`Read*ModelInfo_INTERNAL(path)` → Owner::Init 解析 model.json 拆出 NetworkInfo/AnimatorData/params 三段。分文件路径（回归版 internal/parse_helper.h:96-102 吃五个路径：networkInfo/network/emotionDatabase/modelConfig/modelData；扩散版 175-181 接受 identityCount+两组路径数组）。Bundle 路径：`InitBase(nbTracks, emotionsCount)`（internal/parse_helper.h:335）先建累积器池再装执行器，`outModelInfo` 出参把模型信息还给调用方。

## 设计决策

- **命名空间而非类名前缀**：`IRegressionModel::INetworkInfo` 与 `IDiffusionModel::INetworkInfo` 同名不同物，避免 `IRegressionNetworkInfo` 式命名膨胀；代价是图谱必须消歧——audio2face 侧用 `-2` 后缀去重，两文件共 **8 对**同名类节点（公共层 4 对 + Owner 层 4 对）；audio2emotion 侧用命名空间限定名（`IClassifierModel::IEmotionModelInfo`），两种策略并存。
- **Owner 模式装真数据**：接口只读，Owner 成员是 `std::vector<std::string>/HostTensorFloat` 等真存储（internal/parse_helper.h:138-142），生命期由 `Destroy()` 管理。
- **扩散按 identity 向量化**：`IdentityData{inputStrength, defaultAnimatorParams, animatorData}` 打包成 vector（internal/parse_helper.h:186-191），与回归版单份成员镜像对仗——两轨代码逐行对照读效率最高。
- **两次开命名空间**：BlendshapeSolve 部分（internal/parse_helper.h:236,266）离第一段 100+ 行后再开同名命名空间，上游的排版选择。

## 新人提示

1. 判断模型是回归还是扩散，看返回指针类型前的命名空间限定即可，两轨的 `GetExecutorCreationParameters` 签名不同，混用编译期就报错。
2. `GetAnimatorData()` 回归版返回引用、扩散版按 index 返回指针（可能为 null），空指针分支别漏。
3. 图谱检索时同名类要带命名空间上下文；`INetworkInfo-2` 这类后缀节点代表扩散轨（文件内第二个出现者）。
4. Bundle 的 `outModelInfo` 出参所有权归调用方，需自行 `Destroy()`，不随 Bundle 释放。
