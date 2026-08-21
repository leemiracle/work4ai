"""
实验 04 — RAG 评估: faithfulness(忠实度) + relevance(相关性)
对应文档: 讲透RAG/04-评估.md
核心结论:
  1. RAG 评估不止看"答案对不对", 而是拆成: 检索质量 + 生成质量
  2. faithfulness(忠实度): 答案的事实是否都能在检索文档中找到(防幻觉)
  3. relevance(相关性): 答案是否切题回答了问题
  4. 本实验用 token 重叠近似(无LLM裁判); 真实 RAGAS 用 LLM-as-Judge
跑法: python3 -u 04_evaluation.py
"""
def P(*a): print(*a, flush=True)
def chars(s): return set(s.replace("，","").replace("。","").replace(" ",""))

def overlap(a, b):  # 字符重叠率
    A, B = chars(a), chars(b)
    return len(A & B) / max(len(A), 1)

def faithfulness(answer, docs):
    """答案字符有多少能在文档找到(近似忠实度, 防幻觉)"""
    doc_chars = chars("".join(docs))
    ans_chars = chars(answer)
    return len(ans_chars & doc_chars) / max(len(ans_chars), 1)

def relevance(answer, query):
    """答案与问题的相关度(近似)"""
    return overlap(answer, query)

docs = ["DeepSeek-V3 于2024年12月发布, 总参数671B, 采用MoE架构, 每token激活37B"]
query = "DeepSeek V3 有多少参数?"

P("="*60); P("RAG 评估: faithfulness(忠实) + relevance(相关)"); P("="*60)
P("检索文档: %s" % docs[0])
P("问题: %s\n" % query)

cases = {
    "✅好答案(忠于文档+切题)": "DeepSeek-V3 有 671B 总参数",
    "❌幻觉(编造数字)":        "DeepSeek-V3 有 175B 参数, 2023年发布",
    "❌跑题(答非所问)":         "DeepSeek-V3 采用 MoE 架构, 每token激活37B",
}
P("%-26s%12s%12s%12s"%("案例","忠实度","相关度","综合"))
for name, ans in cases.items():
    f = faithfulness(ans, docs)
    r = relevance(ans, query)
    P("%-26s%12.2f%12.2f%12.2f"%(name, f, r, f*r))
P("\n==> 好答案: 忠实+相关都高. 幻觉: 忠实度低(175B/2023编造). 跑题: 相关度低.")
P("\n真实 RAGAS 用 LLM-as-Judge(更准但贵):")
P("  faithfulness: 让LLM逐句检查'答案每句能否被文档支撑'")
P("  answer_relevance: 让LLM判断'答案是否完整回答了问题'")
P("  context_precision: 检索的文档有几条真相关(检索质量)")
P("  context_recall:    答案需要的信息是否都被检索到")
P("\n==> RAG 要分别评【检索】和【生成】, 不能只看最终答案. ")
P("    检索差→召回不全; 生成差→忠实度低(幻觉). 定位瓶颈才能优化.")
