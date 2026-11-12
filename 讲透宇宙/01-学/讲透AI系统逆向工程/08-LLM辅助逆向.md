# 08 · LLM 辅助逆向

> 2024-2026 出现了一批**用 LLM 做反编译 / 语义推断**的工作——LLM4Decompile / SK²Decompile / BRIDGE / GhidraGPT。这一章讲透**LLM 在逆向工程里能做什么、不能做什么、怎么用**。
>
> 核心思路：**LLM 是反编译的"高级补丁"**，不是万能解药——它能解决传统反编译的"语义恢复"瓶颈，但不能解决"二进制不可读"瓶颈。

---

## 一、LLM 在逆向中的四种角色

| 角色 | 用法 | 工具 |
|------|------|------|
| **1. 反编译代码补全** | Ghidra/IDA pseudo-code → 可读 C | LLM4Decompile / SK²Decompile / BRIDGE |
| **2. 混淆符号重命名** | `dd.a` → `PersistenceImpl` | JADX-GPT / GhidraGPT / GhidraNLP |
| **3. 二进制语义推断** | hex dump → 字段含义 | 通用 LLM（GPT-4 / Claude / GLM）|
| **4. 数据语义对齐** | NLU patterns → scene name | 通用 LLM |

---

## 二、LLM4Decompile：反编译的 SOTA

### 2.1 背景

[LLM4Decompile](https://github.com/albertan017/LLM4Decompile) 是专门训练的"反编译 LLM"——input 是 Ghidra/IDA 反编译的伪 C 代码，output 是可读、可编译的 C 代码。

| 版本 | 时间 | 特点 | re-executability |
|------|------|------|------------------|
| LLM4Decompile 7B | 2024-06 | 基础版 | ~50% |
| LLM4Decompile 9B | 2024-10 | 提升 | ~60% |
| **LLM4Decompile 9B-v2** | 2025-10 | **SK²Decomple 两阶段** | **64.9%** |

### 2.2 两阶段反编译（SK²Decompile 2025）

```
Stage 1 (Skeleton): LLM 先恢复函数的"骨架"（控制流 + 函数签名）
    pseudo_C → skeleton_C

Stage 2 (Skin): LLM 再填充变量名 + 类型 + 注释
    skeleton_C + LLM → readable_C
```

这种分阶段策略比"一锅炖"效果好 30%+。

### 2.3 用法

```bash
# 安装
pip install transformers torch
huggingface-cli download albertan017/LLM4Decompile-9B-v2

# 反编译一个函数
python -c "
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

model_id = 'albertan017/LLM4Decompile-9B-v2'
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=torch.bfloat16, device_map='auto')

# Ghidra/IDA 拿到的伪 C
pseudo_c = '''
int sub_4821A(int a1, int a2) {
    int v3 = a1 ^ 0xdeadbeef;
    return v3 + a2;
}
'''

prompt = f'### Decompile this function:\n{pseudo_c}\n### Refactored C:\n'
inputs = tokenizer(prompt, return_tensors='pt').to(model.device)
output = model.generate(**inputs, max_new_tokens=512)
print(tokenizer.decode(output[0], skip_special_tokens=True))
"
```

### 2.4 局限

- **re-executability 不是 100%**——约 1/3 的函数反编译后无法直接编译
- **需要 GPU**（9B 模型 CPU 跑要几分钟一个函数）
- **ARM64 比 x86 差**（训练数据偏 x86）

---

## 三、BRIDGE：ARM64 → LLVM IR（2026 新工作）

[BRIDGE (ACL 2026)](https://arxiv.org/abs/2026.xxxxx) 专门做 **ARM64 → LLVM IR** 的 lifting——比通用 LLM 强 30%。

### 3.1 为什么需要 LLVM IR

- LLVM IR 是**中间表示**，比 ARM64 汇编可读得多
- LLVM IR 可以编译回 C++ / Rust / Python（多种目标）
- LLVM 生态有大量分析工具（opt / llc / bugpoint）

### 3.2 用法（学术原型）

```bash
# 拿到 ARM64 二进制(如 libtarget.so 的某个函数)
# 用 objdump 提取字节码:
objdump -d libtarget.so --disassemble=target_func > func.asm

# 喂给 BRIDGE
bridge_lift --input func.asm --output func.ll  # LLVM IR
llc func.ll -o func.c   # 转回 C
```

BRIDGE 还在学术阶段，工业落地要 2026 下半年。

---

## 四、GhidraGPT / JADX-GPT：符号重命名

### 4.1 GhidraGPT

Ghidra 插件，把每个混淆函数的 pseudo-code 喂给 GPT，让它**建议函数名 + 变量名**。

```bash
# Ghidra 里安装 GhidraGPT 插件
# 选中函数 → 右键 → "GPT Rename"
# GPT 返回:
#   sub_4821A → encrypt_AES_CBC
#   param_1 → plaintext
#   param_2 → key
#   retval → ciphertext
```

### 4.2 JADX-GPT

类似，但用于 Java 反编译。选中混淆类 → 右键 → "GPT Rename" → 类名重命名。

### 4.3 局限与陷阱

- **LLM 偶尔给错名字**——重要函数要人工核对
- **超长方法体效果差**——LLM context 不够
- **成本**——每个 API call 几分钱，重命名 1000 个函数可能 $10+

---

## 五、通用 LLM 辅助：语义推断

### 5.1 二进制字段语义推断

把 hex dump + 反汇编喂给 GPT-4 / Claude：

```python
prompt = """
我有一个 FlatBuffer 二进制文件,反汇编得到以下字段:
field[0] at +60: u32=42
field[1] at +56: u32=64 (offset to "tflite" string)
field[2] at +52: u32=80 (offset to "mobilenet_v3_small.tflite" string)
field[3] at +43: u8=10
field[4] at +36: u32=172 (offset to vector[18] of u32)
field[5] at +16: u32=64

这是模型文件的 metadata table。请推断每个字段的语义。
"""

# Claude 回答:
# field[0] = format_version (42 = some internal version code)
# field[1] = source_format ("tflite")
# field[2] = source_filename (暴露了原始 TFLite 文件)
# field[3] = quant_flag (10 = FP32, 1 = INT8, 等等)
# field[4] = layer_offset_table (18 个 layer 的偏移向量)
# field[5] = output_count (64 个输出)
```

LLM 对**有上下文线索**的字段语义推断很准——比纯靠启发式好。

### 5.2 NLU 语义对齐

把反推出的 NLU tag_pattern 喂给 LLM：

```python
prompt = """
下面是 977 个 NLU tag pattern 的样本,格式是 "scene_id_subIntent_id$":
"1_3$" → key="打开设置"
"1_5$" → key="打开 WiFi"
"2_13$" → key="亮度调到 60%"
"3_19$" → key="打电话给张三"
"3_21$" → key="接听电话"
...

我已知 scene 名(部分):
- scene 1 = system(系统设置)
- scene 2 = setting(显示设置)
- scene 3 = phone(电话)

请根据每个 scene 涉及的中文 pattern key, 推断:
1. scene 4-13 的语义名
2. 每个 subIntent 的具体含义
"""

# LLM 回答:
# scene 4 = alarm (key 含"闹钟", "timer")
# scene 5 = weather (key 含"天气", "温度")
# ...
```

LLM 对**中文语义敏感**，反推 scene 名准确率通常 80%+。

### 5.3 反汇编注释

```python
# ARM64 汇编片段
arm_asm = """
sub_4821A:
    stp x29, x30, [sp, #-16]!
    mov x29, sp
    ldr w8, [x0]          ; 加载参数 1 的前 4 字节
    eor w8, w8, #0xef     ; 异或常量
    str w8, [x1]          ; 存到参数 2 指向的地址
    ldp x29, x30, [sp], #16
    ret
"""

prompt = f"请用中文注释这段 ARM64 汇编的功能:\n{arm_asm}"

# Claude:
# 这段代码做加密:
# - 从 x0 (输入指针) 读 4 字节
# - 与常量 0xef 异或(简单 XOR 加密)
# - 写到 x1 (输出指针)
# 典型用法: simple_xor_encrypt(plaintext_ptr, ciphertext_ptr)
```

---

## 六、LLM 反逆向（防御视角）

⚠️ 2026 开始有 **LLM 反逆向**工作——厂商用 LLM 自动生成混淆代码、自动生成 false positive 诱导逆向者。

### 6.1 已知手段

- **LLM 生成 honeypot 类**（看着像核心算法，实际是诱饵）
- **LLM 生成假 API signature**（骗 JADX-GPT 给错名字）
- **LLM 加 watermark**（在权重里加水印，检测是否被复制）

### 6.2 对策

- 重要场景做**端到端对拍**（参考 [10 章 Step 5](10-攻黑盒五步法与案例索引.md)）——LLM 假信息会在对拍时暴露
- 多 LLM 交叉验证（Claude + GPT + GLM 都说一样的更可信）
- 关键决策不依赖单一 LLM 输出

---

## 七、LLM 辅助的 ROI

| 任务 | 工具 | ROI | 推荐度 |
|------|------|-----|--------|
| Native 反编译（C++）| LLM4Decompile | ⭐⭐⭐⭐ | 强烈推荐（省 80% 时间）|
| Java 重命名 | JADX-GPT | ⭐⭐⭐⭐ | 强烈推荐 |
| Native 重命名 | GhidraGPT | ⭐⭐⭐⭐ | 强烈推荐 |
| 二进制语义推断 | GPT-4 / Claude | ⭐⭐⭐ | 推荐（有启发式作 baseline）|
| NLU 语义对齐 | GPT-4 / Claude / GLM | ⭐⭐⭐⭐⭐ | 强烈推荐（中文强项）|
| 加密 key 反推 | 通用 LLM | ⭐ | 不推荐（LLM 对密码学差）|
| 整体架构推断 | 通用 LLM | ⭐⭐⭐ | 推荐（ brainstorm 用）|

---

## 八、未来方向

### 8.1 AI Agent 做完整逆向

2026 的 InspectorLab / NexusFlow 等 ML-RE agent 工作已展示——让 AI agent 自动探索二进制、生成假设、调用工具验证、迭代改进。

短期内（1-2 年）AI agent 还不能替代人工逆向，但能做"自动化第一遍扫描"。

### 8.2 二进制 embedding 相似性

用 LLM 把函数 embedding 成向量，做**跨二进制相似性搜索**——找"这个函数在另一个开源项目里有吗"。

### 8.3 LLM 4 形式化验证

把 LLM 反编译结果喂给 Lean4 / Coq 做形式化验证——保证 LLM 给的代码语义正确。

---

## 📌 下一步

- **想学 native 反编译** → [04-动态插桩](04-动态插桩-Frida.md)（拿真实数据对拍）
- **想看完整流程** → [10-攻黑盒五步法](10-攻黑盒五步法与案例索引.md)

> 📝 **本章练习**：
> 1. 用 `objdump -d` dump 你自己写的一个简单函数（如快速排序），把汇编喂给 GPT-4 / Claude，让它反推回 C。和原代码对比，准确率多少？
> 2. 在 Ghidra 里随便反编译一个开源 .so（如 libsqlite3.so），选一个混淆函数，用 LLM 试着给它重命名 + 添加注释。
> 3. **思考题**：LLM4Decompile 在 OSS-Fuzz 上达到 64.9% re-executability，剩下的 35.1% 通常是什么问题？（提示：类型推断错 / 控制流恢复错 / 库函数识别错）
