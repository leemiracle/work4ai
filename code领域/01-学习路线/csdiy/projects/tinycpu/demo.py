#!/usr/bin/env python3
"""
tinycpu/demo.py — CPU 模拟器端到端演示

4 个 demo：
  1. SEQ CPU 执行算术（参照 csapp Ch4 SEQ）
  2. SEQ CPU 条件跳转（循环求和）
  3. Pipeline CPU 执行同样程序（对比 CPI）
  4. Pipeline 性能分析（CPI / stalls / forwarding 效果）
"""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tinycpu.core import CPU
from tinycpu.pipeline import PipelinedCPU
from tinycpu.isa import assemble, REGISTERS

def demo_seq_arith():
    print("┌─────────────────────────────────┐")
    print("│  Demo 1: SEQ CPU 算术运算       │")
    print("└─────────────────────────────────┘\n")
    asm = """
    irmovl 42 eax
    irmovl 58 ecx
    addl eax ecx
    irmovl 100 edx
    subl edx ecx
    halt
    """
    cpu = CPU(); cpu.load_assembly(asm)
    print(f"  程序: 42+58-100")
    cpu.run()
    print(f"  周期数: {cpu.cycles}")
    print(f"  结果:")
    cpu.dump_registers()

def demo_seq_loop():
    print("\n┌─────────────────────────────────┐")
    print("│  Demo 2: SEQ CPU 循环求和       │")
    print("└─────────────────────────────────┘\n")
    asm = """
    irmovl 5 eax
    irmovl 0 ecx
    loop:
    addl eax ecx
    irmovl -1 edx
    addl edx eax
    irmovl 0 edx
    subl edx eax
    jg loop
    halt
    """
    cpu = CPU(); cpu.load_assembly(asm)
    print(f"  程序: sum = 5+4+3+2+1")
    cpu.run()
    print(f"  周期数: {cpu.cycles}")
    print(f"  ecx (sum) = {cpu.regs[1]}")
    print(f"  ZF={cpu.alu.ZF} SF={cpu.alu.SF}")

def demo_pipeline():
    print("\n┌─────────────────────────────────┐")
    print("│  Demo 3: Pipeline CPU           │")
    print("└─────────────────────────────────┘\n")
    asm = """
    irmovl 10 eax
    irmovl 20 ecx
    addl eax ecx
    irmovl 5 edx
    subl edx ecx
    halt
    """
    cpu = PipelinedCPU(); cpu.load_assembly(asm)
    stats = cpu.run()
    print(f"  程序: 10+20-5")
    print(f"  周期数: {stats['cycles']}")
    print(f"  完成指令: {stats['instructions']}")
    print(f"  CPI: {stats['cpi']:.2f}（理想=1.0）")
    print(f"  ecx (result) = {cpu.regs[1]}")
    print(f"  Forwarding 生效 → 接近理想 CPI")

def demo_comparison():
    print("\n┌─────────────────────────────────┐")
    print("│  Demo 4: SEQ vs Pipeline 对比   │")
    print("└─────────────────────────────────┘\n")
    asm = """
    irmovl 1 eax
    irmovl 2 ecx
    addl eax ecx
    irmovl 3 edx
    addl edx ecx
    irmovl 4 ebx
    addl ebx ecx
    halt
    """
    seq = CPU(); seq.load_assembly(asm); seq.run()
    pipe = PipelinedCPU(); pipe.load_assembly(asm); pipe.run()
    pipe_stats = {"cycles": pipe.cycles, "instructions": pipe.instructions_completed,
                  "cpi": pipe.cycles / max(1, pipe.instructions_completed)}
    print(f"  {'Metric':15s} {'SEQ':>10s} {'Pipeline':>10s}")
    print(f"  {'─'*15} {'─'*10} {'─'*10}")
    print(f"  {'Cycles':15s} {seq.cycles:>10d} {pipe.cycles:>10d}")
    print(f"  {'CPI':15s} {1.0:>10.1f} {pipe_stats['cpi']:>10.2f}")
    print(f"  {'Speedup':15s} {'1.0x':>10s} {seq.cycles/max(1,pipe.cycles):>9.1f}x")
    print(f"  {'Result (ecx)':15s} {seq.regs[1]:>10d} {pipe.regs[1]:>10d}")

def main():
    print("=" * 60)
    print("  tinycpu — CPU 模拟器（参照 csapp Ch4 SEQ + PIPE）")
    print("=" * 60)
    t0 = time.time()
    demo_seq_arith()
    demo_seq_loop()
    demo_pipeline()
    demo_comparison()
    print(f"\n{'='*60}")
    print(f"  完成 ({time.time()-t0:.1f}s)")
    print(f"  tinycpu = isa.py(指令集) + core.py(SEQ CPU) + pipeline.py(5级流水线)")
    print(f"  覆盖: Y86 指令集 → SEQ 单周期 → PIPE 5级流水线 → Forwarding")
    print(f"{'='*60}")

if __name__ == "__main__": main()
