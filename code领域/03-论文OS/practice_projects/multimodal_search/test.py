"""
测试脚本 - 多模态搜索引擎
"""

import unittest
import torch
from config import Config


class Test多模态搜索引擎(unittest.TestCase):
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
