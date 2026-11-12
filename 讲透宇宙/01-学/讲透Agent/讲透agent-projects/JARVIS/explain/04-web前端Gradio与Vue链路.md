# 04 · 前端双形态：web/ Vue3 应用与 Gradio 演示链路

## 一、角色定位

HuggingGPT 有两个用户入口：正式产品是 `hugginggpt/web/` 的 Vue3+Vite+Tailwind 单页应用（432 行的 `hugginggpt/web/src/views/home.vue` 承载全部交互），轻量演示是 `hugginggpt/server/run_gradio_demo.py`（131 行，Hugging Face Space 同款）。前端的核心职责只有两件：把用户消息发给 8004 端点的控制器、把控制器回复里的媒体路径渲染成图片/音频/视频气泡。它还有一个隐藏人格——双击设置图标可切换成直连 OpenAI 的纯 ChatGPT 模式（`home.vue:327` 的 `@dblclick="switchChatGPT()"`），一份代码两种产品。

## 二、内部结构

**web/ 的骨架**：`hugginggpt/web/src/main.ts:5-8` 标准 createApp+router 挂载；`hugginggpt/web/src/router/index.ts:3-14` 唯一路由 `/` 指向 home.vue；`hugginggpt/web/src/types/index.ts:1-20` 定义 `ChatMessage`（role/type/first/content 四字段，type 含 image/audio/video/code）与纯文本 `CleanChatMessage`；`hugginggpt/web/src/config/index.ts:1-8` 集中三个常量——`HUGGINGGPT_BASE_URL` 默认 `http://localhost:8004`、`CHAT_GPT_URL`、`CHAT_GPT_LLM`。API 层两个文件：`hugginggpt/web/src/api/hugginggpt.ts:9-31` 以 **180 秒超时**（`:19`）POST `/hugginggpt`——四阶段管线动辄一两分钟，常规 30s 超时必炸；`hugginggpt/web/src/api/chatgpt.ts:7-33` 直连 OpenAI `/v1/chat/completions`，key 从 localStorage 取。

**home.vue 的三块**：①发送链 `sendChatMessage`（`home.vue:38-78`）——收集 `first: true` 的消息清洗净化（`:46-51`），按 `isChatgpt` 分流两 API（`:55-59`），失败消息以 system 角色回显（`:73-76`）；②**媒体抽取与渲染** `messageListMM` computed（`:81-209`）——对每条文本消息跑三组正则（图片 `:92`、音频 `:121`、视频 `:149`），把 URL 替换成带 `<img>`/`<audio>`/`<video>` 标签的内联 HTML 片段（本地相对路径自动拼 `HUGGINGGPT_BASE_URL`，`home.vue:105-106`），去重后再以 `type: image/audio/video` 追加为独立气泡（`:185-200`）；③配置管理——`saveConfig` 校验 key 必须 `sk-` 开头且**恰好 51 字符**（`home.vue:249-252`），存 localStorage（`:254`）。

**Gradio 链路**：`run_gradio_demo.py:6` 直接 import `chat_huggingface`（触发 awesome_chat 切 gradio 配置的机关，`awesome_chat.py:34-36`）；`extract_medias`（`run_gradio_demo.py:15-34`）三组正则抽用户消息里的媒体 URL；`add_text` 把远程图片下载转存 `public/images/`（`:48-54`）；`bot`（`:75-94`）调 `chat_huggingface(all_messages, OPENAI_KEY, "openai", "https://api.openai.com/v1/completions")`（`:78`）后同样抽媒体渲染；`gr.Blocks` 界面（`:96-129`）带 7 条内置 Examples（`:119-127`）。

## 三、外部连接

前端→控制器：仅 `/hugginggpt` 一端点（`hugginggpt.ts:10`），`/tasks` `/results` 两端点（`awesome_chat.py:1024/:1037`）预留给中间结果消费但前端未用——是给二次开发留的探针。媒体服务复用 awesome_chat 的 Flask 静态目录 `public/`（`awesome_chat.py:1019`，static_folder），所以 `/images/xxxx.png` 由控制器进程直接供图，前端无需自己的文件服务。Electron 壳（`hugginggpt/web/electron/main.js:10-23`）只是 BrowserWindow 加载构建产物 `index.html`（`:20`），preload（`preload.js`）仅回填版本号，无自定义 IPC——桌面形态是最薄的包装。构建链：`vite.config.ts:7-13` dev 端口 9999、`@` 别名；`hugginggpt/web/package.json:11-12` 的 `e:dev/e:build` 先 vite build 再拷 electron 目录进 dist。

## 四、数据流

一轮对话：用户输入 → `sendOrSave`（`home.vue:211-221`）判配置态或发送态 → `sendChatMessage` 净化消息（剥掉演示气泡等非 first 项）→ axios POST 8004 → 后端四阶段管线跑完返回 `{"message": "..."}`（内含 `/images/a1b2.png` 之类路径）→ `messageListMM` 正则把路径替换为可点击 `<a><img></a>` 并追加独立图片气泡 → `watch(messageListMM)` 触发 `scrollToBottom`（`home.vue:303-305`）。Key 的流向：HuggingGPT 模式下 key 不从前端走（后端配置或 server 模式动态注入，`awesome_chat.py:1054-1056`）；ChatGPT 模式下 key 走 localStorage→Authorization 头（`chatgpt.ts:14-15`）。

## 五、设计决策

1. **正则即多模态协议**：前后端之间没有结构化媒体字段，媒体传递全靠"文本里的文件扩展名"——后端 `get_content_type`（`taskbench/evaluate.py:149-164`）与 Gradio/前端三套正则各自为政。简单，但 URL 不带扩展名即失明（Gradio 端 placeholder 明说"必须带扩展名"，`run_gradio_demo.py:111`）。
2. **`v-html` 直染 LLM 输出**（`home.vue:343`）：XSS 面——LLM 输出可注入任意 HTML。2023 年仓常见，复用须过 sanitize。
3. **51 字符 key 校验**（`home.vue:250`）：把 OpenAI key 格式硬编码进前端，key 长度政策一变即误杀。
4. **Gradio 演示的已知崩溃点**：`run_gradio_demo.py:59`、`:68` 的 `uuid.uuid4()[:4]` 是 TypeError（UUID 对象不可切片；正确写法 `:52`）——用户消息带音频/视频 URL 必崩；且 `:68` 视频误存 `public/audios/`。
5. **双模式人格的代价**：`isChatgpt` 分支遍布发送/渲染/标题/别名四层（`home.vue:233-247`），mode 下拉与 promptCollection（`hugginggpt/web/src/prompt/index.ts:3-23` 的 Linux 终端等种子模板）联动——单文件塞下两个产品，读的时候建议先追 `isChatgpt` 的全部赋值点。

## 六、新人提示

跑前端的顺序：先起 models_server（可选）、再起 awesome_chat `--mode server`（8004）、改 `hugginggpt/web/src/config/index.ts:1` 指向后端 IP（README 提醒 LAN 部署时必须改，`config.default.yaml:22` 同款注释）、`yarn && yarn dev` 起 9999。调试多模态渲染直接在浏览器 console 里看 `messageListMM` 的正则替换结果，注意 `seq_added_accum` 偏移补偿逻辑（`home.vue:96-111`）——多处替换时下标累计是易错点。想理解双模式切换就双击右上角设置图标（`home.vue:327-329`），标题与角色别名即时切换（`switchChatGPT`，`:233-247`）。
