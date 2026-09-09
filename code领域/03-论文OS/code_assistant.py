"""
Paper-OS 智能代码助手
整合代码检索、生成、对比功能
"""
import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import defaultdict
import re


class CodeIndexer:
    """代码索引器 - 构建代码搜索索引"""
    
    def __init__(self, index_dir: str = "code_index"):
        self.index_dir = Path(index_dir)
        self.index_dir.mkdir(exist_ok=True)
        
        self.function_index = {}  # 函数名 -> 文件路径列表
        self.class_index = {}      # 类名 -> 文件路径列表
        self.keyword_index = defaultdict(list)  # 关键词 -> 代码片段列表
    
    def build_index(self, code_files: List[str]):
        """构建代码索引"""
        print("🔨 构建代码索引...")
        
        for file_path in code_files:
            self._index_file(file_path)
        
        # 保存索引
        self._save_index()
        
        print(f"✅ 索引构建完成!")
        print(f"   函数: {len(self.function_index)}")
        print(f"   类: {len(self.class_index)}")
        print(f"   关键词: {len(self.keyword_index)}")
    
    def _index_file(self, file_path: str):
        """索引单个文件"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # 提取函数
            functions = re.findall(r'def\s+(\w+)\s*\([^)]*\):', content)
            for func in functions:
                if func not in self.function_index:
                    self.function_index[func] = []
                self.function_index[func].append(file_path)
            
            # 提取类
            classes = re.findall(r'class\s+(\w+)\s*[:\(]', content)
            for cls in classes:
                if cls not in self.class_index:
                    self.class_index[cls] = []
                self.class_index[cls].append(file_path)
            
            # 提取关键词
            keywords = re.findall(r'\b(?:class|def|import|from|return|yield|async|await)\b', content)
            for keyword in set(keywords):
                self.keyword_index[keyword].append({
                    'file': file_path,
                    'count': content.count(keyword)
                })
            
        except Exception as e:
            print(f"  ⚠️  索引失败 {file_path}: {e}")
    
    def _save_index(self):
        """保存索引"""
        with open(self.index_dir / 'function_index.json', 'w', encoding='utf-8') as f:
            json.dump(self.function_index, f, indent=2)
        
        with open(self.index_dir / 'class_index.json', 'w', encoding='utf-8') as f:
            json.dump(self.class_index, f, indent=2)
        
        with open(self.index_dir / 'keyword_index.json', 'w', encoding='utf-8') as f:
            json.dump(self.keyword_index, f, indent=2)
    
    def load_index(self):
        """加载索引"""
        try:
            with open(self.index_dir / 'function_index.json', 'r', encoding='utf-8') as f:
                self.function_index = json.load(f)
            
            with open(self.index_dir / 'class_index.json', 'r', encoding='utf-8') as f:
                self.class_index = json.load(f)
            
            with open(self.index_dir / 'keyword_index.json', 'r', encoding='utf-8') as f:
                self.keyword_index = json.load(f)
            
            return True
        except:
            return False


class CodeAssistant:
    """智能代码助手"""
    
    def __init__(self, indexer: CodeIndexer, code_index_dir: str = "code_index"):
        self.indexer = indexer
        self.code_index_dir = Path(code_index_dir)
        
        # 加载代码分析结果
        self.code_analyses = self._load_code_analyses()
    
    def _load_code_analyses(self) -> Dict[str, Any]:
        """加载代码分析结果"""
        analyses = {}
        analysis_dir = Path("code_index")
        
        if analysis_dir.exists():
            for file_path in analysis_dir.glob("*_analysis.json"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        analysis = json.load(f)
                        analyses[analysis.get('project_name', file_path.stem)] = analysis
                except:
                    pass
        
        return analyses
    
    def search_function(self, function_name: str) -> List[Dict[str, Any]]:
        """搜索函数"""
        results = []
        
        if function_name in self.indexer.function_index:
            for file_path in self.indexer.function_index[function_name]:
                results.append({
                    'type': 'function',
                    'name': function_name,
                    'file': file_path
                })
        
        return results
    
    def search_class(self, class_name: str) -> List[Dict[str, Any]]:
        """搜索类"""
        results = []
        
        if class_name in self.indexer.class_index:
            for file_path in self.indexer.class_index[class_name]:
                results.append({
                    'type': 'class',
                    'name': class_name,
                    'file': file_path
                })
        
        return results
    
    def search_keyword(self, keyword: str) -> List[Dict[str, Any]]:
        """搜索关键词"""
        results = []
        
        if keyword in self.indexer.keyword_index:
            for item in self.indexer.keyword_index[keyword]:
                results.append({
                    'type': 'keyword',
                    'name': keyword,
                    'file': item['file'],
                    'count': item['count']
                })
        
        return results
    
    def search_code(self, query: str) -> List[Dict[str, Any]]:
        """综合搜索"""
        results = []
        
        # 搜索函数
        func_results = self.search_function(query)
        results.extend(func_results)
        
        # 搜索类
        class_results = self.search_class(query)
        results.extend(class_results)
        
        # 搜索关键词
        keyword_results = self.search_keyword(query)
        results.extend(keyword_results)
        
        return results
    
    def get_function_examples(self, function_name: str) -> List[str]:
        """获取函数示例"""
        examples = []
        
        for result in self.search_function(function_name):
            file_path = result['file']
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # 提取函数定义
                pattern = rf'def\s+{re.escape(function_name)}\s*\([^)]*\):.*?(?=\n(?:def |class ))'
                matches = re.findall(pattern, content, re.DOTALL)
                
                for match in matches:
                    # 限制示例长度
                    example = match[:500] + '...' if len(match) > 500 else match
                    examples.append(f"# {file_path}\n{example}")
                
            except:
                pass
        
        return examples
    
    def compare_implementations(self, function_name: str) -> List[Dict[str, Any]]:
        """对比不同实现"""
        implementations = []
        
        for result in self.search_function(function_name):
            file_path = result['file']
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # 提取函数信息
                func_pattern = rf'def\s+{re.escape(function_name)}\s*\([^)]*\):'
                if re.search(func_pattern, content):
                    implementations.append({
                        'file': file_path,
                        'project': self._get_project_name(file_path),
                        'lines': len(content.splitlines())
                    })
                
            except:
                pass
        
        return implementations
    
    def _get_project_name(self, file_path: str) -> str:
        """获取项目名称"""
        parts = Path(file_path).parts
        for i, part in enumerate(parts):
            if part in ['transformers', 'vllm', 'sglang', 'mmdetection']:
                return part
        return 'unknown'
    
    def generate_code_suggestion(self, description: str) -> str:
        """生成代码建议"""
        # 简单的关键词匹配
        suggestions = {
            'attention': '''
# 自注意力机制示例
import torch
import torch.nn as nn

class MultiHeadAttention(nn.Module):
    def __init__(self, d_model, num_heads):
        super().__init__()
        self.num_heads = num_heads
        self.d_model = d_model
        
        self.qkv_proj = nn.Linear(d_model, 3 * d_model)
        self.out_proj = nn.Linear(d_model, d_model)
    
    def forward(self, x):
        batch_size, seq_len, _ = x.shape
        qkv = self.qkv_proj(x)
        q, k, v = qkv.chunk(3, dim=-1)
        
        # 计算注意力
        attn = torch.matmul(q, k.transpose(-2, -1)) / (self.d_model ** 0.5)
        attn = torch.softmax(attn, dim=-1)
        out = torch.matmul(attn, v)
        
        return self.out_proj(out)
''',
            'resnet': '''
# ResNet残差块示例
import torch
import torch.nn as nn

class ResidualBlock(nn.Module):
    def __init__(self, in_channels, out_channels, stride=1):
        super().__init__()
        self.conv1 = nn.Conv2d(in_channels, out_channels, 3, stride, 1)
        self.bn1 = nn.BatchNorm2d(out_channels)
        self.conv2 = nn.Conv2d(out_channels, out_channels, 3, 1, 1)
        self.bn2 = nn.BatchNorm2d(out_channels)
        
        self.shortcut = nn.Sequential()
        if stride != 1 or in_channels != out_channels:
            self.shortcut = nn.Sequential(
                nn.Conv2d(in_channels, out_channels, 1, stride),
                nn.BatchNorm2d(out_channels)
            )
    
    def forward(self, x):
        out = F.relu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))
        return F.relu(out + self.shortcut(x))
''',
            'diffusion': '''
# 扩散模型示例
import torch
import torch.nn as nn

class DiffusionModel(nn.Module):
    def __init__(self, in_channels, time_emb_dim=256):
        super().__init__()
        self.time_embed = nn.Sequential(
            nn.Linear(time_emb_dim, time_emb_dim),
            nn.SiLU(),
            nn.Linear(time_emb_dim, time_emb_dim)
        )
        self.conv1 = nn.Conv2d(in_channels, 64, 3, padding=1)
        self.conv2 = nn.Conv2d(64, 128, 3, padding=1)
        self.conv_out = nn.Conv2d(128, in_channels, 3, padding=1)
    
    def forward(self, x, t):
        t_emb = self.time_embed(t)
        h = F.relu(self.conv1(x))
        h = F.relu(self.conv2(h))
        return self.conv_out(h)
'''
        }
        
        # 简单的关键词匹配
        for keyword, suggestion in suggestions.items():
            if keyword in description.lower():
                return suggestion
        
        return "# 代码建议：请提供更具体的功能描述"
    
    def interactive_mode(self):
        """交互式模式"""
        print("\n" + "=" * 60)
        print("🤖 Paper-OS 智能代码助手")
        print("=" * 60)
        print("\n功能:")
        print("  1. 搜索函数/类")
        print("  2. 查看代码示例")
        print("  3. 对比实现")
        print("  4. 生成代码建议")
        print("  0. 退出")
        print("=" * 60)
        
        while True:
            print("\n" + "-" * 60)
            choice = input("选择功能 (0-4): ").strip()
            
            if choice == '0':
                print("\n👋 感谢使用!")
                break
            elif choice == '1':
                self._search_mode()
            elif choice == '2':
                self._example_mode()
            elif choice == '3':
                self._compare_mode()
            elif choice == '4':
                self._suggest_mode()
            else:
                print("⚠️  无效选择")
    
    def _search_mode(self):
        """搜索模式"""
        query = input("输入搜索内容 (函数名/类名/关键词): ").strip()
        if not query:
            return
        
        results = self.search_code(query)
        
        if not results:
            print(f"\n❌ 未找到: {query}")
            return
        
        print(f"\n🔍 搜索结果: {query}")
        print("-" * 60)
        
        for result in results[:10]:
            type_icon = {'function': '📦', 'class': '📁', 'keyword': '🔑'}
            print(f"{type_icon.get(result['type'], '•')} [{result['type']}] {result['name']}")
            print(f"   文件: {result['file']}")
            if 'count' in result:
                print(f"   出现次数: {result['count']}")
            print()
    
    def _example_mode(self):
        """示例模式"""
        query = input("输入函数名: ").strip()
        if not query:
            return
        
        examples = self.get_function_examples(query)
        
        if not examples:
            print(f"\n❌ 未找到示例: {query}")
            return
        
        print(f"\n💡 代码示例: {query}")
        print("-" * 60)
        
        for i, example in enumerate(examples[:3], 1):
            print(f"\n示例 {i}:")
            print(example)
            print("-" * 40)
    
    def _compare_mode(self):
        """对比模式"""
        query = input("输入函数名: ").strip()
        if not query:
            return
        
        implementations = self.compare_implementations(query)
        
        if not implementations:
            print(f"\n❌ 未找到实现: {query}")
            return
        
        print(f"\n🔄 实现对比: {query}")
        print("-" * 60)
        
        for i, impl in enumerate(implementations, 1):
            print(f"\n实现 {i}:")
            print(f"  项目: {impl['project']}")
            print(f"  文件: {impl['file']}")
            print(f"  代码行数: {impl['lines']}")
    
    def _suggest_mode(self):
        """建议模式"""
        description = input("描述你想要的功能: ").strip()
        if not description:
            return
        
        suggestion = self.generate_code_suggestion(description)
        
        print(f"\n💡 代码建议:")
        print("-" * 60)
        print(suggestion)


def main():
    """主函数"""
    # 检查索引是否存在
    indexer = CodeIndexer()
    
    if not indexer.load_index():
        print("🔨 首次运行，正在构建索引...")
        
        # 查找所有Python文件
        python_files = []
        for project_dir in ['transformers', 'vllm', 'sglang', 'mmdetection', 'mmsegmentation']:
            if os.path.exists(project_dir):
                for file_path in Path(project_dir).rglob('*.py'):
                    python_files.append(str(file_path))
        
        print(f"找到 {len(python_files)} 个Python文件")
        
        if python_files:
            indexer.build_index(python_files)
        else:
            print("⚠️  未找到Python文件")
    else:
        print("✅ 加载索引完成")
    
    # 启动助手
    assistant = CodeAssistant(indexer)
    assistant.interactive_mode()


if __name__ == "__main__":
    main()
