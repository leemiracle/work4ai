# 精讲：model.py — 模型架构注册中心

> 位置：`python/mlc_llm/model/model.py` · 750 行 · 复杂度 complex · 扇出 126（全仓最高）
> 图谱标签：registry / entry-point / model-registry / data-model

## 角色定位

model.py 是 MLC-LLM 的「模型目录本」。编译流程第一步——把 HuggingFace 模型名（`llama`/`qwen3`/`deepseek_v2`...）翻译成实现类——完全依赖 `MODELS` 字典。convert_weight 与 compile 都以它为唯一查找入口：**没注册的架构在 MLC 里就不存在**。

设计哲学是纯声明式：750 行几乎没有逻辑分支，只有 import + 数据类 + 47 条注册项，聪明之处全在 `Model` dataclass 的类型合同里。

## 内部结构

**`Model` dataclass——架构四要素合同**：

- `name`：架构标识（对应 HF config.json 的 model_type）
- `config`：配置类，约定有 `from_file(path)` 类方法解析 config.json
- `model`：`Callable[[ModelConfig], nn.Module]`——构建 TVM nn 模块（计算图定义）
- `source: Dict[str, FuncGetExternMap]`：权重来源映射（键如 huggingface-torch/safetensor/awq），值把 MLC 参数名映射到外部权重名
- `quantize: Dict[str, FuncQuantization]`：量化装配表，由工厂批量生成
- `model_task` + `embedding_metadata`：区分 chat 与 embedding 模型；`__post_init__` 强制校验——embedding 必须带元数据（pooling/归一化），chat 禁止携带

**MODELS 字典 47 条目**：import 41 个架构包（每包一对 `*_model.py`+`*_loader.py`），含别名复用——`deepseek_v3` 直接复用 deepseek_v2 实现只多开 block_scale、`gemma3_text`/`qwen3_5_text` 是纯文本版、`bert-bge` 复用 BertModel 换 loader。

**量化工厂**：每条目的 quantize 来自 `make_quantization_functions(ModelClass, supports_awq=..., supports_ft_quant=...)`——支持开关逐模型声明（Gemma 系全关 ft_quant），是「能力矩阵」式声明编程。

## 外部连接

- **被依赖**：`model/__init__.py` re-export；interface 层 gen_config/convert_weight/compile 按名查表
- **依赖**（126 条 import）：41 个架构包 + `loader/`（ExternMapping）+ `quantization/`（工厂）+ `tvm.relax.frontend.nn` 类型系统

## 数据流

```
用户: mlc_llm compile --model Qwen/Qwen3-8B
  ↓ config.json 的 model_type = "qwen3" → MODELS["qwen3"]
  ↓ config 要素: Config.from_file(...)
  ↓ quantize 要素: quantize["q3f16_1"](config)
  │    └─ 工厂内部 ModelClass(config) 建图 + 量化变换 → QuantizeMapping
  ↓ source 要素(convert_weight): source["huggingface-safetensor"]
       └─ MLC 参数名 → HF 张量名，逐条搬运+量化
```

即：**model 定义「图长什么样」，loader 定义「权重从哪来」，quantization 定义「权重变成什么样」**，三者在注册表汇合。

## 设计决策

1. **显式 import 而非插件动态发现**：换 IDE 可跳转 + CI 静态查四要素齐全；新架构=新目录+两行 import+一条目。
2. **注册时校验合同**：embedding 元数据与 task 互斥检查在 `__post_init__` 报错——错误左移到 import 时刻。
3. **别名复用而非继承**：deepseek_v3/V2 共享实现，差异在表里声明，避免继承悄悄改坏前代。
4. **750 行单文件代价**：扇出 126 意味着任何架构包 import 错误都引爆注册中心——各包 `__init__.py` 必须极薄。

## 新人提示

- **加新架构**：复制最像的目录（推荐 `llama/` 起步）改 config+权重映射，本文件加三行；官方 `docs/compilation/define_new_models.rst` 即此流程。
- **排查「不支持某量化」**：先查条目的 supports_* 开关，别急着改 quantization/ 实现。
- **找实现**：永远从 MODELS 顺 import 跳，别 glob 目录——别名（deepseek_v3）会骗你。
- **embedding 模型**：qwen3-embedding（decoder+last pooling）与 bert（encoder+cls pooling）是两个参照系。
