"""
Paper-OS 代码实践体系生成器
"""
import os
from data_manager import DatabaseManager
from utils import ConfigManager, QuizGenerator, CodeTemplateGenerator
from pathlib import Path


class CodePracticeGenerator:
    def __init__(self, db_manager: DatabaseManager, base_dir: str):
        self.db = db_manager
        self.base_dir = Path(base_dir)
        self.practice_dir = self.base_dir / "code_practice"
        self.quiz_generator = QuizGenerator()
        self.code_generator = CodeTemplateGenerator()
        
        self.practice_dir.mkdir(exist_ok=True)
        
        self.category_templates = {
            'Transformer基础': self._generate_transformer_practice,
            '生成模型': self._generate_diffusion_practice,
            '视觉模型': self._generate_resnet_practice,
            '大语言模型': self._generate_llm_practice,
            'RAG与检索增强': self._generate_rag_practice,
            '推理与思维链': self._generate_reasoning_practice,
            '优化与压缩': self._generate_optimization_practice,
            '多模态': self._generate_multimodal_practice,
            'RL与Agent': self._generate_rl_practice
        }

    def generate_all_practices(self):
        """为所有论文生成实践练习"""
        print("🔧 生成代码实践体系...")
        print("=" * 60)
        
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT DISTINCT category FROM papers WHERE category IS NOT NULL")
        categories = cursor.fetchall()
        
        for cat in categories:
            category = cat[0]
            if category in self.category_templates:
                print(f"\n 生成 {category} 实践练习...")
                self.category_templates[category](category)
        
        print("\n" + "=" * 60)
        print("✅ 代码实践体系生成完成!")

    def _generate_transformer_practice(self, category: str):
        """生成Transformer实践练习"""
        category_dir = self.practice_dir / category
        category_dir.mkdir(exist_ok=True)
        
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT * FROM papers WHERE category = ?", (category,))
        papers = cursor.fetchall()
        
        exercises = [
            {
                'name': '01_attention_mechanism',
                'title': '自注意力机制实现',
                'difficulty': '初级',
                'description': '实现基础的自注意力机制，理解Q、K、V的计算',
                'tasks': [
                    '实现单头注意力计算',
                    '实现多头注意力机制',
                    '添加位置编码',
                    '测试不同序列长度的性能'
                ],
                'template': self.code_generator.generate_transformer_template()
            },
            {
                'name': '02_encoder_decoder',
                'title': '编码器-解码器架构',
                'difficulty': '中级',
                'description': '构建完整的Transformer编码器-解码器架构',
                'tasks': [
                    '实现Transformer Block',
                    '构建编码器层',
                    '构建解码器层',
                    '实现端到端翻译任务'
                ],
                'template': '''
from attention import MultiHeadAttention

class TransformerEncoderLayer(nn.Module):
    def __init__(self, d_model, num_heads, d_ff, dropout=0.1):
        super().__init__()
        self.attention = MultiHeadAttention(d_model, num_heads)
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        self.ffn = nn.Sequential(
            nn.Linear(d_model, d_ff),
            nn.ReLU(),
            nn.Linear(d_ff, d_model)
        )
        self.dropout = nn.Dropout(dropout)
    
    def forward(self, x, mask=None):
        # TODO: 实现前向传播
        pass

class TransformerDecoderLayer(nn.Module):
    def __init__(self, d_model, num_heads, d_ff, dropout=0.1):
        super().__init__()
        self.self_attention = MultiHeadAttention(d_model, num_heads)
        self.cross_attention = MultiHeadAttention(d_model, num_heads)
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        self.norm3 = nn.LayerNorm(d_model)
        self.ffn = nn.Sequential(
            nn.Linear(d_model, d_ff),
            nn.ReLU(),
            nn.Linear(d_ff, d_model)
        )
        self.dropout = nn.Dropout(dropout)
    
    def forward(self, x, enc_output, self_mask=None, cross_mask=None):
        # TODO: 实现前向传播
        pass
'''
            },
            {
                'name': '03_bert_pretraining',
                'title': 'BERT预训练任务',
                'difficulty': '高级',
                'description': '实现BERT的MLM和NSP预训练任务',
                'tasks': [
                    '实现Masked Language Model',
                    '实现Next Sentence Prediction',
                    '构建预训练数据加载器',
                    '训练小规模BERT模型'
                ],
                'template': '''
class BERTPretrainer(nn.Module):
    def __init__(self, vocab_size, d_model=768, num_heads=12):
        super().__init__()
        self.bert = BERTModel(vocab_size, d_model, num_heads)
        self.mlm_head = nn.Linear(d_model, vocab_size)
        self.nsp_head = nn.Linear(d_model, 2)
    
    def forward(self, input_ids, attention_mask, token_type_ids, masked_positions):
        # TODO: 实现MLM和NSP任务
        pass

# TODO: 实现预训练数据生成和训练循环
'''
            }
        ]
        
        for exercise in exercises:
            self._write_exercise(category_dir, exercise)

    def _generate_diffusion_practice(self, category: str):
        """生成扩散模型实践练习"""
        category_dir = self.practice_dir / category
        category_dir.mkdir(exist_ok=True)
        
        exercises = [
            {
                'name': '01_ddpm_implementation',
                'title': 'DDPM模型实现',
                'difficulty': '中级',
                'description': '从零实现Denoising Diffusion Probabilistic Models',
                'tasks': [
                    '实现前向扩散过程（添加噪声）',
                    '实现逆向去噪过程',
                    '构建U-Net架构',
                    '实现训练循环'
                ],
                'template': self.code_generator.generate_diffusion_template()
            },
            {
                'name': '02_conditional_diffusion',
                'title': '条件扩散模型',
                'difficulty': '高级',
                'description': '实现基于条件的扩散模型（如Stable Diffusion）',
                'tasks': [
                    '添加条件信息到模型',
                    '实现文本编码器集成',
                    '实现Classifier-free Guidance',
                    '实现文本到图像生成'
                ],
                'template': '''
class ConditionalDiffusionModel(nn.Module):
    def __init__(self, in_channels, text_emb_dim, time_emb_dim=256):
        super().__init__()
        self.text_encoder = TextEncoder(text_emb_dim)
        self.time_embed = nn.Linear(time_emb_dim, time_emb_dim)
        
        # TODO: 构建U-Net架构
        self.down_blocks = nn.ModuleList()
        self.up_blocks = nn.ModuleList()
    
    def forward(self, x, t, text):
        t_emb = self.time_embed(t)
        text_emb = self.text_encoder(text)
        
        # TODO: 结合文本和时间信息
        pass

# TODO: 实现 Classifier-free Guidance 采样
'''
            },
            {
                'name': '03_latent_diffusion',
                'title': '潜在空间扩散模型',
                'difficulty': '高级',
                'description': '实现Stable Diffusion的Latent Diffusion架构',
                'tasks': [
                    '实现VAE编码器/解码器',
                    '在潜在空间训练扩散模型',
                    '实现文本到图像流程',
                    '优化采样质量和速度'
                ],
                'template': '''
class VAE(nn.Module):
    def __init__(self, in_channels=3, latent_dim=4):
        super().__init__()
        self.encoder = nn.Sequential(
            # TODO: 实现编码器
            pass
        )
        self.decoder = nn.Sequential(
            # TODO: 实现解码器
            pass
        )
    
    def encode(self, x):
        # TODO: 编码到潜在空间
        pass
    
    def decode(self, z):
        # TODO: 从潜在空间解码
        pass

class LatentDiffusion(nn.Module):
    def __init__(self, vae, diffusion_model):
        super().__init__()
        self.vae = vae
        self.diffusion = diffusion_model
    
    def forward(self, x, text):
        latent = self.vae.encode(x)
        # TODO: 在潜在空间训练扩散模型
        pass
'''
            }
        ]
        
        for exercise in exercises:
            self._write_exercise(category_dir, exercise)

    def _generate_resnet_practice(self, category: str):
        """生成ResNet实践练习"""
        category_dir = self.practice_dir / category
        category_dir.mkdir(exist_ok=True)
        
        exercises = [
            {
                'name': '01_residual_block',
                'title': '残差块实现',
                'difficulty': '初级',
                'description': '实现ResNet的核心残差块结构',
                'tasks': [
                    '实现BasicBlock',
                    '实现Bottleneck',
                    '添加Batch Normalization',
                    '测试梯度流动'
                ],
                'template': self.code_generator.generate_resnet_template()
            },
            {
                'name': '02_resnet_architecture',
                'title': 'ResNet完整架构',
                'difficulty': '中级',
                'description': '构建ResNet-18/34/50/101等完整架构',
                'tasks': [
                    '实现ResNet-18',
                    '实现ResNet-34',
                    '实现ResNet-50 (Bottleneck)',
                    '在ImageNet上测试'
                ],
                'template': '''
class ResNet(nn.Module):
    def __init__(self, block, layers, num_classes=1000):
        super().__init__()
        self.in_channels = 64
        self.conv1 = nn.Conv2d(3, 64, 7, 2, 3)
        self.bn1 = nn.BatchNorm2d(64)
        self.maxpool = nn.MaxPool2d(3, 2, 1)
        
        self.layer1 = self._make_layer(block, 64, layers[0])
        self.layer2 = self._make_layer(block, 128, layers[1], stride=2)
        self.layer3 = self._make_layer(block, 256, layers[2], stride=2)
        self.layer4 = self._make_layer(block, 512, layers[3], stride=2)
        
        self.avgpool = nn.AdaptiveAvgPool2d(1)
        self.fc = nn.Linear(512 * block.expansion, num_classes)
    
    def _make_layer(self, block, out_channels, blocks, stride=1):
        # TODO: 实现层构建
        pass
    
    def forward(self, x):
        # TODO: 实现前向传播
        pass

def resnet18(num_classes=1000):
    return ResNet(BasicBlock, [2, 2, 2, 2], num_classes)

def resnet50(num_classes=1000):
    return ResNet(Bottleneck, [3, 4, 6, 3], num_classes)
'''
            },
            {
                'name': '03_image_classification',
                'title': '图像分类应用',
                'difficulty': '中级',
                'description': '使用ResNet进行实际图像分类任务',
                'tasks': [
                    '准备CIFAR-10数据集',
                    '实现数据增强',
                    '训练ResNet分类器',
                    '可视化注意力图'
                ],
                'template': '''
import torch
import torchvision
import torchvision.transforms as transforms

def get_cifar10_loaders(batch_size=128):
    transform = transforms.Compose([
        transforms.RandomCrop(32, padding=4),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
    ])
    
    trainset = torchvision.datasets.CIFAR10(root='./data', train=True,
                                          download=True, transform=transform)
    trainloader = torch.utils.data.DataLoader(trainset, batch_size=batch_size,
                                             shuffle=True, num_workers=2)
    
    # TODO: 加载测试集
    return trainloader, testloader

def train_model(model, trainloader, epochs=100):
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.SGD(model.parameters(), lr=0.1,
                                momentum=0.9, weight_decay=5e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)
    
    # TODO: 实现训练循环
    pass
'''
            }
        ]
        
        for exercise in exercises:
            self._write_exercise(category_dir, exercise)

    def _generate_llm_practice(self, category: str):
        """生成LLM实践练习"""
        category_dir = self.practice_dir / category
        category_dir.mkdir(exist_ok=True)
        
        exercises = [
            {
                'name': '01_gpt_training',
                'title': 'GPT模型训练',
                'difficulty': '高级',
                'description': '训练一个简单的GPT风格语言模型',
                'tasks': [
                    '实现GPT架构',
                    '准备文本数据',
                    '实现因果注意力掩码',
                    '训练语言模型'
                ],
                'template': '''
class GPT(nn.Module):
    def __init__(self, vocab_size, d_model=768, n_heads=12, n_layers=12, 
                 max_seq_len=1024):
        super().__init__()
        self.token_emb = nn.Embedding(vocab_size, d_model)
        self.pos_emb = nn.Embedding(max_seq_len, d_model)
        
        self.layers = nn.ModuleList([
            TransformerBlock(d_model, n_heads) for _ in range(n_layers)
        ])
        
        self.ln_f = nn.LayerNorm(d_model)
        self.lm_head = nn.Linear(d_model, vocab_size, bias=False)
    
    def forward(self, idx):
        B, T = idx.shape
        tok_emb = self.token_emb(idx)
        pos_emb = self.pos_emb(torch.arange(T, device=idx.device))
        x = tok_emb + pos_emb
        
        for layer in self.layers:
            x = layer(x)
        
        x = self.ln_f(x)
        return self.lm_head(x)

# TODO: 实现训练循环
'''
            }
        ]
        
        for exercise in exercises:
            self._write_exercise(category_dir, exercise)

    def _generate_rag_practice(self, category: str):
        """生成RAG实践练习"""
        category_dir = self.practice_dir / category
        category_dir.mkdir(exist_ok=True)
        
        exercises = [
            {
                'name': '01_basic_rag',
                'title': '基础RAG系统',
                'difficulty': '中级',
                'description': '实现一个基础的检索增强生成系统',
                'tasks': [
                    '实现文本嵌入',
                    '构建向量数据库',
                    '实现相似度搜索',
                    '集成LLM生成'
                ],
                'template': '''
from sentence_transformers import SentenceTransformer

class RAGSystem:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        self.embedder = SentenceTransformer(model_name)
        self.documents = []
        self.embeddings = None
    
    def add_documents(self, docs):
        self.documents.extend(docs)
        if self.embeddings is None:
            self.embeddings = self.embedder.encode(docs)
        else:
            new_embeddings = self.embedder.encode(docs)
            self.embeddings = np.vstack([self.embeddings, new_embeddings])
    
    def retrieve(self, query, top_k=5):
        query_embedding = self.embedder.encode([query])
        similarities = np.dot(self.embeddings, query_embedding.T).flatten()
        top_indices = similarities.argsort()[-top_k:][::-1]
        return [self.documents[i] for i in top_indices]

# TODO: 集成LLM生成
'''
            }
        ]
        
        for exercise in exercises:
            self._write_exercise(category_dir, exercise)

    def _generate_reasoning_practice(self, category: str):
        """生成推理实践练习"""
        category_dir = self.practice_dir / category
        category_dir.mkdir(exist_ok=True)
        
        exercises = [
            {
                'name': '01_chain_of_thought',
                'title': '思维链提示',
                'difficulty': '中级',
                'description': '实现和使用思维链提示技术',
                'tasks': [
                    '实现CoT提示模板',
                    '构建few-shot示例',
                    '测试推理能力',
                    '对比不同提示方法'
                ],
                'template': '''
class ChainOfThoughtPrompter:
    def __init__(self, llm_client):
        self.llm = llm_client
        self.few_shot_examples = [
            {
                "question": "Roger有5个网球。他又买了2罐网球，每罐有3个球。他现在有几个网球？",
                "reasoning": "Roger一开始有5个球。2罐 × 每罐3个球 = 6个球。5 + 6 = 11。",
                "answer": "11"
            }
        ]
    
    def format_prompt(self, question):
        examples = "\\n\\n".join([
            f"问题: {ex['question']}\\n推理: {ex['reasoning']}\\n答案: {ex['answer']}"
            for ex in self.few_shot_examples
        ])
        prompt = f"{examples}\\n\\n问题: {question}\\n推理:"
        return prompt
    
    def generate(self, question):
        prompt = self.format_prompt(question)
        return self.llm.generate(prompt)

# TODO: 测试不同的CoT变体
'''
            }
        ]
        
        for exercise in exercises:
            self._write_exercise(category_dir, exercise)

    def _generate_optimization_practice(self, category: str):
        """生成优化技术实践练习"""
        category_dir = self.practice_dir / category
        category_dir.mkdir(exist_ok=True)
        
        exercises = [
            {
                'name': '01_lora_finetuning',
                'title': 'LoRA微调',
                'difficulty': '中级',
                'description': '实现LoRA（Low-Rank Adaptation）微调方法',
                'tasks': [
                    '实现LoRA层',
                    '冻结原始模型权重',
                    '训练低秩适配器',
                    '对比全参数微调'
                ],
                'template': '''
class LoRALayer(nn.Module):
    def __init__(self, in_features, out_features, rank=4, alpha=1):
        super().__init__()
        self.rank = rank
        self.alpha = alpha
        self.scaling = alpha / rank
        
        self.lora_A = nn.Parameter(torch.zeros(rank, in_features))
        self.lora_B = nn.Parameter(torch.zeros(out_features, rank))
        
        nn.init.kaiming_uniform_(self.lora_A, a=math.sqrt(5))
        nn.init.zeros_(self.lora_B)
    
    def forward(self, x):
        return self.scaling * (x @ self.lora_A.T @ self.lora_B.T)

def apply_lora_to_linear(linear_layer, rank=4):
    # TODO: 将LoRA应用到Linear层
    pass

# TODO: 实现LoRA微调流程
'''
            }
        ]
        
        for exercise in exercises:
            self._write_exercise(category_dir, exercise)

    def _generate_multimodal_practice(self, category: str):
        """生成多模态实践练习"""
        category_dir = self.practice_dir / category
        category_dir.mkdir(exist_ok=True)
        
        exercises = [
            {
                'name': '01_clip_training',
                'title': 'CLIP模型训练',
                'difficulty': '高级',
                'description': '实现CLIP（Contrastive Language-Image Pre-training）',
                'tasks': [
                    '实现图像编码器',
                    '实现文本编码器',
                    '实现对比学习损失',
                    '训练CLIP模型'
                ],
                'template': '''
import torch.nn.functional as F

class CLIP(nn.Module):
    def __init__(self, image_encoder, text_encoder, embed_dim=512):
        super().__init__()
        self.image_encoder = image_encoder
        self.text_encoder = text_encoder
        
        self.image_projection = nn.Linear(image_encoder.output_dim, embed_dim)
        self.text_projection = nn.Linear(text_encoder.output_dim, embed_dim)
        
        self.logit_scale = nn.Parameter(torch.ones([]) * np.log(1 / 0.07))
    
    def forward(self, images, texts):
        image_features = self.image_projection(self.image_encoder(images))
        text_features = self.text_projection(self.text_encoder(texts))
        
        image_features = F.normalize(image_features, dim=-1)
        text_features = F.normalize(text_features, dim=-1)
        
        logits = (image_features @ text_features.T) * self.logit_scale.exp()
        
        labels = torch.arange(logits.shape[0], device=logits.device)
        loss_i = F.cross_entropy(logits, labels)
        loss_t = F.cross_entropy(logits.T, labels)
        loss = (loss_i + loss_t) / 2
        
        return loss

# TODO: 实现训练循环
'''
            }
        ]
        
        for exercise in exercises:
            self._write_exercise(category_dir, exercise)

    def _generate_rl_practice(self, category: str):
        """生成强化学习实践练习"""
        category_dir = self.practice_dir / category
        category_dir.mkdir(exist_ok=True)
        
        exercises = [
            {
                'name': '01_ppo_training',
                'title': 'PPO算法实现',
                'difficulty': '高级',
                'description': '实现Proximal Policy Optimization（PPO）算法',
                'tasks': [
                    '实现Actor-Critic网络',
                    '实现PPO损失函数',
                    '实现GAE（Generalized Advantage Estimation）',
                    '在简单环境中测试'
                ],
                'template': '''
class PPO:
    def __init__(self, actor_critic, clip_ratio=0.2, target_kl=0.01):
        self.actor_critic = actor_critic
        self.clip_ratio = clip_ratio
        self.target_kl = target_kl
        self.optimizer = torch.optim.Adam(actor_critic.parameters(), lr=3e-4)
    
    def compute_loss(self, batch):
        states, actions, old_logp, advantages, returns = batch
        
        # 计算新的策略概率
        pi, value = self.actor_critic(states)
        logp = self.actor_critic.get_log_prob(pi, actions)
        
        # 计算比率
        ratio = torch.exp(logp - old_logp)
        
        # PPO clipped损失
        surr1 = ratio * advantages
        surr2 = torch.clamp(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio) * advantages
        policy_loss = -torch.min(surr1, surr2).mean()
        
        # 价值函数损失
        value_loss = F.mse_loss(value, returns)
        
        # KL散度惩罚
        approx_kl = (old_logp - logp).mean()
        
        return policy_loss + value_loss - 0.5 * approx_kl

# TODO: 实现训练循环和GAE
'''
            }
        ]
        
        for exercise in exercises:
            self._write_exercise(category_dir, exercise)

    def _write_exercise(self, category_dir: Path, exercise: dict):
        """写入练习文件"""
        exercise_dir = category_dir / exercise['name']
        exercise_dir.mkdir(exist_ok=True)
        
        readme_content = f"""# {exercise['title']}

**难度**: {exercise['difficulty']}
**描述**: {exercise['description']}

## 学习任务

"""
        for i, task in enumerate(exercise['tasks'], 1):
            readme_content += f"{i}. {task}\n"
        
        readme_content += f"""

## 代码模板

参见 `template.py` 文件。

## 实现指南

1. 阅读 `template.py` 中的TODO注释
2. 按照学习任务的顺序逐步实现
3. 参考相关论文和应用代码
4. 测试每个模块的功能

## 参考资料

- 相关论文
- HuggingFace Transformers库
- PyTorch文档
"""
        
        with open(exercise_dir / 'README.md', 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        with open(exercise_dir / 'template.py', 'w', encoding='utf-8') as f:
            f.write(exercise.get('template', '# TODO: 实现这个练习\n'))
        
        print(f"  ✓ {exercise['title']}")


def main():
    config = ConfigManager()
    db_manager = DatabaseManager(config.get('paths.db_file', 'data/paper_os.db'))
    
    generator = CodePracticeGenerator(db_manager, config.get('paths.base_dir', '.'))
    generator.generate_all_practices()
    
    db_manager.close()


if __name__ == "__main__":
    main()
