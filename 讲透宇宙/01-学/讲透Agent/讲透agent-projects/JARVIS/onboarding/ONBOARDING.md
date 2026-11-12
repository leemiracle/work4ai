# JARVIS（microsoft/JARVIS）新人上手指南

> 微软"LLM 控制器 + 专家模型执行器"系统仓：HuggingGPT（arXiv:2303.17580）官方实现，附 EasyTool（2401.06201）与 TaskBench（2311.18760）。图谱 188 节点/297 边/13 层/16 步，锚均经源码核实。

## 一、一图流总览

monorepo 三项目，互不 import：

```
hugginggpt/   HuggingGPT 本体：四阶段 agent（控制器 8004 + 模型服务 8005 + web 9999）
easytool/     EasyTool：精简工具指令 + 四基准执行器（离线评测脚本群）
taskbench/    TaskBench：任务自动化基准（数据生成→推理→图匹配评测）
```

主张：LLM 只做规划/选择/总结三段决策（tprompt 编号 #1/#2/#4，`hugginggpt/server/configs/config.default.yaml:30-36`——执行归专家模型故无 #3），专家池=673 条注册表 `hugginggpt/server/data/p0_models.jsonl`。三进程：`hugginggpt/server/models_server.py`（8005 推理）、`hugginggpt/server/awesome_chat.py:1014-1062`（8004 控制器，`/hugginggpt` `/tasks` `/results`）、`hugginggpt/web/`（Vue3）+ `hugginggpt/server/run_gradio_demo.py`。

## 二、技术栈与依赖

2023 年历史仓，重型库 commit 钉死（`hugginggpt/server/requirements.txt:1-3`，diffusers/transformers/controlnet_aux 三连）+`tiktoken==0.3.3`/`gradio==3.24.1`。API 漂移四坑：

1. `InferenceApi`（`hugginggpt/server/awesome_chat.py:26`）新版 huggingface_hub 已删；
2. `openai.Embedding.create(engine=)`（`easytool/easytool/toolbench_retrieve.py:46`）旧式参数；
3. `from langchain import LLMChain`（`easytool/easytool/funcQA.py:14`）0.1+ 已搬迁；
4. `load_metric`（`taskbench/evaluate.py:6`）新版 datasets 已砍。

`runwayml/stable-diffusion-v1-5` 等仓主名已易主（`hugginggpt/server/models/download.sh:5-14`）。硬件：VRAM≥24GB、full 磁盘 284GB（`hugginggpt/README.md:64-70`）；零 GPU 用 `hugginggpt/server/configs/config.lite.yaml`。

## 三、目录地图：三子项目

**hugginggpt/**：`awesome_chat.py`（1070 行引擎）+ `models_server.py`（635 行）+ `get_token_ids.py` + `configs/` 四份 + `demos/` 三份 few-shot + `p0_models.jsonl` + `web/src/views/home.vue`（432 行）+ `Dockerfile.jetson`。

**easytool/**：入口 `easytool/main.py`（91 行分发）+ `easytool/easytool/` 五模块（`funcQA.py` 675 行、`toolbench.py` 718 行、`toolbench_retrieve.py` 736 行、`restbench.py` 111 行、`util.py` 109 行）+ 三份工具指令数据 + `data_process.py`。`easytool/data_funcqa/funchub/math.py` 有 16 个可执行数学函数（实证），名一律 `_` 结尾避开内建；其 `import math` 系标准库，图谱曾误判假边。

**taskbench/**：生成链 `generate_graph.py`→`graph_sampler.py`→`data_engine.py`（354 行）→`format_data.py`；评测链 `inference.py`（296 行）→`evaluate.py`（552 行）→`batch_evaluate.sh`。三域实测：7458/5555/4318 条共 17331（工具图 23 工具 225 边、40/449、40/1560），README 称 28271，见勘误⑥。

## 四、核心链路：awesome_chat 四阶段 pipeline

总控 `chat_huggingface`（`hugginggpt/server/awesome_chat.py:891`）：

1. **任务规划**：`parse_task`（`awesome_chat.py:317`）以 few-shot+tprompt 解析出任务 JSON 数组；历史过长逐条丢弃（`awesome_chat.py:323-336`）留 800 token 余量；失败或 `[]` 降级 `chitchat`（`awesome_chat.py:907-918`）。
2. **依赖整理**：`unfold`（`awesome_chat.py:281`）把多占位拆成多任务副本；`fix_dep`（`awesome_chat.py:268`）反推 dep，无依赖记 `[-1]`。`<GENERATED>-id` 是跨任务资源传递的文本协议。
3. **模型选择+执行**：调度器（`awesome_chat.py:937-958`）按拓扑层并发——dep 全落已完成集合的任务各起线程跑 `run_task`（`awesome_chat.py:720`），0.5s 轮询、`retry>160` 收工。`run_task` 先替换占位为上游产物（`awesome_chat.py:733-776`），再走三捷径：ControlNet 钉死本地（`awesome_chat.py:798-814`）；五类纯 NLP 让 ChatGPT 代跑（`awesome_chat.py:815-825`）；其余取前 10 候选（`awesome_chat.py:834`），`get_avaliable_models`（`awesome_chat.py:678`）探测双端点，候选>1 时 `choose_model`（`awesome_chat.py:350`）选型，`model_inference`（`awesome_chat.py:638`）分派本地（`awesome_chat.py:532`）或远程（`awesome_chat.py:400`）。
4. **响应生成**：`response_results`（`awesome_chat.py:377`）把结果按 id 排序入 demo，LLM 生成用户回复（`awesome_chat.py:968`）。

暗门两处：`__main__` 分流 test/server/cli（`awesome_chat.py:1064-1070`）；被 import 时强制切 gradio 配置（`awesome_chat.py:34-36`）。

## 五、关键设计决策

- **LLM 只当调度器**：text-davinci-003（`config.default.yaml:13-14`），规划/选择/总结归 LLM、推理归专家模型——2023 年"小 LLM 驾驭大模型池"代表架构。
- **约束解码替代 JSON mode**：`logit_bias` 把任务名/字段名 token 偏置抬到 0.1/5（`config.default.yaml:27-29`），token id 集合由 `hugginggpt/server/get_token_ids.py:43-53` 离线编码。
- **三层解析容错**：`json.loads`→`find_json`（`awesome_chat.py:222`）→`field_extract`（`awesome_chat.py:230`）；全仓一律异常驱动重试。
- **单卡显存互斥**：`pipes[id]['using']` 自旋锁（`hugginggpt/server/models_server.py:366-369`），推理前 `pipe.to(device)`（`models_server.py:376-381`）、后即 `pipe.to("cpu")`（`models_server.py:604-611`）——单卡跑数十模型的腾挪术。
- **hybrid 双通道**：`inference_mode: hybrid`（`config.default.yaml:15`）本地/HF 择优；失败记 `log_fail.jsonl`（`awesome_chat.py:245-252`）。
- **断点续跑**：easytool 进度文件（`easytool/easytool/util.py:92-105`）、taskbench 已推理 id 集（`taskbench/inference.py:55-69`）。

## 六、数据流实例走读

多轮样例"canny 图→再生成新图"（`awesome_chat.py:994-999`）：

1. `parse_task` 产出两任务：`canny-control(id:1,dep:[-1])` 与 `canny-text-to-image(id:2,dep:[1],image:<GENERATED>-1)`；
2. 调度器首轮只放行任务 1；ControlNet 捷径钉死 `canny-control` → `CannyDetector` 出图（`models_server.py:408-418`），`{"path":...}` 改写为 `generated image`（`awesome_chat.py:546-550`）；
3. 任务 2 占位替换为真实路径（`awesome_chat.py:768-770`）后走 `sd-controlnet-canny`，管线换 control 权重出图（`models_server.py:397-406`）；
4. `response_results` 汇总回复；媒体 URL 由前端渲染成气泡（`hugginggpt/web/src/views/home.vue:92-174`）。

## 七、扩展点

- **加本地专家模型**：`load_pipes` 注册（`models_server.py:85-339`）+ `/models/<id>` 分支（`models_server.py:384-597`）+ `p0_models.jsonl` 追加。
- **加任务类型**：同步改任务清单（`config.default.yaml:32`）与关键词集合（`get_token_ids.py:44`），漏一处即失效。
- **换 LLM 后端**：优先级 local>azure>openai（`awesome_chat.py:82-89`），`dev: true` 直连任意 OpenAI 兼容 `/v1`（`awesome_chat.py:98-99`）——接 vLLM 的官方暗门。
- **EasyTool 换基准**：仿 `funcQA.py` 执行器 + `easytool/main.py:21-90` 分发链挂载。
- **TaskBench 加域**：`tool_desc.json`→`generate_graph.py`→`data_engine.py`→`format_data.py` 四步。

## 八、新人上手路径

1. `README.md` + `hugginggpt/README.md` 建图（30 分钟）；
2. 精读 `chat_huggingface`→`parse_task`→`run_task`→`response_results` 四函数（核心 400 行）；
3. 对照 `config.default.yaml:30-46` 与 `hugginggpt/server/demos/` 三份 demo 理解 prompt 三元组；
4. `models_server.py` 的 `load_pipes` 与 using 互斥段；
5. `config.lite.yaml` 零 GPU 跑通，再上 hybrid；
6. 分流：prompt 工程看 easytool，评测方法学看 taskbench。

**勘误清单（源码实证，图谱摘要/README 与源码不符处以源码为准）**：

1. `taskbench/evaluate.py:60-62` 匈牙利匹配死代码（零调用，`linear_sum_assignment` 见 `evaluate.py:57`）；实际指标全为"No Matching"集合 F1（`evaluate.py:499-515`），"图编辑距离"实为 Levenshtein 工具 id 序列相似度（`evaluate.py:528-536`）。
2. `taskbench/inference.py:161` `results +=`：变量仅当 `--log_first_detail` 真时于 `inference.py:154` 定义，默认 False 必 NameError。
3. `hugginggpt/server/run_gradio_demo.py:59`、`:68` `uuid.uuid4()[:4]` 是 TypeError（正确写法 `:52`），传音频/视频必崩且视频误存 audios 目录。
4. `hugginggpt/server/models_server.py:504` 双等值 and 条件恒假，`Intel/dpt-hybrid-midas` 分支永不执行。
5. `taskbench/evaluate.py:415-423` 变量交叉：预测侧进 `label_task_arg_name*`、金标侧进 `predcition_task_arg_name*`，`evaluate.py:518`/`:523` 互换喂 flatten——binary F1 靠对称性幸存、P/R 镜像。
6. TaskBench README 称 28271 样本，仓内 `data.json` 实为 17331 条（7458+5555+4318），口径差未说明。
7. `easytool/easytool/toolbench_retrieve.py` 与 `toolbench.py` 90% 同构（diff 实证：仅 `toolbench_retrieve.py:45-60` 两函数+`:668-669` 检索差异），改一漏一是维护风险。
8. `easytool/easytool/funcQA.py:539`、`:623` `depend_id=[1]` 硬编码，首子任务也恒走带依赖分支。
9. `hugginggpt/server/awesome_chat.py:701` 误查 dict 键而非端点桶，理论可重复入桶，`awesome_chat.py:865` 过滤兜底。
10. `config.default.yaml:46` response_results prompt 尾带孤立 `}`（gradio 配置同款 artifact），会拼进 prompt。

---

*understand-anything 讲透写手，2026-11-02。图谱：仓内 `.understand-anything/knowledge-graph.json`（188 节点/297 边/13 层/16 步）。*
