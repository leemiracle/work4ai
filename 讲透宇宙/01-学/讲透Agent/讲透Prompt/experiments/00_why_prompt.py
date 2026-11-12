"""
实验 00 — 为什么 Prompt 是控制信号: 条件概率视角
对应文档: 讲透Prompt/00-为什么Prompt是控制信号.md
核心结论:
  1. LLM 是条件概率模型 P(输出|输入), Prompt 就是那个【条件】—— 改 prompt = 改输出分布
  2. 同一模型, 不同 prompt 激发完全不同的输出(本实验用小 trigram LM 演示)
  3. Prompt 工程本质: 在固定模型下, 找最优 prompt 使输出符合需求 —— 用自然语言"编程"模型
  注: 小 trigram 只演示'prompt作为条件'; 真实 LLM 的指令/例子/CoT 是更复杂的条件(后几篇)
跑法: python3 -u 00_why_prompt.py
"""
from collections import defaultdict, Counter

def P(*a): print(*a, flush=True)

# 训练一个迷你 trigram 语言模型(模拟一个"已训练好的固定模型")
text = ("cats are animals . dogs are animals . fish are animals . "
        "cars are machines . planes are machines . trains are machines . "
        "roses are plants . trees are plants . grass are plants .")
words = text.split()
tri = defaultdict(Counter)
for i in range(len(words) - 2):
    tri[(words[i], words[i+1])][words[i+2]] += 1

def dist(prompt):  # 给定 prompt(条件), 返回下一个词的分布
    pw = prompt.split()
    d = tri[(pw[-2], pw[-1])]
    t = sum(d.values())
    return {w: round(c/t, 2) for w, c in d.most_common(4)}

P("="*60); P("Part 1: Prompt 是条件 —— 改 prompt = 改输出分布"); P("="*60)
P("同一个固定模型(trigram), 不同 prompt 激发不同输出:")
for prompt in ["cats are", "cars are", "roses are", "dogs are"]:
    P("  P(next | '%s') = %s" % (prompt, dist(prompt)))
P("==> 模型权重没变, 只因 prompt(条件)不同, 输出分布完全不同.")
P("    这就是 Prompt 的本质: 它是 P(输出|输入) 里的那个'输入/条件'.\n")

P("="*60); P("Part 2: Prompt 的三要素 (指令 + 上下文 + 例子)"); P("="*60)
P("真实 Prompt 不只是一个 prefix, 它由三部分组成:")
P("  ① 指令(Instruction): '把句子翻译成英文' —— 定任务")
P("  ② 上下文(Context):   背景信息/RAG检索到的文档 —— 给知识")
P("  ③ 例子(Examples):    '输入A→输出B' —— 示范格式/模式 (Few-shot)")
P("三者组合成条件, 控制 LLM 的输出分布. Prompt 工程就是调这三者.\n")

P("="*60); P("Part 3: 为什么说 Prompt 是'用自然语言编程'"); P("="*60)
P("传统编程: 代码 → 编译器 → 确定输出")
P("Prompt :  自然语言 → LLM → 概率输出")
P("相似: 都是用'语言'描述需求, 让'机器'执行.")
P("不同: 代码精确确定; Prompt 是概率的, 需要调试(就像调代码).")
P("==> Prompt 工程师 = 用自然语言写'程序'的人. 模型是解释器, prompt 是代码.")
P("    好的 prompt 像好代码: 清晰、无歧义、给足必要信息.\n")

P("="*60); P("诚实声明"); P("="*60)
P("本实验用 trigram 只演示'prompt 改变条件概率'这个最底层原理.")
P("真实 Prompt 工程(指令遵循/Few-shot ICL/CoT)依赖大模型的涌现能力,")
P("小 trigram 做不到(它只看2词统计). 后续篇用文献证据+大模型现象讲透.")
