#!/usr/bin/env python3
"""
Paper-OS 初始化脚本 - 完善项目结构
"""
import json
from pathlib import Path

def update_implementation_guides():
    """为实践项目添加更详细的实现指南"""
    
    guides = {
        'llm_chatbot': {
            'dataset': '对话数据集（如DailyDialog、PersonaChat）',
            'data_preprocessing': '''
# 数据预处理示例
from datasets import load_dataset

# 加载数据集
dataset = load_dataset("daily_dialog")

# 预处理对话
def preprocess_dialog(example):
    # TODO: 实现对话预处理
    return {"text": processed_text}
            ''',
            'core_module': '''
# LLM聊天机器人核心模块
import torch
import torch.nn as nn

class ChatBot(nn.Module):
    def __init__(self, model_name="gpt2"):
        super().__init__()
        # TODO: 加载预训练模型
        pass
    
    def generate_response(self, input_text, max_length=100):
        # TODO: 实现响应生成
        pass
            ''',
            'eval_metrics': '困惑度（Perplexity）、BLEU分数、人工评估',
            'optimization': '添加对话历史管理、优化提示工程、添加温度控制',
            'extensions': '多轮对话、个性化对话、情感识别'
        },
        'image_classifier': {
            'dataset': 'CIFAR-10、ImageNet或自定义数据集',
            'data_preprocessing': '''
# 数据预处理示例
from torchvision import transforms

transform = transforms.Compose([
    transforms.Resize(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                        std=[0.229, 0.224, 0.225])
])
            ''',
            'core_module': '''
# CNN图像分类器
import torch
import torch.nn as nn

class ImageClassifier(nn.Module):
    def __init__(self, num_classes=10):
        super().__init__()
        # TODO: 实现CNN网络
        pass
    
    def forward(self, x):
        # TODO: 实现前向传播
        pass
            ''',
            'eval_metrics': '准确率（Accuracy）、F1分数、混淆矩阵',
            'optimization': '数据增强、学习率调度、Dropout正则化',
            'extensions': '迁移学习、模型蒸馏、对抗训练'
        },
        'text_classifier': {
            'dataset': 'IMDB情感分析、AG News、自定义文本数据集',
            'data_preprocessing': '''
# 文本预处理示例
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

def preprocess_text(text):
    tokens = tokenizer(text, 
                      padding=True, 
                      truncation=True, 
                      max_length=128,
                      return_tensors="pt")
    return tokens
            ''',
            'core_module': '''
# Transformer文本分类器
import torch
import torch.nn as nn

class TextClassifier(nn.Module):
    def __init__(self, num_classes, model_name="bert-base-uncased"):
        super().__init__()
        # TODO: 加载预训练模型
        pass
    
    def forward(self, input_ids, attention_mask):
        # TODO: 实现前向传播
        pass
            ''',
            'eval_metrics': '准确率、精确率、召回率、F1分数',
            'optimization': '调整batch size、使用预训练模型、添加正则化',
            'extensions': '多标签分类、层级分类、零样本分类'
        },
        'rag_qa_system': {
            'dataset': '文档集合、问答对（如SQuAD）',
            'data_preprocessing': '''
# RAG数据预处理示例
from langchain.text_splitter import RecursiveCharacterTextSplitter

def split_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    return splitter.split_documents(documents)
            ''',
            'core_module': '''
# RAG问答系统
class RAGSystem:
    def __init__(self):
        # TODO: 初始化检索器和生成器
        pass
    
    def query(self, question):
        # TODO: 实现RAG查询流程
        # 1. 检索相关文档
        # 2. 生成答案
        pass
            ''',
            'eval_metrics': '检索准确率、答案准确率、响应时间',
            'optimization': '优化索引、调整检索参数、优化提示模板',
            'extensions': '多模态RAG、对话式RAG、实时更新索引'
        }
    }
    
    for project_key, guide_data in guides.items():
        guide_path = Path(f'practice_projects/{project_key}/IMPLEMENTATION_GUIDE.md')
        if guide_path.exists():
            content = guide_path.read_text(encoding='utf-8')
            
            # 替换数据集链接
            content = content.replace('[数据集链接或说明]', guide_data['dataset'])
            
            # 替换数据预处理代码
            content = content.replace('''```python
# TODO: 添加数据预处理代码示例
```''', f'''```python
{guide_data['data_preprocessing']}
```''')
            
            # 替换核心模块代码
            content = content.replace('''```python
# TODO: 添加核心模块实现
```''', f'''```python
{guide_data['core_module']}
```''')
            
            # 替换评估指标
            content = content.replace('[评估指标说明]', guide_data['eval_metrics'])
            
            # 替换优化建议
            content = content.replace('[优化建议]', guide_data['optimization'])
            
            # 替换扩展思路
            content = content.replace('[扩展思路]', guide_data['extensions'])
            
            guide_path.write_text(content, encoding='utf-8')
            print(f'✅ Updated {project_key}/IMPLEMENTATION_GUIDE.md')
        else:
            print(f'⚠️ Not found: {guide_path}')

def create_quick_test_scripts():
    """创建快速测试脚本"""
    
    test_script = '''#!/usr/bin/env python3
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
    print("\\n🔍 测试配置文件...")
    
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
        print("\\n✅ 所有测试通过！")
        return 0
    else:
        print("\\n❌ 测试失败，请检查环境配置")
        return 1

if __name__ == "__main__":
    sys.exit(main())
'''
    
    # 为每个实践项目创建测试脚本
    for project_dir in Path('practice_projects').iterdir():
        if project_dir.is_dir():
            test_path = project_dir / 'quick_test.py'
            test_path.write_text(test_script, encoding='utf-8')
            test_path.chmod(0o755)
            print(f"✅ Created {project_dir.name}/quick_test.py")

def create_project_template_improvements():
    """改进代码模板，添加更多TODO注释和学习提示"""
    
    template_improvements = {
        'code_practice/Transformer基础/01_attention_mechanism/template.py': '''
import torch
import torch.nn as nn

class MultiHeadAttention(nn.Module):
    """
    多头注意力机制实现
    
    学习任务:
    1. 理解Q、K、V的计算
    2. 实现缩放点积注意力
    3. 实现多头并行计算
    """
    
    def __init__(self, d_model, num_heads):
        super().__init__()
        assert d_model % num_heads == 0, "d_model must be divisible by num_heads"
        
        self.d_model = d_model
        self.num_heads = num_heads
        self.head_dim = d_model // num_heads
        
        # TODO 1: 理解为什么需要三个线性投影？
        # 提示: Q(query)、K(key)、V(value)分别用于计算注意力权重和值
        self.qkv_proj = nn.Linear(d_model, 3 * d_model)
        self.out_proj = nn.Linear(d_model, d_model)
    
    def forward(self, x, mask=None):
        """
        前向传播
        
        Args:
            x: 输入张量 [batch_size, seq_len, d_model]
            mask: 可选的掩码张量
        
        Returns:
            输出张量 [batch_size, seq_len, d_model]
        """
        batch_size, seq_len, _ = x.shape
        
        # TODO 2: 一次性计算Q、K、V，为什么这样效率高？
        qkv = self.qkv_proj(x)
        q, k, v = qkv.chunk(3, dim=-1)
        
        # TODO 3: 理解reshape和transpose的作用
        # 提示: 将多头注意力头分离出来，便于并行计算
        q = q.view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        k = k.view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        v = v.view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        
        # TODO 4: 实现缩放点积注意力
        # 提示: 使用sqrt(head_dim)进行缩放，防止梯度消失
        attn = torch.matmul(q, k.transpose(-2, -1)) / (self.head_dim ** 0.5)
        
        # TODO 5: 如果需要，应用mask（例如在解码器中）
        if mask is not None:
            attn = attn.masked_fill(mask == 0, float('-inf'))
        
        attn = torch.softmax(attn, dim=-1)
        
        # TODO 6: 计算加权和
        out = torch.matmul(attn, v)
        
        # TODO 7: 将多头结果合并回原始形状
        out = out.transpose(1, 2).contiguous().view(batch_size, seq_len, self.d_model)
        return self.out_proj(out)

# 测试代码
if __name__ == "__main__":
    # 创建测试输入
    batch_size, seq_len, d_model = 2, 10, 512
    num_heads = 8
    
    x = torch.randn(batch_size, seq_len, d_model)
    
    # 创建注意力层
    mha = MultiHeadAttention(d_model, num_heads)
    
    # 前向传播
    output = mha(x)
    
    print(f"输入形状: {x.shape}")
    print(f"输出形状: {output.shape}")
    print(f"✅ 测试通过！")
'''
    }
    
    for file_path, new_content in template_improvements.items():
        path = Path(file_path)
        if path.exists():
            path.write_text(new_content, encoding='utf-8')
            print(f"✅ Updated {file_path}")

def main():
    print("🚀 Paper-OS 项目完善脚本")
    print("=" * 60)
    
    print("\n📝 第1步: 更新实现指南...")
    update_implementation_guides()
    
    print("\n📝 第2步: 创建快速测试脚本...")
    create_quick_test_scripts()
    
    print("\n📝 第3步: 改进代码模板...")
    create_project_template_improvements()
    
    print("\n" + "=" * 60)
    print("✅ 项目完善完成！")
    print("=" * 60)

if __name__ == "__main__":
    main()
