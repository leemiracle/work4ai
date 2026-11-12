# Maya-ACE 新人上手指南（ONBOARDING）

> 图谱 957 节点/1511 边/14 层/16 步 tour（commit `f0dc136`）。行号锚均经源码核实，路径相对仓库根。

## 1. 项目定位与背景

Maya-ACE（插件模块名 **mace**）是 NVIDIA 官方 Audio2Face-3D Maya 插件：语音音频一键生成面部动画——输出 ARKit 52 表情 blendshape 权重曲线或脸/舌几何变形。版本 2.0.0（`source/VERSION.md:1`），由 `CMakeLists.txt:27` file(READ) 读入注入 mace.mod。CHANGELOG 把 2.0.0（2025-08-27）定性为"本地推理"大版本：此前只有云端链。

双工作流是第一把钥匙：**本地**走 A2X SDK+TensorRT，在 ≥8GB VRAM 的 GPU 上跑 v3.0（diffusion 多身份）/v2.3.x（regression，Claire/James/Mark）模型；**云端**经 NVCF gRPC 调 build.nvidia.com 的 A2F-3D NIM，本地只需网络与 API key。

C++/Python 混合：C++ 侧 maya_ace 插件 .mll、ace_client 云端客户端库、ace_grpc_cpp 生成物；Python 侧 grpc_py 同契约绑定、mock_server 假服务、maya_ace/scripts 脚本链；另有脱离 Maya 的 metahuman_batch 批量样板。平台 Maya 2024/2025+Windows（CMake 留 WANT_MAYA_2022..2026 选项），模型经 `download_models.bat:33-39` 从 HuggingFace 五组拉取。

## 2. 总体架构：14 层逐层概述

| 层 | 名称 | 文件数 | 概述 |
|---|---|---|---|
| L01 | Proto 契约源 | 35 | 12 个 .proto（音频流/动画数据/情感/服务接口）+protoc 驱动脚本+wheel。 |
| L02 | C++ gRPC 生成物 | 87 | 51 组 pb/grpc.pb/mock 桩，ace_client 类型底座，勿手改。 |
| L03 | Python 生成物与 Mock | 54 | grpc_py 各模块 pb2 绑定+mock_server 四服务假实现。 |
| L04 | C++ 云端客户端 | 22 | NVCFGrpcClient 基类、IA2FClient 接口、controller/healthcheck/config 三客户端、audio 重采样、NetworkedAnimation 主入口。 |
| L05 | 插件骨架与节点 | 18 | plugin.cpp 注册 7 种 MPxData+双播放节点+双命令；A2FAnimationPlayer（本地 72 属性）与 AceAnimationPlayer（云端 55 属性）。 |
| L06 | 公共数据与本地推理 | 12 | a2x_data 智能指针体系、a2x_executors 工厂、a2x_models 轻量解析、names 常量、maya_utils/nvcloud/timeslider。 |
| L07 | Maya 脚本工具链 | 36 | ace_tools（setup/config/preset/ui）、ace_ae_templates（AE 界面）、trtgen（TRT 引擎构建）。 |
| L08 | 插件 Python 测试 | 21 | pytest 覆盖插件加载/双节点/配置新旧格式/preset/trtgen。 |
| L09 | C++ 单元测试 | 23 | tests/{ace,a2x,maya} 三线 GoogleTest+gmock；test_with_coverage.py 汇总。 |
| L10 | MetaHuman 批处理示例 | 18 | batch_a2f.py grpc.aio 双向流批量推理+FBX 导出；Mace_Add-On 对话框与 ACE2Rig 映射。 |
| L11 | 示例与样例资产 | 26 | 三角色场景（Git LFS）+短音频；README 含模型三要素匹配指南。 |
| L12 | 用户文档与许可 | 43 | docs/ 十篇手册+30 份第三方许可。 |
| L13 | 构建与依赖 | 32 | 根 CMakeLists+12 个查找器（FindMaya/FindTensorRT 等）+packman 工具链+deps 清单。 |
| L14 | 工程门面 | 19 | README 等+12 个根目录 .bat 入口。 |

依赖方向：L01→L02/L03 双语言生成物→L04/L10 分别消费；L05 同时依赖 L04（云端）与 L06（本地）；L07 驱动 L05；L08/L09 两侧验证。

## 3. 核心链路数据流

**云端 NIM 链（音频→gRPC→帧缓存→Maya）**：①`source/maya_ace/nodes/ace_player.cpp:291` computeLoadAudio 读 WAV，`source/ace_client/audio.h:29` DEFAULT_SAMPLE_RATE=16000、`audio.h:37` resample 归一采样率；②点 Request New Animation 触发 `source/maya_ace/nodes/ace_player.cpp:528`→`source/ace_client/animation.h:71` ConnectAndSendAudio：经 `source/ace_client/a2f_controller_client.h:49` SendAudio 以双向流 ProcessAudioStream（`nvidia_ace.services.a2f_controller.v1.proto:29`）推音频、同步收动画流；③返回权重组装成 AnimDataFrame（`source/ace_client/frame_receiver.h:29`：blendshape/emotion 名称+权重+音频样本+时间戳），由 NetworkedAnimation（`source/ace_client/animation.h:46`）按 30fps（同文件 `:40`）缓存；④播放时 `:72` FetchAnimationFrame 补拉、`:51` GetBlendshapeWeights 取帧写输出属性；⑤经 setup.py 连线驱动 blendshape 节点。服务三元组 networkAddress/apiKey/functionId（`source/maya_ace/nodes/ace_player.h:84-86`）默认 NVCF：地址与 function_id 硬编码于 `source/ace_client/grpc_client.h:60/64`，超时 3 秒（`:31`）。

**本地 TRT 链（音频→累加器→双执行器→几何/权重）**：①trtgen 离线建引擎：`source/maya_ace/scripts/trtgen/models.py:25` 读 A2F_MODEL_DIRS、`:90` 以 network.trt 判就绪，builder.py `:31/34` 包装 trtexec；②首次求值惰性建资源：`source/maya_ace/nodes/a2f_player.cpp:186` 音频累加器、`:206` CUDA 流、`:226` 后台求值线程，全部包成 MayaData MPxData 注册为内部属性（`source/maya_ace/nodes/a2f_player.h:141-151`）；③执行器装配：`source/maya_ace/common/a2x_executors.h:48/95` 两工厂依 Audio2FaceModelInfo（`source/maya_ace/common/a2x_models.h:38`）分叉——regression 走 `:75`、diffusion 走 `:88`；④播放时 `a2f_player.cpp:93` compute 总分发，`:146` computeBlendshapeSolveResults 输出（GPU/CPU 求解器由 `a2f_player.h:73` 切换）；⑤输出 blendshape 权重（52，`source/maya_ace/common/names.h:24`）+几何+情绪（10，`:26`）。

两链汇合点相同：时间滑块→compute→输出属性→blendshape/mesh。quickstart：本地 james_v3_fullface.ma 60fps 等时间轴绿线（`docs/quickstart.md:33-37`）；云端 ace_v2_arkit.ma 30fps 等 Received frames（`:84-106`）。

## 4. 模块深读

**插件本体**：`source/maya_ace/plugin.cpp:74` initializePlugin 注册 7 种 MPxData（`:81-93`）、两节点（`:96-103`）、两命令（`:105-108`：request_sendaudio 手动触发云端推理、export_service_config 拉服务端配置）与节点增删回调。`source/maya_ace/nodes/a2x_plugin_data.h:45` 的 MayaData<T,Tid> 模板把执行器/CUDA 流等 C++ 重对象注册成 Maya 数据类型（`:64` BackgroundEvaluationData 携带后台线程上下文，推理在后台跑）。A2FAnimationPlayer（`source/maya_ace/nodes/a2f_player.h:35`）72 属性：音频段 `:63-66`、模型配置 modelConfigs 下 a2eModelPath/a2fModelPath/identityIndex/useGpuBlendshapeSolver `:69-73`；compute 为总分发+子例程结构（`:186/206/226/242/262/282` 一 compute 一资源）。AceAnimationPlayer（`source/maya_ace/nodes/ace_player.h:41`）55 属性，多服务三元组而无需模型/TRT 属性。

**ace_client**：`source/ace_client/status.h:25` AceClientStatus 十态+`:38` AceClientResult 统一错误语义；`source/ace_client/a2f_client_interface.h:39` IA2FClient 纯虚接口解耦动画逻辑与传输；`source/ace_client/grpc_client.h:49` NVCFGrpcClient 基类封装 channel/鉴权。三客户端：A2FControllerClient（`source/ace_client/a2f_controller_client.h:36`，`:49/55` SendAudio/FetchFrame）、健康检查（同目录 a2f_healthcheck_client.h:31）、配置（a2x_config_client.h:41）。参数体系（`source/ace_client/parameters.h:31-81`）：面部 13 项+情感后处理 6 项（`:61-62` 默认 1.0/0.6）+情绪状态 10 维。

**proto 契约**：数据侧 a2f.v1（AudioStream+BlendShapeParameters 的 offsets/multipliers map）、animation_data.v1（15 个 message，带时码原语）；服务侧四组——PushAudioStream 单向流（`nvidia_ace.services.a2f.v1.proto:25`）、ProcessAudioStream 双向流（a2f_controller `:29`）、AnimationDataService Push/Pull 双 rpc（`nvidia_ace.services.animation_data.v1.proto:36/42`）。`examples/metahuman_batch/proto/generate_code_from_protos.py:45` 驱动 grpc_tools.protoc 批量生成、`:148-156` 递归补 __init__.py；C++ 侧 51 组生成物含 mock 桩直接供 gmock 用。

**Python 脚本链**：ace_tools/setup.py 是装配编排层——`source/maya_ace/scripts/ace_tools/setup.py:44-45` 节点类型常量、`:189` connect_a2f_player_to_mesh 拆 mesh 历史接线、`:263` 把时间滑块音频接到所有 player；`source/maya_ace/scripts/ace_tools/config.py:42` export_a2f_parameters 按映射表导出、`:81-83` YAML 优先（`:314-316` 无 PyYAML 降级 JSON）、兼容旧扁平格式。ace_ae_templates 渲染两节点 AE 界面。trtgen 可 `python -m trtgen` 脱离 Maya 跑。`python/mock_server.py` 四 Servicer（`:52-62`），默认 127.0.0.1:50051（`:183`、`--port` `:218`），可独立进程也可嵌入 pytest（`:191-198` 自动设默认 URL 环境变量）。批处理 `examples/metahuman_batch/scripts/batch_a2f.py:193` write_to_stream 推音频、`:132` read_from_stream 收流、`:444` grpc.aio 异步双工；ACE2Rig 依 MH_Mapping.json 把 52 ARKit 权重线性组合映射 MetaHuman 控制通道。

## 5. 关键设计决策

1. **接口解耦传输**：IA2FClient（`a2f_client_interface.h:39`）让 NetworkedAnimation 帧缓存逻辑不感知 gRPC，测试可换 mock 替身。
2. **MayaData 模板包装**：不可序列化的 GPU 资源经 MPxData 注册进依赖图（`source/maya_ace/nodes/a2x_plugin_data.h:45`）；代价是存场景后重开须惰性重建。
3. **Destroyer/UniquePtr**：SDK 对象必须 Destroy() 而非 delete，`source/maya_ace/common/a2x_data.h:36/46` 把约定固化进类型系统。
4. **rapidjson 轻量解析**：SDK ModelInfo 读秒级太慢，`source/maya_ace/common/a2x_models.h:38` 直读 model.json 判 regression/diffusion。
5. **生成物进仓**：双语言生成物提交进仓，用户装插件无需 protoc 工具链。
6. **mock 双形态**：mock_server 独立进程/嵌入 pytest 两用+C++ mock 桩，无云端账号全链可测。
7. **版本单一真源**：VERSION.md 由 CMake 读入（`CMakeLists.txt:27`），一处改动全产物跟随。

## 6. 测试与质量体系

三线一网：①tests/ace 云端客户端线——`tests/ace/test_a2f_controller_client.cpp:41` 用 mock 桩 MockA2FControllerServiceStub+`:52` 手写 MockClientReaderWriter 模拟双向流，被测类以 friend class 开私有成员（`source/ace_client/a2f_controller_client.h:79-81`、`a2x_config_client.h:84` 同模式）；②tests/a2x 本地线——`test_a2x_models.cpp` 803 行 25 用例临时目录夹具全覆盖，`test_a2x_executors.cpp` 回归/扩散×GPU/CPU×身份组合；③tests/maya 线 ResolvePath 六用例；插件 Python 侧 common.py 预设 Qt 上下文，test_config_old.py 起真 Maya 做集成往返、export/import 大量 mock 做单元；`tools/test_with_coverage.py` 汇总 CTest+pytest 出覆盖率，根目录四条 test_*.bat 是快捷入口。

## 7. 新人上手路径（16 步 tour 精选 9 步）

1. **[t01] 鸟瞰**：README+`docs/concepts.md:15/25`（架构总览与双工作流对比）。带走双链心智模型。
2. **[t02] 契约源**：files_to_compile.yaml+代表 proto。带走"服务语义全在 proto"。
3. **[t04] 通道与参数**：grpc_client.h/a2f_client_interface.h/parameters.h。带走三要素与 AceClientResult 错误语义。
4. **[t06] 数据主动脉**：animation.h+frame_receiver.h+audio.h。带走音频上行/动画下行如何合成帧序列。
5. **[t07] 插件注册**：通读 plugin.cpp（<150 行）。带走 .mll 边界：7 数据+2 节点+2 命令。
6. **[t08] 双节点对照**：并排读两 player 头文件属性区。带走 72 vs 55 属性差=两链之差。
7. **[t09] 本地心脏**：a2x_data.h→a2x_models.h→a2x_executors.h。带走 Destroy() 约定与模型分叉点。
8. **[t13] trtgen**：models.py+builder.py，跑 `python -m trtgen list`（无需 Maya）。带走 A2F_MODEL_DIRS 约定。
9. **[t14+t16] 测试与构建收口**：test_with_coverage.py+根 CMakeLists/FindMaya.cmake/fetch_deps.bat。带走 clone→maya_ace_2025.mll 全路径与 mock 测试法。

其余 t03/t05/t10/t11/t12/t15（生成物细节、healthcheck、AE 模板、样例资产、MetaHuman 批处理）按需回图谱补读。

## 8. 常见坑与勘误（均经源码核实）

1. **logger.h 宏缺陷**：`source/ace_client/logger.h:36` 在 ERROR 档未启用的 #else 分支误定义 LOG_INFO（应为 LOG_ERROR）。`-D ACE_CLIENT_LOG_LEVEL=0` 时 LOG_ERROR 未定义、调用点编译失败；默认 DEBUG 档（`logger.h:30`）无症状，属"默认配置下休眠"的 bug。
2. **a2f_authoring 契约源不在仓内**：生成物覆盖 a2f_authoring 与 a2x_export_config（mock_server.py:38/44 直接 import 其 Python 绑定），但 protobuf_files/ 下 12 个 proto 两者皆无源——来自外部 A2X SDK，只能随 SDK 再生成。
3. **样例场景全是 LFS 指针**：sample_project 17 个 .ma 未拉 LFS 时仅 130 字节指针文本（james_arkit_v3.ma 实体 74.8MB），不 `git lfs pull` 按 quickstart 开场景必败。
4. **files_to_compile.yaml 清单缺陷**：`:23` 与 `:32` 重复列 animation_data.v1.proto（12 项实为 11 唯一），且漏列目录中存在的 services.animation_data.v1.proto——按此 YAML 再生成会缺 AnimationDataService 桩。
5. **docs 死链**：docs/gettingstarted-a2f.md 不存在，但 `docs/buildandtest.md:177/179/186` 与 `docs/setupinstructions.md:71/127` 五处仍引用。
6. **grpc_client.h 硬编码默认 function_id**：`grpc_client.h:64` 写死 build.nvidia.com audio2face-3d 的 UUID，排"连不上云端"先查此默认值是否仍有效。
7. **云端预设半数弃用**：`source/maya_ace/presets/nvcf_ace_presets.json` 四条中三条（`:11/27/43`）标注 2025-07-25 后弃用，仅 Local Host（`:4`，配 mock_server）存活。
8. **图谱 tour 勘误**：t14 称"FRIEND_TEST 直窥私有成员"——实际是手写 fixture+friend class 前置声明（`source/ace_client/a2f_controller_client.h:79-81`），全仓无 FRIEND_TEST 宏，照宏搜代码扑空。
9. **protobuf 版本双线**：proto/requirements.txt 锁 4.25.8（protobuf-gen 还重复列两次）vs 根 deps/requirements.txt 5.26.1，两套生成物不互换。
10. **版本口径三分**：插件 2.0.0（VERSION.md）/proto wheel 1.0.0（sample_wheel）/契约注释 v1.0.0（各 proto 尾部）互不同步，报 issue 须注明口径。
