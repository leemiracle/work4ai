# 07 · 模型部署完整指南

> 本文整合了模型服务的所有部署方式：第三方 API、本地 vLLM、本地 SGLang、Docker 镜像，
> 以及部署后的验证脚本和故障排查。源材料来自 [README.md](../README.md)、`requirements.txt`、`scripts/` 和 [DeepWiki 8.x](https://deepwiki.com/zai-org/Open-AutoGLM/8-model-deployment)。

## 三种部署路径对比

| 方案 | 硬件要求 | 配置复杂度 | 适用场景 |
|------|---------|-----------|---------|
| **第三方 API**（智谱 BigModel / ModelScope）| 无（云端）| 低（仅 API key）| 快速上手、生产、无 GPU |
| **本地 vLLM** | 24GB+ VRAM GPU、~20GB 磁盘 | 高（下载模型 + 配置参数）| 研究、隐私、大批量 |
| **本地 SGLang** | 24GB+ VRAM GPU、~20GB 磁盘 | 高（同上）| 同上，VLM 内存效率更优 |

**新手强烈推荐第三方 API**（README 原话）。本地部署主要适合：数据隐私敏感、长期高频调用、或研究模型行为。

## 两个模型变体

| 模型名 | HuggingFace ID | 优化场景 |
|-------|---------------|---------|
| `AutoGLM-Phone-9B` | `zai-org/AutoGLM-Phone-9B` | 中文手机应用 |
| `AutoGLM-Phone-9B-Multilingual` | `zai-org/AutoGLM-Phone-9B-Multilingual` | 英语/多语言场景 |

两者架构相同（基于 `GLM-4.1V-9B-Thinking`），只是训练数据不同。下载地址：

- Hugging Face：`https://huggingface.co/zai-org/`
- ModelScope：`https://modelscope.cn/models/ZhipuAI/`

> **模型文件约 20GB**。推理引擎（vLLM/SGLang）首次启动会自动下载，后续从本地缓存加载。

## 方案 A：第三方 API

无需 GPU、无需下载模型，最简单。

### A1. 智谱 BigModel

| 项 | 值 |
|---|---|
| 文档 | https://docs.bigmodel.cn/cn/api/introduction |
| `--base-url` | `https://open.bigmodel.cn/api/paas/v4` |
| `--model` | `autoglm-phone` |
| `--apikey` | 在智谱平台申请 |

```bash
python main.py \
  --base-url https://open.bigmodel.cn/api/paas/v4 \
  --model autoglm-phone \
  --apikey "your-bigmodel-api-key" \
  "打开美团搜索附近的火锅店"
```

### A2. ModelScope（魔搭社区）

| 项 | 值 |
|---|---|
| 文档 | https://modelscope.cn/models/ZhipuAI/AutoGLM-Phone-9B |
| `--base-url` | `https://api-inference.modelscope.cn/v1` |
| `--model` | `ZhipuAI/AutoGLM-Phone-9B` |
| `--apikey` | 在 ModelScope 平台申请 |

```bash
python main.py \
  --base-url https://api-inference.modelscope.cn/v1 \
  --model ZhipuAI/AutoGLM-Phone-9B \
  --apikey "your-modelscope-api-key" \
  "打开美团搜索附近的火锅店"
```

### 通过环境变量配置（推荐）

避免每次敲长命令：

```bash
export PHONE_AGENT_BASE_URL="https://open.bigmodel.cn/api/paas/v4"
export PHONE_AGENT_MODEL="autoglm-phone"
export PHONE_AGENT_API_KEY="your-key"

# 之后只需
python main.py "打开美团"
```

## 方案 B：本地 vLLM 部署

### 硬件要求

| 组件 | 最低 | 推荐 |
|------|------|------|
| GPU | NVIDIA CUDA GPU | A100 / A6000 / 4090 (24GB+) |
| VRAM | 20GB | 24GB+ |
| 系统内存 | 32GB | 64GB+ |
| 磁盘 | 25GB 空闲 | 50GB+ SSD |
| CUDA | 11.8+ | 12.0+ |

### 安装 vLLM

```bash
# 方式 1: pip
pip install vllm>=0.12.0
pip install -U transformers --pre   # 升级到 5.0.0rc0+,依赖冲突可忽略

# 方式 2: Docker(推荐,环境隔离)
docker pull vllm/vllm-openai:v0.12.0
# 进入容器后执行
pip install -U transformers --pre
```

### 启动 vLLM 服务

**这些参数必须严格遵循**，否则模型行为异常：

```shell
python3 -m vllm.entrypoints.openai.api_server \
 --served-model-name autoglm-phone-9b \
 --allowed-local-media-path / \
 --mm-encoder-tp-mode data \
 --mm_processor_cache_type shm \
 --mm_processor_kwargs "{\"max_pixels\":5000000}" \
 --max-model-len 25480 \
 --chat-template-content-format string \
 --limit-mm-per-prompt "{\"image\":10}" \
 --model zai-org/AutoGLM-Phone-9B \
 --port 8000
```

切到 Multilingual 模型只需把 `--model` 改成 `zai-org/AutoGLM-Phone-9B-Multilingual`。

### 参数详解

| 参数 | 作用 | 为什么这个值 |
|------|------|-------------|
| `--served-model-name` | OpenAI API 暴露的模型名 | 必须与客户端 `--model` 一致 |
| `--allowed-local-media-path /` | 允许从文件系统加载图片 | 多模态必需 |
| `--mm-encoder-tp-mode data` | 视觉编码器张量并行模式 | VLM 优化 |
| `--mm_processor_cache_type shm` | 视觉预处理缓存类型 | 共享内存提速 |
| `--mm_processor_kwargs '{"max_pixels":5000000}'` | 图片最大像素 | 容纳 1080×2400 截图（约 250 万像素）|
| `--max-model-len 25480` | 最大 token 数（文本+图片嵌入）| 容纳多张截图+历史 |
| `--chat-template-content-format string` | chat template 内容格式 | 与模型训练一致 |
| `--limit-mm-per-prompt '{"image":10}'` | 每个 prompt 最多图片数 | 实际 Agent 每步只发 1 张 |
| `--port 8000` | HTTP 端口 | 默认值 |

启动成功标志：日志出现 `Uvicorn running on http://0.0.0.0:8000`。

## 方案 C：本地 SGLang 部署

### 安装 SGLang

```bash
# 方式 1: pip
pip install sglang>=0.5.6.post1
pip install -U transformers --pre

# 方式 2: Docker
docker pull lmsysorg/sglang:v0.5.6.post1
# 进入容器后执行
pip install nvidia-cudnn-cu12==9.16.0.29
```

### 启动 SGLang 服务

```shell
python3 -m sglang.launch_server \
 --model-path zai-org/AutoGLM-Phone-9B \
 --served-model-name autoglm-phone-9b \
 --context-length 25480 \
 --mm-enable-dp-encoder \
 --mm-process-config '{"image":{"max_pixels":5000000}}' \
 --port 8000
```

### vLLM vs SGLang 对照

| 维度 | vLLM | SGLang |
|------|------|--------|
| 成熟度 | 稳定，社区大 | 较新，活跃开发 |
| VLM 内存效率 | 良好 | **优化更好**（可能省 VRAM）|
| 吞吐量 | 高 | 高 |
| 参数语法 | 较冗长 | 较简洁 |
| Docker 支持 | 官方镜像 | 官方镜像 |
| 视觉编码器并行 | `--mm-encoder-tp-mode` | `--mm-enable-dp-encoder` |
| 多模态配置 | `--mm_processor_kwargs` (JSON) | `--mm-process-config` (JSON) |

两者都生产可用。**SGLang 对 VLM 内存效率更优**，vLLM 社区更大。

## 部署后验证

### 用项目自带脚本

项目提供**中英文两个验证脚本**，功能一致，只是测试消息语言不同：

| 脚本 | 默认测试消息 | 测试场景 |
|------|------------|---------|
| `scripts/check_deployment_cn.py` | `scripts/sample_messages.json` | 中文 prompt + 小红书比价任务 |
| `scripts/check_deployment_en.py` | `scripts/sample_messages_en.json` | 英文 prompt + 同类任务 |

```bash
# 中文验证
python scripts/check_deployment_cn.py \
  --base-url http://localhost:8000/v1 \
  --model autoglm-phone-9b

# 英文验证
python scripts/check_deployment_en.py \
  --base-url http://localhost:8000/v1 \
  --model autoglm-phone-9b
```

两份 `sample_messages.json` 都包含完整 system prompt + 一张手机截图（base64）+ 任务指令，模拟真实 Agent 调用场景。

### 验证脚本工作原理

`scripts/check_deployment_cn.py`（115 行）做的事：

1. 解析 CLI 参数（`--base-url` / `--model` / `--apikey` / `--messages-file` 等）
2. 加载 `scripts/sample_messages.json` —— 内含完整 system prompt + 一张小红书截图（base64）+ 任务"这个牌子的洗发水，去京东和淘宝上比价，选择最便宜的平台下单"
3. 用 `openai.OpenAI` 发**非流式** chat completion 请求（注意：与 `ModelClient.request` 的 `stream=True` 不同）
4. 打印模型回复 + token 统计（prompt_tokens / completion_tokens / total_tokens）
5. 异常时打印错误类型 + 消息 + 排查提示

### 全部 CLI 参数

| 参数 | 类型 | 必需 | 默认 | 说明 |
|------|------|------|------|------|
| `--base-url` | str | ✅ | — | API 地址 |
| `--model` | str | ✅ | — | 模型名 |
| `--apikey` | str | ❌ | `EMPTY` | API 密钥 |
| `--messages-file` | str | ❌ | `scripts/sample_messages.json` | 测试消息 JSON |
| `--max-tokens` | int | ❌ | `3000` | 最大生成 token |
| `--temperature` | float | ❌ | `0.0` | 采样温度 |
| `--top_p` | float | ❌ | `0.85` | nucleus sampling |
| `--frequency_penalty` | float | ❌ | `0.2` | 频率惩罚 |

### 期望输出

```
开始测试模型推理...
Base URL: http://localhost:8000/v1
Model: autoglm-phone-9b
================================================================================

模型推理结果:
================================================================================
<think>用户想要比较这个洗发水在京东和淘宝上的价格...
我需要：
1. 先启动京东app，搜索这个洗发水
2. 查看京东的价格
3. 再启动淘宝app，搜索这个洗发水
4. 查看淘宝的价格
5. 比较价格后，选择最便宜的京东或淘宝下单

首先，我需要从当前的小红书界面退出，然后启动京东app。</think>
<answer>do(action="Launch", app="京东")</answer>
================================================================================

统计信息:
  - Prompt tokens: 1245
  - Completion tokens: 156
  - Total tokens: 1401
```

**判定标准**：
- ✅ **正常**：thinking 有逻辑（多步规划），action 是合法的 `do(...)` 或 `finish(...)` 格式
- ❌ **异常**：thinking 很短（一两句）、出现乱码、action 无法解析 —— 说明部署失败

### 用自定义测试场景

```bash
# 写自己的测试消息
cat > my_test.json <<EOF
[
  {"role": "system", "content": "你是手机操作助手..."},
  {"role": "user", "content": [{"type": "text", "text": "打开微信"}]}
]
EOF

python scripts/check_deployment_cn.py \
  --base-url http://localhost:8000/v1 \
  --model autoglm-phone-9b \
  --messages-file my_test.json
```

### 手动 curl 探活

```bash
# 模型列表
curl http://localhost:8000/v1/models

# 健康检查
curl http://localhost:8000/health

# 简单 chat
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"autoglm-phone-9b","messages":[{"role":"user","content":"Hi"}],"max_tokens":5}'
```

## 故障排查

### 模型下载失败

```bash
# 手动下载
huggingface-cli download zai-org/AutoGLM-Phone-9B

# 指定缓存位置
export HF_HOME=/path/to/cache
```

### CUDA OOM（显存不足）

| 降配方案 | 命令 |
|---------|------|
| 减小上下文 | `--max-model-len 8192`（最低，影响多步记忆）|
| 关其他 GPU 进程 | `nvidia-smi` 查占用 |
| 多卡张量并行 | `--tensor-parallel-size 4`（vLLM）/ `--tp-size 4`（SGLang）|

预期 VRAM 占用：基模 ~18-20GB，带上下文峰值 ~22-24GB。

### 启动卡住

- 确认 `transformers >= 5.0.0rc0`：`pip show transformers`
- CUDA/cuDNN 版本匹配推理引擎要求
- 磁盘空间足够（模型缓存 ~20GB）

### 连接被拒

```bash
# 1. 确认服务在跑
curl http://localhost:8000/health

# 2. 检查端口
ss -tlnp | grep 8000

# 3. 改用 127.0.0.1
python main.py --base-url http://127.0.0.1:8000/v1 ...
```

### 远程服务器部署

```bash
# 服务器端启动 vLLM(监听所有网卡)
python3 -m vllm.entrypoints.openai.api_server ... --host 0.0.0.0 --port 8000

# 客户端
python main.py --base-url http://SERVER_IP:8000/v1 ...
```

**注意**：开放 8000 端口要检查防火墙和网络安全组。

## 性能调优

### 多 GPU 张量并行

```bash
# vLLM: 4 卡并行
python3 -m vllm.entrypoints.openai.api_server ... --tensor-parallel-size 4

# SGLang: 4 卡并行
python3 -m sglang.launch_server ... --tp-size 4
```

模型权重跨卡切分，提升吞吐并支持更大 batch。

### 批处理配置（vLLM）

```bash
--max-num-batched-tokens 8192   # 单 batch 最大 token
--max-num-seqs 256              # 最大并发序列
```

SGLang 自动管理批处理。

### 监控 GPU 利用率

```bash
# 实时监控
watch -n 1 nvidia-smi

# 若 GPU 利用率低,瓶颈可能在 CPU 预处理(图片解码)或网络 IO
```

## OpenAI 兼容端点

部署后暴露的 HTTP 端点（vLLM/SGLang 一致）：

| 端点 | Method | 用途 |
|------|--------|------|
| `/v1/chat/completions` | POST | 提交 chat 请求（支持图片）|
| `/v1/models` | GET | 列出可用模型 |
| `/health` | GET | 健康检查 |

`ModelClient`（phone_agent/model/client.py（待写/未落盘））只用 `/v1/chat/completions`。

## 与 PhoneAgent 集成

部署验证通过后，配置 PhoneAgent 使用：

```python
from phone_agent import PhoneAgent
from phone_agent.agent import AgentConfig
from phone_agent.model import ModelConfig

agent = PhoneAgent(
    model_config=ModelConfig(
        base_url="http://localhost:8000/v1",  # 或远程 IP
        model_name="autoglm-phone-9b",
        api_key="EMPTY",                       # 本地部署默认 EMPTY
    ),
    agent_config=AgentConfig(max_steps=50),
)
print(agent.run("打开美团搜索火锅"))
```

## 部署清单（快速核对）

新手按这个清单一步步核对：

- [ ] 选定方案（A/B/C）
- [ ] 方案 A：申请到 API key
- [ ] 方案 B/C：GPU 满足 24GB+ VRAM
- [ ] 方案 B/C：安装 vLLM 或 SGLang
- [ ] 方案 B/C：升级 `transformers` 到 5.0.0rc0+
- [ ] 启动服务，看到 `Uvicorn running` 日志
- [ ] `curl http://localhost:8000/health` 返回 200
- [ ] 跑 `scripts/check_deployment_cn.py` 看到 thinking + 合法 action
- [ ] 配置 `PHONE_AGENT_BASE_URL` 等环境变量
- [ ] `python main.py "打开微信发消息给文件传输助手：部署成功"` 端到端验证

## 下一步

- 部署完成 → [01-entry-cli.md](01-entry-cli.md) 学 CLI 用法
- 想理解模型客户端 → [05-model-client.md](05-model-client.md)
- 想做开发 → [08-development.md](08-development.md)
- 部署踩坑 → 本文「故障排查」小节

---
