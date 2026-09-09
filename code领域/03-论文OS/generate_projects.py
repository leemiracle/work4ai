"""
Paper-OS 实践项目生成器
基于论文和应用生成完整可运行的项目
"""
import json
from pathlib import Path
from typing import Dict, List, Any
from data_manager import DatabaseManager
from utils import ConfigManager


class ProjectGenerator:
    """实践项目生成器"""
    
    def __init__(self, db_manager: DatabaseManager, output_dir: str = "practice_projects"):
        self.db = db_manager
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.project_templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, Dict]:
        """加载项目模板"""
        return {
            'transformer_implement': {
                'name': 'Transformer实现项目',
                'description': '从零实现Transformer模型',
                'difficulty': '中级',
                'duration': '2周',
                'prerequisites': ['Python基础', 'PyTorch基础', '线性代数'],
                'papers': ['Attention Is All You Need'],
                'skills': ['自注意力机制', '位置编码', '编码器-解码器架构'],
                'output': '完整的Transformer模型'
            },
            'text_classifier': {
                'name': '文本分类器',
                'description': '使用BERT进行文本分类',
                'difficulty': '初级',
                'duration': '1周',
                'prerequisites': ['Python基础', 'PyTorch基础'],
                'papers': ['BERT: Pre-training of Deep Bidirectional Transformers'],
                'skills': ['BERT微调', '文本预处理', '模型评估'],
                'output': '可部署的文本分类API'
            },
            'image_generator': {
                'name': '图像生成器',
                'description': '实现DDPM进行图像生成',
                'difficulty': '高级',
                'duration': '3周',
                'prerequisites': ['Python基础', 'PyTorch基础', '深度学习基础'],
                'papers': ['Denoising Diffusion Probabilistic Models'],
                'skills': ['扩散模型', 'U-Net架构', '采样算法'],
                'output': '高质量的图像生成模型'
            },
            'rag_qa_system': {
                'name': 'RAG问答系统',
                'description': '构建检索增强生成系统',
                'difficulty': '中级',
                'duration': '2周',
                'prerequisites': ['Python基础', '向量数据库基础', 'LLM基础'],
                'papers': ['Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks'],
                'skills': ['向量检索', 'Prompt工程', '系统集成'],
                'output': '可运行的问答系统'
            },
            'image_classifier': {
                'name': '图像分类器',
                'description': '使用ResNet进行图像分类',
                'difficulty': '初级',
                'duration': '1周',
                'prerequisites': ['Python基础', 'PyTorch基础', 'CNN基础'],
                'papers': ['Deep Residual Learning for Image Recognition'],
                'skills': ['ResNet架构', '数据增强', '迁移学习'],
                'output': '图像分类模型'
            },
            'llm_chatbot': {
                'name': 'LLM聊天机器人',
                'description': '构建基于LLM的聊天机器人',
                'difficulty': '中级',
                'duration': '2周',
                'prerequisites': ['Python基础', 'LLM API使用', 'Prompt工程'],
                'papers': ['Improving Language Understanding by Generative Pre-Training'],
                'skills': ['LLM调用', '上下文管理', 'API开发'],
                'output': 'Web聊天机器人'
            },
            'multimodal_search': {
                'name': '多模态搜索引擎',
                'description': '实现图文跨模态搜索',
                'difficulty': '高级',
                'duration': '3周',
                'prerequisites': ['Python基础', '深度学习基础', 'CLIP基础'],
                'papers': ['Learning Transferable Visual Models From Natural Language Supervision'],
                'skills': ['CLIP模型', '特征提取', '相似度计算'],
                'output': '多模态搜索引擎'
            },
            'code_generator': {
                'name': '代码生成器',
                'description': '实现基于Transformer的代码生成模型',
                'difficulty': '高级',
                'duration': '4周',
                'prerequisites': ['Python基础', 'Transformer基础', '代码数据集处理'],
                'papers': ['Attention Is All You Need', 'GPT系列论文'],
                'skills': ['代码数据集处理', '模型训练', '代码评估'],
                'output': '代码生成模型'
            }
        }
    
    def generate_all_projects(self):
        """生成所有实践项目"""
        print("🔨 生成实践项目...")
        print("=" * 60)
        
        for project_id, template in self.project_templates.items():
            self._generate_project(project_id, template)
        
        print("\n" + "=" * 60)
        print(f"✅ 完成! 共生成 {len(self.project_templates)} 个实践项目")
        print(f"📁 输出目录: {self.output_dir.absolute()}")
    
    def _generate_project(self, project_id: str, template: Dict):
        """生成单个实践项目"""
        project_dir = self.output_dir / project_id
        project_dir.mkdir(exist_ok=True)
        
        print(f"\n📦 生成项目: {template['name']}")
        
        # 1. 生成README
        self._generate_readme(project_dir, template)
        
        # 2. 生成项目结构
        self._generate_structure(project_dir, template)
        
        # 3. 生成代码模板
        self._generate_code_template(project_dir, template)
        
        # 4. 生成测试文件
        self._generate_tests(project_dir, template)
        
        # 5. 生成学习指南
        self._generate_guide(project_dir, template)
        
        print(f"   ✅ 完成: {project_dir.relative_to(self.output_dir.parent)}")
    
    def _generate_readme(self, project_dir: Path, template: Dict):
        """生成README文件"""
        readme = f"""# {template['name']}

> {template['description']}

**难度**: {template['difficulty']}  
**预计时长**: {template['duration']}  
**生成时间**: {template.get('date', 'N/A')}

---

## 📋 项目概述

本项目旨在帮助你深入理解{template['description']}的核心概念。

### 学习目标

通过完成本项目，你将掌握：
"""
        for skill in template['skills']:
            readme += f"- {skill}\n"
        
        readme += f"""

### 前置要求

"""
        for prereq in template['prerequisites']:
            readme += f"- {prereq}\n"
        
        readme += f"""

### 参考论文

"""
        for paper in template['papers']:
            readme += f"- {paper}\n"
        
        readme += """

---

## 🚀 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行项目

```bash
python main.py
```

---

## 📁 项目结构

```
{template['name'].lower().replace(' ', '_')}/
├── README.md          # 本文件
├── requirements.txt   # 依赖列表
├── main.py           # 主程序入口
├── model.py          # 模型定义
├── train.py          # 训练脚本
├── test.py           # 测试脚本
├── config.py         # 配置文件
└── data/             # 数据目录
```

---

## 📝 实现步骤

1. 环境搭建
2. 数据准备
3. 模型实现
4. 训练模型
5. 测试评估
6. 优化改进

详见 `IMPLEMENTATION_GUIDE.md`

---

## 🎯 交付成果

{template['output']}

---

## 📚 参考资料

- 相关论文
- 项目模板代码
- 在线文档

---

## ❓ 常见问题

如有问题，请查看 `IMPLEMENTATION_GUIDE.md` 或提交Issue。

---

**Paper-OS Practice Projects**
"""
        
        with open(project_dir / 'README.md', 'w', encoding='utf-8') as f:
            f.write(readme)
    
    def _generate_structure(self, project_dir: Path, template: Dict):
        """生成项目结构"""
        # 创建必要的目录
        (project_dir / 'data').mkdir(exist_ok=True)
        (project_dir / 'models').mkdir(exist_ok=True)
        (project_dir / 'logs').mkdir(exist_ok=True)
        (project_dir / 'checkpoints').mkdir(exist_ok=True)
    
    def _generate_code_template(self, project_dir: Path, template: Dict):
        """生成代码模板"""
        project_name = template['name'].lower().replace(' ', '_')
        
        # requirements.txt
        requirements = """torch>=2.0.0
numpy>=1.24.0
pandas>=2.0.0
tqdm>=4.65.0
"""
        with open(project_dir / 'requirements.txt', 'w', encoding='utf-8') as f:
            f.write(requirements)
        
        # config.py
        config = f'''"""
配置文件 - {template['name']}
"""

class Config:
    """项目配置"""
    
    # 模型配置
    MODEL_NAME = "{template['name']}"
    
    # 训练配置
    BATCH_SIZE = 32
    LEARNING_RATE = 1e-4
    NUM_EPOCHS = 10
    
    # 路径配置
    DATA_DIR = "data"
    MODEL_DIR = "models"
    LOG_DIR = "logs"
    CHECKPOINT_DIR = "checkpoints"
    
    # 其他配置
    DEVICE = "cuda"  # 或 "cpu"
    RANDOM_SEED = 42


# TODO: 根据项目需求添加更多配置项
'''
        with open(project_dir / 'config.py', 'w', encoding='utf-8') as f:
            f.write(config)
        
        # main.py
        main = f'''"""
主程序 - {template['name']}
"""

import argparse
from config import Config


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='{template['name']}')
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
'''
        with open(project_dir / 'main.py', 'w', encoding='utf-8') as f:
            f.write(main)
    
    def _generate_tests(self, project_dir: Path, template: Dict):
        """生成测试文件"""
        tests = f'''"""
测试脚本 - {template['name']}
"""

import unittest
import torch
from config import Config


class Test{template['name'].replace(' ', '')}(unittest.TestCase):
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
'''
        with open(project_dir / 'test.py', 'w', encoding='utf-8') as f:
            f.write(tests)
    
    def _generate_guide(self, project_dir: Path, template: Dict):
        """生成实现指南"""
        guide = f"""# {template['name']} - 实现指南

本指南将逐步指导你完成{template['name']}的实现。

---

## 第1步: 环境搭建

### 安装依赖

```bash
pip install -r requirements.txt
```

### 验证安装

```bash
python -c "import torch; print(torch.__version__)"
```

---

## 第2步: 数据准备

### 下载数据

[数据集链接或说明]

### 预处理数据

```python
# TODO: 添加数据预处理代码示例
```

---

## 第3步: 模型实现

### 核心模块

```python
# TODO: 添加核心模块实现
```

### 辅助函数

```python
# TODO: 添加辅助函数
```

---

## 第4步: 训练模型

### 训练脚本

```bash
python main.py --mode train
```

### 监控训练

查看 `logs/` 目录下的日志文件。

---

## 第5步: 测试评估

### 运行测试

```bash
python test.py
```

### 评估指标

[评估指标说明]

---

## 第6步: 优化改进

### 性能优化

[优化建议]

### 功能扩展

[扩展思路]

---

## 常见问题

### Q1: 训练速度慢怎么办？
A: ...

### Q2: 模型不收敛怎么办？
A: ...

---

## 进阶方向

1. [进阶方向1]
2. [进阶方向2]
3. [进阶方向3]

---

**祝你学习愉快！** 🚀
"""
        with open(project_dir / 'IMPLEMENTATION_GUIDE.md', 'w', encoding='utf-8') as f:
            f.write(guide)


def main():
    """主函数"""
    config = ConfigManager()
    db_manager = DatabaseManager(config.get('paths.db_file', 'data/paper_os.db'))
    
    generator = ProjectGenerator(db_manager)
    generator.generate_all_projects()
    
    db_manager.close()


if __name__ == "__main__":
    main()
