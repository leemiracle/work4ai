#!/usr/bin/env python3
"""
快速测试脚本 - 验证环境配置
"""
import sys

def test_imports():
    """测试必要的依赖包"""
    print("🔍 测试依赖包...")
    
    try:
        import torch
        print(f"  ✅ PyTorch {torch.__version__}")
    except ImportError:
        print("  ❌ PyTorch 未安装")
        return False
    
    try:
        import transformers
        print(f"  ✅ Transformers {transformers.__version__}")
    except ImportError:
        print("  ❌ Transformers 未安装")
        return False
    
    return True

def test_config():
    """测试配置文件"""
    print("\n🔍 测试配置文件...")
    
    try:
        import config
        print(f"  ✅ 配置文件加载成功")
        return True
    except Exception as e:
        print(f"  ❌ 配置文件加载失败: {e}")
        return False

def main():
    print("=" * 50)
    print("Paper-OS 快速测试")
    print("=" * 50)
    
    if test_imports() and test_config():
        print("\n✅ 所有测试通过！")
        return 0
    else:
        print("\n❌ 测试失败，请检查环境配置")
        return 1

if __name__ == "__main__":
    sys.exit(main())
