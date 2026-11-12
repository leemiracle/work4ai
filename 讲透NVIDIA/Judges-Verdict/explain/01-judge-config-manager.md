# 01 · judge_config_manager.py —— 配置心脏：三框架、一数据类、一个 Manager

## 角色定位

`llm_judge_benchmark/judge_config_manager.py`（319 行）是 Judge's Verdict 的配置中枢，回答三问：裁判走哪个服务框架？API key 从哪来？请求打到哪个 URL？评分引擎对它的依赖收敛在两个调用——get_model 拿配置（llm_judge_scoring.py:135）、create_langchain_llm 造实例（llm_judge_scoring.py:161）。门面 judge_config.py:17 在 import 时模块级实例化它。

## 内部结构

**① ServingFramework 枚举**（judge_config_manager.py:21-26）只收 litellm/oneapi/nvdev：litellm 是官方公开路线，oneapi/nvdev 是 NVIDIA 内部框架。__post_init__（judge_config_manager.py:50-56）把 YAML 字符串自动转枚举、非法值当场抛错——配置错误在加载期暴露。

**② JudgeModelConfig 数据类**（judge_config_manager.py:29-48）15 字段：模型标识、鉴权、Azure 系、推理超参（temperature 0.0、max_tokens **8**——裁判只需短判定）、扩展 dict。两个路由方法承担全部环境感知：

- `get_api_key()`（judge_config_manager.py:69-104）三级 fallback：直配 > api_key_env > 按前缀猜。`local/` 前缀返回字面量 "EMPTY"（本地 vLLM 免鉴权哨兵，judge_config_manager.py:82）、`nvidia_nim/`→NVIDIA_NIM_API_KEY（:85），**未知前缀默认 OPENAI_API_KEY**（judge_config_manager.py:93）；nvdev/oneapi 各绑死一个环境变量。
- `get_effective_base_url()`（judge_config_manager.py:106-121）：显式 base_url > NVIDIA NIM 读 NVIDIA_NIM_API_BASE > OneAPI deployment 拼内部代理 URL（judge_config_manager.py:118-119）。

**③ JudgeConfigManager**（judge_config_manager.py:124-306）：构造即四路径搜索配置文件（judge_config_manager.py:148-153）；load_config 逐模型**只补缺键**合并 defaults（judge_config_manager.py:184-186）；add_model/save_config（judge_config_manager.py:209-231）让配置可编程编辑后落盘。`create_langchain_llm`（judge_config_manager.py:233-306）按框架分派：nvdev→ChatNVIDIA（:255）；oneapi→ChatOpenAI（judge_config_manager.py:263-295，内嵌 o1/o3 不传 temperature 的规则，:276）；**litellm→直接 NotImplementedError**（judge_config_manager.py:300-303），把"绕开 LangChain"焊死在类型层。

## 外部连接

被门面 judge_config.py 包装：六个便捷函数全委托单例（judge_config.py:20-65），其中 get_oneapi_config 给 api_version 兜底 "2024-12-01-preview"（judge_config.py:42，Azure 遗存）。评分引擎 main 用它做环境变量预检（llm_judge_scoring.py:328-338）。与 litellm_ragas_wrapper.py 是平行而非调用关系：LiteLLM 路径下 Manager 只出数据（llm_judge_scoring.py:147-156）不出对象。

## 数据流

写向：YAML --safe_load（judge_config_manager.py:175）--> dict --defaults 补缺（:184）--> from_dict 即 cls(**data)（judge_config_manager.py:65-67）--> models 字典。读向两条：查询链 get_model→get_api_key/get_effective_base_url→直连包装参数；对象链 create_langchain_llm→ChatNVIDIA/ChatOpenAI。

## 设计决策

- 前缀路由 API key 而非显式声明：26 模型零 api_key 字段也能跑；代价是"未知前缀默认 OpenAI"（judge_config_manager.py:93）接新供应商时可能静默配错。
- LiteLLM 分支抛 NotImplementedError 而非返回 None：宁可类型层报错不留"假 LLM"——最官方的路线恰恰不走这个工厂。

## 新人提示

改配置先看 judge_config_manager.py:184-186 的"只补缺"语义——defaults 加新键不会覆盖既有定制。接新裁判时模型键名就是 results/ 目录名（llm_judge_scoring.py:12-14）。oneapi 内部 URL（judge_config_manager.py:119）与 api_version 兜底是内网遗产，外部用户可忽略。

——锚核对于 2026-11-08，commit dfbcd5ee。
