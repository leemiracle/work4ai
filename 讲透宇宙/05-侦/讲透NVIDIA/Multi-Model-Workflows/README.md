# 讲透 NVIDIA Multi-Model-Workflows

> 源码仓：`/usr-data/data2/repos/agent-repos/NVIDIA/Multi-Model-Workflows` @ commit `453688df`
> 知识图谱：仓内 `.understand-anything/knowledge-graph.json`

## 全链状态表

| 阶段 | 状态 | 产物 |
|---|---|---|
| 批分析（5 批/29 文件） | ✅ 5/5 | 终验 0 issues；imports 1:1 对账（scanner 零漏边，AST 重扫确认） |
| understand 图谱 | ✅ 完成 | **76 节点 / 150 边 / 8 层 / 11 步导览**，validator **0 issues 0 warnings**，fingerprints 基线 **29 文件 @ 453688df** |
| Onboarding | ✅ 完成 | `onboarding/ONBOARDING.md`（8 节 / 5000 不计空格字符 / 50 锚 / 4 勘误） |
| explain 精讲 | ✅ 3/3 | `explain/01-03`，六节结构、行号锚全源码核实 |

## explain 索引（3 篇）

| # | 篇目 | 主题 | 字数（不计空格） |
|---|---|---|---|
| 01 | app_image.py | Gradio 视频理解主入口：上传→抽帧→Grounding DINO NIM→可视化 | 4534 |
| 02 | openai_runner/ | OpenAI 兼容 NIM API 调用线（202 轮询/重试/executor） | 5049 |
| 03 | utils/ | kitti_util 度量 + config_util YAML 配置（合篇） | 4076 |

## 勘误与甄别（源码一手核实）

1. **README 系统性路径漂移（TAO 模板残留）**：README 引用的 `docker/Dockerfile`、`scripts/envsetup.sh`、`release/docker/Dockerfile`、`requirements-pip/apt.txt` 仓内均不存在——实为 `docker/Dockerfile.build`、`runner/envsetup.sh`、`docker/requirements.txt`（批分析+onboard 双重核实）。
2. **build.sh 死参数**：传 `--build-arg PYTORCH_BASE_IMAGE` 但 `docker/Dockerfile.build` 无对应 ARG 声明。
3. **`cv_nim/gdino_nim.py:129` 裸名 bug**：202 轮询分支引用 `header_auth` 缺 `self.`（必 NameError）；`while(MAX_RETRIES)` 递减的是模块全局。
4. **`utils/kitti_util.py:14-15` 缩进错位**：OCR-检测框空间关联静默失效（polygon_points 恒单点）。
5. **`schema/default_config.py` GradioApp 双重定义**：L20-26 server 配置版被 L38-48 顶层 schema 版模块级覆盖；类体执行期解析到第一定义。
6. **双入口复制粘贴**：app_image/app_video 的 extract_noun_chunks 等三函数逐行复制而非复用（duplicated-code）。
7. **requirements.txt 被扫描器归 docs**：实为 pip 依赖清单（openai==1.16.2 对应 openai_nim.py），已按 document 节点建模并注明。

## 一句话

多模型工作流编排示例仓：Gradio 双入口 + OpenAI 兼容 NIM 调用线 + TAO 微调线，工程完成度中等——README 与源码存在系统性路径漂移，以源码为准。
