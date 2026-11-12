# Multi-Model-Workflows 新人入门指南

> 图谱 76 节点/150 边/8 层；锚经源码核实（453688d）。

## 1. 项目定位

NVIDIA TAO 的多模型工作流示例仓：「文本 LLM+开集检测+OCR+代码生成 LLM」串成图像/视频理解流水线，推理全走 NIM 云 API，Gradio 交付。核心命题：检测框不会"回答画面问题"——Llama3-70B 抽名词块作类别，Grounding DINO 开集检测，ocdrnet 补 OCR，统一转 KITTI 标注后由 Codestral-22B **现场生成 Python 后处理函数**并动态执行（`llm_nim/executor.py:L10-43`）。栈：Python/Gradio/OpenAI SDK/shapely/hydra/ffmpeg/Docker+NGC CLI，约 30 个源文件。README 明言不接受贡献、2024-11 停止演进——学模式，别当产品。

## 2. 架构总览

图谱 8 层，依赖单向（app→llm_nim/cv_nim/schema/utils）：

| 层 | 职责 | 代表文件 |
|---|---|---|
| L01 配置与Schema | hydra 基座 | `schema/default_config.py`、`config/config.yaml:L1-10` |
| L02 常量与工具 | 密钥与工具 | `utils/constants.py:L4-9` |
| L03 容器与环境 | 开发容器 | `docker/Dockerfile.build:L1`、`runner/tao_ws.py:L26-31` |
| L04 LLM NIM客户端 | 客户端+执行 | `llm_nim/openai_nim.py:L13-61` |
| L05 CV NIM客户端 | CV 双骨架 | `cv_nim/gdino_nim.py:L18-187` |
| L06 本地推理备选 | NGC 备选（停用） | `primary_cv/model_handler.py:L15-97` |
| L07 Gradio入口 | 端到端编排 | `app/app_image.py:L79-139` |
| L08 文档 | README（漂移） | `README.md` |

两条主线：云 NIM 线（L04+L05，在用）与本地推理线（L06，停用）。

## 3. 核心链路

以图像模式 `run_demo`（`app/app_image.py:L79-139`）为主数据流，视频模式仅加 ffmpeg：

1. **装配**：hydra_runner 装饰（`app/app_image.py:L141-145`）读 config.yaml 起 gr.Interface（:8000）。
2. **抽名词块**：`NounChunkNIM`（仅输出 JSON，`llm_nim/openai_nim.py:L101-117`）调 llama3-70b 抽名词作 GDINO 检测类别。
3. **双 CV 批推理**：GDINO/OCD 各 16 线程并发；单帧=图片转 JPEG 上传 NVCF 换 asset_id→POST→解包 .response（`cv_nim/gdino_nim.py:L26-71`）；GDINO 逐框写 KITTI 15 列，OCD 按质心排序。
4. **合并**：`read_kitti`（`utils/kitti_util.py:L22-50`）解析检测行，shapely 判 OCR 多边形与框相交，文字拼进 `object_text`。
5. **生成并执行后处理**：`InstructionalNIM` 调 codestral-22b 生成 postprocessor 单函数、按缩进剥函数体（`llm_nim/openai_nim.py:L81-98`）；`Executor` 写临时 .py 经 importlib 执行（`llm_nim/executor.py:L24-34`）；视频首帧生成后续复用（`app/app_video.py:L63`）。
6. **视频增量**：`ffmpeg -vf fps=3` 抽帧（`app/app_video.py:L92`）→ 全链路 → 绿框红字叠加 → libx264 重编码（`app/app_video.py:L137-140`）。

## 4. 关键文件深读

**`llm_nim/openai_nim.py`（117 行，设计最好）**——模板方法类族：基类 `OpenAINIM` 封装流式 chat.completions，子类只各写提示词+解析器；`InstructionalNIM` 把"单函数/import 入函数体/单入参"约束写死在 prompt（`llm_nim/openai_nim.py:L68`）。

**`llm_nim/executor.py`（44 行，最危险）**——生成-执行闭环终点：mkstemp 落盘、importlib 取句柄（`llm_nim/executor.py:L17-32`）。except 吞异常（`llm_nim/executor.py:L33-34`），失败时 execute 才炸；__del__ 只弹字面量 /tmp（`llm_nim/executor.py:L40-43`）。

**`cv_nim/gdino_nim.py`（188 行）**——NVCF 资产式推理协议范本：assets 换 S3 直传 URL、asset_id 以 data URI 内嵌 messages（`cv_nim/gdino_nim.py:L80-99`）、200 解包/202 轮询。202 分支有真 bug：裸 `header_auth` 缺 `self.`（`cv_nim/gdino_nim.py:L129`）。

**`utils/kitti_util.py`（87 行）**——`read_kitti` 按 `row[-15:]` 取框坐标、其余全归类名（`utils/kitti_util.py:L29-39`）；`_polygon_intersection` 求交但缩进有 bug（见第 7 节）。

## 5. 模块间关系

- **`utils` 是地基**：`execute_command`（`utils/utils.py:L11-31`）是 ffmpeg/ngc/TAO 统一 bash 入口，签名声称 `str|List[str]` 但实现固定 shell=True；NVCF_API/URL 全仓共享。
- **`schema`→hydra 契约**：双入口 `@hydra_runner(schema=GradioApp)` 校验 config.yaml；config_root 相对自身定位（`app/app_image.py:L32`），任意 cwd 可启动。
- **`llm_nim` 双轨**：`openai_nim.py` 类族被 app 引用；`openai_runner.py` 是零引用参考实现。
- **`cv_nim` 双生骨架**：GDINO/OCD 上传/推理近乎复制；ocd 的 `infer` 无 202 处理（`cv_nim/ocd_nim.py:L85-93`）；两类 `parse_output` 同名不同义（写 labels.txt vs 返回 dict）。
- **KITTI 是通用语**：gdino 写、kitti_util 读、overlay 再读。**`primary_cv` 悬挂**：仅被注释 import 引用（`app/app_image.py:L15-16`），`primary_cv/gdino_infer.py:L24` 硬编码容器路径。

## 6. 构建与运行

无 setup.py，一切依赖开发容器：①source `runner/envsetup.sh` 得 tao_ws 函数（`runner/envsetup.sh:L14-17`）；②可选 `docker/build.sh -b` 构建 `docker/Dockerfile.build:L1`（FROM TAO toolkit pyt v5.2.0）+openai==1.16.2+NGC CLI（`docker/Dockerfile.build:L7-10`），推送后打印 digest 人工回写 manifest（`docker/build.sh:L65-68`）；③`tao_ws --port 8000:8000 -- python app/app_video.py`（`README.md:L229-233`）。跑通前提：改 `utils/constants.py:L4-6` 的 key 占位+nvstaging 仓权限（无 .env 机制）。无测试无 CI，验证=起 Gradio 手工上传；启用本地推理线需解开 `app/app_video.py:L158-167` 填 local_model_path。

## 7. 设计决策与取舍（含勘误）

1. **【勘误】README 系统性路径漂移**：`README.md:L79` 引 `docker/Dockerfile`（实为 Dockerfile.build）、L178 引 requirements-pip/apt.txt（实为单行 requirements.txt）、L215 引 release/docker/Dockerfile（目录不存在）、`README.md:L220` 写 `scripts/envsetup.sh`（实为 runner/，L38 又写对）；`runner/envsetup.sh:L7` 同病。
2. **【勘误】build-arg 死参数**：`docker/build.sh:L59` 传 `--build-arg PYTORCH_BASE_IMAGE`，但 Dockerfile.build 无 ARG、FROM 硬编码——换基座须改 FROM。
3. **【勘误】GDINO 202 轮询必炸**：`cv_nim/gdino_nim.py:L129` 缺 `self.`，且模块级 MAX_RETRIES 自减污染；图像模式多 200 直回故未暴露。
4. **【勘误】OCR 空间关联失效**：`utils/kitti_util.py:L14-15` 缩进错位（point 在 for 内 if 外、append 在 for 外），polygon_points 恒单点、intersects 恒 False——object_text 永远为空，不崩溃但失效。
5. **失败语义**：executor 吞异常（`llm_nim/executor.py:L33-34`）属"演示优先"；参考实现 `llm_nim/openai_runner.py:L125` 的 `strip(".py")` 按字符集误剥文件名，正确是 `[:-3]`。
6. **schema 同名类覆盖**：`schema/default_config.py:L19-26` server 版 GradioApp 被 L37-48 组合版同名覆盖，字段默认值求值时绑定第一个定义——功能正确但极易误导；NIMConfig 默认值缺 `>`（`schema/default_config.py:L33`）。
7. **云优先/本地留位**：推理全走云端，primary_cv 本地线写完即停用。由 `app/app_image.py:L24` 未用的 SAMPLING_FPS、L83 死变量、L46-76 与视频版重复的函数推断：app_video 先写、app_image 是复制版。

## 8. 新人上路

**先看**：README 只取启动命令（路径以第 2 节表为准）→ `config/config.yaml` → `app/app_image.py` 全文 → `llm_nim/openai_nim.py`。**再改**：链路动 app/ 的 run_demo；LLM 能力抄 openai_nim 子类；CV 模型抄 gdino_nim 骨架。**常见坑**：①README 路径是模板残留；②`--build-arg` 换不了基座；③GDINO 异步 202 会 NameError；④object_text 恒空是缩进 bug；⑤视频模式后处理函数仅按首帧生成、后续帧复用（`app/app_video.py:L63`）；⑥exit_cleanup 会 rmtree 中间目录，调试留现场注释 finally；⑦manifest 老 digest 拉不动时自建镜像回写。

一句话：NIM 云 API + LLM 现场写代码的教学级参考实现——模式值得抄（模板方法客户端族、资产式上传、生成-执行闭环），健壮性别指望（吞异常/缩进 bug/路径漂移都是真的）。
