"""
Paper-OS 工具类和实用函数
"""
import os
import json
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path


class ConfigManager:
    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self.config = self.load_config()

    def load_config(self) -> Dict[str, Any]:
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return self.get_default_config()

    def get_default_config(self) -> Dict[str, Any]:
        return {
            "project": {
                "name": "Paper-OS",
                "version": "1.0.0"
            },
            "paths": {
                "base_dir": os.getcwd(),
                "data_dir": "data",
                "papers_dir": "learning_paths_by_report/extended_papers",
                "export_dir": "exports"
            }
        }

    def get(self, key_path: str, default: Any = None) -> Any:
        keys = key_path.split('.')
        value = self.config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value

    def save(self):
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)


class PaperParser:
    @staticmethod
    def parse_arxiv_id(text: str) -> Optional[str]:
        pattern = r'(\d{4}\.\d{4,5})'
        match = re.search(pattern, text)
        return match.group(1) if match else None

    @staticmethod
    def extract_authors(authors_text: str) -> str:
        if not authors_text or authors_text == "Unknown":
            return "Unknown"
        if " et al." in authors_text:
            return authors_text
        if len(authors_text) > 100:
            return authors_text.split(',')[0] + " et al."
        return authors_text

    @staticmethod
    def parse_difficulty(difficulty_text: str) -> str:
        if "初级" in difficulty_text:
            return "初级"
        elif "中级" in difficulty_text:
            return "中级"
        elif "高级" in difficulty_text:
            return "高级"
        else:
            return "中级"

    @staticmethod
    def parse_importance(importance_text: str) -> int:
        if "极高影响力" in importance_text:
            return 5
        elif "高影响力" in importance_text:
            return 4
        elif "中等影响力" in importance_text:
            return 3
        elif "低影响力" in importance_text:
            return 2
        elif "新兴论文" in importance_text:
            return 1
        return 3

    @staticmethod
    def normalize_filename(filename: str) -> str:
        return filename.replace(' ', '_').replace('/', '_')


class FileOrganizer:
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)

    def ensure_directories(self):
        dirs = [
            "data",
            "exports",
            "logs",
            "interactive_learning",
            "code_practice",
            "knowledge_graph",
            "ai_qa"
        ]
        for dir_name in dirs:
            (self.base_dir / dir_name).mkdir(exist_ok=True)

    def find_pdf_files(self, search_dir: str) -> List[str]:
        search_path = Path(search_dir)
        pdf_files = []
        for pdf_file in search_path.rglob("*.pdf"):
            pdf_files.append(str(pdf_file))
        return pdf_files

    def find_markdown_files(self, search_dir: str) -> List[str]:
        search_path = Path(search_dir)
        md_files = []
        for md_file in search_path.rglob("*.md"):
            md_files.append(str(md_file))
        return md_files


class ProgressCalculator:
    @staticmethod
    def calculate_overall_progress(progress_data: List[Dict[str, Any]]) -> float:
        if not progress_data:
            return 0.0
        total = len(progress_data)
        completed = sum(1 for p in progress_data if p.get('status') == 'completed')
        return round((completed / total) * 100, 2)

    @staticmethod
    def calculate_path_progress(path_papers: List[Dict[str, Any]]) -> float:
        if not path_papers:
            return 0.0
        reading_progress = sum(p.get('reading_progress', 0) for p in path_papers)
        return round(reading_progress / len(path_papers), 2)

    @staticmethod
    def estimate_completion_time(total_papers: int, completed_papers: int, 
                                   weeks_per_paper: float = 2.0) -> str:
        remaining = total_papers - completed_papers
        weeks = remaining * weeks_per_paper
        if weeks < 1:
            return f"{int(weeks * 7)}天"
        elif weeks < 4:
            return f"{int(weeks)}周"
        else:
            months = weeks / 4
            return f"{int(months)}个月"


class DataExporter:
    @staticmethod
    def export_to_json(data: Any, output_path: str):
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    @staticmethod
    def export_to_markdown(data: Dict[str, Any], output_path: str):
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# Paper-OS 学习报告\n\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            for key, value in data.items():
                f.write(f"## {key}\n\n")
                if isinstance(value, dict):
                    for k, v in value.items():
                        f.write(f"- **{k}**: {v}\n")
                elif isinstance(value, list):
                    for item in value:
                        f.write(f"- {item}\n")
                else:
                    f.write(f"{value}\n")
                f.write("\n")

    @staticmethod
    def export_progress_report(progress_data: List[Dict[str, Any]], output_path: str):
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# 学习进度报告\n\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            completed = sum(1 for p in progress_data if p.get('status') == 'completed')
            in_progress = sum(1 for p in progress_data if p.get('status') == 'in_progress')
            not_started = sum(1 for p in progress_data if p.get('status') == 'not_started')
            
            f.write("## 总体统计\n\n")
            f.write(f"- 已完成: {completed}\n")
            f.write(f"- 进行中: {in_progress}\n")
            f.write(f"- 未开始: {not_started}\n\n")
            
            f.write("## 详细进度\n\n")
            for paper in progress_data:
                status_emoji = {
                    'completed': '✅',
                    'in_progress': '🔄',
                    'not_started': '⏸️'
                }.get(paper.get('status', 'not_started'), '⏸️')
                
                f.write(f"{status_emoji} **{paper.get('title')}**\n")
                f.write(f"   - 进度: {paper.get('reading_progress', 0)}%\n")
                if paper.get('rating'):
                    stars = '⭐' * paper['rating']
                    f.write(f"   - 评分: {stars}\n")
                if paper.get('notes'):
                    f.write(f"   - 笔记: {paper['notes'][:50]}...\n")
                f.write("\n")


class QuizGenerator:
    @staticmethod
    def generate_basic_quizzes(paper: Dict[str, Any]) -> List[Dict[str, Any]]:
        quizzes = []
        
        quizzes.append({
            'question': f"这篇论文《{paper.get('title')}》的主要作者是谁？",
            'options': [paper.get('authors'), "Unknown", "OpenAI", "Google Brain"],
            'correct_answer': 0,
            'explanation': f"论文的主要作者是 {paper.get('authors')}",
            'difficulty': '简单'
        })
        
        quizzes.append({
            'question': f"这篇论文发表于哪一年？",
            'options': [str(paper.get('year', 2020)), "2021", "2022", "2023"],
            'correct_answer': 0,
            'explanation': f"论文发表于 {paper.get('year', 2020)} 年",
            'difficulty': '简单'
        })
        
        quizzes.append({
            'question': f"这篇论文的引用次数大约是多少？",
            'options': [
                f"~{paper.get('citation_count', 0)}",
                "1000+",
                "10000+",
                "50000+"
            ],
            'correct_answer': 0,
            'explanation': f"论文引用次数约为 {paper.get('citation_count', 0)}",
            'difficulty': '简单'
        })
        
        return quizzes

    @staticmethod
    def generate_concept_quizzes(category: str) -> List[Dict[str, Any]]:
        quizzes = []
        
        category_quizzes = {
            'Transformer基础': [
                {
                    'question': "Transformer架构的核心创新是什么？",
                    'options': ["自注意力机制", "卷积层", "循环层", "池化层"],
                    'correct_answer': 0,
                    'explanation': "Transformer通过自注意力机制捕获序列中的长距离依赖",
                    'difficulty': '中等'
                }
            ],
            '生成模型': [
                {
                    'question': "扩散模型在生成过程中的关键是？",
                    'options': ["逐步去噪", "直接生成", "随机采样", "反向传播"],
                    'correct_answer': 0,
                    'explanation': "扩散模型通过逐步去除噪声来生成样本",
                    'difficulty': '中等'
                }
            ]
        }
        
        return category_quizzes.get(category, [])


class CodeTemplateGenerator:
    @staticmethod
    def generate_transformer_template() -> str:
        return '''
import torch
import torch.nn as nn

class MultiHeadAttention(nn.Module):
    def __init__(self, d_model, num_heads):
        super().__init__()
        self.d_model = d_model
        self.num_heads = num_heads
        self.head_dim = d_model // num_heads
        
        self.qkv_proj = nn.Linear(d_model, 3 * d_model)
        self.out_proj = nn.Linear(d_model, d_model)
    
    def forward(self, x):
        batch_size, seq_len, _ = x.shape
        qkv = self.qkv_proj(x)
        q, k, v = qkv.chunk(3, dim=-1)
        
        q = q.view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        k = k.view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        v = v.view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        
        attn = torch.matmul(q, k.transpose(-2, -1)) / (self.head_dim ** 0.5)
        attn = torch.softmax(attn, dim=-1)
        out = torch.matmul(attn, v)
        
        out = out.transpose(1, 2).contiguous().view(batch_size, seq_len, self.d_model)
        return self.out_proj(out)

# TODO: 实现完整的Transformer层
'''

    @staticmethod
    def generate_diffusion_template() -> str:
        return '''
import torch
import torch.nn as nn
import torch.nn.functional as F

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
        
        h = F.silu(self.conv1(x))
        h = F.silu(self.conv2(h))
        return self.conv_out(h)

# TODO: 实现训练循环和采样过程
'''

    @staticmethod
    def generate_resnet_template() -> str:
        return '''
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

# TODO: 实现完整的ResNet架构
'''
