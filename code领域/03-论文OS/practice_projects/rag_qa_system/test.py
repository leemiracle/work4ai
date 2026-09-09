"""
测试脚本 - RAG问答系统
"""

import unittest
import torch
from config import Config


class TestRAG问答系统(unittest.TestCase):
    """测试类"""
    
    def setUp(self):
        """测试初始化"""
        self.config = Config()
    
    def test_config(self):
        """测试配置"""
        self.assertIsNotNone(self.config.MODEL_NAME)
        self.assertEqual(self.config.BATCH_SIZE, 32)
    
    # TODO: 添加更多测试用例


if __name__ == '__main__':
    unittest.main()
