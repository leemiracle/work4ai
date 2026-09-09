"""
主程序 - 文本分类器
"""

import argparse
from config import Config


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='文本分类器')
    parser.add_argument('--mode', type=str, default='train', 
                        choices=['train', 'test', 'inference'],
                        help='运行模式')
    parser.add_argument('--config', type=str, default='config.py',
                        help='配置文件')
    
    args = parser.parse_args()
    
    # TODO: 加载配置
    
    if args.mode == 'train':
        # TODO: 训练逻辑
        print("训练模式")
    elif args.mode == 'test':
        # TODO: 测试逻辑
        print("测试模式")
    elif args.mode == 'inference':
        # TODO: 推理逻辑
        print("推理模式")


if __name__ == "__main__":
    main()
