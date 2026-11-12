"""Simple and clean LLM model interface supporting both cloud and local models"""

# =============================================================================
# 【模块定位】多 LLM 客户端统一接口层：按密钥文件懒建 OpenAI / Claude /
#              Gemini / DeepSeek / local（OpenAI 兼容端点）客户端，一个
#              invoke_llm() 入口屏蔽全部后端差异。
# 【论文映射】论文 §3.1 / §3.2 所有 LLM agent（Bug Pattern Analysis、Plan
#   Synthesis、Implementation、Syntax Repair、triage、refinement）的推理
#   调用都经本模块 invoke_llm() 发出；模型由 config.yaml 的 model 项指定：
#   论文默认 o3-mini，消融实验用 GPT-4o / DeepSeek-R1（API 名
#   deepseek-reasoner）/ Gemini-2-flash（§4 消融表）。get_embeddings() 用
#   ada-002 支撑 RAG 知识库检索（官方 CSA checker 的 pattern/plan
#   embedding 存于 checker_database/*/{pattern,plan}_embedding.pt，检索方
#   在 checker_example.choose_example：cosine 相似度取 top-3 作 few-shot）。
# 【管线角色】上游：agent.py 各 agent 函数 + checker_gen/checker_refine/
#   checker_scan 的 triage 逻辑；下游：各家云 API / 本地 OpenAI 兼容端点。
#   main() 在模式分派前调用 init_llm() 完成初始化。
# 【依赖与坑】①anthropic 为可选依赖（try-import + ANTHROPIC_AVAILABLE
#   开关，未装时 Claude 分支以 NoneType 兜底不崩）；②OpenAI o 系推理模型
#   （o1/o3-mini/o4-mini/o1-preview/gpt-5）不接受 temperature 参数，按
#   子串匹配剔除；③OpenAI 新接口参数名是 max_completion_tokens（不是
#   max_tokens）；④<think> 剥离兼容 DeepSeek-R1 类推理模型输出；⑤prompt
#   超 40 万字符（约 10 万 token）直接放弃返回 None，防上下文溢出与成本
#   失控；⑥重试 6 次、间隔 2s，最后一次失败 re-raise。
# =============================================================================
import time  # 重试间隔 time.sleep(2) 用
from typing import Any, Dict, Optional  # 类型标注（clients 池 / 可选参数）

from google import genai  # Google Gemini 官方 SDK（genai.Client）
from openai import OpenAI  # OpenAI 官方 SDK；local/deepseek/自定义 provider
# 复用同一个类（一切 OpenAI 兼容端点都走它 + base_url）

from global_config import global_config, logger  # 全局配置单例（读密钥/模型项）+ 日志

# Claude SDK 为可选依赖：未安装时置 ANTHROPIC_AVAILABLE=False，相关分支退化
try:
    import anthropic

    ANTHROPIC_AVAILABLE = True
except ImportError:
    anthropic = None  # 占位 None：后续 isinstance 判断用 NoneType 兜底
    ANTHROPIC_AVAILABLE = False

# Global clients
# 客户端池：键为逻辑名（openai/local/claude/google/deepseek/自定义 provider
# 名），由 init_llm() 按密钥文件填充；invoke 时按模型名从这里取客户端
clients: Dict[str, Any] = {}
# 默认模型参数：init_llm() 会用 config.yaml 的 model/temperature/max_tokens
# 覆盖。max_tokens=16000 保证装得下完整 checker.cpp（论文合成 checker 平均
# 125.7 行，但要给 few-shot 复用与长 plan 留余量）
model_config = {
    "model": "gpt-4o",  # 占位默认，实际以 config.yaml 为准（论文用 o3-mini）
    "temperature": 1.0,  # 采样温度默认 1.0（o 系推理模型会被自动剔除该参数）
    "max_tokens": 16000,  # 单次回复 token 上限
}


def init_llm():
    """Initialize LLM clients from configuration"""
    # 【职责】按 llm_keys.yaml 中出现的密钥项懒建各后端客户端，并从
    #   config.yaml 读 model/temperature/max_tokens 覆盖默认参数。
    # 【论文语义】对应论文实验中 LLM 后端的选择（默认 o3-mini）：密钥文件
    #   里放什么 key 就启用什么后端——换消融模型只改配置不改代码。
    # 【返回】无；密钥全空时抛 ValueError（管线处处要调 LLM，早死早超生）
    keys = global_config.get_key_config()

    # Initialize OpenAI client (or compatible)
    # 官方 OpenAI 客户端：有 openai_key 才建（get_embeddings 也只依赖它）
    if "openai_key" in keys:
        clients["openai"] = OpenAI(api_key=keys["openai_key"])

    # Initialize local/custom OpenAI-compatible client
    # 本地/自建 OpenAI 兼容端点（vLLM/llama.cpp/Ollama 等）：配置 base_url
    # 即启用；api_key 缺省 "dummy"（本地端点通常不校验鉴权）
    if "base_url" in keys:
        clients["local"] = OpenAI(
            base_url=keys["base_url"], api_key=keys.get("api_key", "dummy")
        )

    # Initialize Claude client
    # Anthropic Claude 客户端：需 claude_key 且 SDK 已安装（可选依赖）
    if "claude_key" in keys and ANTHROPIC_AVAILABLE:
        clients["claude"] = anthropic.Anthropic(api_key=keys["claude_key"])

    # Initialize Google client
    # Google Gemini 客户端（论文消融模型 Gemini-2-flash 走这里）
    if "google_key" in keys:
        clients["google"] = genai.Client(api_key=keys["google_key"])

    # Initialize DeepSeek client
    # DeepSeek 官方端点：OpenAI 兼容协议，base_url 硬编码；论文消融模型
    # DeepSeek-R1 对应模型名 deepseek-reasoner
    if "deepseek_key" in keys:
        clients["deepseek"] = OpenAI(
            api_key=keys["deepseek_key"], base_url="https://api.deepseek.com/v1"
        )

    # Initialize custom providers
    # 自定义 provider 表：keys["providers"] = {名字: {base_url, api_key}}，
    # 每个 provider 各建一个 OpenAI 兼容客户端（模型名用 "名字:模型" 路由）
    providers = keys.get("providers", {})
    for name, config in providers.items():
        clients[name] = OpenAI(
            base_url=config["base_url"], api_key=config.get("api_key", "dummy")
        )

    # Set model configuration from config.yaml
    # 用 config.yaml 覆盖默认模型参数（model 项即论文实验的 LLM 选择，
    # config-example.yaml 中为 o3-mini）
    model_config["model"] = global_config.get("model", "gpt-4o")
    model_config["temperature"] = global_config.get("temperature", 1.0)
    model_config["max_tokens"] = global_config.get("max_tokens", 16000)

    logger.info(f"Init LLM with model: {model_config['model']}")

    # 一个客户端都没有 = 密钥文件为空/缺 key：直接报错终止
    if not clients:
        raise ValueError("No LLM clients configured")


def get_client_and_model(model_name: str) -> tuple:
    """Determine which client to use and actual model name"""

    # 【职责】把逻辑模型名解析成 (客户端, 后端真实模型 ID) 二元组。
    # 【参数】model_name：逻辑模型名（注册表键名 / "local:xxx" /
    #   "provider:xxx" / 任意裸名字走兜底）。
    # 【返回】clients 池中的客户端对象 + 该后端的真实模型标识符。
    # Model to client mapping
    # 已知模型注册表：逻辑名 → (客户端键, 后端真实模型 ID)。
    # o3-mini=论文默认；gpt-4o / deepseek-reasoner(=DeepSeek-R1) /
    # gemini-2.0-flash-exp(=Gemini-2-flash)=论文 §4 消融模型；其余条目为
    # fork 增量支持（o4-mini/gpt-5 等）。
    model_mapping = {
        # OpenAI models
        "gpt-4o": ("openai", "gpt-4o"),  # 消融模型之一
        "o1": ("openai", "o1"),
        "o3-mini": ("openai", "o3-mini"),  # 论文默认 LLM
        "o4-mini": ("openai", "o4-mini"),
        "o1-preview": ("openai", "o1-preview"),
        "gpt-5": ("openai", "gpt-5"),
        # Claude models
        # 逻辑名 "claude" 映射到具体日期快照版（API 要求带版本号）
        "claude": ("claude", "claude-3-5-sonnet-20241022"),
        "claude-3-5-sonnet": ("claude", "claude-3-5-sonnet-20241022"),
        "claude-3-5-haiku": ("claude", "claude-3-5-haiku-20241022"),
        "claude-3-opus": ("claude", "claude-3-opus-20240229"),
        # Google models
        "google": ("google", "gemini-2.0-flash-exp"),  # 消融模型 Gemini-2-flash
        "gemini": ("google", "gemini-2.0-flash-exp"),
        # DeepSeek models
        "deepseek-reasoner": ("deepseek", "deepseek-reasoner"),  # = DeepSeek-R1
        "deepseek-chat": ("deepseek", "deepseek-chat"),
    }

    # Check if it's a known model
    # 命中注册表且对应客户端已配置（密钥存在）→ 直接返回真实模型 ID
    if model_name in model_mapping:
        client_name, actual_model = model_mapping[model_name]
        if client_name in clients:
            return clients[client_name], actual_model

    # Check if it's a local model (format: local:model_name)
    # "local:<模型名>"：显式路由到 OpenAI 兼容本地端点；[6:] 切掉 "local:"
    # 前缀（len("local:")==6），剩余部分即端点侧真实模型名
    # （如 "local:openai/gpt-oss-120b" → "openai/gpt-oss-120b"）
    if model_name.startswith("local:") and "local" in clients:
        actual_model = model_name[6:]  # Remove "local:" prefix
        return clients["local"], actual_model

    # Check custom providers (format: provider:model_name)
    # "<provider>:<模型名>"：通用自定义路由；split(":", 1) 只切第一个冒号，
    # 模型名里再含冒号/斜杠也不受影响（如 "myvllm:org/model-x"）
    if ":" in model_name:
        provider, actual_model = model_name.split(":", 1)
        if provider in clients:
            return clients[provider], actual_model

    # Default to local client if available
    # 兜底 1：有本地端点就当万能后端（端点自行解析模型名，方便接新模型）
    if "local" in clients:
        return clients["local"], model_name

    # Fallback to OpenAI if available
    # 兜底 2：把名字原样交给 OpenAI（不改注册表也能直接用新模型名）
    if "openai" in clients:
        return clients["openai"], model_name

    # 既没命中也没兜底 → 无可用后端，抛 ValueError（调用方捕获后走失败路径）
    raise ValueError(f"No client available for model {model_name}")


def invoke_llm(
    prompt: str,
    temperature: Optional[float] = None,
    model: Optional[str] = None,
    max_tokens: Optional[int] = None,
) -> Optional[str]:
    """Invoke LLM with the given prompt"""
    # 【职责】管线唯一的 LLM 推理入口：patch2pattern（Bug Pattern Analysis
    #   §3.1.1）/ pattern2plan（Plan Synthesis §3.1.2）/ plan2checker +
    #   repair_syntax（Implementation + Syntax Repair §3.1.3）/ check_report +
    #   reduce_report（triage §3.2）/ repair_FP（refinement §3.2）各 agent
    #   的 prompt 全部从这里发出。
    # 【参数】prompt：拼装完成的提示词（few-shot 例子 + utility 清单 +
    #   任务输入）；temperature/model/max_tokens 允许单次调用覆盖全局默认
    #   （None 表示用 init_llm() 载入的 model_config）。
    # 【返回】模型回答文本（已剥离 <think> 段）；prompt 超长或后端不可得
    #   返回 None；重试 6 次仍异常则抛出最后的异常（由上层决定终止）。

    # 未显式指定则回退全局默认（model_config 由 init_llm 从 config.yaml 载入）
    model = model or model_config["model"]
    temperature = (
        temperature if temperature is not None else model_config["temperature"]
    )
    max_tokens = max_tokens or model_config["max_tokens"]

    logger.info(f"Start LLM process: {model}")

    # Simple token check
    # 粗略长度闸门：40 万字符 ≈ 10 万 token（英文约 4 字符/token 的近似）。
    # 超长直接放弃返回 None——避免必然失败/超窗的请求浪费时延与预算
    if len(prompt) > 400000:  # ~100k tokens
        logger.warning("Prompt too long, skipping")
        return None

    # Get client and actual model name
    # 解析后端：模型名 → (客户端, 真实模型 ID)；解析失败（如该后端没配
    # 密钥）记错误并返回 None，让调用方走各自的失败重试路径
    try:
        client, actual_model = get_client_and_model(model)
    except ValueError as e:
        logger.error(f"Error getting client and model for  {model}")
        logger.error(str(e))
        return None

    # Retry logic
    # 最多 6 次尝试：网络抖动/限流等瞬时错误 sleep 2s 后重试；第 6 次
    # （attempt>=5）仍失败则 re-raise，快速暴露系统性问题
    for attempt in range(6):
        try:
            # Handle different client types
            # isinstance 技巧：ANTHROPIC_AVAILABLE=False 时用 NoneType 参与
            # 比较，避免对 None 取 .Anthropic 属性报 AttributeError；且任何
            # 真实客户端都不是 None 实例，该分支自然不会命中
            if isinstance(
                client, anthropic.Anthropic if ANTHROPIC_AVAILABLE else type(None)
            ):
                # Claude API
                # Anthropic Messages API：temperature/max_tokens 均直接支持
                response = client.messages.create(
                    model=actual_model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    temperature=temperature,
                )
                # 响应是 content 块列表，取第一块（文本块）的 .text
                answer = response.content[0].text

            elif isinstance(client, genai.Client):
                # Google Gemini：generate_content 接口，contents 直接收纯
                # 文本（不套 messages 结构）；不传 temperature 走端点默认
                response = client.models.generate_content(
                    model=actual_model,
                    contents=prompt,
                )
                answer = response.text

            else:  # OpenAI or compatible
                # OpenAI 及一切兼容端点（local/deepseek/自定义 provider）：
                # chat.completions 标准接口
                kwargs = {
                    "model": actual_model,
                    "messages": [{"role": "user", "content": prompt}],
                    # 新版参数名 max_completion_tokens（o 系推理模型只认它）
                    "max_completion_tokens": max_tokens,
                }

                # Only add temperature for models that support it
                # o1/o3-mini/o4-mini/o1-preview/gpt-5 等 OpenAI 推理模型不
                # 接受 temperature；用子串包含判断剔除（粗匹配但够用：
                # 常规模型名不含这些子串）
                no_temp_models = ["o1", "o3-mini", "o4-mini", "o1-preview", "gpt-5"]
                if not any(m in actual_model for m in no_temp_models):
                    kwargs["temperature"] = temperature

                response = client.chat.completions.create(**kwargs)
                # 取首个候选回复的正文
                answer = response.choices[0].message.content

            logger.info("Finish LLM process")

            # Remove think tags if present
            # 剥离推理模型的思考段：DeepSeek-R1（deepseek-reasoner）等会输出
            # <think>...</think>；按闭标签 split 取最后一段即正文。
            # 【坑】只检测 "<think>" 是否出现；若闭标签缺失，split 结果只有
            # 一段（原文本身），[-1] 恰好返回原文，行为安全
            if answer and "<think>" in answer:
                answer = answer.split("</think>")[-1].strip()

            return answer

        except Exception as e:
            # 本轮失败：记录后重试；已到最后一次则抛出让上层处理
            logger.error(f"Error attempt {attempt + 1}: {e}")
            if attempt >= 5:
                logger.error("Failed too many times")
                raise e
            time.sleep(2)

    # 理论不可达（循环内必 return 或 raise），保险起见返回 None
    return None


def get_embeddings(text: str) -> list:
    """Get embeddings using OpenAI API"""
    # 【职责】文本 → 向量，供 RAG 检索相似 checker：调用方
    #   checker_example.choose_example 用它嵌入查询内容，再与
    #   checker_database 里官方 CSA checker 的 pattern/plan embedding 做
    #   cosine 相似度排序，取 top-3 作为 few-shot 参考例子（论文 RAG
    #   知识库机制）。
    # 【坑】只支持 OpenAI 客户端（embedding 依赖 openai_key）
    if "openai" not in clients:
        raise ValueError("OpenAI client required for embeddings")

    # ada-002：与 checker_database 库内嵌入同款模型（1536 维），
    # 保证查询向量与库向量处于同一空间可直接算相似度
    response = clients["openai"].embeddings.create(
        input=text, model="text-embedding-ada-002"
    )
    # 单条输入 → data[0].embedding 即文本向量
    return response.data[0].embedding


# Backwards compatibility
# 向后兼容 shim：旧代码的 token 计数函数；len//4 是"英文约 4 字符/token"
# 的粗略近似（中文会明显低估 token 数），仅够闸门类判断、非精确计费
def num_tokens_from_string(string: str) -> int:
    """Simple token approximation"""
    # 整除 4 的近似：prompt 长度估 token 数（历史上用于成本预警）
    return len(string) // 4
