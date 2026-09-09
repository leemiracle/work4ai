#!/usr/bin/env python3

import subprocess
import tempfile
import os

def compile_to_llvm_ir(c_code, output_file="output.ll"):
    """将 C 代码编译为 LLVM IR"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
        f.write(c_code)
        c_file = f.name
    
    try:
        # 编译为 LLVM IR
        cmd = ["clang", "-S", "-emit-llvm", c_file, "-o", output_file]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"编译错误: {result.stderr}")
            return None
        
        # 读取生成的 IR
        with open(output_file, 'r') as f:
            return f.read()
    finally:
        os.unlink(c_file)


def optimize_llvm_ir(input_file, output_file, optimization_level="-O2"):
    """优化 LLVM IR"""
    cmd = ["opt", optimization_level, input_file, "-S", "-o", output_file]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"优化错误: {result.stderr}")
        return None
    
    with open(output_file, 'r') as f:
        return f.read()


def analyze_llvm_ir(ir_code):
    """分析 LLVM IR 代码"""
    analysis = {
        "functions": [],
        "instructions": {},
        "types": set()
    }
    
    for line in ir_code.split('\n'):
        line = line.strip()
        
        # 识别函数定义
        if line.startswith('define'):
            parts = line.split()
            if len(parts) >= 2:
                analysis["functions"].append(parts[1])
        
        # 统计指令
        for inst in ['add', 'sub', 'mul', 'div', 'icmp', 'br', 'call', 'load', 'store']:
            if inst in line:
                analysis["instructions"][inst] = analysis["instructions"].get(inst, 0) + 1
        
        # 识别类型
        if 'i32' in line:
            analysis["types"].add('i32')
        if 'i64' in line:
            analysis["types"].add('i64')
        if 'float' in line:
            analysis["types"].add('float')
        if 'double' in line:
            analysis["types"].add('double')
    
    return analysis


def compare_ir(before_ir, after_ir):
    """对比优化前后的 IR"""
    print("=== IR 对比分析 ===\n")
    
    before_stats = analyze_llvm_ir(before_ir)
    after_stats = analyze_llvm_ir(after_ir)
    
    print("函数数量:")
    print(f"  优化前: {len(before_stats['functions'])}")
    print(f"  优化后: {len(after_stats['functions'])}")
    
    print("\n指令统计:")
    all_insts = set(before_stats['instructions'].keys()) | set(after_stats['instructions'].keys())
    for inst in sorted(all_insts):
        before = before_stats['instructions'].get(inst, 0)
        after = after_stats['instructions'].get(inst, 0)
        diff = after - before
        print(f"  {inst:10s}: {before:4d} -> {after:4d} ({diff:+4d})")
    
    print("\n类型使用:")
    all_types = before_stats['types'] | after_stats['types']
    for t in sorted(all_types):
        before_in = t in before_stats['types']
        after_in = t in after_stats['types']
        print(f"  {t:8s}: {'✓' if before_in else '✗'} -> {'✓' if after_in else '✗'}")


def example_sum_function():
    """生成求和函数的 C 代码"""
    return """
int sum(int n) {
    int total = 0;
    for (int i = 1; i <= n; i++) {
        total += i;
    }
    return total;
}
"""


def example_fibonacci():
    """生成斐波那契函数的 C 代码"""
    return """
int fibonacci(int n) {
    if (n <= 1) {
        return n;
    }
    return fibonacci(n - 1) + fibonacci(n - 2);
}
"""


def example_string_ops():
    """生成字符串操作的 C 代码"""
    return """
int string_length(const char* str) {
    int len = 0;
    while (str[len] != '\\0') {
        len++;
    }
    return len;
}
"""


def main():
    print("=== LLVM IR 生成与分析工具 ===\n")
    
    # 示例 1: 求和函数
    print("示例 1: 求和函数")
    print("-" * 50)
    
    c_code = example_sum_function()
    print("C 代码:")
    print(c_code)
    
    ir_code = compile_to_llvm_ir(c_code, "sum.ll")
    if ir_code:
        print("\n生成的 LLVM IR:")
        print(ir_code)
        
        # 优化 IR
        optimized_ir = optimize_llvm_ir("sum.ll", "sum_opt.ll")
        if optimized_ir:
            print("\n" + "="*50)
            print("优化后的 LLVM IR:")
            print(optimized_ir)
            
            # 对比分析
            compare_ir(ir_code, optimized_ir)
    
    # 示例 2: 斐波那契
    print("\n\n示例 2: 斐波那契函数")
    print("-" * 50)
    
    c_code = example_fibonacci()
    print("C 代码:")
    print(c_code)
    
    ir_code = compile_to_llvm_ir(c_code, "fib.ll")
    if ir_code:
        print("\n生成的 LLVM IR:")
        print(ir_code[:1000] + "...")  # 只显示部分
        
        optimized_ir = optimize_llvm_ir("fib.ll", "fib_opt.ll", "-O3")
        if optimized_ir:
            print("\n" + "="*50)
            print("优化后的 LLVM IR:")
            print(optimized_ir[:1000] + "...")
    
    # 示例 3: 字符串操作
    print("\n\n示例 3: 字符串操作")
    print("-" * 50)
    
    c_code = example_string_ops()
    print("C 代码:")
    print(c_code)
    
    ir_code = compile_to_llvm_ir(c_code, "string.ll")
    if ir_code:
        print("\n生成的 LLVM IR:")
        print(ir_code[:800] + "...")
        
        # 分析 IR
        analysis = analyze_llvm_ir(ir_code)
        print(f"\n分析结果:")
        print(f"  函数: {analysis['functions']}")
        print(f"  指令: {analysis['instructions']}")
        print(f"  类型: {analysis['types']}")
    
    # 清理临时文件
    for f in ["sum.ll", "sum_opt.ll", "fib.ll", "fib_opt.ll", "string.ll"]:
        if os.path.exists(f):
            os.unlink(f)


if __name__ == "__main__":
    main()