# 02 · llm_nim/ — LLM NIM 客户端与动态执行器（openai_nim.py + executor.py）

## 1. 角色定位

llm_nim/ 是仓内"生成—执行"闭环的大脑与手，共三个文件：**openai_nim.py（117 行）= 大脑**——按 OpenAI 兼容协议调 NVIDIA hosted NIM（base_url=`https://integrate.api.nvidia.com/v1`），模板方法类族：基类 OpenAINIM 管流式调用与提示词装配，两个子类只写"提示词模板+输出解析"；**executor.py（44 行）= 手**——把 LLM 生成的 Python 函数字符串落盘临时 .py、importlib 动态加载、按函数名取回句柄执行（executor.py:24-38）；**openai_runner.py（189 行）= 僵尸前作**——同一功能的脚本式初版。图谱属 L04 LLM NIM 客户端层。

**勘误·选材路径**：派发单写作"openai_runner/ 目录"——实际目录名是 `llm_nim/`（app_image.py:12-13 的 import 可证），openai_runner.py 只是其中文件之一。派发单附注的"202 轮询、重试；L129 裸 header_auth"也不在本目录——那是 CV NIM 的 NVCF 资产协议，实际位置 cv_nim/gdino_nim.py:121-145，本篇第 5 节一并钉死。**openai_runner.py:10 `from config.config_util import load_config` 是断链 import**：config/ 下只有 config.yaml 与 gdino_spec.yaml，config_util.py 实际在 utils/——该文件一旦被导入立即 ModuleNotFoundError；全仓 grep 证实零消费（两个 app 只 import openai_nim 与 executor）。

## 2. 内部结构

**openai_nim.py**：
- :13-61 OpenAINIM 基类。:18-21 构造 OpenAI client（凭据经 app 层从 utils/constants.py:4-6 的占位符传入）；:23-26 与 :58-61 两个 `@abstractmethod`——**但类未继承 ABCMeta，装饰器无强制力**（子类都实现了所以无感，新增子类漏写要到运行才炸）。:28-30 assign_model 绑定模型名；:32-49 get_completion_output 固定 temperature=0.1/top_p=1/max_tokens=1024/stream=True，:46-48 逐 chunk 拼 delta.content；:51-56 infer=取补全+parse_output，模板方法把流程钉死在基类。
- :64-99 InstructionalNIM。:68 把代码生成约束全部写进提示词：单函数、必须叫 postprocessor、单入参、import 语句放函数体内、"safe and ethical"话术、bbox 为 XYXY 且可能含 object_text 字段；{codellama_prompt}/{bbox_prompt} 两个 format 槽。:71-99 parse_output 用缩进扫描剥函数体：:81 定位 def 行，:84 取 def 行缩进为基线，:88-95 逐行直到"缩进≤基线且非空行"（:92 空行不终止，函数体内空行合法），:98 切片。模型违规输出两个函数时只截第一个。
- :101-117 NounChunkNIM。:105-111 提示词定义 noun chunks 语义+复数归一单数+排除抽象名词+只输出 JSON；:114-117 parse_output **裸 `json.loads`**——模型输出 fence 或前后缀文字会直接 JSONDecodeError，无任何剥离加固（对照 InstructionalNIM 的缩进扫描，两个解析器健壮性差距明显）。

**executor.py**：
- :12-15 __init__——postprocessor=None，function_name 默认 "postprocessor"。
- :17-22 save_python_function——:19 `tempfile.mkstemp(suffix=".py")` 落盘返回路径。
- :24-34 load_function_from_string——:27 sys.path.append 临时文件目录；:29-31 importlib.import_module(文件名[:-3])；:32 getattr 取句柄；**:33-34 except 只把 traceback 赋给局部变量 traceback_str 后丢弃——静默吞异常**。
- :36-38 execute——直接 `self.postprocessor(metadata)`。
- :40-43 __del__——pop sys.path 里的字面量 "/tmp"。

**openai_runner.py（僵尸对照）**：:16-30 get_open_api_output（与基类同款参数的函数版）；:33-50 read_kitti（kitti_util.read_kitti 的旧复制）；:52-77 硬编码的 demo postprocessor（robot/pallets 中心距<100 判定——设计意图的"参考答案"）；:80-104 extract_function（InstructionalNIM.parse_output 的逐字前身）；:107-133 infer 生成→落盘→importlib→执行一条龙；:150-189 infer_with_string_inp（视频 KITTI 字符串输入变体，整段 prompt 硬编码）。

## 3. 外部连接

- openai_nim 与 executor 被 app/app_image.py:12-13 和 app/app_video.py:12-13 消费（InstructionalNIM/NounChunkNIM/Executor 三件套）。
- openai_nim 依赖 openai SDK；URL/NVCF_API 由 app 层从 utils/constants.py 注入。
- executor 只用标准库（importlib/sys/tempfile/traceback）。
- **两个文件的契约点**是函数名 "postprocessor"（openai_nim.py:68 的提示词约束 与 executor.py:12/:32 的默认名）加上单参数签名——任一侧改名即断。
- openai_runner.py 零消费且 import 断链（:10），是纯参考化石；其 read_kitti/extract_function 与 kitti_util、InstructionalNIM.parse_output 逐字重复，证明后两者由它提炼。

## 4. 数据流

名词块线：question → app 拼 "Given text: {prompt}"（app_image.py:52）→ llama3-70b 流式 → json.loads → {"noun_chunks": [...]}。

代码线：metadata 经 `base_prompt.format(bbox_prompt=json.dumps(metadata), codellama_prompt=question)`（app_image.py:68-71）→ codestral-22b 流式拼串 → 缩进扫描剥出函数源码 → Executor：mkstemp 写盘 → sys.path 注入 → import_module → getattr → `execute(metadata)` 返回后处理结果。注意 metadata 在提示词里是 json.dumps 的字符串、在 execute 里传的是原 Python 对象——两条通路类型不同。

## 5. 设计决策（含勘误）

- 模板方法的取舍：协议（流式/参数/拼接）收在基类，子类只写 prompt 与 parse 两个纯函数——新增 NIM 特化零协议知识；代价是解析器健壮性参差（裸 json.loads vs 缩进扫描）。temperature=0.1 是两个脆弱解析器的确定性锚，调高会同时威胁 JSON 合法性与函数体缩进。
- **勘误·mkstemp 唯一文件名是绕开 sys.modules 缓存的关键**：每次生成新文件名=新模块名，同进程反复加载不会命中旧模块。对照 openai_runner.py:125 `os.path.basename(temp_py_file).strip(".py")`——**strip 是按字符集从两端剥离，不是去后缀**：临时名尾字符落在 {p,y,.} 时会被多剥一位，模块名与文件名错位→间歇性 ImportError。executor.py:30 的 `[:-3]` 才是正确写法。
- **勘误·吞异常**：executor.py:33-34 加载失败静默，postprocessor 保持 None，错误延迟到 app 层调用 execute（:38）时以 'NoneType' object is not callable 的 TypeError 爆出——根因（语法错/缺函数名/import 失败）被吃掉，排障要回到 stdout 的生成代码。
- **勘误·__del__ 错位**：executor.py:42 只匹配字面量 "/tmp"，而 :27 append 的是 os.path.dirname(临时文件)——仅当 mkstemp 恰落在 /tmp 直下才相等（TMPDIR 定制或嵌套目录时 sys.path 条目永久累积）；__del__ 时机不定，多实例逐个泄漏。另 :19 `_, temp_pyfile = tempfile.mkstemp(...)` 丢弃 fd 未关闭——POSIX 无碍，Windows 上锁文件。
- LLM 生成代码直接 importlib 执行=eval 级信任：提示词里的 "safe and ethical"（openai_nim.py:68）是软约束，真正的隔离只在 Docker 容器层（tao_ws 用法）。
- **勘误·202 轮询三层叠加 bug（实际在 cv_nim/gdino_nim.py:121-145）**：派发单点名的 :129 裸 header_auth 确认存在（`"Authorization": header_auth` 缺 self.），但它只排第二——:127 `while(MAX_RETRIES)` 先炸 **UnboundLocalError**：:133 `MAX_RETRIES -= 1` 使该名字成为 infer 的局部变量，首次求值即引用未赋值（本地独立复现验证）；补 global 声明后才轮到 :129 的 NameError；两个都修完还有第三层——模块级 MAX_RETRIES（:15）被 batch_infer 的 16 线程（:157）共享递减，重试预算全进程耗尽加竞态。结论：202 分支 dead-on-arrival，线上能跑只因 NVCF 通常同步返回 200（:115）；OCD 客户端更干脆，压根没写 202 处理（ocd_nim.py:85-96 直接把响应体当 zip 解）。

## 6. 新人提示

- 新增 LLM 特化：继承 OpenAINIM 写 get_base_prompt/parse_output 即可；别动基类采样参数（temperature 0.1 同时护着两个解析器）。
- Executor 排障顺序：看 stdout 的生成代码（openai_nim.py:75 print 全文）→ 手动跑该临时 .py → 核对函数名恰为 postprocessor（提示词约束≠保证）。
- 复活 openai_runner.py 任何函数前先修 :10 断链 import（改 `from utils.config_util import ...` 或删除）；它 :127 的 `json.loads(metadata)` 按 str 设计，与 executor 直接传对象的语义不同。
- 修 202 轮询要三件套一起上：global MAX_RETRIES、self.header_auth、每次调用局部重试计数——只修一个照样炸（层叠顺序见第 5 节）。
- NounChunkNIM 换模型若输出 markdown fence，先给 :114 的 parse_output 加 fence 剥离，否则 JSONDecodeError 会栈到 app 层难定位。
