# gpu-webgpu-decoder —— WebGPUDecoderImpl：GPU 进程侧的 WebGPU 命令解码器

## 1. 角色定位

`gpu/command_buffer/service/webgpu_decoder_impl.cc`（2579 行）是 WebGPU 在 **GPU 进程侧的命令解码器**。renderer 的 WebGPU 调用不直接碰驱动：Dawn wire client 先序列化成字节流，连同 Chromium 命令缓冲控制命令经 IPC 进 GPU 进程，本文件就是这些命令的"海关+执行器"。职责三块：命令分发（`DoCommands` L1893）、Dawn 整块接管（`HandleDawnCommands` L1965，语义校验归 Dawn）、Chromium 互操作（SharedImage 关联 L2145、隔离 token L2529、适配器选择 L1632）。实现全藏在匿名 namespace（L81-L1043），对外只露工厂 `CreateWebGPUDecoderImpl`（L1045），头文件仅 45 行一个声明。

## 2. 内部结构

`class WebGPUDecoderImpl final : public WebGPUDecoder`（L131，至 L1027）。命令分发三件套：`CmdHandler` 函数指针 typedef（L315-317）、`CommandInfo`（L320-325）、`command_info` 静态表（L1029-1041）——由 `WEBGPU_COMMAND_LIST` 宏生成（handler 原型同宏批量声明 L333-336），改命令集只动 autogen 清单。继承自 DecoderContext 的几十个 GLES2 味接口几乎全是 `NOTREACHED()`（L156-L312）；有真身的少数：`MakeCurrent`（L158-163）、`PerformPollingWork`（L208 起，`InstanceProcessEvents` L216 + 剪枝死设备 L218-226）。

mailbox 包装是类内精华，三族派生自纯虚基类 `SharedImageRepresentationAndAccess`（L453-459）：**Dawn 直连版**（L462-477）零拷贝包装 ScopedAccess；**Skia fallback 版**（L481 起，格式白名单 L495-501）给 CPU 适配器用，内部 MapAsync 读回+writePixels 上传+信号量同步（L810-892）；**Error 版**（L905-933/L971-993）失败时 CreateErrorTexture（L922）兜底。两张 flat_map 按 `<ID, generation>` 登记纹理/buffer（L937-939/L997-999）；`known_device_metadata_`（L1018-1019）在 RequestDeviceImpl（L1426）回填（L1601-1613），是 Dawn/Skia 分派依据（L2215-2224）。其余方法行号均经 grep 实证（Destroy L1197、IsFeatureExposed L1261、CreatePreferredAdapter L1632、OnGetIsolationKey L2515 等）。

## 3. 外部连接

图谱中该文件 51 条出边（36 imports + 14 contains + 1 inherits）。**继承**：`WebGPUDecoderImpl → WebGPUDecoder`；`webgpu_decoder.h` L40 显示父链是 **DecoderContext 而非 GLES2DecoderBase**（见第 5 节）。**Dawn 服务层**：dawn_instance（L1114 创建、L1181 注入）、dawn_platform（L1097）、dawn_wire_server（L1178）、memory transfer（L1104）与 serializer（L1105）。**SharedImage 体系**：shared_image_representation.h 三类表示的消费端在本文件，shared_context_state 是 Skia fallback 载体；isolation_key_provider 唯一实现是 GpuChannel，契约 provider outlive decoder 故只存 raw_ptr（L435-438）。**创建链**（入边取证）：`webgpu_decoder.cc` L29 Create→CreateWebGPUDecoderImpl（calls 边）；上游 `webgpu_command_buffer_stub.cc` L100（GPU 进程主路径）与 `in_process_command_buffer.cc` L329（单进程/测试）。

## 4. 数据流

一帧 WebGPU canvas 渲染时序（行号实证）：

1. **renderer 序列化**：Dawn wire client 序列化进共享内存，`DawnCommands` 命令排入命令缓冲；canvas 新帧由 `client_shared_image.cc` L1456 发 DissociateMailboxForPresent。
2. **分发**：`DoCommands`（L1893）做 size/越界校验（L1910-1918），`destroyed_` 为真直接 kLostContext（L1925-1928），查表执行 `(this->*info.cmd_handler)(...)`（L1935），公共命令走 DoCommonCommand（L1940）。
3. **Dawn 反序列化**：`HandleDawnCommands` 取字节流（L1976-1977），套 `ScopedParentDecoder(this)`（L1991，把 this 放 thread_local `parent_decoder`，L118-129），`wire_server_->HandleCommands`（L1992）一条命令携带任意多条 Dawn 命令，失败即 kLostContext（L1993），随后 PerformPollingWork（L2000）。
4. **proc 拦截**：构造时把 instanceRequestAdapter/adapterHasFeature/adapterGetFeatures/adapterRequestDevice 四个 proc 换成从 TLS 取 decoder 转发（L1148-1176），createInstance 直接 NOTREACHED（L1149-1150）——实例只能由 Chrome 注入。RequestAdapterImpl（L1320）判 compat 选适配器（L1335-1348）；isolation key 未就绪则 defer 回调（L1362-1388），等 OnGetIsolationKey（L2515）兑现（L2521-2524）。链头 SetWebGPUExecutionContextToken（L2529）识别四类上下文并异步取 key（L2535-2574）。
5. **交换链出帧**：HandleAssociateMailboxImmediate（L2145）校验+查重（L2164-2212），CPU 适配器走 Skia 否则 Dawn 直连（L2215-2224），失败注 error texture（L2226-2234），成功 InjectTexture+登记（L2238/L2246）。Present 时查初始化态（L2302-2303），未初始化则清黑（L2306-2309）——compositor 把未初始化纹理画成红色。
6. **回程**：Dawn 回调经 wire_serializer_ 打包，client 端 OnGpuControlReturnData（webgpu_implementation.cc L321/L338）交 dawn_wire_->HandleCommands（L341）回 renderer。

## 5. 设计决策

**独立 decoder 不复用 GLES2 解码器**：WebGPU 语义验证权在 Dawn wire，命令缓冲层只剩外壳命令，故继承 WebGPUDecoder→DecoderContext 只为接入统一调度/生命周期，几十个 GL 接口用 NOTREACHED() 明示边界（L156-L312）而非从 GLES2DecoderBase 裁死代码——代价是占位税，收益是两条解码路径互不污染。

**thread_local parent_decoder 而非全局单例**（L118-129）：wire server 是 C 风格 proc table 无法持有成员上下文，TLS 让多 decoder 并存时拦截 proc 仍能找回宿主，RAII 处理完即清空。

**错误三级隔离**：usage 校验失败只让该次 Associate 失败（L2017-2071，注释明言 usage 可能来自网页，必须优雅处理而不能丢 context/device）；彻底失败注 error texture/buffer（L2226-2234）；wire server 失败或销毁后才 kLostContext（L1926/L1993）。Destroy（L1197）按 deferred 回调→map→device.Destroy()→wire server→断连 platform 顺序拆台（L1203-1223）。

**安全门控前置**：IsFeatureExposed（L1261）三级安全档（L1263-1274）+ runtime_unsafe_features_ 过滤（L1302-1312）+ default 拒绝（L1314-1315）；RequestDeviceImpl 强制 disallow_spirv（L1552-1554，只保证 WGSL 安全）并私加平台 interop features（L1477-1514）；use_blocklist（L1624-1630）只在 unsafe 模式放行 blocklisted 适配器（L1788）。

## 6. 新人提示

- **改命令集别改这里**：表注册由宏生成（L333-336/L1029-1041），清单在 `common/webgpu_cmd_format_autogen.h`（py 脚本再生成）。
- **volatile 纪律**：命令数据来自 renderer 可写共享内存，经 const volatile 指针读、校验拷贝后才 UNSAFE_TODO 解引用（L2169-2198），忘记 volatile 是安全评审红线。
- **生命周期**：isolation_key_provider_ raw_ptr 契约靠 GpuChannel 保证（L435-438）；deferred 回调 Unretained(this) 依赖析构先跑 Destroy 兑付（L1384-1385/L1203-1206）。
- **测试**：`service/webgpu_decoder_unittest.cc`（L38 建 decoder）；mailbox/interop 在 `tests/webgpu_mailbox_unittest.cc`（25 个 TEST，Skia fallback 白名单见 L494 注释）。
- **调试**：perfetto 类目 gpu.dawn 已埋点（L1984-1988）；命令行开关映射 safety_level_/backend_types/power preference（L1107-1126/L1748-1777）；改强制 toggle 同步 GetDawnTogglesForWebGPU()（about:gpu，L1546-1547）。
