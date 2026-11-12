# 04 · Python 脚本链与 trtgen：菜单、接线、AE 模板与 TRT 引擎构建器

> 源码：`source/maya_ace/scripts/`（userSetup.mel + ace_tools/ + ace_ae_templates/ + trtgen/）
> 勘误：userSetup.mel 实为 **10 个命令菜单项**（Create/Modify/Config/Model 组 3+3+3+1），非 11 个（divider 见 `userSetup.mel:4,24,45,65`）。

## 一、角色定位

C++ 节点只负责"算"，本目录 Python 包负责"装"：`ace_tools` 是节点编排层（建播放器、接线、参数导入导出、preset 搜索），`ace_ae_templates` 是两个播放器的 Attribute Editor 模板，`trtgen` 是本地 TRT engine 构建工具（CLI + Qt 对话框双形态）。入口 `userSetup.mel` 以 10 个菜单项暴露到 "ACE/A2F" 菜单（`userSetup.mel:1`）。

## 二、内部结构

**userSetup.mel 转发机制**：每个 `-command` 是自包含 Python 单行——loadPlugin + `from ace_tools import setup; setup.<函数>()` 压在一行（`userSetup.mel:8`），Maya 启动零导入成本。唯一例外是 TRT 管理项：不 loadPlugin，直接 `from trtgen import builder_ui`（`userSetup.mel:69`）——不依赖 C++ 节点。

**ace_tools 七模块**：`setup.py` 为核心——三个 attach_* 创建入口（如 `setup.py:93`）；`connect_animation_player_to_blendshapes`（:299）按别名匹配把 `outputWeights[i]` 接到 `blendShape.weight[i]`（别名清洗 :430，失配按下标硬连 :385-388）；`initialize_output_aliases`（:565）按 names.py 常量设 `out_*` 别名（TODO :81 承认等服务器下发）。`audio.py` 管时间轴音频（`mel.eval` 拿滑条 :142）。`config.py` 双代 I/O：检测 `"a2e"/"a2f"` 键（:144）走新格式，否则回退废弃旧扁平导入（:333）。`parameters.py` 用 `MappingProxyType` 只读封装映射（:42）；`preset.py` 默认通配 `*ace_presets.json`（:33）；`names.py` 纯数据（52 ARKit :34 + 16 舌头 :94）；`utils.py` 的 `cache_array_aliases`（:222）做小写键别名缓存。

**AE 模板链**：MEL 侧 `AEA2FAnimationPlayerTemplate.mel` 只是桥，`python(...)` 调入 Python 类（命名约定 `AE<节点类型>Template` 自动发现）。`AEA2FAnimationPlayer(AEA2FShared)`（`ae_a2f_animation_player.py:42`），基类（`ae_a2f_shared.py:36`）分五组装音频/情绪/脸/舌/blendshape 控件。**函数体内延迟 import 是关键模式**：`ManageModelFilesButton.onRequest`（`ae_a2f_animation_player.py:124-127`）点击瞬间才 `from trtgen.builder_ui import show_trt_builder_dialog`——打断模块环，把 PySide 推迟到确有 GUI 时（headless mayapy 不炸）。

**trtgen 五文件**：`builder.py` 的 `build_trt_command`（:34）从 ONNX 同目录读 `trt_info.json`（:65），用 defaults `str.format`（:80）拼 trtexec 命令；list/build/clean/list_trt 四子命令（:151-197），模型发现 `skip_invalid=False`（:122，连无效也列出）；构建即 `subprocess.run`（:244）。`models.py` 从 `A2F_MODEL_DIRS`/`A2E_MODEL_DIRS`（:43）扫 `*/*.onnx`，`is_valid_model` 只看同目录 `network.trt`（:90）。`builder_ui.py` 开头 PySide2/6 兼容层（:27-36）；`__main__.py` 按 `argv[1]=="ui"` 分发 CLI/GUI（:26-33）。

## 三、外部连接

菜单项全部先 loadPlugin——Python 不注册节点类型，`cmds.createNode`（`setup.py:516`）要求 C++ 插件已加载。环境变量是配置通道：`ACE_ANIMATION_CONTROLLER_DEFAULT_URL`（:47，写入 networkAddress :523-525）、`NVCF_API_KEY`（:48）、`TRTEXEC_PATH`（`builder.py:277`，分号取首段再逐 PATH 搜 :281-284）。`trtgen.bat` 是 Windows 胶水：按插件目录/repo 根推 MODELS_DIR/TRTEXEC_PATH，优先 mayapy。preset 搜索跨两根：正则替换 `__file__` 推出安装目录（`preset.py:74`）+ Maya 用户目录（:92）。

## 四、数据流

以 "A2F Player on Blendshapes" 为例：菜单单行 → attach → `get_blendshapes_from_node`（选中→shape→`listHistory` 上溯，`utils.py:107`）→ `create_a2f_animation_player`（createNode + 接 `time1.outTime` :553）→ 有音频则按 `AUDIO_CONNECTIONS` 四对连接（`setup.py:49-55`）→ 逐权重接线。配置流：节点属性 → `_collect_config_parameters`（递归，`config.py:165-202`）→ 有 PyYAML 优先 YAML（:81）否则 JSON。TRT 构建流：glob ONNX → 读 `trt_info.json` → 强制 `MAX_BATCH_SIZE=1`（`builder.py:76-78`）→ `.trt` 落 ONNX 旁。

## 五、设计决策

- **菜单即脚本**：MEL 只声明转发，业务全在可单测的 Python 模块；每个 command 自带 loadPlugin，菜单项互相独立。
- **别名作命名契约**：权重匹配走"清洗+小写"（`utils.py:238-241`），比下标硬连多一层语义兼容，小写重名是已知风险。
- **延迟 import 解耦 UI**（`ae_a2f_animation_player.py:125`）：AE 模板必被加载，顶层 import trtgen/PySide 拖慢启动，重依赖推迟到点击。
- **只读映射防漂移**：`parameters.py` 把"配置键↔属性名"固化为常量，与服务端共享词表。
- **双入口一套命令**：CLI 与 TRT Manager 对话框共用 `build_trt_command`；构建参数随模型目录（`trt_info.json`）而非全局配置。

## 六、新人提示

①改菜单只需动 userSetup.mel，新函数须挂 `ace_tools.setup` 才合菜单 import 约定；②`trtgen.bat list` 列出"无效模型"不是 bug（`builder.py:122` 刻意 skip_invalid=False），build 前先查 `trt_info.json`；③路径分隔符全为分号（Windows 假设）；④preset 文件名匹配 `*ace_presets.json` 即被收编（`preset.py:54-57`），Maya 用户目录同名文件也入搜；⑤测试走 `test_maya_scripts.bat`（见 05 篇），裸 CPython 跑 `from maya import cmds` 必炸。
