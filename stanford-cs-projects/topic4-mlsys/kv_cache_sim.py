"""
CS349E - Efficient ML Infrastructure
覆盖课程模块：vLLM / PagedAttention / KV Cache / 量化

实现内容：
1. KV Cache 模拟
2. PagedAttention（分页 KV，vLLM 核心）
3. INT8 量化模拟
4. Continuous batching 模拟

参考：
- Kwon et al. "Efficient Memory Management for LLM with PagedAttention" (vLLM, SOSP 2023)
- Frantar et al. "GPTQ" ICLR 2023
"""
from __future__ import annotations
import math
import random
from dataclasses import dataclass, field
from typing import Optional


# ============ 1. KV Cache ============

@dataclass
class KVCache:
    """每个请求的 KV cache"""
    request_id: str
    tokens: list[int] = field(default_factory=list)
    K: list[list[float]] = field(default_factory=list)  # [seq_len, d_head]
    V: list[list[float]] = field(default_factory=list)
    
    def append(self, token: int, k: list[float], v: list[float]):
        self.tokens.append(token)
        self.K.append(k)
        self.V.append(v)

    def __len__(self):
        return len(self.tokens)


class SimpleKVCacheManager:
    """传统 KV cache（每请求独立内存）"""

    def __init__(self, max_seq_len: int = 2048, d_head: int = 64):
        self.max_seq_len = max_seq_len
        self.d_head = d_head
        self.caches: dict[str, KVCache] = {}

    def create(self, request_id: str):
        self.caches[request_id] = KVCache(request_id)

    def append(self, request_id: str, token: int, k: list[float], v: list[float]):
        cache = self.caches[request_id]
        if len(cache) >= self.max_seq_len:
            raise RuntimeError(f"超出 max_seq_len {self.max_seq_len}")
        cache.append(token, k, v)

    def memory_usage(self) -> int:
        """总内存（float 个数）"""
        return sum(2 * len(c) * self.d_head for c in self.caches.values())


# ============ 2. PagedAttention（vLLM） ============

@dataclass
class Block:
    """KV cache 块"""
    block_id: int
    size: int  # 每块的 token 数（vLLM 默认 16）
    tokens: list[int] = field(default_factory=list)
    K: list[list[float]] = field(default_factory=list)
    V: list[list[float]] = field(default_factory=list)
    ref_count: int = 0  # 引用计数（前缀共享用）


class PagedAttentionManager:
    """vLLM PagedAttention: 分块分配 KV cache"""

    def __init__(self, total_blocks: int = 1024, block_size: int = 16, d_head: int = 64):
        self.total_blocks = total_blocks
        self.block_size = block_size
        self.d_head = d_head
        # 物理块池
        self.blocks: list[Block] = [
            Block(block_id=i, size=block_size) for i in range(total_blocks)
        ]
        self.free_block_ids: list[int] = list(range(total_blocks))
        # 每个请求 → block 列表
        self.block_table: dict[str, list[int]] = {}

    def allocate(self, request_id: str, prompt_tokens: list[int]):
        """为新请求分配 blocks"""
        self.block_table[request_id] = []
        for token in prompt_tokens:
            self._append_token(request_id, token, [0.1] * self.d_head, [0.2] * self.d_head)

    def _append_token(self, request_id: str, token: int, k: list[float], v: list[float]):
        # 当前最后一个 block 是否还有空间
        if request_id not in self.block_table or not self.block_table[request_id]:
            # 分配新块
            if not self.free_block_ids:
                raise RuntimeError("OOM: no free blocks")
            bid = self.free_block_ids.pop(0)
            self.block_table[request_id].append(bid)
            self.blocks[bid].ref_count += 1

        last_bid = self.block_table[request_id][-1]
        last_block = self.blocks[last_bid]
        if len(last_block.tokens) >= self.block_size:
            # 块满，分配新块
            if not self.free_block_ids:
                raise RuntimeError("OOM")
            bid = self.free_block_ids.pop(0)
            self.block_table[request_id].append(bid)
            self.blocks[bid].ref_count += 1
            last_block = self.blocks[bid]

        last_block.tokens.append(token)
        last_block.K.append(k)
        last_block.V.append(v)

    def free(self, request_id: str):
        """释放请求的所有块"""
        for bid in self.block_table.get(request_id, []):
            self.blocks[bid].ref_count -= 1
            if self.blocks[bid].ref_count <= 0:
                self.blocks[bid] = Block(block_id=bid, size=self.block_size)
                self.free_block_ids.append(bid)
        del self.block_table[request_id]

    def memory_fragmentation(self) -> float:
        """碎片率：内部浪费"""
        used = sum(1 for b in self.blocks if b.ref_count > 0)
        wasted = sum(self.block_size - len(b.tokens) for b in self.blocks if b.ref_count > 0)
        total_capacity = used * self.block_size
        return wasted / max(total_capacity, 1)

    def free_blocks(self) -> int:
        return len(self.free_block_ids)


# ============ 3. INT8 量化 ============

def quantize_int8(weights: list[float]) -> tuple[list[int], float, float]:
    """对称 INT8 量化：返回 (quantized, scale, zero_point)"""
    if not weights:
        return [], 1.0, 0.0
    abs_max = max(abs(w) for w in weights)
    scale = abs_max / 127.0
    quantized = [int(w / scale) for w in weights]
    return quantized, scale, 0.0


def dequantize_int8(quantized: list[int], scale: float, zero_point: float = 0) -> list[float]:
    return [q * scale + zero_point for q in quantized]


def quantization_error(weights: list[float]) -> float:
    """量化误差（RMSE）"""
    q, s, z = quantize_int8(weights)
    deq = dequantize_int8(q, s, z)
    if not weights:
        return 0.0
    mse = sum((a - b) ** 2 for a, b in zip(weights, deq)) / len(weights)
    return math.sqrt(mse)


# ============ 4. Continuous Batching ============

@dataclass
class Request:
    id: str
    prompt_len: int
    max_output: int
    generated: int = 0
    done: bool = False


def continuous_batching_sim(requests: list[Request], max_batch: int = 4,
                              max_iter: int = 100) -> dict:
    """
    模拟 continuous batching：
    - 每步选 max_batch 个未完成请求
    - 每个请求生成 1 token
    - 完成的立即移出 batch
    """
    queue = list(requests)
    throughput_log = []
    for step in range(max_iter):
        active = [r for r in queue if not r.done][:max_batch]
        if not active:
            break
        for r in active:
            r.generated += 1
            if r.generated >= r.max_output:
                r.done = True
        throughput_log.append(len(active))
    total_tokens = sum(r.generated for r in requests)
    wall_time = max(len(throughput_log), 1)
    return {
        "total_tokens": total_tokens,
        "wall_time_steps": wall_time,
        "throughput": total_tokens / wall_time,
        "utilization": sum(throughput_log) / max(len(throughput_log) * max_batch, 1),
    }


# ============ Demo ============

def demo():
    print("=" * 60)
    print("CS349E: ML Infrastructure Demo")
    print("=" * 60)

    random.seed(42)

    # 1. KV Cache
    print("\n📋 1. KV Cache 传统管理")
    mgr = SimpleKVCacheManager(max_seq_len=2048, d_head=64)
    mgr.create("req1")
    for i in range(100):
        mgr.append("req1", i, [random.gauss(0, 1) for _ in range(64)],
                   [random.gauss(0, 1) for _ in range(64)])
    print(f"   req1: 100 tokens, 内存 {mgr.memory_usage()} floats")
    print(f"   = {mgr.memory_usage() * 4 / 1024:.1f} KB")

    # 2. PagedAttention
    print("\n📋 2. PagedAttention (vLLM 核心)")
    pm = PagedAttentionManager(total_blocks=100, block_size=16, d_head=64)
    pm.allocate("req1", list(range(40)))   # 40 tokens → 3 blocks
    pm.allocate("req2", list(range(20)))   # 20 tokens → 2 blocks
    pm.allocate("req3", list(range(8)))    # 8 tokens → 1 block
    print(f"   Free blocks: {pm.free_blocks()}/100")
    print(f"   Fragmentation: {pm.memory_fragmentation():.2%}")

    # 释放
    pm.free("req2")
    print(f"   After free req2: free = {pm.free_blocks()}")

    # 3. INT8 量化
    print("\n📋 3. INT8 量化")
    weights = [random.gauss(0, 0.1) for _ in range(1000)]
    q, s, z = quantize_int8(weights)
    err = quantization_error(weights)
    fp32_size = len(weights) * 4  # bytes
    int8_size = len(q)
    print(f"   FP32 大小: {fp32_size} bytes")
    print(f"   INT8 大小: {int8_size} bytes ({int8_size/fp32_size:.0%})")
    print(f"   量化误差 RMSE: {err:.6f}")

    # 4. Continuous Batching
    print("\n📋 4. Continuous Batching")
    reqs = [Request(f"r{i}", prompt_len=10, max_output=random.randint(10, 30))
            for i in range(10)]
    result = continuous_batching_sim(reqs, max_batch=4, max_iter=50)
    print(f"   总 tokens: {result['total_tokens']}")
    print(f"   wall time: {result['wall_time_steps']} steps")
    print(f"   吞吐: {result['throughput']:.2f} tokens/step")
    print(f"   GPU 利用率: {result['utilization']:.2%}")

    print("\n✅ CS349E 完成！")
    print("\n💡 覆盖：")
    print("   - KV Cache（推理优化基础）")
    print("   - PagedAttention（vLLM 核心）")
    print("   - INT8 量化（4x 显存节省）")
    print("   - Continuous batching（吞吐优化）")


if __name__ == "__main__":
    demo()
