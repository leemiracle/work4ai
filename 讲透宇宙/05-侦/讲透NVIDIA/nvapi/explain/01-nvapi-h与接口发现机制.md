# 讲透 nvapi 之一：nvapi.h 与接口发现机制

## 一、角色定位

`nvapi.h` 是 NVAPI 的 ABI 母契约：26124 行纯 C 声明，覆盖显示、GPU、OpenGL、D3D、G-SYNC、时钟、驱动设置等数百个 `NvAPI_*` 入口（`NVAPI_INTERFACE NvAPI` 前缀实测 488 条）。它与 `nvapi_interface.h`（接口 ID 总表）、四架构 `.lib`（存根库）共同构成"头文件即 SDK"的三件套——**声明在这里、符号存根在 .lib 里、函数实体在驱动里**。任何 Windows 平台想用 NVIDIA 专有能力（超出 DirectX/OpenGL 标准面的部分）的程序，最终都要落到这两个头文件所定义的世界里。

## 二、内部结构

`nvapi.h` 的 26k 行不是平铺的，是**拼接 + 分区**的：

- 头部 `nvapi.h:38-43` 依次 include 六个 lite 子头：salstart→common→sli→surround→stereo→d3dext；尾部 include `nvapi_lite_salend.h` 收口。lite 子族也可被单独包含（只要自己先带 salstart/salend）；
- 结构对齐由 `nvapi.h:47` 的 `#pragma pack(push,8)` 全局统一；D3D 接口区另有两段 `pack(push,4)` 特例（`nvapi.h:14629,15242`，配对的 pop 在 `:15179` 等），说明 COM 风格接口有独立的对齐契约；
- 生命周期约定写在最前：`nvapi.h:73` "mandatory to call NvAPI_Initialize before calling any other NvAPI"，声明在 `nvapi.h:87`；`NvAPI_Unload` 在 `nvapi.h:117`，注释要求成对调用；
- 类型基座在 lite_common：`NvU32` 的多编译器 typedef 展开（`nvapi_lite_common.h:71,86-97`）、`NvAPI_Status` 状态码枚举（`:264`）、句柄类型（NvPhysicalGpuHandle 等）与高频接口（`NvAPI_EnumPhysicalGPUs` 在 `:633`）。

`nvapi_interface.h` 只有 556 行，主体是 `nvapi_interface_table[]`（`:30` 起，实测 522 条）：每行 `{ "接口名", 32位魔数 }`，如 `{ "NvAPI_Initialize", 0x0150e828 }`（`:32`）。表是按名→ID 的静态字典，驱动侧用同一张表的逆向来分发。

## 三、外部连接

- **向左（使用方）**：示例代码与一切第三方封装。`Sample_Code/GPUHandleEnumeration/gpuHandleEnumeration.c:65/86` 直接调 SYS 枚举；`Sample_Code/DisplayColorControl/NVHelper.cpp:40` 是标准初始化范式（Initialize→GetErrorMessage 翻译错误→失败即退）；
- **向右（实体层）**：GPU 驱动。四架构存根 `x86/nvapi.lib`（439838B）、`amd64/nvapi64.lib`（999686B）、`aarch64/nvapia64.lib`（840896B）、`arm64ec/nvapia64ec.lib`（1102180B）只为链接期供给符号，运行时绑定驱动的 nvapi.dll；ARM64EC 版本的存在说明 Windows on ARM 的 x64 兼容进程被当作一等场景；
- **向上（语义层）**：`docs/R615-NVAP-Reference-OpenSource.chm`（6.37MB）+ 同代 Release Notes PDF——头文件给签名，CHM 给行为语义；
- **同层（专题头）**：`nvapi_lite_d3dext.h:84`（D3D11 CreateDevice 扩展）、`nvapi_lite_sli.h:92`（SLI 状态）、`nvapi_lite_stereo.h`（21 个 Stereo 接口）等按需被拼进主头。

## 四、数据流

一次典型调用的完整路径：

1. 进程启动，链了 `.lib` 的映像里 `NvAPI_QueryInterface` 入口直接可用（存根解析）；
2. 调 `NvAPI_Initialize`（`nvapi.h:87`）——驱动侧完成会话建立；此后其余入口的函数指针既可经存根直连（.lib 提供全部符号），也可走 QueryInterface + 魔数（`nvapi_interface.h` 表）动态获取，两条路并存；
3. 业务调用，例如 `NvAPI_GPU_GetMemoryInfoEx`（`nvapi_lite_common.h:600`）——注意旧接口 `GetMemoryInfo`（`:538`）已从 R520 起废弃（`:519` 注释、`:537` 编译器废弃标注），新代码必须走 Ex 版；
4. 每次调用返回 `NvAPI_Status`，用 `NvAPI_GetErrorMessage` 翻译（示例 `NVHelper.cpp:36`）；
5. 退出前 `NvAPI_Unload`（`nvapi.h:117`）——实践中示例几乎都不做，见 onboarding 第六节的甄别。

## 五、设计决策

1. **魔数 ID 而非导出表**：522 条 ID 表让驱动可按版本裁剪实体、跨 580/R615 等驱动代际保持 ABI 稳定；代价是静态分析工具与调试器看不到常规导出表，第三方绑定要靠这张表文件（这也是 `nvapi_interface.h` 单独成文件的原因——它是机器可读的 ABI 清单）；
2. **lite 子族拼接**：26k 行巨头的维护性靠专题分解；salstart（813 行，`__in` 等空宏从 `nvapi_lite_salstart.h:41` 起）/salend（809 行，`#undef` 从 `nvapi_lite_salend.h:29` 起）卫生对保证"包含 nvapi 头之后用户宏空间零污染"——这是被反复低估的工程质量；
3. **表尾生长**：RISE 三件套与 NGX 条目位于 `nvapi_interface.h` 表尾（`NvAPI_RegisterRiseCallback/RequestRise/UninstallRise` 等），新接口追加在尾部、旧 ID 永不复用——字典是 append-only 的版本化石。

## 六、新人提示

- 先读 `nvapi.h` 前 100 行再读任何教程：初始化强制性与 Unload 配对都写在注释里；
- 写任何代码前 grep 一遍 `deprecated`：`GetMemoryInfo` 这类坑头文件已经标了，别等编译器警告；
- 数接口数量时注意口径：488 条 `NVAPI_INTERFACE NvAPI` 声明 vs 522 条魔数表条目并不一一对应（有宏包装与条件编译），引用数字时说明口径；
- 想理解"魔数从哪来"：它们是驱动侧分发表的 key，`nvapi_interface.h` 是公开镜像；魔数没有算法，只有登记；
- 上手顺序建议：GPUHandleEnumeration（101 行，`gpuHandleEnumeration.c:45` 起）→ NVHelper 范式（`NVHelper.cpp:40-55`）→ 按专题进对应 lite 头。
