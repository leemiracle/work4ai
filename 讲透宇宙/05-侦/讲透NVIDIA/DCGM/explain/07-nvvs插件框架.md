# 07 · NVVS 插件框架：Plugin 基类、PluginDevice 与 dlopen 注册链路

## 角色定位

NVVS 是 DCGM 的诊断执行引擎，插件框架是它的可扩展骨架：memtest/targetedpower/pcie/diagnostic/nccl_tests/nvbandwidth 等测试均以独立 .so 挂入。框架分三层：C++ 基类 `Plugin`（nvvs/include/Plugin.h:54）、宿主加载器 `PluginLib`（nvvs/include/PluginLib.h:45）、中间的纯 C ABI（PluginInterface.h 七个 `extern "C"` 入口）。C ABI 是进程边界防腐层：两侧可用不同编译器/STL 版本，符号对齐即可协作。

## 内部结构

`Plugin` 唯一纯虚函数是 `Go(testName, entityInfo, numParameters, testParameters)`（nvvs/include/Plugin.h:62），即"执行测试"；另有可覆写的 `GetResults` 虚函数，其余是具体方法（`SetResultForGpu`/`AddError`）与进程启动器 `LaunchExecutable`（nvvs/include/Plugin.h:474，返回 `std::expected<int, dcgmReturn_t>`）。每个测试名对应一个 `PluginTest` 结果容器（nvvs/include/PluginTest.h:33）。**勘误一**：图谱口径"go/Init/passOrFail 虚函数体系"不准确——`passOrFail` 全树零命中；`Init` 只是具体插件的普通成员函数（nvvs/plugin_src/targetedpower/TargetedPower_wrapper.cpp:170 的 `ConstantPower::Init`），真实生命周期是 `Go → Init → worker 线程 → SetResult`。

设备抽象 `PluginDevice` 位于 **nvvs/plugin_src/include/PluginDevice.h:25**（勘误二：在 plugin_src/include/ 而非 nvvs/include/）。它聚合 CUDA 序号/GPU ID/设备属性与 NVML 视角的 `NvvsDevice`，构造时用 `cudaDeviceGetByPCIBusId`（nvvs/plugin_src/include/PluginDevice.h:68）把 DCGM GPU ID 翻成 CUDA 设备序号。nvvs/plugin_src/include/PluginDevice.h:80 的 `#if 0` 块禁用锁频，注释：否则 root/非 root 行为分叉。`CPDevice : public PluginDevice`（nvvs/plugin_src/targetedpower/TargetedPower_wrapper.h:51）是典型扩展。

## 外部连接

`PluginLib::LoadPlugin` 先 `dlopen(path, RTLD_LAZY)`（nvvs/src/PluginLib.cpp:180），再经 `dlsym`（nvvs/src/PluginLib.cpp:271）取六个必需符号（GetPluginInterfaceVersion/GetPluginInfo/InitializePlugin/RunTest/RetrieveCustomStats/RetrieveResults），ShutdownPlugin 可选；nvvs/src/PluginLib.cpp:202 校验接口版本等于 `DCGM_DIAG_PLUGIN_INTERFACE_VERSION`（当前 v7，nvvs/include/PluginInterface.h:47），析构时回调 ShutdownPlugin 后 dlclose。插件 .so 用版本脚本 nvvs/plugin_src/nvvs_plugin.linux_def:2 只导出这七个符号。插件侧外壳范例见 nvvs/plugin_src/diagnostic/DiagnosticWrapper.cpp:78（`InitializePlugin` 里 `new GpuBurnPlugin` 存入 userData）与 :95 的 `RunTest`（一行 `gbp->Go(...)`）。宿主侧 `PluginCoreFunctionality`（nvvs/include/PluginCoreFunctionality.h:28）承担 DcgmRecorder 字段监控与 stats 写出。

## 数据流

起点 TestFramework::loadPlugins（nvvs/include/TestFramework.inl:677）：先单独 dlopen `libpluginCommon.so.4` 作符号资源库，再扫 `cudaless` 与按驱动版本选择的 `cuda{N}` 目录；`LoadPluginWithDir`（nvvs/include/TestFramework.inl:562）只接受 `*.so.<纯数字>` 文件且要求属主/权限与 nvvs 二进制一致。每个库过 `LoadPlugin → InitializePlugin → GetPluginInfo` 三关才进 `m_plugins`；nvvs/include/TestFramework.inl:705 为每个 supported test 造 `Test` 对象并按 testCategory 归类——diag 配置（dcgmi diag -r 或 JSON）正是在此按类别/名字挑测试。运行期 `PluginLib::RunTest` 注入 fail_early 隐式参数后在 nvvs/src/PluginLib.cpp:632 调 `m_runTestCB`，结束后回收 stats 与 results。

## 设计决策

其一，**C ABI 优先于 C++ 工厂**：nvvs/include/Plugin.h:514 声明的 `maker_t` 工厂与 factory map 全树零消费者，属遗留声明，真正的注册链是 dlsym 取 C 函数指针。其二，**新旧两代布局并存**：老式巨石布局如 TargetedPower_wrapper.cpp（1527 行，插件类+CudaInit+worker 线程同文件）；新式如 nccl_tests 把插件类独立（`DcgmNs::Nvvs::Plugins` 命名空间），`GetNcclTestsExecutablePath()` 返回 `std::expected<boost::filesystem::path, dcgmReturn_t>`（nvvs/plugin_src/nccl_tests/NcclTestsPlugin.cpp:31）是 C++23 风格先行者。其三，**异常三重防御**：宿主对回调套三层 catch，插件抛异常不击穿主进程。其四，挂起检测按插件豁免（nvvs/src/PluginLib.cpp:894 排除 EUD，防 worker 等待造成假阳性）。

## 新人提示

- **勘误三**："CudaInit 约 359 行"指函数长度而非行号：`ConstantPower::CudaInit` 起于 nvvs/plugin_src/targetedpower/TargetedPower_wrapper.cpp:245、止于 :603，函数体恰 359 行。
- **勘误四**：NcclTestsPlugin.cpp 引 boost/process 只用 `this_process::environment` 与 boost::filesystem 做环境变量/权限检查；子进程实际由基类 `LaunchExecutable`（nvvs/src/Plugin.cpp:372，fork+exec+waitpid）派生，别记成"boost::process 管子进程"。
- 写新插件从 DiagnosticWrapper.cpp 复制起步；`aux_source_directory` 把目录所有 .cpp 收编进同一 .so——目录内两个 wrapper 是分工而非弃用：大文件提供类实现，小的提供 C ABI。
- 排查"插件没被加载"逆链查：目录是否 cuda{驱动主版本}、文件名是否 `.so.数字`、权限属主是否与 nvvs 一致、接口版本是否 v7、numTests 是否超 20（nvvs/src/PluginLib.cpp:339 拒绝）。
