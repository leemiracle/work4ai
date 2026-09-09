#!/usr/bin/env python3
import json
from pathlib import Path

PROJECT_ROOT = Path("/home/lwz/learn-os/paper-os")
EXTENDED_PAPERS_DIR = PROJECT_ROOT / "learning_paths_by_report" / "extended_papers"

# 论文深度解读内容（基于AI情报挖掘）
PAPER_DEEP_ANALYSIS = {
    "1706.03762": {
        "core_contributions": [
            "提出了Transformer架构，完全基于注意力机制，不使用RNN或CNN",
            "引入了多头自注意力机制，让模型能同时关注不同的位置",
            "提出了位置编码来处理序列中的位置信息"
        ],
        "key_innovations": [
            "自注意力机制（Self-Attention）",
            "多头注意力（Multi-Head Attention）",
            "位置编码（Positional Encoding）",
            "编码器-解码器架构"
        ],
        "experimental_results": [
            "在WMT 2014英德翻译任务上达到28.4 BLEU，超过此前最佳模型2个BLEU",
            "在WMT 2014英法翻译任务上达到41.8 BLEU",
            "训练时间远少于RNN/CNN模型"
        ],
        "applications": [
            "机器翻译",
            "文本摘要",
            "问答系统",
            "语言模型"
        ],
        "related_papers": [
            "BERT (1810.04805)",
            "GPT (1706.03762)",
            "ViT (2010.11929)"
        ],
        "my_understanding": """
Transformer是现代AI的基石，它彻底改变了NLP领域。

核心思想：
1. 自注意力机制让模型能够捕捉长距离依赖关系
2. 并行化计算使得训练效率大幅提升
3. 可扩展性强，易于构建大规模模型

影响：
- BERT、GPT等所有现代LLM都基于Transformer
- ViT将Transformer应用于计算机视觉
- 成为多模态学习的基础架构

学习要点：
- 理解Q、K、V的计算方式
- 理解多头注意力的作用
- 理解位置编码的必要性
"""
    },
    "1810.04805": {
        "core_contributions": [
            "提出了双向Transformer编码器BERT",
            "引入了Masked Language Model (MLM)预训练任务",
            "引入了Next Sentence Prediction (NSP)预训练任务"
        ],
        "key_innovations": [
            "双向上下文表示",
            "掩码语言模型（MLM）",
            "下一句预测（NSP）",
            "预训练+微调范式"
        ],
        "experimental_results": [
            "在GLUE基准测试上达到SOTA",
            "在SQuAD 1.1上达到93.2 F1",
            "在11项NLP任务上超过当时的最佳模型"
        ],
        "applications": [
            "文本分类",
            "命名实体识别",
            "问答系统",
            "语义相似度"
        ],
        "related_papers": [
            "GPT (1803.02999)",
            "GPT-2 (1803.02999)",
            "RoBERTa (1907.11692)"
        ],
        "my_understanding": """
BERT是预训练语言模型的重要里程碑。

核心创新：
1. 双向编码器能够同时看到左右上下文
2. MLM预训练任务让模型学会预测被掩码的词
3. 预训练+微调范式成为标准

为什么重要：
- 解决了GPT只能单向编码的问题
- 预训练的表示可以迁移到各种下游任务
- 为后续的RoBERTa、DeBERTa等模型奠定基础

实践要点：
- 可以直接使用HuggingFace的BERT模型
- 微调通常只需要少量数据和训练时间
- 适合文本分类、NER等任务
"""
    },
    "1512.03385": {
        "core_contributions": [
            "提出了残差学习框架解决深层网络的退化问题",
            "引入了残差块（Residual Block）",
            "证明了深层网络可以通过残差连接有效训练"
        ],
        "key_innovations": [
            "残差连接（Residual Connection）",
            "残差块（Identity Mapping）",
            "批量归一化（Batch Normalization）"
        ],
        "experimental_results": [
            "在ImageNet上达到3.57% top-5错误率（152层）",
            "击败了VGG、GoogLeNet等之前的最佳模型",
            "证明了深层网络的有效性"
        ],
        "applications": [
            "图像分类",
            "目标检测",
            "图像分割",
            "特征提取"
        ],
        "related_papers": [
            "DenseNet (1611.05531)",
            "MobileNet (1704.04861)",
            "EfficientNet (1905.11946)"
        ],
        "my_understanding": """
ResNet解决了深度学习的核心问题：深度网络难以训练。

核心思想：
1. 残差块让网络学习残差而不是直接学习目标
2. 梯度可以通过残差连接直接流向浅层
3. 使得训练超深网络成为可能

影响：
- 成为计算机视觉的标准backbone
- 被集成到各种模型中（检测、分割等）
- 激发了大量改进工作（DenseNet、MobileNet等）

学习要点：
- 理解残差连接的数学原理
- 理解为什么残差连接有助于梯度传播
- 掌握使用预训练的ResNet模型
"""
    },
    "1406.2661": {
        "core_contributions": [
            "提出了生成对抗网络（GAN）框架",
            "引入了生成器（Generator）和判别器（Discriminator）的对抗训练",
            "证明了GAN能够生成逼真的样本"
        ],
        "key_innovations": [
            "生成对抗训练",
            "纳什均衡",
            "无需显式密度模型",
            "对抗损失函数"
        ],
        "experimental_results": [
            "在MNIST、TFD、CIFAR-10上生成高质量图像",
            "生成样本与真实样本难以区分",
            "判别器准确率在50%左右"
        ],
        "applications": [
            "图像生成",
            "风格迁移",
            "数据增强",
            "图像修复"
        ],
        "related_papers": [
            "DCGAN (1511.06434)",
            "StyleGAN (1710.10196)",
            "CycleGAN (1703.10593)"
        ],
        "my_understanding": """
GAN是生成模型的突破，开创了对抗训练的新范式。

核心思想：
1. 生成器试图生成逼真的样本欺骗判别器
2. 判别器试图区分真假样本
3. 两者相互对抗，共同提升

训练挑战：
- 模式崩溃（Mode Collapse）
- 梯度消失和爆炸
- 训练不稳定

实际应用：
- 图像生成：StyleGAN、BigGAN
- 图像翻译：CycleGAN、Pix2Pix
- 数据增强：用于扩充训练数据
"""
    },
    "2006.11239": {
        "core_contributions": [
            "提出了去噪扩散概率模型（DDPM）",
            "将扩散过程建模为高斯噪声的逐步添加",
            "通过逆向扩散过程生成样本"
        ],
        "key_innovations": [
            "前向扩散过程",
            "逆向扩散过程",
            "得分匹配（Score Matching）",
            "变分下界（ELBO）"
        ],
        "experimental_results": [
            "在CIFAR-10上达到3.17 FID",
            "在LSUN上达到5.06 FID",
            "生成图像质量优于GAN"
        ],
        "applications": [
            "图像生成",
            "视频生成",
            "音频生成",
            "3D模型生成"
        ],
        "related_papers": [
            "Stable Diffusion (2112.10752)",
            "DALL-E 2 (2204.06125)",
            "Imagen (2205.11487)"
        ],
        "my_understanding": """
DDPM重新定义了生成模型，扩散模型成为新的主流。

核心思想：
1. 前向过程：逐步添加噪声直到变成纯噪声
2. 逆向过程：学习从噪声中逐步恢复原始数据
3. 使用神经网络预测噪声

优势：
- 训练更稳定
- 可解释性强
- 生成质量高

扩散模型进化：
- DDPM (2006.11239) 基础模型
- DDIM (2010.02502) 加速采样
- Stable Diffusion (2112.10752) 潜空间扩散

实际应用：
- 文生图：Stable Diffusion、DALL-E
- 图像修复：Inpainting
- 风格迁移：ControlNet
"""
    },
    "2005.14165": {
        "core_contributions": [
            "提出了GPT-3，规模达175B参数的语言模型",
            "展示了LLM的few-shot学习能力",
            "证明了模型规模提升性能（Scaling Law）"
        ],
        "key_innovations": [
            "大规模预训练",
            "Few-shot learning",
            "Zero-shot learning",
            "模型缩放定律"
        ],
        "experimental_results": [
            "在few-shot设置下与微调模型竞争",
            "在算术推理、翻译等任务上表现优异",
            "展示了涌现能力"
        ],
        "applications": [
            "文本生成",
            "对话系统",
            "代码生成",
            "任务执行"
        ],
        "related_papers": [
            "GPT-2 (1810.04805)",
            "GPT-4 (2303.08768)",
            "LLaMA (2302.13971)"
        ],
        "my_understanding": """
GPT-3是LLM的重要里程碑，展示了模型的scaling能力。

核心发现：
1. 模型规模越大，few-shot能力越强
2. LLM展现出推理、代码等涌现能力
3. 预训练可以替代微调

Scaling Laws：
- 性能与模型规模、数据量、计算量的幂律关系
- 大规模训练至关重要
- 推理性能随规模提升

影响：
- 激发了开源LLM（LLaMA、Mistral等）
- 推动了Agent和工具使用的发展
- 成为ChatGPT等产品的基础

实践要点：
- 理解few-shot、zero-shot、one-shot
- 掌握prompt engineering
- 了解API调用和资源需求
"""
    },
    "2005.11401": {
        "core_contributions": [
            "提出了检索增强生成（RAG）框架",
            "结合检索系统和生成模型",
            "解决了LLM知识截止和幻觉问题"
        ],
        "key_innovations": [
            "检索增强生成",
            "密集向量检索",
            "上下文拼接",
            "端到端训练"
        ],
        "experimental_results": [
            "在知识密集型任务上显著提升性能",
            "在Jeopardy!和TriviaQA上达到SOTA",
            "减少了模型幻觉"
        ],
        "applications": [
            "问答系统",
            "文档检索",
            "知识库问答",
            "企业搜索"
        ],
        "related_papers": [
            "REALM (2002.08909)",
            "DPR (2004.04906)",
            "GraphRAG (2404.16130)"
        ],
        "my_understanding": """
RAG是LLM应用的核心架构，解决了LLM的知识局限。

核心思想：
1. 检索：从知识库中检索相关文档
2. 增强：将检索到的文档作为上下文
3. 生成：基于上下文生成回答

优势：
- 避免知识截止问题
- 减少模型幻觉
- 可更新知识（只需更新知识库）

RAG组件：
- 向量数据库：Chroma、Pinecone、Milvus
- 嵌入模型：OpenAI、Sentence-Transformers
- 检索算法：余弦相似度、BM25

实践要点：
- 选择合适的向量数据库
- 优化chunk策略和嵌入模型
- 使用重排序（Reranking）提升精度
"""
    },
    "2201.11903": {
        "core_contributions": [
            "提出了思维链（Chain-of-Thought, CoT）提示",
            "引导LLM逐步推理",
            "大幅提升了LLM的推理能力"
        ],
        "key_innovations": [
            "思维链提示",
            "逐步推理",
            "Few-shot prompting",
            "推理轨迹生成"
        ],
        "experimental_results": [
            "在GSM8K上从10.4%提升到58.1%",
            "在数学推理、常识推理等任务上显著提升",
            "激发了大量后续研究"
        ],
        "applications": [
            "数学推理",
            "逻辑推理",
            "问题求解",
            "复杂任务执行"
        ],
        "related_papers": [
            "Tree-of-Thought (2305.10601)",
            "Least-to-Most (2205.10625)",
            "Self-Consistency (2203.11171)"
        ],
        "my_understanding": """
CoT是提升LLM推理能力的关键技术。

核心思想：
1. 提示LLM生成逐步推理过程
2. 让模型"思考"后再给出答案
3. 通过few-shot示例展示推理模式

CoT模式：
- Zero-shot CoT：直接要求"Let's think step by step"
- Few-shot CoT：提供推理示例
- Auto-CoT：自动生成推理示例

扩展技术：
- Self-Consistency：多次采样投票
- Tree-of-Thought：树状推理
- Least-to-Most：分解问题

实践要点：
- 在提示中明确要求逐步推理
- 提供合适的few-shot示例
- 验证推理过程的合理性
"""
    },
    "2106.09685": {
        "core_contributions": [
            "提出了低秩适应（LoRA）",
            "仅训练少量参数即可适配新任务",
            "大幅降低了微调的存储和计算成本"
        ],
        "key_innovations": [
            "低秩分解",
            "秩分解更新",
            "适配器模块",
            "参数高效微调（PEFT）"
        ],
        "experimental_results": [
            "在GLUE上达到全量微调性能",
            "参数量减少10000倍",
            "推理开销几乎为零"
        ],
        "applications": [
            "模型微调",
            "个性化适配",
            "多任务学习",
            "资源受限场景"
        ],
        "related_papers": [
            "QLoRA (2305.14314)",
            "Prefix Tuning (2101.00190)",
            "Prompt Tuning (2101.00190)"
        ],
        "my_understanding": """
LoRA是参数高效微调的代表性方法。

核心思想：
1. 冻结预训练模型的权重
2. 添加低秩适配器矩阵
3. 只训练适配器参数

数学原理：
- W' = W + ΔW = W + BA
- B和A是低秩矩阵
- ΔW的秩设得很低（如r=8, r=16）

优势：
- 参数量大幅减少
- 存储需求低
- 推理无额外开销
- 可快速切换任务

实际应用：
- 多语言适配：每个语言一个LoRA
- 个性化：每个用户一个LoRA
- 领域适配：医疗、法律等
"""
    },
    "2103.00020": {
        "core_contributions": [
            "提出了CLIP（Contrastive Language-Image Pre-training）",
            "使用大规模图像-文本对进行对比学习",
            "实现了零样本图像分类"
        ],
        "key_innovations": [
            "对比学习",
            "视觉-语言多模态",
            "零样本迁移",
            "大规模预训练"
        ],
        "experimental_results": [
            "零样本分类与监督训练竞争",
            "在ImageNet上达到76.2% top-1",
            "展现了强大的泛化能力"
        ],
        "applications": [
            "零样本分类",
            "图像检索",
            "文本检索",
            "多模态生成"
        ],
        "related_papers": [
            "ALIGN (2102.05918)",
            "BLIP (2201.12086)",
            "DALL-E (2102.12092)"
        ],
        "my_understanding": """
CLIP是多模态学习的突破，打通了视觉和语言的桥梁。

核心思想：
1. 使用对比学习训练视觉-语言编码器
2. 推理图像和文本嵌入的相似度
3. 无需标注即可进行分类

训练过程：
- 收集大规模图像-文本对（4亿）
- 对比学习拉近正样本，推开负样本
- 使用温度缩放调整相似度

零样本能力：
- 将类别名称编码为文本
- 计算图像与类别文本的相似度
- 选择相似度最高的类别

实际应用：
- 图像搜索：上传图片找相似图片
- 文本生成图：DALL-E、Midjourney
- 图像理解：Visual QA
"""
    },
    "1707.06347": {
        "core_contributions": [
            "提出了近端策略优化（PPO）",
            "改进了策略梯度算法的稳定性",
            "成为强化学习的主流算法"
        ],
        "key_innovations": [
            "截断（Clipping）",
            "信任区域（Trust Region）",
            "重要性采样（Importance Sampling）",
            "优势函数（Advantage Function）"
        ],
        "experimental_results": [
            "在Atari游戏上达到人类水平",
            "训练稳定，易于调参",
            "采样效率高"
        ],
        "applications": [
            "游戏AI",
            "机器人控制",
            "推荐系统",
            "优化问题"
        ],
        "related_papers": [
            "TRPO (1502.05477)",
            "A3C (1602.01783)",
            "SAC (1801.01239)"
        ],
        "my_understanding": """
PPO是强化学习最重要的算法之一，平衡了性能和稳定性。

核心改进：
1. 截断策略更新，防止过大更新
2. KL散度约束，保持在信任区域
3. GAE（广义优势估计）估计优势

PPO特点：
- 简单易实现
- 训练稳定
- 采样效率高
- 支持连续和离散动作空间

训练流程：
1. 采集样本与环境交互
2. 计算优势函数和策略新旧比
3. 截断并优化目标函数
4. 更新策略网络

实际应用：
- OpenAI Five：Dota 2 AI
- ChatGPT：使用PPO进行RLHF
- 机器人控制策略学习
"""
    },
    "2010.11929": {
        "core_contributions": [
            "提出了Vision Transformer（ViT）",
            "将Transformer应用于计算机视觉",
            "验证了纯Transformer在视觉任务上的有效性"
        ],
        "key_innovations": [
            "图像patch",
            "位置编码",
            "Transformer编码器",
            "大规模预训练"
        ],
        "experimental_results": [
            "在ImageNet-21K上达到88.55% top-1",
            "超过CNN模型",
            "需要大规模预训练"
        ],
        "applications": [
            "图像分类",
            "目标检测",
            "图像分割",
            "视频理解"
        ],
        "related_papers": [
            "Swin Transformer (2103.14030)",
            "PVT (2102.12122)",
            "DeiT (2010.11929)"
        ],
        "my_understanding": """
ViT将Transformer的成功扩展到计算机视觉。

核心思想：
1. 将图像切分成patch，像token一样处理
2. 使用标准Transformer编码器
3. 使用位置编码保持空间信息

ViT优势：
- 全局感受野
- 长距离依赖建模
- 可扩展性强
- CNN+Transformer混合

挑战：
- 需要大规模预训练（JFT-300M）
- 数据增强至关重要
- 计算资源需求高

实际应用：
- 图像分类：ViT-B、ViT-L、ViT-H
- 目标检测：DETR
- 图像分割：SegFormer
"""
    },
    "2203.15556": {
        "core_contributions": [
            "提出了Chinchilla scaling laws",
            "研究了模型规模、数据量和计算量的最优关系",
            "确定了给定计算预算下的最优模型大小"
        ],
        "key_innovations": [
            "compute-optimal training",
            "scaling laws",
            "data scaling",
            "模型缩放"
        ],
        "experimental_results": [
            "确定了compute-optimal模型大小",
            "Chinchilla模型效率更高",
            "模型大小和数据量应等比例增长"
        ],
        "applications": [
            "LLM训练",
            "资源配置",
            "性能预测",
            "模型设计"
        ],
        "related_papers": [
            "Kaplan et al. (2020)",
            "GPT-3 (2005.14165)",
            "LLaMA (2302.13971)"
        ],
        "my_understanding": """
Chinchilla论文揭示了LLM训练的scaling law。

核心发现：
1. 模型大小和数据量应等比例缩放
2. 给定计算预算，存在最优模型大小
3. 当前模型大多训练不足（under-trained）

Scaling Laws：
- Loss ~ N^(-α), D^(-β), C^(-γ)
- α ≈ 0.5, β ≈ 0.3
- Compute-optimal: N = 20 * D

Chinchilla模型：
- 70B参数（比GPT-3小）
- 1.4T token（比GPT-3多）
- 性能更好，训练成本更低

实际意义：
- 不要盲目追求最大模型
- 数据质量和规模同样重要
- 训练效率比模型大小更重要
"""
    },
    "2305.14314": {
        "core_contributions": [
            "提出了QLoRA（Quantized LoRA）",
            "结合量化和LoRA",
            "大幅降低了LLM微调的显存需求"
        ],
        "key_innovations": [
            "4-bit量化",
            "双重量化",
            "分页优化器",
            "低秩适配器"
        ],
        "experimental_results": [
            "65B模型微调只需48GB显存",
            "性能接近全量微调",
            "可以在单GPU上微调大模型"
        ],
        "applications": [
            "大模型微调",
            "本地LLM微调",
            "个性化适配",
            "多任务学习"
        ],
        "related_papers": [
            "LoRA (2106.09685)",
            "GPTQ (2210.17313)",
            "AWQ (2306.00978)"
        ],
        "my_understanding": """
QLoRA让在消费级GPU上微调大模型成为可能。

核心创新：
1. 4-bit量化权重到NF4格式
2. 反向传播时解量化到BF16
3. 双重量化（量化常量+动态量化）
4. 分页优化器减少显存碎片

显存需求：
- 权重：4-bit量化
- 梯度：BF16
- 优化器状态：不存储
- LoRA适配器：少量参数

性能：
- 几乎不损失性能
- 训练稳定
- 推理速度接近原始模型

实际应用：
- 微调LLaMA-2 70B（需48GB）
- 微调Falcon 40B（需24GB）
- 在消费级GPU上微调大模型

工具：
- PEFT库：HuggingFace
- bitsandbytes：优化器
- AutoGPTQ：推理加速
"""
    },
    "2112.10752": {
        "core_contributions": [
            "提出了Stable Diffusion",
            "在潜空间进行扩散过程",
            "大幅提升了生成速度和质量"
        ],
        "key_innovations": [
            "潜空间扩散",
            "VQ-VAE编码器",
            "文本条件（CLIP）",
            "Cross-attention"
        ],
        "experimental_results": [
            "生成质量优于DDPM",
            "FID分数达到3.6",
            "推理速度快10倍以上"
        ],
        "applications": [
            "文生图",
            "图生图",
            "图像编辑",
            "视频生成"
        ],
        "related_papers": [
            "DDPM (2006.11239)",
            "DALL-E 2 (2204.06125)",
            "Imagen (2205.11487)"
        ],
        "my_understanding": """
Stable Diffusion让扩散模型普及到大众。

核心改进：
1. 潜空间扩散：在低维空间操作
2. VQ-VAE：编码器压缩图像
3. U-Net：带cross-attention的架构
4. CLIP：文本条件

Stable Diffusion架构：
- Text Encoder: CLIP编码文本
- VQ-VAE: 编码和解码图像
- U-Net: 在潜空间去噪
- Cross-attention: 融合文本和图像

优势：
- 生成速度快（4-50倍）
- 显存需求低（4GB即可运行）
- 开源免费
- 社区生态丰富

衍生技术：
- LoRA：风格微调
- ControlNet：控制生成
- Inpainting：图像修复
- Image-to-Image：图生图
"""
    },
    "2205.11916": {
        "core_contributions": [
            "展示了LLM的零样本推理能力",
            "验证了LLM无需训练即可推理",
            "系统评估了LLM的推理性能"
        ],
        "key_innovations": [
            "零样本推理",
            "推理benchmark",
            "思维链提示",
            "多任务评估"
        ],
        "experimental_results": [
            "在多个推理任务上表现优异",
            "CoT大幅提升性能",
            "大模型推理能力更强"
        ],
        "applications": [
            "逻辑推理",
            "数学推理",
            "常识推理",
            "问题求解"
        ],
        "related_papers": [
            "CoT (2201.11903)",
            "Self-Consistency (2203.11171)",
            "Tree-of-Thought (2305.10601)"
        ],
        "my_understanding": """
该论文系统性评估了LLM的推理能力。

核心发现：
1. LLM无需训练即可进行推理
2. 规模越大，推理能力越强
3. 思维链显著提升性能

推理类型：
1. 数学推理
2. 符号推理
3. 常识推理
4. 算法推理

评估方法：
1. 基准数据集
2. 人工评估
3. 与人类对比
4. 与传统方法对比

零样本推理：
- 直接提示模型解决问题
- 提供推理示例（few-shot）
- 要求模型逐步推理（CoT）

实际应用：
- 代码生成和调试
- 数学问题求解
- 逻辑谜题
- 任务规划
"""
    },
    "2305.10601": {
        "core_contributions": [
            "提出了思维树（Tree-of-Thought, ToT）",
            "将思维链扩展为树状结构",
            "通过搜索和评估提升推理质量"
        ],
        "key_innovations": [
            "思维树",
            "生成-评估-搜索",
            "系统1和系统2",
            "回溯和剪枝"
        ],
        "experimental_results": [
            "在Game of 24上达到60%成功率",
            "大幅超越CoT",
            "展示了系统化推理能力"
        ],
        "applications": [
            "复杂推理",
            "问题求解",
            "规划任务",
            "算法设计"
        ],
        "related_papers": [
            "CoT (2201.11903)",
            "Least-to-Most (2205.10625)",
            "RAP (2201.11903)"
        ],
        "my_understanding": """
ToT将思维链提升为系统化的推理框架。

核心思想：
1. 生成多个可能的推理路径
2. 评估每个路径的质量
3. 选择最优路径继续
4. 类似蒙特卡洛树搜索

ToT架构：
- 离散推理：候选数量有限
- 连续推理：生成候选
- BFS/DFS搜索
- 评估函数指导搜索

系统1和系统2：
- 系统1：快速生成候选
- 系统2：评估候选质量

优势：
- 考虑多种可能性
- 避免陷入错误路径
- 系统化推理过程

挑战：
- 计算开销大
- 评估函数设计
- 搜索策略优化
"""
    },
    "2002.08909": {
        "core_contributions": [
            "提出了REALM（Retrieval-Augmented Language Model）",
            "结合检索和生成进行预训练",
            "在知识密集任务上大幅提升性能"
        ],
        "key_innovations": [
            "检索增强预训练",
            "知识检索",
            "端到端训练",
            "弱监督学习"
        ],
        "experimental_results": [
            "在Open-SQuAD上提升55.7%",
            "在NaturalQuestions上提升27.5%",
            "在HotpotQA上提升32%"
        ],
        "applications": [
            "问答系统",
            "知识库问答",
            "文档检索",
            "对话系统"
        ],
        "related_papers": [
            "RAG (2005.11401)",
            "DPR (2004.04906)",
            "FiD (2011.09839)"
        ],
        "my_understanding": """
REALM是RAG的重要先驱工作。

核心思想：
1. 在预训练时引入检索
2. 检索到的文档作为上下文
3. 学习检索+生成端到端

REALM架构：
- 检索器：从Wikipedia检索
- 编码器：BERT编码文档和查询
- 生成器：基于上下文生成

预训练任务：
- Masked LM with retrieval
- MLM + NSP with context

优势：
- 提升知识密集任务性能
- 减少模型幻觉
- 可更新外部知识

RAG生态：
- DPR: 密集向量检索
- FiD: Fusion-in-Decoder
- ReAct: 推理+行动
"""
    }
}

def update_paper_analysis(arxiv_id: str, analysis_dir: Path):
    """更新论文的深度解读"""
    analysis_file = analysis_dir / f"{arxiv_id}_analysis.md"
    
    if not analysis_file.exists():
        print(f"  ⚠ 未找到分析文件: {analysis_file}")
        return False
    
    # 读取现有内容
    with open(analysis_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 获取深度分析
    deep_analysis = PAPER_DEEP_ANALYSIS.get(arxiv_id)
    if not deep_analysis:
        print(f"  ⚠ 未找到深度分析: {arxiv_id}")
        return False
    
    # 更新内容
    sections = {
        "核心贡献": deep_analysis["core_contributions"],
        "关键创新": deep_analysis["key_innovations"],
        "实验结果": deep_analysis["experimental_results"],
        "应用场景": deep_analysis["applications"],
        "相关论文": deep_analysis["related_papers"],
        "我的理解": deep_analysis["my_understanding"]
    }
    
    updated_content = content
    
    # 更新各个部分
    for section_name, section_content in sections.items():
        # 找到对应的部分
        section_pattern = f"## {section_name}"
        if section_pattern in updated_content:
            # 生成新的部分内容
            new_section = f"\n## {section_name}\n\n"
            
            if section_name == "我的理解":
                new_section += "```"
                new_section += section_content
                new_section += "\n```"
            elif isinstance(section_content, list):
                for i, item in enumerate(section_content, 1):
                    new_section += f"{i}. {item}\n"
            else:
                new_section += str(section_content)
            
            new_section += "\n"
            
            # 替换原有内容（从该部分开始到下一个##或文件结束）
            import re
            pattern = rf"(## {re.escape(section_name)}.*?)(\n## |$)"
            match = re.search(pattern, updated_content, re.DOTALL)
            if match:
                # 保留该部分之前的所有内容
                before_section = updated_content[:match.start(1)]
                # 保留该部分之后的所有内容
                after_section = match.group(2) if match.group(2) else ""
                
                updated_content = before_section + new_section + after_section
    
    # 写回文件
    with open(analysis_file, "w", encoding="utf-8") as f:
        f.write(updated_content)
    
    print(f"  ✓ 已更新: {arxiv_id}_analysis.md")
    return True

def main():
    print("=" * 80)
    print("为扩展论文添加深度解读")
    print("=" * 80)
    
    success_count = 0
    fail_count = 0
    
    for category_dir in EXTENDED_PAPERS_DIR.iterdir():
        if not category_dir.is_dir():
            continue
        
        print(f"\n处理类别: {category_dir.name}")
        
        for analysis_file in category_dir.glob("*_analysis.md"):
            arxiv_id = analysis_file.stem.replace("_analysis", "")
            
            if update_paper_analysis(arxiv_id, category_dir):
                success_count += 1
            else:
                fail_count += 1
    
    print("\n" + "=" * 80)
    print("深度解读更新完成")
    print("=" * 80)
    print(f"成功: {success_count}")
    print(f"失败: {fail_count}")
    print("=" * 80)

if __name__ == "__main__":
    main()
