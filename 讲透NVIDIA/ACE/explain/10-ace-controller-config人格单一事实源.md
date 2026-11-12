# 10 · ace-controller config.yaml——数字人人格的单一事实源

> 源：`workflows/tokkio/5.0.0-ga/src/llm-rag/configs/config.yaml`（91 行）及六个 chart 挂载副本 `llm-rag/tokkio-*/config/ace-controller/config.yaml`——七份 md5 全同（7fcbe9f24e550aea8ab9616d28df2a6c）

## 一、角色定位

这 91 行 YAML 是 Tokkio 数字人 **Aki 的全部"灵魂"与管线行为开关**：system prompt 人设、三家 LLM 通道参数、填充语、欢迎/告别语、主动搭话节拍、RAG 引用置信阈值、姿态动画目录，全在一文件。它是 config.py pydantic Config 模型（config.py:62-72）的数据面——bot.py:80-83 启动时 `Config(**yaml.safe_load(...))` 反序列化，字段名即契约。运维视角它是**热改入口**：customization-notebooks 01/02/06 三册（改名/改提示词/换 LLM）的操作对象都是它，经 ACE Configurator 下载→改→上传回路生效，容器内挂载点刷新策略为 HotReload（tokkio-app-params.yaml:229-234）——**改人格不重启、在途会话不断**。

## 二、内部结构

九个段按"被谁消费"分三层：

1. **管线开关段** `Pipeline:`（config.yaml:1-10）：`llm_processor: "NvidiaLLMService"`（:6）三选一黑马——决定 bot.py:143-169 实例化哪个服务；`filler`（:7-9，"Let me think"/"Hmmm"）与 `time_delay: 2.0`（:10）喂填充语机制（见 08 篇）。
2. **人格段** `OpenAILLMContext:`（:20-33）：`name: "Aki"`（:21）+ 13 行 prompt（:22-33）——营销传播专家人设、点名 Audio2Face-3D/Riva Parakeet/ElevenLabs 自我认知、禁股票建议禁竞品对比、RTX4090 情结、**"单句 ≤100 字符、禁列表/Markdown/表情"** 的语音友好纪律。`{name}` 占位符在 bot.py:206 替换。
3. **三通道参数段**：`NvidiaRAGService:`（:36-41，use_knowledge_base/max_tokens 1000/rag_server_url 0.0.0.0:8081/collection_name/suffix_prompt"≤75 字符"）、`NvidiaLLMService:`（:44-46，integrate.api.nvidia.com + meta/llama-3.1-8b-instruct）、`OpenAILLMService:`（:49-50，gpt-4o）——**未选中的两段仍必填**（pydantic Config 根模型无默认，config.py:67-69）。
4. **处理器参数段**：`UserPresenceProcesssor:`（:12-14，Hello/Bye）、`ProactivityProcessor:`（:16-18，100 秒后"I'm here if you need me!"）、`RAGMultimodalResponseProcessor:`（:52-54，confidence_threshold 0.37、top_n 2）、`FacialGestureProviderProcessor:`（:56-59，Taunt/Pensive 手势、probability 0.5）。
5. **进阶段** `AnimationGraphService:`（:64-91）：posture 五姿态 clip 目录（Talking/Listening/Idle/Thinking/Attentive，:72-91），启动期被 `pregenerate_animation_databases` 预计算（bot.py:85）——注释明言"场景不支持则改了无效"（:62-63）。

## 三、外部连接

**消费方**：bot.py（全部段的装配来源）、rag_multimodal_response_processor.py:36-46（独立再读一次 CONFIG_PATH 取阈值——模块加载期自建降级 SimpleConfig，**读文件失败静默回落 0.5**，与 yaml 的 0.37 不同值，见 §五-4）；audio2face-3d-tuning 的 bot.py 也 import 同一 Config（图谱 depends_on 边）。**分发链**：源内 configs/config.yaml →（构建/部署时复制）→ 六 chart 各自 config/ace-controller/ 挂载份 → tokkio-app.yaml:52-53 声明 `files: config.yaml: ./config/ace-controller/config.yaml` 挂进 ace-controller 组件 → 容器内 entrypoint.sh:12 `CONFIG_PATH` 默认 `./configs/config.yaml` 指向。**修改回路**：ACE Configurator（热）/ 重建镜像（冷）两途。

## 四、数据流

启动期：entrypoint.sh 设 CONFIG_PATH → bot.py:80-83 yaml→pydantic（缺段/类型错立即 ValidationError 拒启）→ Config 对象全程内存传递（AnimationGraphService 段在 bot.py:85 变成预生成动画库；Pipeline 段在 :148/:156/:167 变成服务构造参数；OpenAILLMContext 段在 :202-215 变成首条 system 消息）。运行期热改：Configurator 写 PV 挂载文件 → uvicorn `--reload-include $CONFIG_PATH`（entrypoint.sh:53）把该 yaml 纳入监听，变更即触发应用重载——所谓 HotReload 是"Pv 文件热更 + uvicorn 自动重载"两层叠加，**不需要 kubectl 重启 pod**，但进程内重载仍会打断在途 WebSocket 会话（重连即恢复）。

## 五、设计决策

1. **人格与管线同文件**：换人设（改 prompt）与换大脑（改 llm_processor）一个入口——对"数字人定制"这一核心场景，运维粒度故意压到单文件；代价是并发容量等部署参数被隔离到 values/params，两处分工清晰。
2. **拼写错误成为契约**：段名 `UserPresenceProcesssor`（三个 s，config.yaml:12）与 config.py:64 字段名互锁——改名要两侧同步，历史 typo 已固化。
3. **三段全必填**：未用通道也占位，防止切换 llm_processor 时才发现缺段——把"换模型"从两步（补段+改开关）压成一步。
4. **双读者两套默认**：config.py:58 的 confidence_threshold 默认 0.5，yaml 实值 0.37（:53），而 rag_multimodal_response_processor.py:33 的降级常量又是独立 0.5——三处数字各写各的，改阈值时 yaml 是唯一生效源（只要它能读到位）。
5. **七份同源靠复制纪律**：无 symlink 无生成脚本，md5 一致纯靠人工/流程同步——改任何一份的检查命令：`md5sum tokkio-*/config/ace-controller/config.yaml src/llm-rag/configs/config.yaml`。

## 六、新人提示

- 快速换人格：只改 `OpenAILLMContext.prompt`（:22-33）即可热生效；想彻底换角色连 `name`（:21）一起改，`{name}` 占位符会自动跟进。
- prompt 里的输出纪律（单句/无 Markdown）是为 TTS+A2F 唱歌写定的——做文本场景可以放开，语音场景别删。
- 切到 RAG 通道记得三件事：`llm_processor` 改名、`rag_server_url` 从 0.0.0.0 改真地址、`collection_name` 从占位串改成真集合。
- `FacialGestureProviderProcessor` 段（:56-59）在 llm-rag 管线里**无消费点**（bot.py 未实例化该处理器，全文件 grep 零命中）——config.py:70 要求它必填，属于"必填但闲置"段，删段会炸启动，留着不生效。
- 验证热改是否到位：看 uvicorn 重载日志 + 欢迎语（UserPresence 段最直观）。

## 甄别记录

任务书称 "七份逐字节同源…entrypoint.sh:12 挂载"；实证微调：entrypoint.sh:12 是 CONFIG_PATH 默认值的**消费点**，真正的挂载声明在 tokkio-app.yaml:52-53（files 映射）与 tokkio-app-params.yaml:229-234（HotReload Pv 策略）；七份同源（6 chart+1 源内）md5 全同确认无误。图谱 summary 称 "91 行" 与 wc -l 实证一致。
