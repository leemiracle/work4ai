# 03 · BERT-FMHA 插件：bertQKV 全家、FMHA v1/v2 双调度头与 pimpl 心脏

## 角色定位

`plugin/bertQKVToContextPlugin/` 是全仓最大单插件（图谱 L05 逻辑层 20 节点 + L06 二进制层 181 节点），实现 BERT 的 fused QKV→context 多头注意力。一个注册名 **`CustomQKVToContextPluginDynamic`**（`qkvToContextPlugin.cpp:47`）之下藏着六个 Creator、两代接口、两代 FMHA kernel、三档降级路径——它是理解 TensorRT 插件工程学的最佳标本。目录四条线：`qkvToContextPlugin.cpp`（1534 行，V3 主实现）、`qkvToContextPluginLegacy.cpp`（V2 双轨）、`qkvToContextInt8InterleavedPlugin.cpp`（int8 交错变体）、`mhaRunner.{h,cu}`（调度心脏）。版本坐标：Legacy 固定/变长序列为 "1"/"2"（`qkvToContextPluginLegacy.cpp:46-47`），V3 固定/变长为 "4"/"5"（`qkvToContextPlugin.cpp:45-46`），int8 交错 "6"（`qkvToContextInt8InterleavedPlugin.cpp:41`）。

## 内部结构

V3 主类 `QKVToContextPluginDynamic` 四重继承 `IPluginV3+OneCore+OneBuild+OneRuntime`（`qkvToContextPlugin.h:55-59`），双构造器分工：build 期走字段构造，反序列化期走携带 MHARunner 状态的九参构造（:66-68，从 `runnerStateBuffer` 复活 dispatcher）。变长序列姊妹 `QKVToContextVarSeqlenPlugin`（:184）与两个 Creator（:160/:289）构成 V3 侧四件。核心策略对象是 `MHARunner` 抽象基类（`mhaRunner.h:42`）：`setup(S,B,headSize)`（:64）预算 QKV/out 的 ld 与 stride，双 `run` 纯虚（:82-96）对应单/多张量两代 enqueue 协议。四条 fused 具体类分层两代——v1 `FusedMHARunnerFP16`/`FusedMHARunnerInt8`（:148/:176）走 cublas+自研 softmax 非融合路径增强版，v2 `FusedMHARunnerFP16v2`/`FusedMHARunnerInt8v2`（:205/:233）对应 cubin 资产二代（04 篇）。**pimpl 模式**：每个 fused 类的真身是 `.cu` 里嵌套的 `mhaImpl`（`mhaRunner.cu:630/:773/:920` 三处 `class Xxx::mhaImpl`），头文件只留 `std::unique_ptr<MHARunner>` 成员（`qkvToContextPlugin.h:136-138` 的 fusedDispatcher/unfusedDispatcher、:262 的 mDispatcher），编译防火墙同时隐藏 CUDA 依赖。

## 外部连接

向上：`REGISTER_TENSORRT_PLUGIN` 双注册（cpp:50/:55）；创建器字段表 `{"type_id","S","B","hidden_size","num_heads","has_mask","SM","hasUnfusedDispatcher"}`（:638）——SM 由引擎传入决定 cubin 档位，`hasUnfusedDispatcher`（:568 序列化字段）记录克隆时降级态。向旁：`plugin/common/bertCommon.h` 的 `getMHAMaskPackedSize`（:100-127）按 64/96/128/384 四档 seqlen 决定 mask 打包尺寸（:112/:116/:120/:124），maskIdx 格式与 embLayerNormPlugin 跨插件互认（README 明文引用其文档）——05 篇的 LN 插件族共享同一套 BERT 输入语义。向下：v2 路径依赖 04 篇的 cubin 资产表；v1/降级路径经 `createPluginCublasWrapper`（02 篇基座）取 cuBLAS 句柄做 QKV 投影。`zeroPadding2d.{h,cu}` 的 `QkvPaddingRunner`（h:38，cu:150）是变长序列的补丁器：v2 cubin 只按 headSize=64 编译，非 64 的头宽先零填充再裁剪。

## 数据流

build 期：Creator 解析字段 → 构造插件 → `configure`/`onShapeChange` 阶段反复调用 `createMHARunner()`（cpp:128-145）——按类型选 `FusedMHARunnerFP16`（:134）或 `Int8`（:137），并恒定构造 `unfusedDispatcher` 兜底（:142）；随后以 `fusedDispatcher->isValid(mHeadSize, mS)`（:335/:392/:411）探测 cubin 覆盖，失败即整批回退 unfused。clone（:144-160）是个精巧动作：把 unfused dispatcher 的运行态序列化进 `mRunnerStateBuffer`（h:157）供反序列化构造器复活。变长序列路径（:852-883）：先断言 `mHeadSize<=64`（:859），非 64 挂 `QkvPaddingRunner`（:862-864），再选 v2 runner（:867/:871），否则退回 `UnfusedMHARunner`（:880）。执行期 `enqueue`（:522 邻域）按 mask 有效性与 `isValid` 终裁分派。INT8 特殊约束：seqlen 仅支持 128/384（:224 错误信息），mask 打包尺寸对账失败即拒（:262）。

## 设计决策

①**一个注册名六个版本号的「地铁图」**：同名不同 version 是注册表寻址键，V2/V3 双轨共存、固定/变长/int8 三业务线共享一个 ONNX 算子名——迁移期引擎图无缝换轨，代价是任何人改 version 常量都会静默改变解析器选择。②**pimpl 到 .cu 层而非只到 .cpp**：插件公共头（被 parser 与 NvInfer 侧大量 include）零 CUDA 符号泄漏，编译隔离比常规 pimpl 更深一层。③**isValid 运行时探测而非 build 期硬表**：headSize×seqlen×SM 组合空间大，逐 shape 探测 cubin 覆盖后降级，把「支持矩阵」变成数据而非文档承诺。④**克隆即序列化降级态**：fused 与 unfused 的选择发生在 build 期 shape 收集后，clone 必须携带该决策，否则子上下文行为漂移。⑤**v2 只编 headSize=64 + 补丁器**：不为长尾头宽扩 cubin 矩阵，用零填充复用主流档——性能换资产规模的经典取舍。

## 新人提示

读代码顺序建议：`qkvToContextPlugin.h`（类族地图）→ `mhaRunner.h:42-96`（Runner 协议）→ cpp:128-145/:852-883（两条装配线）→ `mhaRunner.cu` 任一 `mhaImpl`。三个高频困惑：① grep `IPluginV2DynamicExt` 在主实现里找不到是对的——V3 时代只存在 Legacy 文件；② `hasUnfusedDispatcher` 出现在序列化字段（:568）不是 bug，是克隆降级态的持久化；③ 调试 mask 问题时先看 `bertCommon.h:100-127` 的四档打包尺寸，seqlen 96 的 packed mask 与 128 用不同常量。PluginConfig.yaml 中 `var_seqlen=1` 被注释禁用（SM 专属测试未支持），想在 yaml 层跑变长序列会踩空。
