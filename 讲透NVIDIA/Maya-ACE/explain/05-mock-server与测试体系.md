# 05 · mock server 与测试体系：云端接口 mock 先行，双测试线一网打尽

> 源码：`python/`（mock_server.py + pb2_all.py + grpc_py/ 生成码包）+ `source/maya_ace/tests/`（unittest 15 文件）+ `tests/`（GoogleTest 三目标）
> 勘误：grpc_py/__init__.py 是**空标记文件**；全仓 `.proto` 仅 examples/metahuman_batch/proto/protobuf_files 12 个，**a2f_authoring 与 a2x_export_config 的 .proto 不随仓分发**——mock 的契约只能从生成码反推。

## 一、角色定位

`python/` 是云端 gRPC 接口的 Python 侧基座：`grpc_py/` 为 vendored 生成码（`nvidia_ace` 域子包 8 个 + services/ 六服务 + health/version），`pb2_all.py` 聚合再导出 22 个消息类型（`pb2_all.py:22-59`），`mock_server.py` 是本机秒起的"假 A2F 云服务"——让两条测试线（Python unittest、C++ GoogleTest）脱离真实 NIM/NVCF 跑通，"云端接口 mock 先行"由此成为本仓范式：服务端未部署，客户端协议栈已可验证。

## 二、内部结构

**导入前提**：生成码全是绝对导入，mock_server 文件头先 `sys.path.append(.../grpc_py)`（`mock_server.py:34-35`，注释明言"to ensure nvidia_ace can be imported"）——不挂 path，pb2_all 的 `from health_pb2 import ...`（`pb2_all.py:22`）立即失败。

**4 个 Mock Servicer**：①`MockHealthServicer.Check` 恒回 SERVING（`mock_server.py:60-63`）；②`MockA2XExportConfigServiceServicer` 流式回两条假配置（:52-57）；③`MockA2FAuthoringServiceServicer`——UploadAudioClip 回伪 sha256 句柄 + 55 个 blendshape 名（:66-72），GetAvatarFacePose 回全零 55 维（:74-75）；④`MockA2FControllerServiceServicer.ProcessAudioStream`（:78）最重：首块必须是 header 否则报 ERROR 并抽干流（:84-91）；回 `AnimationDataStreamHeader`（face0..face51，:96-104）；按 **533 样本/帧**切块（注释 16000/30fps，:120-122），blendshape 给单调递增假数据 `1.0+i/52`（:133）便于断言，音频原样回传（:140）；`end_of_audio` 发 END（:109）、迟到包 WARNING（:147-149）、SUCCESS 收尾（:152-153）。

**装配与生命周期**：`setup_grpc_server`（:156）开 ThreadPoolExecutor(10) 挂四个 servicer，`add_insecure_port` 失败降级 `":0"` 找空闲口（:177）。`MockServerContext`（:181）是上下文管理器：`__enter__` 把实际地址写进 `ACE_ANIMATION_CONTROLLER_DEFAULT_URL`（:198）——mock 与子进程的唯一信道——顺手设 `MAYA_ACE_UNIT_TEST=1`（:199，**全仓无消费者**，单向标记）；`__exit__` 停服。`__main__`（:212）接受 `--host/--port` + REMAINDER：外部已设 URL 则不起 mock 直接透传（:227）——同一入口可在 mock 或真云端跑同一命令；否则上下文内 `subprocess.run`（:237）。

**双测试线**：Python 线 `source/maya_ace/tests/` 15 个 test_*.py（unittest；`common.py:34-38` 定义插件名/节点类型/环境变量名，:42-44 锚 sample_data 音频；setUp 里 `standalone.initialize` + loadPlugin）。C++ 线 `tests/` 三个 GoogleTest 目标：ace（9 文件 39 TEST，链 ace_client）、a2x（42）、maya（8）；`tests/ace/main.cpp:32-36` **硬性要求** `ACE_ANIMATION_CONTROLLER_DEFAULT_URL` 已设否则 exit -1——不可裸跑。

**tested_by 网络**（图谱 34 条边）：Python 侧同名配对（utils.py→test_utils.py），**config.py 被测最重（3 个测试文件** old/import/export），names.py 挂 2 个；C++ 侧头文件主导（grpc_client.h→test_nvcf_client.cpp；a2x_data.h 一头挂 3 个测试文件）——"数据结构头变更引爆多测试"的拓扑直接可见。

## 三、外部连接

- `test_ace_client.bat:9`：`python -m mock_server "...tests_ace_client.exe"`——C++ 测试作 mock 子进程启动，靠环境变量继承拿地址。
- `test_maya_scripts.bat:29,32`：mock 包 `env_maya.bat + mayapy + unittest discover`（或 coverage 包装器），Python 线整层跑在 mock 下。
- `run_mock_server.bat:23`：建 `_venv` 后 `python -m mock_server` 长跑，供交互调试。
- `grpc_py/` 与 C++ 侧生成头同源不同语言；examples 的 nvidia_ace-1.0.0 wheel 是第三个副本——改协议三处同步。

## 四、数据流

C++ 线全链：bat 起 mock_server → env 注 URL → subprocess 起 tests_ace_client.exe → main.cpp 读 env 进 TEST_URL → 各 TEST 建 channel → ace_client 发 AudioStream → mock 回 header/假帧/SUCCESS → 断言。Python 线同壳换 mayapy，驱动 `ace_tools` 建 A2F/Ace 节点接线；AceAnimationPlayer 走 gRPC 打 mock，A2FAnimationPlayer 的本地 TRT 部分依赖模型文件。ProcessAudioStream 的流式协议与 06 篇 batch_a2f.py 客户端互为镜像。

## 五、设计决策

- **mock 先行**：a2f_authoring/a2x_export_config 无 .proto 在仓，服务行为以生成 stub + mock 为准——客户端先于云端成熟。
- **环境变量即 IPC**：对任意 exe/bat/mayapy 透明，且与生产同名（插件运行时读的正是这同一个变量）。
- **端口自愈**（:177）：并发多套测试不冲突，实际端口回写 env。
- **透传开关**（:227）：设了 URL 就不起 mock——测试矩阵可换真 NIM。
- **可断言的假数据**：55 维命名 blendshape、单调值、音频回传，客户端能校验收全与否。
- **533 常量**（:120-122）锚定 16k/30fps——帧率假设写死在 mock 与产品两侧。

## 六、新人提示

①别直接跑 `_build/.../tests_ace_client.exe`（main.cpp 拒绝）；②mock 是合成数据，适合测协议与装配，不适合调 blendshape 美学；③改 proto 需同步 grpc_py、C++ 生成头、examples wheel 三处；④Python 测试须 mayapy（`from maya import cmds`），CI 用 test_maya_scripts.bat；⑤`MAYA_ACE_UNIT_TEST` 无消费者，引用前先确认假设。
