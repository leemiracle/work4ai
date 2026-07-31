"""
实验 01 — Few-shot 与 In-Context Learning (ICL)
对应文档: 讲透Prompt/01-Few-shot与ICL.md
核心结论:
  1. Few-shot: prompt 里放几个'输入→输出'例子, 模型跟随例子模式处理新输入
  2. ICL 的奇迹: 模型从例子学新任务, 但【不更新任何权重】(区别于微调)
  3. ICL 是大模型的涌现能力: 小模型不会, GPT-3(13B+) 突然会
  4. 机制(Mechanistic): 大模型内部形成'induction head', 做前缀匹配式推理
  注: 本实验用'最近邻'类比模拟 ICL(从例子找最相似的); 真实 LLM 的 ICL 更复杂
跑法: python3 -u 01_few_shot.py
"""
from collections import Counter

def P(*a): print(*a, flush=True)

def chars(s): return set(s.replace(" ",""))
def sim(a, b):  # Jaccard 字符相似度
    A, B = chars(a), chars(b)
    return len(A & B) / max(len(A | B), 1)

# 模拟 ICL: 从 prompt 的例子里找最相似的, 用其标签(最近邻类比)
def icl_predict(query, examples, k=3):
    ranked = sorted(examples, key=lambda e: -sim(query, e[0]))[:k]
    votes = Counter(e[1] for e in ranked)
    winner, cnt = votes.most_common(1)[0]
    return winner, cnt/k

P("="*60); P("Part 1: Few-shot —— prompt 放例子, 跟随模式"); P("="*60)
# 一个情感分类任务的 few-shot prompt
examples = [("好看","正面"),("难看","负面"),("精彩","正面"),
            ("无聊","负面"),("糟糕","负面"),("漂亮","正面"),("难吃","负面")]
P("Few-shot prompt 里的例子:")
for x,y in examples: P("  '%s' → %s"%(x,y))
P("\n模型对新输入的判断(从例子里找最相似的):")
for q in ["精美","难听","出色","乏味"]:
    pred, conf = icl_predict(q, examples)
    P("  '%s' → %s (置信%.0f%%)"%(q, pred, conf*100))
P("==> 模型没见过'精美/难听', 但从相似例子推断出情感. 这就是 ICL 的核心.\n")

P("="*60); P("Part 2: ICL 的奇迹 —— 不更新权重学新任务"); P("="*60)
P("微调: 用数据更新权重 → 学会任务(慢, 永久改变, 需训练)")
P("ICL : 把例子塞进 prompt → 当场学会(快, 临时, 推理完就忘)")
P("对比:")
P("  微调: 改模型参数(几千~几万步训练) → 任务能力永久写入权重")
P("  ICL :  不改任何参数(一次前向) → 能力只在当前 prompt 上下文里")
P("==> ICL 是'用上下文代替梯度'. 同一个模型, 塞不同例子就能做不同任务.\n")

P("="*60); P("Part 3: ICL 是涌现能力 —— 小模型不会"); P("="*60)
P("GPT-3 论文(2020)的关键发现:")
P("  小模型(<6B)的 Few-shot 效果接近随机(学不会从例子)")
P("  模型到 ~13B 后, Few-shot 准确率突然飙升 —— ICL 是涌现能力")
P("(呼应 讲透基础模型/03-涌现能力: 平滑的 loss 下, 某能力在阈值后突现)")
P("\n机制解释(Olsson 2022, induction head):")
P("  大模型内部形成'归纳头'电路: 做前缀匹配——")
P("  看到 prompt 里'[A]→[B]', 后续遇到[A]就倾向输出[B].")
P("  这个电路在训练中突然形成, 一旦形成 ICL 就出现.\n")

P("="*60); P("诚实声明"); P("="*60)
P("本实验用'最近邻'类比模拟 ICL(从例子找最相似). 真实 LLM 的 ICL 不是简单最近邻,")
P("而是内部多层注意力的复杂计算(induction head). 但'从上下文例子学'的核心一致.")
P("Few-shot 的真实威力要在大模型上才显现(小模型不会真 ICL).")
