# 01 · app/app_image.py — 单图多模型问答主入口

## 1. 角色定位

app_image.py（173 行）是 Multi-Model-Workflows 的**图像模式** Gradio 入口：用户上传一张图加一句自然语言问题，本文件把五个远端模型接力成一条流水线——Llama3-70B 抽名词块当检测类别（app_image.py:46-55）→ Grounding DINO 开集检测（app_image.py:94-96）→ ocdrnet OCR（app_image.py:99-101）→ shapely 空间融合（app_image.py:114-116）→ Codestral-22B 现场生成 Python 后处理函数并动态执行（app_image.py:58-76），函数返回值就是界面上的答案文本（app_image.py:129）。在图谱 8 层结构里它属 L07 Gradio 应用入口层；姊妹文件 app/app_video.py 是视频模式，两文件约 80% 逐字复制。

**勘误（选材描述）**：派发单把本文件描述为"视频理解主入口：上传→抽帧→可视化输出全链"——三件事都不在此文件：抽帧在 app_video.py:92（`ffmpeg -vf "fps=3"`），叠加可视化在 app_video.py:133，视频重编码在 app_video.py:137-144。app_image 的输入是 `gr.Image(type="filepath")`（app_image.py:155），输出只有一个 `gr.Textbox`（app_image.py:160）。准确定性：它是视频链的单图调试/演示版。

## 2. 内部结构

- app_image.py:24 `SAMPLING_FPS = 3` — 复制文件头带过来的**死常量**，本文件零引用（视频版 :92/:137 才用于抽帧与重编码帧率）。
- app_image.py:32 config_root — 相对 `__file__` 上溯定位 config/，任意工作目录可启动（对照 config_util.py 按 cwd 解析相对路径的隐患，见 03 篇）。
- app_image.py:35-43 exit_cleanup — 断言入参为 list 后 `shutil.rmtree` 逐个删除中间目录。
- app_image.py:46-55 extract_noun_chunks — 构造 NounChunkNIM(URL, NVCF_API)，`assign_model("meta/llama3-70b-instruct")`，返回 `data["noun_chunks"]`。
- app_image.py:58-76 generate_analytics — L63 `if not code_executor.postprocessor` 才调 InstructionalNIM 生成代码（缓存语义），L72 infer 出函数字符串，L73 交给 Executor 加载，L76 返回 `(execute 结果, code_executor)`。
- app_image.py:79-139 run_demo — 编排主体（第 4 节逐步展开）。
- app_image.py:141-145 `@hydra_runner(config_path=config_root, config_name="config.yaml", schema=GradioApp)` — hydra 装饰的配置装载点。
- app_image.py:146-169 main — :148 `model_config = cfg.model` 赋值后未用；:149-152 两个 `global`（model_instances/demo_configuration）全是死代码，其唯一潜在消费者 pull_and_cache_models 在 app_video.py:158 起整体被注释；:161-169 gr.Interface 并 launch（server_port 默认 8000，来自 schema）。
- app_image.py:15-16 被注释的 primary_cv 本地推理 import — 本地推理线停用的化石证据（primary_cv 至今仍消费 utils.constants/utils.utils，成为 L06 悬挂层）。

## 3. 外部连接

imports 集中在 app_image.py:12-22：`llm_nim.openai_nim` 的 InstructionalNIM/NounChunkNIM、`llm_nim.executor.Executor`、仓外 TAO 依赖 `nvidia_tao_pytorch.core.hydra.hydra_runner`、`cv_nim` 的 OCDNIM/GDINONIM、`schema.default_config.GradioApp`、`utils.constants` 的 NVCF_API/URL、`utils.kitti_util`、`utils.utils.execute_command`——最后一个**导入后从未使用**（视频版用它跑 ffmpeg），又一处复制残留。

被谁消费：入口文件，全仓无人 import 它；经 `python app/app_image.py` 或容器内 `tao_ws --port 8000:8000 -- python app/app_video.py` 同款方式启动（README.md:233 给的是视频版命令）。run_demo 作为 Gradio 回调绑定在 `gr.Interface(fn=run_demo, ...)`（app_image.py:162）。

## 4. 数据流

输入 input_image（Gradio 上传文件的临时路径字符串）+ question，八步：

1. app_image.py:88 `','.join(extract_noun_chunks(question))` — 把名词块列表拼成 "robot,pallet" 形式的类别提示串。
2. app_image.py:92 `os.path.dirname(input_image)` — Gradio 把上传文件收进临时目录，取目录整体当批推理输入。
3. app_image.py:94-96 GDINONIM.batch_infer → model_output_path/gdino_inference/<帧名>/ 下产出 KITTI 15 列 labels.txt。
4. app_image.py:99-101 OCDNIM.batch_infer → ocd_inference/<帧名>/ 下产出 *.response（JSON）。
5. app_image.py:110 与 :113 两个 parse_output — OCD 返回按质心排序的 OCR 元数据 dict；GDINO 把检测结果写成 labels.txt。
6. app_image.py:114-116 kitti_util.read_kitti(labels.txt, ocd_data=...) → `list[{class_name, bbox, confidence, object_text}]`（object_text=框内 OCR 词）。
7. app_image.py:122 generate_analytics — metadata json.dumps 进 prompt，codestral 生成 postprocessor，Executor 落盘/importlib/执行；:123 str(result) 写 analytics 文本。
8. app_image.py:129 return result → Textbox 显示；:133-139 finally 无条件 exit_cleanup 三个中间目录。

## 5. 设计决策（含勘误）

- **勘误·恒空 glob**：app_image.py:104 把 annotations_path 定为 model_output_path/"inference/labels"、:105 对它 glob *.txt——该目录全流程无人写入（GDINO 的 labels 实际落在 gdino_inference/<帧名>/labels.txt，真正读取走 :115 直接拼 GDINO 输出路径），frame_files 恒空。这是从 app_video.py:108-109 抄来的目录约定化石；视频版同样断链且更伤：glob 恒空→逐帧循环体从不执行→app_video.py:133 的 overlay 读空的 analytics 目录会直接 FileNotFoundError。
- **勘误·mkdtemp 泄漏**：app_image.py:83 output_video_path 创建后既不使用也不进 :134-138 的清理列表——每次请求泄漏一个空目录；:84/:85 两个同样无产出的 mkdtemp 至少被清理了。
- **勘误·半成品表格**：:107 建 "Frame ID"/"LLM Output" 两列结构、:126-127 填入一行，:129 却只返回 result 不返回表——视频版 app_video.py:144 会返回 pd.DataFrame，单图版裁剪输出时的残留。
- 单图版的存在逻辑：视频全链贵且慢，单图是最小可演示路径；代价是双文件复制且行为已漂移——本文件 :88 有 `','.join`，视频版 :88 直传 list，f-string 会把类别渲染成 "['robot', 'pallet']"（带引号方括号）进 Grounding DINO 提示，语义不同。
- app_image.py:131-132 `except Exception as e: raise e` 是纯透传占位（无重试无包装）；真正的兜底价值在 finally 的清理。
- Executor 每请求新建（:106），所以 :63 的"生成一次后复用"只在单请求生命周期内有效；想跨请求缓存需挪到 main 层，但要考虑换问题后旧函数语义失效。

## 6. 新人提示

- 改这条链先 grep app_video.py 的同名函数：exit_cleanup/extract_noun_chunks/generate_analytics/main 两份逐字复制，只改一处必然漂移（join vs list 就是现成教训）。
- 想恢复叠加图/视频输出：补 :160 的 outputs、调 kitti_util.overlay_labels_on_images、ffmpeg 重编码（照抄 app_video.py:133-143），并把 output_video_path 加进 :134-138 清理列表。
- 调试第一现场在 stdout：:89 logging 名词块、:117 print 对象级元数据；codestral 生成的完整代码也会被 print（见 02 篇）。
- 改 config/config.yaml 字段必须同步 schema/default_config.py 的 GradioApp——注意该类定义了两次、第二次（schema/default_config.py:38）才是生效版（详见 03 篇）。
- 动 :134-138 清理列表时与 :82-85 的 mkdtemp 对账：现状是"泄漏 output_video_path、却清理两个从未使用的目录"。
