# =============================================================================
# [模块定位] few-shot 示例知识库 + RAG 检索器：装载 checker_database/（121 个子
#            目录 = 118 个官方 CSA checker + 3 个端到端 few-shot 例子 double-free /
#            null-ptr-derefence / uninit，均预计算 pattern/plan 两路 embedding），
#            并按语义相似度为新查询挑选最相近的示例。
#
# [论文映射] KNighter §3.1 Algorithm 1 的 few-shot 支撑层：
#   - 论文 §4 Few-shot examples 的三个端到端例子（40 人时打磨的 double-free /
#     null-ptr-derefence / uninit）本体位于 prompt_template/examples/，由
#     src/agent.py 静态注入各 prompt（default_checker_examples）；本模块加载的
#     checker_database/ 下同名三目录使这三例同时进入 RAG 检索池。
#   - choose_example 实现论文的 RAG 知识库检索（速查卡"RAG 知识库：118 个官方
#     CSA checker + ada-002 embedding → checker_database/*/{pattern,plan}_embedding.pt"）：
#     pattern2plan（§3.1.2）按 type="pattern" 检索、plan2checker（§3.1.3）按
#     type="plan" 检索（agent.py 在 sample_examples=True 时启用）。
#
# [管线角色] 上游：checker_gen.py 生成循环开始时调 init_example() 一次性全量加载；
#            下游：agent.py 的 pattern2plan / plan2checker prompt 装配；embedding
#            依赖 src/model.py get_embeddings（OpenAI text-embedding-ada-002）。
#
# [依赖与坑] 1) torch.load 反序列化 .pt 为 1-D tensor，与查询向量在 dim=0 上做
#            cosine；查询侧 get_embeddings 返回 list 须 torch.tensor() 包装。
#            2) 平级导入 `from model import get_embeddings`（无包结构）——要求以
#            src/ 为 CWD 运行，否则 ImportError。
#            3) load_example_from_dir 不读 patch.md（patch 硬编码 ""）：RAG 条目
#            只用于 pattern→plan / plan→checker 中间态示例，不带 patch 输入。
#            4) 顶部导入的 pydantic.BaseModel 实际未被使用（ExampleChecker 是
#            普通类）；print(pattern_embedding) 为调试遗留（装载 121 条即刷屏
#            121 次）。
# =============================================================================
from pathlib import Path  # 路径操作：定位 checker_database 知识库根目录

import torch  # 张量运算（cosine_similarity）与 .pt embedding 文件反序列化
from pydantic import BaseModel  # （未使用）ExampleChecker 实为普通类，此导入是残留

from model import get_embeddings  # 查询文本 → ada-002 向量（平级导入，要求 CWD=src/）

# RAG 知识库根目录：<仓根>/checker_database（__file__ 即 src/checker_example.py，
# parent.parent 上溯两级到仓根）；121 个子目录每目录含 pattern.md / plan.md /
# checker.cpp / {pattern,plan}_embedding.pt
example_dir = Path(__file__).parent.parent / "checker_database"
example_list = []  # 全局知识库缓存：init_example() 填充的 List[ExampleChecker]（agent.py 读取）


# ----------------------------------------------------------------------------
# ExampleChecker：RAG 知识库的单条条目——一个 checker 的 pattern/plan/checker
# 源码三件套 + 预计算的两路 ada-002 embedding（1-D tensor）。
# 论文语义：§3.1 各 agent prompt 的 few-shot 示例载体；两路 embedding 分别服务
# pattern2plan（按 pattern 相似度检索示例的 plan）与 plan2checker（按 plan
# 相似度检索示例的 checker 源码）。
# ----------------------------------------------------------------------------
class ExampleChecker:
    def __init__(
        self,
        patch: str,  # 对应 bug-fix patch（知识库条目固定为空串，见 load_example_from_dir）
        pattern: str,  # pattern.md 内容：该 checker 防范的 bug 模式描述（§3.1.1 产物形态）
        plan: str,  # plan.md 内容：实现计划——用哪些 CSA 回调、维护什么状态（§3.1.2 产物形态）
        checker_code: str,  # checker.cpp 内容：完整 CSA checker 源码（§3.1.3 产物形态）
        pattern_embedding: torch.Tensor,  # pattern 文本的 ada-002 向量（pattern2plan 检索侧）
        plan_embedding: torch.Tensor,  # plan 文本的 ada-002 向量（plan2checker 检索侧）
    ):
        self.patch = patch  # 空串占位（RAG 示例不携带 patch 输入）
        self.pattern = pattern  # bug 模式描述
        self.plan = plan  # 实现计划
        self.checker_code = checker_code  # checker 源码
        self.pattern_embedding = pattern_embedding  # pattern 向量缓存
        self.plan_embedding = plan_embedding  # plan 向量缓存

    @staticmethod
    def load_example_from_dir(checker_dir: str):
        # 从单个 checker 目录装载一条知识库条目（三份文本 + 两个 .pt 向量）
        checker_dir = Path(checker_dir)
        pattern = (checker_dir / "pattern.md").read_text()  # bug 模式描述
        plan = (checker_dir / "plan.md").read_text()  # 实现计划
        checker_code = (checker_dir / "checker.cpp").read_text()  # checker 源码

        # 预计算向量离线反序列化（.pt 由建库脚本生成，运行时零 embedding API 开销）
        pattern_embedding = torch.load(checker_dir / "pattern_embedding.pt")
        plan_embedding = torch.load(checker_dir / "plan_embedding.pt")
        print(pattern_embedding)  # 调试遗留：每装载一条打印一次 pattern 向量

        # patch 置空串：RAG 条目只作为 pattern→plan / plan→checker 的中间态示例
        return ExampleChecker(
            patch="",
            pattern=pattern,
            plan=plan,
            checker_code=checker_code,
            pattern_embedding=pattern_embedding,
            plan_embedding=plan_embedding,
        )


# ----------------------------------------------------------------------------
# init_example：初始化全局知识库——遍历 checker_database/ 全部子目录（121 个），
# 逐个装载进全局 example_list。
# 调用方：src/checker_gen.py 生成循环开始前调一次；注意无判重逻辑，重复调用
# 会向 example_list 重复追加条目。
# ----------------------------------------------------------------------------
def init_example():
    global example_list  # 声明写全局缓存（agent.py 的 choose_example 读它）
    for checker_dir in example_dir.iterdir():  # 迭代知识库根目录
        if not checker_dir.is_dir():  # 跳过非目录条目（README 等散文件）
            continue
        example_list.append(ExampleChecker.load_example_from_dir(checker_dir))  # 装载并追加


# ----------------------------------------------------------------------------
# choose_example：RAG 检索入口——给定查询文本（已生成的 bug pattern 或 refined
# plan），从知识库挑语义最相似的 num_samples 条示例。
# 论文映射：§3.1 few-shot 示例的动态选择。agent.py 在 sample_examples=True 时
# 调用：pattern2plan（§3.1.2）传 type="pattern"，plan2checker（§3.1.3）传
# type="plan"；sample_examples=False 时退回 prompt_template/examples/ 三例的
# 静态注入（default_checker_examples）。
# 参数：content 查询文本；type 相似度计算的向量侧（"pattern" 或 "plan"）；
#       num_samples 取 top-k（默认 3）。
# 返回：List[ExampleChecker]，按余弦相似度降序的前 num_samples 条。
# ----------------------------------------------------------------------------
def choose_example(content: str, type: str, num_samples=3):
    """Choose the most similar example checker for the given content."""

    embeddings = torch.tensor(get_embeddings(content))  # 查询文本 → ada-002 向量（list 转 1-D tensor）
    similarity_list = []  # 收集器：[(相似度, ExampleChecker), ...]
    for example in example_list:  # 线性扫全库（121 条规模小，无需 ANN 索引）
        if type == "pattern":  # pattern2plan 场景：与库内 pattern 向量比
            similarity = torch.cosine_similarity(
                embeddings, example.pattern_embedding, dim=0
            )
        elif type == "plan":  # plan2checker 场景：与库内 plan 向量比
            similarity = torch.cosine_similarity(
                embeddings, example.plan_embedding, dim=0
            )
        else:
            raise ValueError(f"Invalid type: {type}")  # 只接受 pattern/plan 两路
        similarity_list.append((similarity, example))  # 携带分数入收集器

    similarity_list.sort(key=lambda x: x[0], reverse=True)  # 按相似度降序（key 取 tuple 第 0 元素）
    # 推导式：相似度降序切前 num_samples 条，丢掉分数只留示例对象
    chosen_examples = [example for _, example in similarity_list[:num_samples]]
    return chosen_examples
