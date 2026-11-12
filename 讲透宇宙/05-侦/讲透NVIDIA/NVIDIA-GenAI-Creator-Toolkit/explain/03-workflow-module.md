# 03 — workflows/01-llm-prompt-enhancer/：LLM Agent 提示词增强工作流（第一课）

> 工作流 JSON 1884 行（LiteGraph UI v0.4，22 节点/26 链接/4 分组）+ README/models.md/nodes.md

## 1. 角色定位

十模块中的入门第一课，也是全仓唯一演示 "LLM agent × 扩散模型" 组合的模块：用本地 Ollama gemma3 把弱提示词改写成 Qwen Image 优化的结构化提示词，再交给 Qwen Image 2512 + Lightning 4 步 LoRA 出图。README:11-15 借它教 agent 三要素 Brain/Persona/Task。四件套（JSON+README+models+nodes）是全仓统一形态。

## 2. 内部结构

4 分组实为三条链：

- **Agent 链**：`OllamaConnectivityV2`（JSON:68，url=127.0.0.1:11434、gemma3:latest、keep_alive 5 minutes）→ `OllamaGenerateV2`（JSON:819，persona "You are an AI artist."、format=text），system 槽接 `PrimitiveStringMultiline`（JSON:775，agent 提示词：要求输出 Refined Prompt 与 Keyword Tags 两段、禁止推理）、prompt 槽接用户输入（JSON:1184）→ `RegexExtract`（JSON:966，正则 `Refined Qwen-Image-2512 Prompt:\s*(.+?)(?:\nCompact Keyword Tags:|$)`，dotall、group=1）→ `easy showAnything`（JSON:1278）。
- **扩散底座**：`UNETLoader`（JSON:1417，qwen_image_2512_bf16）→ `LoraLoaderModelOnly`（JSON:1492，Lightning 4-steps）→ `ModelSamplingAuraFlow`（JSON:154，shift=3）；`CLIPLoader`（JSON:263，qwen_2.5_vl_7b）、VAELoader、中英双语负向 `CLIPTextEncode`（JSON:9）。
- **双 KSampler A/B 对照**：Agent 路正向编码（JSON:205）→ `KSampler`（JSON:515，steps=4、cfg=1、euler/simple、seed=715047301221872 fixed）→ SaveImage "Agent"；原始路（JSON:1085）→ `KSampler`（JSON:645，参数与 seed 相同）→ SaveImage "User"。两路共享 `EmptyLatentImage`（JSON:1319，1664×928，即 Note 节点 JSON:1394 宽高比表 16:9 档）。

## 3. 外部连接

依赖 3 个 custom node 包：comfyui-ollama（Connectivity/Generate）、ComfyUI-WJNodes（RegexExtract）、ComfyUI-Easy-Use（showAnything）。模型四件套由 download_models.py catalogue["01"]（:186-203）落盘，`qwen/` 前缀对应 dest_subdir（Windows 侧被 normalize_paths_win.py 改写为反斜杠）。

## 4. 数据流

用户弱提示（默认 "a frog…"）→ gemma3 改写为结构化提示（主体/环境/光照/相机/风格/引号文本）→ RegexExtract 只取 Refined 段 → CLIP 编码与固定负向条件进入 4 步采样 → "Agent" 图；原始提示同时走同 seed 第二采样器产出 "User" 图，并排对比即 agent 增益证据。

## 5. 设计决策

- **cfg=1 + 4 步**是 lightx2v Lightning 蒸馏 LoRA 标准配方：蒸馏模型内嵌负向条件、丢弃 CFG；`ModelSamplingAuraFlow shift=3` 调 sigma 偏移适配低步数。
- **RegexExtract 是抗 LLM 输出噪声的结构化方案**：gemma3 无强制 JSON 模式，system prompt 两段格式软约束，正则硬抽取兜底；改格式必须同步改正则。
- **A/B 对照是教学设计**：同 seed + fixed + 共享 latent，唯一变量是提示词。
- **勘误①（三包依赖各漏一包）**：README:67-68 列 Easy-Use + comfyui-ollama（漏 WJNodes——RegexExtract 是全链咽喉），nodes.md:7-8 列 WJNodes + comfyui-ollama（漏 Easy-Use），安装器实装 3 包（install.sh:281-291）；README:51 "2 packages" 欠数。
- **勘误②（口径矛盾）**：models.md 头部 "~29 GB / VRAM 12–16 GB" 与 README:49-53 "~65 GB / Win 24 Linux 32 GB" 矛盾，其表格加总≈65 GB 站 README 边；LoRA 体积也漂移（README:63 ~1.7 GB vs models.md:13 1 GB）。
- **勘误③（persona 措辞）**：system prompt（JSON:775）自称 "Qwen Image **Edit** 2512"，但 models.md:15 明说 Module 01 用 2512 生成变体——模板复用的措辞漂移。

## 6. 新人提示

改 loader 文件名要三处同步（JSON widget / download_models.py / models.md）。动 Agent 链先保住 system prompt 格式与正则的配对；keep_alive 5 分钟意味着空闲后模型卸载，不是 bug。A/B 对照依赖双 KSampler 逐项一致。此 JSON 是后续模块的模板母版。
