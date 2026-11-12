# 05 lib/ 二进制矩阵：68 个库文件的组织律与分发工程

## 角色定位

`lib/` 是本仓体量的绝对主体（68 文件约 1.31GB，占图谱节点 66/102 中的 68 件 file 节点），承担"预编译即插即用"的分发职责。它分两类角色：**薄壳静态库**（nvsdk_ngx_*.lib/.a，只含 Init 等引导符号，把调用转进动态库）与**特性动态库**（nvngx_*.dll / libnvidia-ngx-*.so，DLSS/RR/FG 神经网络的真正宿主）。运行时真身由 loader 发现链定位（`include/nvsdk_ngx_loader.h:65` Linux 找 `libnvidia-ngx.so.1`，`:315-321` Windows 找 `_nvngx.dll`/`nvngx.dll`/`_arm64_nvngx.dll`）。

## 内部结构（五目录正交展开）

- **`Linux_x86_64`/`Linux_aarch64`（各 7 件）**：根 `libnvsdk_ngx.a` 薄壳（89KB）+ `dev/`/`rel/` 两目录各三件 `libnvidia-ngx-{dlss,dlssd,dlssg}.so.310.9.1`。dev 版带调试信息硕大（dlss.so 60MB、dlssd.so 49MB），rel 版 stripped ELF（file 命令实证）。版本号 310.9.1 与 git 提交名一致。
- **`Windows_x86_64`（34 件，最富）**：`x64/` 主目录十个静态库 = {d,s}×{plain,_dbg,_iterator0,_iterator1} 正交（d=动态 CRT 链接、s=静态 CRT；dbg=Debug 运行库、iteratorN=启用迭代器调试级别 0/1 的变体，供老 MSVC 调试器兼容）；`vs2010/`/`vs2012/`/`vs2013/` 各 4 件老工具集构建（游戏业长尾引擎的编译器兼容承诺）；`khr/x64/` 4 件 Khronos 变体；`uwp/x64/` 2 件 UWP 沙箱变体；`dev/`+`rel/` 各三 DLL。
- **`Windows_aarch64`/`Windows_arm64ec`（各 10 件）**：各 4 静态库（nvsdk_ngx_{d,s}{,_dbg}.lib）+ dev/rel 各三 DLL。arm64ec 是 x64 兼容 ABI 的 ARM64 变体（Windows on ARM 跑 x64 进程用），与原生 aarch64 并列存在本身就是微软双 ABI 现状的税单。

**命名律总结**：DLL 按 `nvngx_{dlss,dlssd,dlssg}` 三特性 × dev/rel 二分；静态导入库按 `nvsdk_ngx_{d|s}{|_dbg|_iteratorN}` × 工具集 × 平台变体展开。18 DLL + 36 .lib + 12 .so + 2 .a = 68。

## 外部连接

应用侧链接姿势三选一：①链 `libnvsdk_ngx.a`/`nvsdk_ngx_d.lib`（薄壳），运行时经 loader 发现驱动内 NGX Core；②随应用分发 `nvngx_*.dll`/`libnvidia-ngx-*.so` 到 exe 目录，让 loader 第一步"应用目录"（`include/nvsdk_ngx_loader.h:324-339`）命中——SDK 版 DLSS 库可绕过驱动 OTA 管控，供开发者固定模型版本调试；③header-only：定义 `NVSDK_NGX_HEADER_ONLY` 后免链接（`include/nvsdk_ngx.h:705-710` 自动拉 loader+standalone_cuda）。搜索路径还可经 `NVSDK_NGX_FeatureCommonInfo.PathListInfo`（`include/nvsdk_ngx_defs.h:402-403`，降序优先级列表）扩充。

## 数据流

dev vs rel 的语义差：dev DLL 供开发期排障（符号/日志更全），rel 供发行。三 DLL 分工对齐 defs.h Feature 枚举——dlss↔SuperSampling(1)（defs.h:190）、dlssd↔RayReconstruction(13)（`:214`）、dlssg↔FrameGeneration(11)（`:210`）；每个特性独立成库使游戏可只分发所需子集。

## 设计决策

1. **薄壳+真身分离**：SDK ABI（nvsdk_ngx_*）极稳，真身（nvngx_*）随驱动/模型频繁 OTA——loader.h 五级发现链就是为这个版本解耦而生。
2. **CRT/工具集正交**：静态库按 CRT 与调试迭代器级别全展开，是对 Windows 游戏引擎碎片化生态的工程妥协（vs2010-2013 目录是活化石层）。
3. **uwp/khr/arm64ec 变体**：每个平台小众形态单独出库而非宏开关，保每个 .lib 都"开箱即链"。

## 新人提示

取库口诀：桌面 Win 主流 = `x64/nvsdk_ngx_d.lib`（或 s）；调试崩溃在 STL 迭代器 = 换 `_iterator` 变体；Linux 只需链根目录 .a。想固定 DLSS 模型版本做 A/B 对比，把 `rel/` 三 so/dll 拷到 exe 旁即可（loader 第一步就会命中）。版本核对看文件名 `.so.310.9.1`，与 git 提交、doc/ 编程指南版本号应一致。
