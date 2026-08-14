"""
实验 01 — 检索数学: 相似度度量 + embedding(词面vs语义) + ANN 索引
对应文档: 讲透RAG/01-检索数学.md
核心结论:
  1. 相似度三选一: 余弦(主流, 只看方向) / 点积(受模长影响) / 欧氏(看绝对距离)
  2. TF-IDF 是【词面匹配】: 词不重叠就匹配不到(汽车↔轿车 匹配差)
     神经 embedding 是【语义匹配】: 同义/近义词映到相近向量(下篇实战)
  3. 大数据精确检索 O(n) 太慢, 用 ANN(HNSW/IVF) 近似检索降到 O(log n)
跑法: python3 -u 01_retrieval_math.py
"""
import numpy as np, time
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.neighbors import NearestNeighbors

def P(*a): print(*a, flush=True)

# ============ Part 1: 三种相似度度量 ============
P("="*60); P("Part 1: 余弦 vs 点积 vs 欧氏"); P("="*60)
v1=np.array([1.,2,3]); v2=np.array([2.,4,6]); v3=np.array([6.,4,2])
P("v1=[1,2,3]  v2=[2,4,6](=2·v1,同向)  v3=[6,4,2](不同向)")
def cos(a,b): return a@b/(np.linalg.norm(a)*np.linalg.norm(b))
P("\n%12s%12s%12s%12s"%("对","余弦","点积","欧氏距离"))
for na,a,nb,b in [("v1",v1,"v2",v2),("v1",v1,"v3",v3),("v2",v2,"v3",v3)]:
    P("%12s%12.3f%12.0f%12.3f"%(na+"-"+nb, cos(a,b), a@b, np.linalg.norm(a-b)))
P("==> v1,v2 同向: 余弦=1(最相似), 但欧氏距离却最大(模不同)!")
P("    余弦只看【方向】不看模长 —— 这就是 RAG 用余弦的原因: 语义相似=方向相近.\n")

# ============ Part 2: TF-IDF 词面匹配的局限 ============
P("="*60); P("Part 2: TF-IDF 只懂词面, 不懂语义"); P("="*60)
docs=["小轿车最高时速200公里","SUV很受家庭欢迎","汽车需要定期保养","我家养了一只猫"]
vec=TfidfVectorizer(analyzer='char_wb',ngram_range=(2,2)); X=vec.fit_transform(docs)
for q in ["轿车价格"," automobiles","宠物吃什么"]:
    qv=vec.transform([q]); sims=cosine_similarity(qv,X).flatten()
    P("Q: %-16s → "%q + "  ".join("[%d:%.2f]"%(i,s) for i,s in enumerate(sims)))
P("==> '轿车'和'汽车'语义同义, 但 TF-IDF 词面不重叠 → 相似度低.")
P("    神经 embedding(bge/m3e)能把同义词映到相近向量, 弥补词面局限(实战用).")
P("    所以真实 RAG 用神经 embedding; TF-IDF 适合关键词精确匹配(如产品编号).\n")

# ============ Part 3: ANN 近似最近邻 (大数据检索) ============
P("="*60); P("Part 3: 暴力检索 O(n) vs ANN 索引 O(log n)"); P("="*60)
for N in [1000, 10000, 100000]:
    d=128; X=np.random.randn(N,d).astype('float32'); q=np.random.randn(d).astype('float32')
    # 暴力: 算 q 与全部 N 个的点积
    t0=time.perf_counter()
    _=(X@q).argmax(); t_brute=time.perf_counter()-t0
    # ANN: ball_tree 索引 (建一次, 查询快)
    nbrs=NearestNeighbors(algorithm='ball_tree').fit(X)
    t0=time.perf_counter(); nbrs.kneighbors([q],n_neighbors=1); t_ann=time.perf_counter()-t0
    P("N=%6d: 暴力 %.4fs, ANN(ball_tree) %.4fs (建索引后查询)"%(N,t_brute,t_ann))
P("==> N 小时 ANN 占优; 但 d=128 高维下 ball_tree 会遇【维度灾难】, 大 N 时未必快于")
P("    numpy 优化的暴力(本实验 N=10万就是例子). 所以工业界用 HNSW(图索引, 高维鲁棒)")
P("    或 faiss IVF + 专门向量数据库(Milvus/Qdrant), 而非 sklearn 的 ball_tree.")
