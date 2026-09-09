#!/usr/bin/env python3
"""
tinymesi/demo.py — MESI 缓存一致性演示

4 个 demo：
  1. 独占读（E 状态）
  2. 共享读（S 状态）
  3. 修改写（M 状态 + 其他核失效）
  4. 写回（M → S → 写回内存）
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tinymesi.mesi import MESISimulator, MESIState

def main():
    print("=" * 60)
    print("  tinymesi — MESI 缓存一致性协议（参照 Patterson §5.5）")
    print("=" * 60)

    sim = MESISimulator(n_cores=4)

    # Demo 1: 独占读
    print("\n┌─────────────────────────────────┐")
    print("│  Demo 1: 独占读（E 状态）       │")
    print("└─────────────────────────────────┘\n")
    val = sim.read(0, 0x1000)
    print(f"  Core 0 read(0x1000) → {val}")
    states = sim.caches[0].count_states()
    print(f"  Core 0 cache: E={states[MESIState.E]}（独占，只有 Core 0 有）")

    # Demo 2: 共享读
    print("\n┌─────────────────────────────────┐")
    print("│  Demo 2: 共享读（S 状态）       │")
    print("└─────────────────────────────────┘\n")
    val = sim.read(1, 0x1000)
    print(f"  Core 1 read(0x1000) → {val}")
    print(f"  Core 0 的 E → S（降级为共享）")
    states0 = sim.caches[0].count_states()
    states1 = sim.caches[1].count_states()
    print(f"  Core 0: S={states0[MESIState.S]}")
    print(f"  Core 1: S={states1[MESIState.S]}（两个核共享）")

    # Demo 3: 修改写
    print("\n┌─────────────────────────────────┐")
    print("│  Demo 3: 修改写（M + 失效）     │")
    print("└─────────────────────────────────┘\n")
    sim.write(0, 0x1000, 42)
    print(f"  Core 0 write(0x1000, 42)")
    states0 = sim.caches[0].count_states()
    states1 = sim.caches[1].count_states()
    print(f"  Core 0: M={states0[MESIState.M]}（已修改，独占）")
    print(f"  Core 1: I={states1[MESIState.I]}（被失效！）")

    # Demo 4: 写回
    print("\n┌─────────────────────────────────┐")
    print("│  Demo 4: 写回（M → S）          │")
    print("└─────────────────────────────────┘\n")
    val = sim.read(2, 0x1000)
    print(f"  Core 2 read(0x1000) → {val}（从 Core 0 的 M 状态写回）")
    states0 = sim.caches[0].count_states()
    states2 = sim.caches[2].count_states()
    print(f"  Core 0: M→S (M={states0[MESIState.M]}, S={states0[MESIState.S]})")
    print(f"  Core 2: S={states2[MESIState.S]}（共享一致数据）")

    print(f"\n{'='*60}")
    sim.report()
    print(f"\n  MESI 协议保证: 多核看到的内存数据一致")
    print(f"  状态转换: I→E→S→M→S→I（由 CPU 读写 + 总线事件驱动）")
    print(f"{'='*60}")

if __name__ == "__main__": main()
