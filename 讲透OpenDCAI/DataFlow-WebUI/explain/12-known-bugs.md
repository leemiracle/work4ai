# 12 · 已知 bug 与坑专篇：工程化外衣下的十个粗糙点

## 角色定位

前几篇讲了这个仓库安装器、CI、ADR 有多考究；本篇讲反面——后端应用层与文档层真实存在的十个坑。它们全部经源码逐行核实（含两处 Python 行为实测），按"影响面 × 修复成本"排列。共同背景是 CLAUDE.md 钉死的产品定位：单用户本地工具、无认证、禁止加登录——所以这里没有一个是安全门类问题，全是正确性与语义债。

## 内部结构（按文件分组）

**main.py：一个死实例与半初始化陷阱（68 行里最贵的 10 行）。** L17 `app = FastAPI()` 创建了一个**从未被使用**的裸实例——没有 title、没有 router、没有 middleware；真正的 app 是 L50 `app = create_app()` 的返回值，把死实例整个覆盖。同文件还有三处伴生混乱：`from fastapi import FastAPI` 被导入两次（L1 与 L11）；`DIST_DIR`/`INDEX_FILE` 定义了两次（模块级 L19-20，create_app 内局部 L36-37）；L52-58 的 `spa_fallback` 路由和 L61-69 的 startup 事件装饰在**模块级 app**（即 L50 的产物）上。组合出一个陷阱：任何人再调一次 `create_app()`（它看起来就是个工厂函数），会得到一个跑通 `setup_dataflow_core()` + `container.init()`（L24-25 重复初始化）却**没有** spa_fallback 路由、**没有** operator 缓存刷新 startup 事件的半成品实例——工厂的形与模块级副作用的神不一致。修复方向：删 L17 与重复 import，把 L52-69 的装饰器移进 create_app 或彻底删掉模块级 app 改用工厂入口。

**resp.py：状态码语义被信封吃掉。** `created()`（L8-13）名字与语义都该返回 201，实际 `status_code=status.HTTP_200_OK` 硬编码；`no_content()`（L14）同理该 204 却 200。更隐蔽的不一致：`ok()` 直接返回 `ApiResponse` pydantic 对象（由 FastAPI 的 response_model 管线序列化），`created()`/`no_content()` 却手工构造 `JSONResponse`——同一个文件里两条响应管线，行为差异会在加统一 header/中间件时显形。消费者侧：`datasets.py` L24/L158、`pipelines.py` L55、`text2sql_database.py` L78 四处在用 `created()`，而 `no_content()` 全后端**零消费者**（grep 实证仅定义处）——死代码，删除类端点全部走 `ok()`。

**serving.py：404 全部被吞成 500，五连。** 每个端点都是同一个模式：try 块内 `raise HTTPException(404, ...)`，同块 `except Exception as e: raise HTTPException(500, ...)` 把它截胡——`HTTPException` 是 `Exception` 的子类，404 永远到不了 handlers.py 的 HTTP 异常处理器。五处：L113→L125-126、L156→L159-161、L176→L178-179、L205→L233-235、L282→L290-292。用户查一个不存在的 serving，得到的不是"不存在"而是"服务器内部错误"。同文件还有两个小坑：L281-282 的 `if not serving_instance` 是**用后检查**的死代码——L279 已实例化、L280 已调用 `generate_from_input`，falsy 实例早就炸了，且该 404 检查的对象应该是 `serving_info` 而非实例；L111 `print(type(serving_data))` 调试残留直通生产日志。修法：每个 except 前加 `except HTTPException: raise` 透传。

**user_prompt_registry.py：docstring 承诺了不存在的接线。** 文件头 L21-22 写"运行时解引用：算子参数中出现 `user_prompt:<id>` 字符串时，由 param_coercion.resolve_user_prompt_ref(...) 拿到对应模板文本"。核实：`param_coercion.py` **没有** `resolve_user_prompt_ref`，全后端 `user_prompt:` 字符串唯一出现处就是这条 docstring 自己。CRUD 侧倒是齐的（prompts.py L25-99 的建查改删预览），但用户在算子参数里填 `user_prompt:<id>` 的引用永远无人解引用——设计只落了存储半边。这解释了为何它"完全解耦"于 PROMPT_REGISTRY（L4-5）：解耦得太彻底，运行时没有任何桥。

**operator_registry.py：pathlib 拼接丢弃左侧。** L13 `OPS_JSON_PATH = BACKEND_DIR / settings.OPS_JSON_PATH`——而 `settings.OPS_JSON_PATH` 在 config.py L28 是 `os.path.join(BASE_DIR, "data", "ops.json")`，**本来就是绝对路径**。pathlib 的 `/` 运算遇右侧绝对路径时左侧整体失效（实测 `Path('/x/backend') / '/x/backend/data/ops.json'` → `/x/backend/data/ops.json`，BACKEND_DIR 写了等于没写）。当前结果碰巧正确（右侧自完整），但这是语义陷阱：读者以为拼接生效，若有人把 config 改成相对路径，行为才真正依赖 BACKEND_DIR。对照 user_prompt_registry.py L34-35 的同构写法——那里 `settings.RESOURCE_DIR = "data"`（config.py L32）是相对路径，拼接真实生效。同款语法、两种真值，读代码时必须逐个回查 config。

## 外部连接（跨文件的三个策略分裂）

**绑定地址双策略。** 发布包 run.sh 默认 `127.0.0.1` 且非 localhost 警告（build_release.sh heredoc），CI 三连断言死守（10 篇）；但开发态 `scripts/start.sh` L19 是 `HOST="${DATAFLOW_HOST:-0.0.0.0}"`——同一个环境变量、两套默认值。开发者在本地 `./scripts/start.sh` 起的服务默认暴露局域网，而"无认证 + pipeline 执行 = 任意代码执行"的警告只保护发布用户。修法一行：start.sh 默认改 127.0.0.1，保留 DATAFLOW_HOST 覆盖。

**README-release 引用本仓不存在的文件。** `README-release-zh.md` L22 `./run.sh`、L32 `DATAFLOW_HOST=0.0.0.0 ./run.sh`——但仓库根**没有 run.sh**（实测）。它由 build_release.sh 打包时 heredoc 现场生成，只存在于解压后的 zip 里。开发仓里按文档执行会 file not found；这个引用关系仅靠 CI 的 zip 清单断言间接维持（run.sh 在 zip 里 → 文档引用成立）。

**.env.production 示例漂移。** `frontend/README.md` L168 与 `frontend/docs/README_zh.md` L150 教用户在 `.env.production` 写 `VITE_BACKEND_URL=http://your-backend-address:8000`，而仓库实际的 `frontend/.env.production` 内容是单行 `VITE_BACKEND_URL=/`。消费点 `src/axios/config.js` L9-11：`import.meta.env.VITE_BACKEND_URL || ''`——当前值 `/` 使 baseURL 为 `/`，与 README 描述的"指向远端后端"玩法完全对不上。文档、示例文件、代码三者在讲三个故事。

**title 仍是脚手架默认。** `frontend/index.html` L7 `<title>Vite App</title>`——发布包用户浏览器标签页显示的是 Vite 模板名，产品身份感为零。一行修复，但无人做过，侧面印证发布链的 CI 断言（文件存在性、绑定地址）不覆盖"内容像不像产品"。

## 数据流（这些坑如何被踩到）

死实例：通常无症状，直到有人 import `app.main.app` 早于 L50 执行（不可能，模块级顺序保证）——真正的触发场景是 IDE 跳转/重构工具把 L17 当成"the app"；404→500：用户在前端删一个已不存在的 serving，看到红色"内部错误"弹窗而非"未找到"；pathlib 陷阱：重构 config 路径的人自信地改了 BASE_DIR 拼接，测试全绿（因为右侧绝对路径根本不看左侧）；user_prompt 解引用缺失：用户按 UI 引导在算子参数填了模板引用，pipeline 照跑但模板文本从未生效，产出静默劣化——最危险的一类，无报错无日志。

## 设计决策（含批判）

这些坑的共因不是能力，是**验证不均衡**：安装器/CI/ADR 线有负向断言护体（09-11 篇），而应用层的验证只有 backend job 的 pytest——serving 端点没有一条"查不存在 id 应得 404"的测试，resp.py 没有一条状态码断言，user_prompt 解引用没有任何运行时测试兜住 docstring 的承诺。批判地看：CI 投入应跟着"故障爆炸半径"走——安装器坏了毁环境，断言密；但 API 语义漂移毁的是用户对错误提示的全部信任，目前的覆盖近似于零。十坑里七个（死实例、双管线、404 吞噬、死代码 no_content、print 残留、pathlib 陷阱、title）都是一小时内的修复，缺的只是把"release 级负向断言"的纪律延伸到 `backend/tests/`。

## 新人提示

1. 改任何端点的错误处理前，先看 serving.py 这五处反例并理解 `except Exception` 会截胡 `HTTPException`——在这个仓库写正确的错误路径，第一步是加 `except HTTPException: raise`。
2. 排查"接口返回 500 但功能应该正常"时直接读 `backend/data/` 下对应 registry 文件确认 id 是否存在——大概率是 404 被吞。
3. 在 config.py 加路径配置时想清楚绝对/相对，消费侧的 `BACKEND_DIR / settings.X` 只在相对路径下有意义；写绝对路径请直接用，别做装饰性拼接。
4. 别信 docstring 的承诺清单——接线是否存在的终审是 grep 消费者（本篇的 `resolve_user_prompt_ref` 即教训）；给 user_prompt 补齐解引用时，落点应在 param_coercion 的参数处理链（与 prompt_template 的 dict-form 分支同层，ray_pipeline_executor.py L438-453）。
