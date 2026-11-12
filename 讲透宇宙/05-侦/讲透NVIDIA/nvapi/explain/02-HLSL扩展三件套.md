# 讲透 nvapi 之二：HLSL Shader 扩展三件套

## 一、角色定位

三件套是 NVAPI 里**唯一深入 GPU 执行侧**的部分：让 HLSL 着色器直接使用 warp shuffle、FP16/FP32/UINT64 原子、VPRS 着色率属性求值、纹理 footprint、wave multi-prefix 扫描、光线追踪 micro-triangle 求交等 NVIDIA 专有 intrinsic。三个文件分工明确——`nvHLSLExtns.h`（2578 行）是应用唯一该 include 的公共函数库；`nvHLSLExtnsInternal.h`（955 行）是报文组装的内部实现，注释明言不应被应用直接调用；`nvShaderExtnEnums.h`（179 行）是双端共享的 opcode 契约。它解决的问题是：HLSL 编译器不认识 NVIDIA 扩展指令，需要一个不依赖编译器改动的旁路通道。

## 二、内部结构

**核心机件是 256 字节通信槽**：`nvHLSLExtnsInternal.h:32` 定义 `NvShaderExtnStruct`，`:50` 的注释写明 "struct size: 256 bytes"；`:68/70` 把它声明成假 UAV `RWStructuredBuffer<NvShaderExtnStruct> g_NvidiaExt`。应用必须在包含前自己 `#define NV_SHADER_EXTN_SLOT u7` 选一个未占用的寄存器槽（`:55-58` 注释示例），驱动编译 DXIL 时识别这个特定 UAV 并把读写翻译成扩展指令。

公共层导出按**重载簇**组织（按返回类型扫描实测 175 个顶层函数）：

- `NvEvaluateAttributeAtSampleForVPRS` 一个名字 **12 个重载**（属性类型各一版）；
- `NvInterlocked*Fp16x2` 一簇 8 个（原子操作 × FP16x2 形态）；
- shuffle 族共享掩码前处理 `__NvGetShflMaskFromWidth`（`nvHLSLExtnsInternal.h:80-83`，把 width 参数转成低 width 位全 1 的掩码）。

内部层 29 个 `__Nv*` 函数承担封包：`__NvReferenceUAVForOp` 有 **28 个重载**——每种 UAV 类型（Texture1D/2D/3D/Buffer/RWTyped...）一版，是"先标记操作对象再发 opcode"协议的统一入口；FP16 原子的报文组装在 `__NvAtomicOpFP16x2`（`:304-314`），footprint 的完整报文（FINE/COARSE 模式 + gran 参数）在 `__NvFootprint`（`:634-657`）。调用模式统一是：`g_NvidiaExt.IncrementCounter()` 取槽位下标（`:89-104` 可见三处样例），填字段，驱动侧消费。

opcode 契约在 `nvShaderExtnEnums.h`：74 个 `#define NV_EXTN_OP_*`（从 `:53` 的 `NV_EXTN_OP_SHFL=1` 起），常量 `NV_SHADER_EXTN_VERSION=1`（`:40`）与 `NV_WARP_SIZE=32`（`:45`）。

## 三、外部连接

- **向上（应用/引擎）**：渲染引擎在 shader 编译流水线里注入三件套头 + 槽位宏；C++ 侧配套入口在 nvapi.h 的 D3D 扩展区（`NvAPI_D3D1x_IsNvShaderExtnOpCodeSupported` 支持性探测）；
- **向下（驱动）**：假 UAV 的写入由驱动编译前端识别并 lowering 成硬件指令——这就是"编译器不改也能扩展指令集"的实现方式；
- **横向**：与 `nvapi_lite_d3dext.h:84` 的 D3D11 设备创建扩展同属 D3D 生态，但三件套工作在 pipeline 的 shader 阶段而非设备阶段；
- **契约面**：`nvShaderExtnEnums.h` 被 HLSL 与 C++ 双端包含（纯宏无类型依赖），是三件套里唯一的跨语言文件。

## 四、数据流

一次 `NvShfl` 类调用的路径：

1. 编译期：HLSL 源 include `nvHLSLExtns.h`，公共函数是普通 HLSL 函数，编译器照常内联展开到内部层；
2. 展开后：`__NvGetShflMaskFromWidth`（`nvHLSLExtnsInternal.h:80`）先算参与掩码；
3. 运行期前奏：`__NvReferenceUAVForOp` 的对应重载把目标 UAV 标记进槽（`g_NvidiaExt[index].markUavRef = 1`，`:89-104` 的三处实例）；
4. 报文：函数号（来自 `nvShaderExtnEnums.h` 的 opcode）、操作数、掩码依次写进 256 字节槽的对应字段；
5. 驱动消费：硬件/驱动识别假 UAV 写入，执行真实扩展操作；结果同样经槽字段返回（如原子操作的新值、footprint 的打包结果——`__NvFootprint` 返回打包返回值，`:634-657`）；
6. 安全闸（host 侧）：上线前 C++ 端用 `NvAPI_D3D1x_IsNvShaderExtnOpCodeSupported` 逐 opcode 探测（`nvShaderExtnEnums.h` 的枚举即探测清单），不支持的路径要留 fallback。

## 五、设计决策

1. **假 UAV 而非新语法**：完全不改 HLSL 前端就能发布新 intrinsic——扩展节奏不受编译器发版约束。代价是每条扩展指令变成一串内存写，肉眼读生成的 PTX/SASS 时可读性差；
2. **256 字节定长槽**：所有扩展共用一个报文格式，版本演进靠 opcode 追加（`NV_SHADER_EXTN_VERSION=1` 长期未动），报文格式的稳定性压倒字段利用率；
3. **重载簇而非模板**：HLSL 模板能力有限，用同一名字多版本（VPRS ×12、UAV 引用 ×28）换取调用侧一致性；图谱按簇建代表节点正是对这种组织的正确建模姿势；
4. **内部/公共分层**：`nvHLSLExtnsInternal.h` 的 56 个函数全部 `__Nv` 前缀，明示私有；公共层的函数签名稳定，内部报文格式允许随驱动调整。

## 六、新人提示

- 顺序：先读 `nvShaderExtnEnums.h`（179 行，opcode 清单即能力清单）→ 再读 `nvHLSLExtnsInternal.h:32-70`（槽结构 + 假 UAV 声明，约 40 行看懂协议骨架）→ 最后按需查 `nvHLSLExtns.h` 的目标簇；
- `NV_SHADER_EXTN_SLOT` 槽位冲突是最常见的集成失败：引擎自己的 UAV 绑定清单要给 `u7` 之类的槽让位，且全管线一致；
- 探测再使用：opcode 支持性因驱动/架构而异，`NV_EXTN_OP` 有 74 个不等于目标机全支持；
- 验证集成是否生效：看生成代码里对 `g_NvidiaExt` 的写入序列是否存在——存在即协议在跑，否则头文件只是被 include 了而没被驱动识别；
- 别直接用内部层：28 个 `__NvReferenceUAVForOp` 重载的选型逻辑在公共层封装里，绕过封装要自己保证报文完整性。
