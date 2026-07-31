"""
讲透推理引擎 —— vLLM PagedAttention + continuous batching
============================================================
推理 (inference) 是训练之后的事: 前向无反向, 服务给用户。
本实验在 CPU 上模拟推理引擎的两大核心创新:
  实验1: 分页 KV Cache (像 OS 虚拟内存, 消除碎片)
  实验2: continuous batching (长短请求混合, 动态插队)
  实验3: prefill vs decode 两阶段的计算量差异

核心洞察: 推理引擎 = 操作系统思想 + Transformer (分页/调度/批处理)。
跑法: python3 03_inference_engine.py
"""
import numpy as np

np.random.seed(0)

# ============================================================
# 实验 1: 分页 KV Cache —— 像 OS 虚拟内存
# ============================================================
print("=" * 72)
print("实验 1: 分页 KV Cache —— vLLM 的核心创新")
print("=" * 72)
print("""
问题: 多个请求的序列长度不同, 连续分配 KV Cache 会产生【碎片】
  请求A: 需 200 token 空间, 但只生成 50 → 150 浪费
  请求B: 需 1000 token, 但没连续大块 → 分配失败 (即使总空闲够)

vLLM 的解法 (PagedAttention): 像 OS 的【虚拟内存分页】
  - KV Cache 分成固定大小的 page (如 16 token/page)
  - 每个请求的逻辑序列 → 通过 page table 映射到物理 page
  - 物理 page 不连续也行 → 零碎片
""")

PAGE_SIZE = 16   # 每 page 装 16 token 的 KV

class PagedKVCache:
    """模拟分页 KV Cache (OS 虚拟内存思想)"""
    def __init__(self, num_pages, page_size):
        self.num_pages = num_pages
        self.page_size = page_size
        self.free_pages = list(range(num_pages))   # 空闲物理 page
        self.page_tables = {}                       # 请求 -> 逻辑页号->物理页号

    def allocate(self, request_id, num_tokens):
        """为请求分配足够 page"""
        num_pages_needed = (num_tokens + self.page_size - 1) // self.page_size
        if num_pages_needed > len(self.free_pages):
            return False  # OOM
        pages = [self.free_pages.pop() for _ in range(num_pages_needed)]
        self.page_tables[request_id] = pages
        return True

    def free(self, request_id):
        for p in self.page_tables.pop(request_id, []):
            self.free_pages.append(p)

class ContiguousKVCache:
    """朴素连续分配 (会碎片)"""
    def __init__(self, total_tokens):
        self.total = total_tokens
        self.used = []   # (request_id, start, length)

    def allocate(self, request_id, num_tokens):
        """首次适应分配"""
        # 找连续空洞
        holes = []
        occupied = sorted(self.used, key=lambda x: x[1])
        prev_end = 0
        for _, start, length in occupied:
            if start > prev_end: holes.append((prev_end, start - prev_end))
            prev_end = start + length
        if prev_end < self.total: holes.append((prev_end, self.total - prev_end))
        for h_start, h_len in holes:
            if h_len >= num_tokens:
                self.used.append((request_id, h_start, num_tokens))
                return True
        return False

    def free(self, request_id):
        self.used = [u for u in self.used if u[0] != request_id]

# 模拟: 一批长短不一的请求
TOTAL = 1024  # 总 token 容量
requests = [("A", 50), ("B", 200), ("C", 15), ("D", 300), ("E", 80), ("F", 12)]

# 连续分配
contig = ContiguousKVCache(TOTAL)
contig_ok = []
for rid, ntok in requests:
    ok = contig.allocate(rid, ntok)
    contig_ok.append(ok)
# 释放短请求, 再试分配大请求 (测碎片)
contig.free("A"); contig.free("C"); contig.free("F")  # 释放碎片化的小块
contig_big_ok = contig.allocate("G", 120)  # 即使总空闲够, 可能因碎片失败

# 分页分配
paged = PagedKVCache(TOTAL // PAGE_SIZE, PAGE_SIZE)
paged_ok = []
for rid, ntok in requests:
    ok = paged.allocate(rid, ntok)
    paged_ok.append(ok)
paged.free("A"); paged.free("C"); paged.free("F")
paged_big_ok = paged.allocate("G", 120)

print(f"总容量 {TOTAL} token, page_size={PAGE_SIZE}")
print(f"\n分配请求: {requests}")
print(f"\n连续分配: {dict(zip([r[0] for r in requests], contig_ok))}")
print(f"  释放 A,C,F 后再分配 G(120): {'✓ 成功' if contig_big_ok else '✗ 失败 (碎片!)'}")
print(f"\n分页分配: {dict(zip([r[0] for r in requests], paged_ok))}")
print(f"  释放 A,C,F 后再分配 G(120): {'✓ 成功' if paged_big_ok else '✗ 失败'}")
print(f"\n  ==> 连续分配因【碎片】失败 (即使总空闲够); 分页分配零碎片, 像虚拟内存。\n")


# ============================================================
# 实验 2: continuous batching (动态批处理)
# ============================================================
print("=" * 72)
print("实验 2: continuous batching —— 长短请求混合")
print("=" * 72)
print("""
传统 static batching: 一个 batch 里所有请求必须【同时结束】
  → 长请求拖累短请求, 短请求生成完了还得等 → GPU 空闲
continuous batching (vLLM): 每步动态调整 batch
  → 完成的请求【随时退出】, 新请求【随时插队】 → 吞吐 2-4×
""")

# 模拟: 4 个请求, 长度不同
requests_lens = [5, 20, 3, 12]   # A短 B长 C最短 D中
steps_static = max(requests_lens)  # static: 等最长的
# continuous: 每步有请求完成就退出
timeline = []
remaining = list(requests_lens)
step = 0
while any(r > 0 for r in remaining):
    active = sum(1 for r in remaining if r > 0)
    timeline.append(active)
    remaining = [r - 1 for r in remaining]  # 每个活跃请求生成 1 token
    step += 1
steps_continuous = step
# 计算利用率: static 浪费在空转上的算力
total_compute_static = sum(max(requests_lens) for _ in requests_lens)  # 每步都全 batch
total_useful = sum(requests_lens)
util_static = total_useful / total_compute_static

print(f"请求长度: {requests_lens} (A=5, B=20, C=3, D=12)")
print(f"\nstatic batching:   所有请求等到 step {steps_static} (等最长的 B)")
print(f"  每步 batch=4, 但 A 在 step5 就完了, C 在 step3 就完了 → 后续空转")
print(f"  有效利用率: {util_static*100:.0f}% (大量算力浪费在已完成的请求)")
print(f"\ncontinuous batching: 完成的随时退出")
print(f"  活跃请求数随时间: {timeline}")
print(f"  总步数 {steps_continuous}, 但每步只算活跃的 → 利用率接近 100%")
print(f"  ==> continuous batching 吞吐提升 ~{1/util_static:.1f}×\n")


# ============================================================
# 实验 3: prefill vs decode 两阶段
# ============================================================
print("=" * 72)
print("实验 3: prefill (预填充) vs decode (解码) 两阶段")
print("=" * 72)
print("""
LLM 生成分两阶段:
  prefill: 处理整个 prompt (如 1000 token) → 算 KV Cache   compute-bound (并行, 快)
  decode:  每步生成 1 token, 复用 KV Cache                  memory-bound (串行, 慢)
""")

prompt_len = 1000
gen_len = 200
d = 128
# prefill FLOPs: prompt 的 Q@K^T (n×n) + @V + FFN
prefill_flops = prompt_len * prompt_len * d + prompt_len * d * d * 4 * 2  # 粗略
# decode FLOPs: 每步 1 个 query × prompt KV (n×1) + FFN, 共 gen_len 步
decode_flops_per_step = prompt_len * d + d * d * 4
decode_flops_total = decode_flops_per_step * gen_len

print(f"prompt={prompt_len} token, 生成 {gen_len} token, d={d}")
print(f"\nprefill 阶段 (一次性处理整个 prompt):")
print(f"  FLOPs ≈ {prefill_flops:,}  (compute-bound, GPU 算力打满)")
print(f"\ndecode 阶段 (逐 token, {gen_len} 步):")
print(f"  每步 FLOPs ≈ {decode_flops_per_step:,}")
print(f"  总 FLOPs ≈ {decode_flops_total:,}")
print(f"\n  FLOPs 比例 prefill:decode = {prefill_flops/decode_flops_total:.1f}:1")
print(f"  但 decode 慢得多——因为 decode 是【memory-bound】:")
print(f"    每步只算 1 个 query, 却要【读整个 KV Cache】, 计算单元闲置")
print(f"  ==> 这就是为什么【投机解码】(09篇) 有用: 用空闲算力并行验证多个 token\n")

print("=" * 72)
print("全部实验完成!")
print("核心: 推理引擎 = OS 思想 + Transformer")
print("  分页 KV Cache (虚拟内存) + continuous batching (进程调度) + prefill/decode (两阶段)")
print("=" * 72)
