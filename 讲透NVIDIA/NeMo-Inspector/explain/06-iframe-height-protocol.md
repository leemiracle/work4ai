# 06 · iframe 高度协议：change_element_height.js + register_textarea.js 的跨语言握手

## 角色定位

NeMo-Inspector 的富文本（ANSI 终端回放、Pygments 高亮代码）都装在 srcDoc iframe 里，而 iframe 在浏览器里**不会自动撑高**——内容多高，框架默认还是声明的高度，超出部分被 `overflow: hidden` 吃掉。这两个 JS 资产脚本（各约 30 行）与 Python 侧 `utils/decoration/common.py` 的三个函数共同构成一条 postMessage 协议，让每个内容 iframe 自己量高、上报、被父页调整。这是全仓唯一的 Python↔JavaScript 接口，也是理解"为什么改一处文本渲染要动三个暗容器"的钥匙。

## 内部结构

**接收端 `change_element_height.js`（有效代码 :15-22）**：父页全局监听 message 事件（:15）；收到消息先做双真值门卫——`event.data.frameHeight && event.data.frameId` 都存在才继续（:16，防无关消息与 0 高度）；按 frameId `getElementById` 找到 iframe（:17）设 `style.height = frameHeight + 'px'`（:18-19）。协议的全部字段就两个：`frameHeight`（数字）与 `frameId`（DOM id 字符串）。脚本本身由 Dash 的 assets 自动加载机制进页面（callbacks/__init__.py:20-26 把 assets_folder 指到 nemo_inspector/assets）。

**textarea 端 `register_textarea.js`（:15-31）**：定义全局函数 `registerTextarea()`——querySelectorAll 拿全部 textarea（:16-17），逐个绑 `updateHeight` 闭包（:18-25）：先把 `style.height` 归零（:19，否则 scrollHeight 永远不超过当前高度）、再取 `Math.max(scrollHeight, offsetHeight, clientHeight)`（:21-22）设回（:24）。绑定三处：`textarea.onload`/`textarea.onresize` 属性赋值（:26-27）+ `addEventListener('input')`（:28）+ 注册时立即执行一次（:29）。**甄别**：:26-27 是死代码——textarea 元素不触发 load 事件（那是 window/img/iframe 的），也没有原生 resize 事件（那是 window 的）；实际生效的只有 input 监听与 :29 的一次性调用。全局函数挂 window 上，是给 iframe 内脚本跨文档调用的（见下）。

**Python 对端（utils/decoration/common.py）**：

- `update_height_js(iframe_id)`（:91-104）生成**内容 iframe 内部执行**的 JS 字符串：取 body/html 的 scrollHeight/offsetHeight/clientHeight 四值最大（:97-98），`parent.postMessage({frameHeight, frameId}, '*')`（:100），window 的 onload 与 onresize 双触发（:102-103）。经 `iframe_template`（:111-139）拼进每个内容 iframe 的 srcDoc——模板本身是 srcDoc 工厂（head/body 拼装 :127-137，无边框全宽样式 :117-121，id 缺省时 `get_random_id` 生成 20 字符随机串 :107-108/:114-115——随机性保证 getElementById 的 frameId 全局唯一）。
- `get_height_adjustment()`（:70-88）是**触发器 iframe**：固定 id `query_params_iframe`（:72）、visibility 隐藏（:87）、srcDoc 里只有一段脚本——DOMContentLoaded 时调 `parent.registerTextarea()`（:80-82）。

**三级触发链**把两端串起来：Dash 重渲染只更新 DOM 不执行 script，于是任何重渲染回调顺带返回 `js_trigger + " "`（如 detailed_sample_info.py:95、count_stats_dataset.py:69）→ `callbacks/common/decoration.py:20-30` 监听 page_content 或 js_trigger 变化，把 `get_height_adjustment()` 重新注入 `js_container`（base_layouts.py:32）→ 新隐藏 iframe 加载，DOMContentLoaded 调 parent.registerTextarea()，全部 textarea 重绑+立即量高；同时内容 iframe 自己的 onload 触发各自 postMessage，接收端逐个调整。

## 外部连接

上游：`design_text_output` 的 ANSI 分支（decoration/common.py:32-48）与 `highlight_code`（utils/decoration/code.py:30）是内容 iframe 的两大产地；骨架层三个暗容器 `js_trigger`/`js_container`/`dummy_output`（base_layouts.py:31-33）是协议的管道。下游：assets/styles/ansi_styles.css 由 iframe 内 link 引用（decoration/common.py:44——该行双 href 笔误见 ONBOARDING §8.5）。返回 `js_trigger + " "` 的回调遍布 detailed_sample_info/count_stats_dataset/label_dataset/sort_dataset 诸文件——"顺带触发高度链"是重渲染回调的公共尾巴。

## 数据流

内容 iframe 内：window.onload/onresize → 量四高取 max → postMessage `{frameHeight, frameId}` → 父页 message 监听 → getElementById → 设高度。textarea 侧：重渲染 → js_trigger 追加空格 → decoration 回调重注入触发器 iframe → DOMContentLoaded → parent.registerTextarea() → 全部 textarea 归零-量高-设回。两条支线共用"重建一个 iframe 让浏览器替我们执行 script"这一核心技巧。

## 设计决策

- **postMessage 而非 CSS**：iframe 高度取决于**子文档**内容，父页 CSS（height:auto/100%）对跨文档边界无能；postMessage 是唯一能让子文档把测量结果递出来的标准通道。
- **量高脚本由 Python 字符串生成**（:91-104 f-string）而非 assets 文件：每个 iframe 的 frameId 不同，脚本必须逐 iframe 定制注入——f-string 是最直接的参数化方式。
- **重建触发器 iframe 而非 eval**：Dash 前端没有受控的"执行一段 JS"出口；让浏览器加载新 iframe、借其 DOMContentLoaded 副作用执行注册，是把脚本执行权还给浏览器生命周期的迂回正解。
- **postMessage 目标 `'*'`**（:100）：同源 srcDoc iframe 下无实际风险，但若日后引入外部内容 iframe，任何页面都能收到带 frameId 的高度消息——收窄为同源 targetOrigin 是一行改动。
- **ResizeObserver 缺席**：现代做法是在内容根挂 ResizeObserver 一次性解决；上游选择 onload/onresize 轮询式触发，窗口缩放能覆盖、字体异步加载后的二次撑高则靠重渲染链兜底——够用但多一次全页往返。
- **固定 id `query_params_iframe`**（:72）：触发器 iframe 始终单实例（js_container 每次整体替换），固定 id 不会撞；名字带 query_params 是历史遗留（曾经服务于查询参数场景）。

## 新人提示

- 调"iframe 高度不对"：浏览器 console 执行 `window.addEventListener('message', e => console.log(e.data))` 先看有没有消息、frameHeight 是多少——再判断是发送端没触发还是接收端没找到元素。
- 新增重渲染回调而忘记返回 `js_trigger + " "`，textarea 自适应就会失效——照 detailed_sample_info.py:95 的双返回（js_container 清空 + js_trigger 追加空格）抄。
- 内容 iframe 内调试直接读 srcDoc（元素审查 iframe 节点）；改动 `iframe_template` 注意 header/content 都是裸 HTML 字符串拼接，不做转义——喂用户内容前先想清楚 XSS 面（ANSI 分支的 ansi2html 输出已是转义后的 HTML）。
- 别给触发器 iframe 改随机 id：decoration 回调每次整体替换 children，旧 iframe 自然销毁，固定 id 反而是最稳的。
