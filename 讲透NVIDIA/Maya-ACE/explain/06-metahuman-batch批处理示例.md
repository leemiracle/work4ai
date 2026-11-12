# 06 · metahuman_batch 批处理示例：云端批量出 MetaHuman 动画的端到端样板

> 源码：`examples/metahuman_batch/`（scripts + Samples + Mace_Add-On + proto）
> 勘误：**BatchList.json 是任务清单格式（扁平未变）**，参数格式演变在 Config_Example1/2（旧扁平）→ Example3.yaml（新嵌套 a2e/a2f）；files_to_compile.yaml:21-33 的 `nvidia_ace.animation_data.v1.proto` **重复列两次**。

## 一、角色定位

本示例是 Maya ACE 之外的第二条消费路径：不开 Maya，独立 Python 客户端把批量音频发给云端 A2F-3D microservice（默认 `127.0.0.1:52000`，`batch_a2f.py:393`），收回 ARKit 关键帧，映射成 MetaHuman rigs 动画写出 FBX。配套 `Mace_Add-On/` 反向补强 Maya 内体验——给已装 ACE 插件"手工打补丁"，加 MetaHuman 接线与批清单对话框。头注释（`batch_a2f.py:22-28`）自述改编自 NVIDIA/ACE 样例，改了 A2F-3D、MH 映射、FBX 轴系。

## 二、内部结构

**batch_a2f.py（467 行，asyncio 双任务）**：文件头 7 条 `from nvidia_ace...v1_pb2 import`（`batch_a2f.py:40-51`）——该包**不在仓内**（装 sample_wheel 或自生成），静态 import 解析是图谱盲区。`main` 读 BatchList.json 五键（:420-424），逐对建 channel，`stub.ProcessAudioStream()`（:452）后 `asyncio.create_task` 并行读写（:455-463）。`write_to_stream`（:193）：音频非 int16/16k 自动 `bf.convert_audio`（:203-211）；配置三分支——json 含 face_params=旧格式直用、含 a2f=新格式转换、yaml 同转（:215-243）；**整秒切块**发送（:305-308），首包夹带十情绪向量（:314-348），终包 EndOfAudio（:361）。`read_from_stream`（:132）：header 存 bs_names（:160-169），逐帧 `zip(bs_names, values)` 组 keyframe（:179-182）并解 emotion_aggregate Any（:106-108），EOF 落盘（:154）。

**batch_functions.py（FBX 工厂）**：`convert_audio`（:39）scipy 重采样；`save_keyframes_to_MH_animation`（:285）——每控制置 0.0 后累加 `ARKit 权重 × multiplier`（:335-340），走 FBX SDK：按 FBX_axis_system 三选轴系（MayaYUp/MayaZUp/Max=Unreal，:376-382）、每控制建 X/Y 平移曲线、`int(timeCode*30)` 转帧号（:416）、二进制导出（ASCII 注释留调试，:435-437）。`process_a2f_params`（:445）把新嵌套格式拍平回旧平行数组。

**Mace_Add-On（4 文件）**：`add-to-setup.py` 的 docstring（:23-26）说清形态——**手工粘贴进 `mace/scripts/ace_tools/setup.py` 的代码段**，补 `attach_ace_player_to_MH`（:40）/`attach_a2f_player_to_MH`（:99）/`open_batch_dialog`（:217）与 `connect_ACE2Rig_to_player_and_Rig`（:155）。`ACE2Rig_Functions.py`：`create_ACE2Rig_node`（:44）建 network 节点，addAttr 出 68 个小写 ARKit 输入 + CTRL 输出属性；`create_expressions`（:374）读同目录 MH_Mapping.json（:387），每控制拼 `out = 0.0 + (mult*arkit_in);`（:404-410）交 `cmds.expression`（:83）。`Batch_List_MayaDialog.py` 的 `Create_Batch_Dialog`（:28）表单收集后 `json.dump` 出 BatchList.json（:400）。Add-On 自带 userSetup.mel 覆盖原版，多 "MetaHuman" 组 3 菜单项。

**MH_Mapping.json（68 条）**= 52 ARKit（含 TongueOut）+ 16 舌头姿态；键 lowerCamelCase，值如 `{"CTRL_L_eye_blink.translateY": 0.8}`；一个 CTRL 可被多条 ARKit 叠加（+=），方向靠 multiplier 正负号（eyeLookInLeft -1.0 vs eyeLookOutLeft 1.0）。

## 三、外部连接

上游是 A2F-3D microservice v1.2（云端推理，本地零 GPU），`-url` 可指远端 NIM；下游 FBX 进 Maya/Unreal 的 MetaHuman。与主仓三处硬连接：Add-On 菜单调用的 `setup.attach_ace_player_to_MH` **只有粘贴补丁后才存在**（裸拷必报错）；MH 控制清单在 `batch_functions.list_MH_controls`（:76）与 `ACE2Rig_Functions.target_rig_controls`（:167）**两处独立维护**（改 rigs 要双改）；proto/ 自带 12 个 .proto + 生成脚本（:50-62）+ wheel，是 grpc_py 之外的第二副本。FBX 依赖 Autodesk FBX Python SDK。

## 四、数据流

批量线：BatchList.json 逐对 → channel → 双任务流（写：header（含三类参数，:283-300）→ 秒块音频 → EndOfAudio；读：header → 逐帧 keyframes → EOF）→ `save_keyframes_to_MH_animation` 线性映射 → FBX 曲线 → `{audio名}_{config名}.fbx`（:433-439）。Maya 线：菜单 → 校验 rig 有 `CTRL_faceGUIShape`（add-to-setup.py:66-72）→ 建 player + ACE2Rig 节点 → outputWeights[i] 接 ARKit 输入（:166-173），CTRL 输出接 rig 控制（:188-191）→ expression 驱动。

## 五、设计决策

- **双格式并存**：以 face_params/a2f 键嗅探新旧（:220-227），新格式客户端转平，服务端契约不变；新嵌套格式与 ace_tools config.py（04 篇）同构，插件与微服务词表趋同。
- **手工粘贴补丁**："文档式代码"零门槛，代价是无版本守卫、粘错位置即坏。
- **表达式节点做映射**：MetaHuman control rig 是 FK 平移不是 blendshape，线性加权 expression 是最低公分母，权重数据化在 JSON。
- **FBX 只写 X/Y 平移**：面部 GUI 控制板约定。
- **asyncio 双任务**：gRPC aio 原生形态。
- **符号乘法器**：一对多叠加 + 正负号编码方向，免建反向控制。

## 六、新人提示

①先起 A2F-3D microservice 再跑批；音频非 16k/16bit/mono 自动转码，临时文件用后删（:364-365）；②装 Add-On 三步缺一不可：拷 scripts、粘 add-to-setup.py、覆盖 userSetup.mel；③换 rigs：MH_Mapping 键保持 ARKit 名改值，两处控制清单要同步；④FBX 轴系选错直接 Z/Y up 错位，"Unreal" 实际映射 `FbxAxisSystem.Max`（:380）；⑤调映射先开 CSV（:345-348）与 ASCII 导出（:435-437）调试注释。
