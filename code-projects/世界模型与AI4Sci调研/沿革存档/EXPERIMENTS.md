# 实验代码索引（Experiments Index）

> **位置**：`/data/usershare/ai/world-ai4sci-math/`
> **目的**：为模块 11/12 的每个章节配套可独立运行的 Python 实验代码

## 设计原则

1. **每个文件 < 200 行，独立可运行**（不需要 GPU）
2. **每个实验对应章节中的一个核心概念**
3. **必须有 bash 实际跑通的验证**
4. **输出清晰、有数据证明结论**

## 实验目录结构

```
world-ai4sci-math/
├── 11-model-components-deep/
│   ├── experiments/             # 01 Attention 章节
│   ├── experiments_ffn/         # 02 FFN/Norm 章节
│   ├── experiments_pe/          # 03 Position Encoding 章节
│   ├── experiments_loss/        # 04 Loss Function 章节
│   └── experiments_optimizer/   # 05 Optimizer 章节
└── 12-model-lifecycle-deep/
    ├── experiments_pretraining/ # 01 Pretraining 章节
    ├── experiments_peft/        # 02 PEFT 章节
    ├── experiments_alignment/   # 03 RLHF/DPO 章节
    ├── experiments_eval/        # 04 Evaluation 章节
    └── experiments_deployment/  # 05 Deployment 章节
```

每章 10 个 .py 实验 + 1 个 README.md，**总计 111 个实验代码文件**。

## 运行方式

每个实验独立运行：

```bash
cd /data/usershare/ai/world-ai4sci-math/11-model-components-deep/experiments/
python3 01_scaled_dot_product_attention.py
```

## 实验清单（共 111）

### 模块 11 组件深处（61 实验）

**Attention 谱系（10 实验）**：
1. `01_scaled_dot_product_attention.py` —— SDPA + √d_k 方差分析
2. `02_multi_head_attention.py` —— MHA 实现
3. `03_mqa_grouped_query.py` —— MQA / GQA + KV cache 对比
4. `04_mla_deepseek.py` —— DeepSeek MLA + absorption trick
5. `05_sliding_window_attention.py` —— 滑动窗口
6. `06_sparse_attention.py` —— BigBird 风格稀疏
7. `07_linear_attention.py` —— Katharopoulos 线性
8. `08_flash_attention_minimal.py` —— Tiling FlashAttention
9. `09_kv_cache_demo.py` —— KV cache 速度对比
10. `10_attention_benchmark.py` —— 全变种大对比

**FFN / Norm（10 实验）**：
1. `01_relu_vs_gelu_vs_swish.py` —— 激活函数对比
2. `02_swiglu_implementation.py` —— SwiGLU 实现
3. `03_batch_norm_vs_layer_norm.py` —— BN vs LN
4. `04_rmsnorm.py` —— RMSNorm
5. `05_prelayer_norm_vs_post.py` —— Pre-LN vs Post-LN 稳定性
6. `06_residual_connections.py` —— 残差连接作用
7. `07_deepnorm.py` —— DeepNorm 深层训练
8. `08_embedding_tied_vs_untied.py` —— Tied embedding
9. `09_ffn_intermediate_dim.py` —— FFN 中间维度
10. `10_full_transformer_block.py` —— 完整 Transformer block

**Position Encoding（10 实验）**：
1. `01_sinusoidal_pe.py` —— 原版 Sinusoidal
2. `02_learned_pe.py` —— 学习型 PE
3. `03_relative_pe.py` —— 相对 PE
4. `04_rope_minimal.py` —— RoPE 完整推导
5. `05_rope_extrapolation.py` —— RoPE 外推
6. `06_ntk_aware_scaling.py` —— NTK-aware
7. `07_yarn.py` —— YaRN
8. `08_alibi.py` —— ALiBi
9. `09_nope.py` —— NoPE
10. `10_pe_comparison.py` —— 全 PE 大对比

**Loss Function（10 实验）**：
1. `01_cross_entropy.py` —— CE 推导
2. `02_focal_loss.py` —— Focal Loss
3. `03_infonce_contrastive.py` —— InfoNCE
4. `04_clip_loss.py` —— CLIP loss
5. `05_vae_elbo.py` —— VAE + ELBO
6. `06_ddpm_loss.py` —— DDPM loss
7. `07_flow_matching.py` —— Flow Matching
8. `08_dpo_loss.py` —— DPO loss
9. `09_ppo_loss.py` —— PPO loss
10. `10_loss_landscape.py` —— Loss surface 可视化

**Optimizer（10 实验）**：
1. `01_sgd_momentum.py` —— SGD + Momentum
2. `02_nesterov.py` —— Nesterov
3. `03_adagrad_rmsprop.py` —— Adagrad / RMSprop
4. `04_adam_from_scratch.py` —— Adam 从零
5. `05_adamw_vs_adam.py` —— AdamW vs Adam
6. `06_lion_optimizer.py` —— Lion
7. `07_sophia_optimizer.py` —— Sophia
8. `08_lr_schedule.py` —— LR 调度
9. `09_gradient_clipping.py` —— 梯度裁剪
10. `10_optimizer_benchmark.py` —— 优化器大对比

**Transformer 变种（10 实验）**：
1. `01_encoder_only_bert.py` —— BERT encoder-only（MLM 双向）
2. `02_decoder_only_gpt.py` —— GPT decoder-only（自回归 LM）
3. `03_encoder_decoder_t5.py` —— T5 encoder-decoder（Seq2Seq）
4. `04_moe_routing.py` —— MoE 路由机制（top-k gating）
5. `05_switch_transformer_minimal.py` —— Switch Transformer（top-1 路由）
6. `06_deepseek_moe.py` —— DeepSeek MoE（共享专家 + 细粒度专家）
7. `07_mamba_block.py` —— Mamba 选择性状态空间模型 block
8. `08_jamba_hybrid.py` —— Jamba 注意力 + SSM 混合架构
9. `09_architecture_comparison.py` —— Transformer 变种大对比
10. `10_modern_architecture_decoder.py` —— 现代架构 decoder（RoPE + RMSNorm + SwiGLU）

### 模块 12 生命周期深处（50 实验）

**Pretraining（10 实验）**：
1. `01_scaling_law_demo.py` —— Kaplan Scaling Law
2. `02_chinchilla_optimal.py` —— Chinchilla 配比
3. `03_data_mixing.py` —— 数据混合
4. `04_bpe_tokenizer.py` —— BPE 训练
5. `05_loss_spike_simulation.py` —— Loss spike
6. `06_gradient_checkpointing.py` —— 梯度检查点
7. `07_zeRO_concept.py` —— ZeRO 分片
8. `08_pipeline_parallel_concept.py` —— 流水线并行
9. `09_mixed_precision.py` —— 混合精度
10. `10_nanogpt_minimal.py` —— 200 行 nanoGPT

**PEFT（10 实验）**：
1. `01_lora_from_scratch.py` —— LoRA 从零
2. `02_lora_rank_ablation.py` —— rank 消融
3. `03_qlora_nf4.py` —— QLoRA + NF4
4. `04_dora.py` —— DoRA
5. `05_adapter_bottleneck.py` —— Adapter
6. `06_prefix_tuning.py` —— Prefix Tuning
7. `07_prompt_tuning.py` —— Prompt Tuning
8. `08_ia3.py` —— IA³
9. `09_catastrophic_forgetting.py` —— 灾难性遗忘
10. `10_peft_comparison.py` —— PEFT 大对比

**RLHF/DPO（10 实验）**：
1. `01_reward_model.py` —— Reward Model
2. `02_ppo_minimal.py` —— PPO 简化版
3. `03_rlhf_pipeline.py` —— RLHF pipeline
4. `04_dpo_loss_from_scratch.py` —— DPO loss 从零
5. `05_dpo_vs_ppo.py` —— DPO vs PPO
6. `06_kto_kahneman_tversky.py` —— KTO
7. `07_grpo_deepseek.py` —— GRPO
8. `08_constitutional_ai_sim.py` —— Constitutional AI
9. `09_self_rewarding.py` —— Self-Rewarding
10. `10_rlvr_verifiable_reward.py` —— RLVR

**Evaluation（10 实验）**：
1. `01_cross_entropy_eval.py` —— Perplexity
2. `02_gsm8k_minimal.py` —— GSM8K 评估
3. `03_few_shot_prompting.py` —— Few-shot
4. `04_chain_of_thought.py` —— CoT
5. `05_self_consistency.py` —— Self-Consistency
6. `06_pass_at_k.py` —— pass@k
7. `07_llm_as_judge.py` —— LLM-as-Judge 偏置
8. `08_elo_rating.py` —— Elo + Bradley-Terry
9. `09_statistical_significance.py` —— 统计显著性
10. `10_contamination_detection.py` —— 污染检测

**Deployment（10 实验）**：
1. `01_kv_cache_demo.py` —— KV cache
2. `02_continuous_batching_sim.py` —— Continuous Batching
3. `03_paged_attention_sim.py` —— PagedAttention
4. `04_speculative_decoding_sim.py` —— Speculative Decoding
5. `05_latency_metrics.py` —— TTFT/TPOT 测量
6. `06_quantization_inference.py` —— 量化推理
7. `07_ab_testing_framework.py` —— A/B 测试
8. `08_drift_detection.py` —— 漂移检测
9. `09_simple_api_server.py` —— FastAPI serving
10. `10_monitoring_dashboard_data.py` —— Prometheus metrics
11. `11_attention_sink_and_spec_decoding.py` —— **2026-07-23 新增**：attention sink 数学 + 推测解码加速比公式（§12 工程深挖配套）

### 模块 13 Agent 系统深处（1 实验，2026-07-23 新增）

1. `experiments_13/01_leandojo_state_machine.py` —— LeanDojo init/run_tactic API 状态机模拟 + sorry 反例 + Lean Copilot 实测数据（§13 形式化验证配套）

### 模块 14 计算数学物理基础（1 实验，2026-07-23 新增）

1. `experiments_05/06_phytium_d3000_fp16_neon.py` —— 飞腾 D3000 ARMv8.2-A 数值特性（FP16 vs FP32 + NEON 元素数 + SDOT 模拟 + 国密双栈 + kpgcc 融合对，5 部分，§11 配套）

## 验证清单

每个实验必须：
- [ ] 能用 `python3 filename.py` 独立运行
- [ ] 不需要 GPU（CPU 即可）
- [ ] 运行时间 < 1 分钟
- [ ] 输出清晰的实验结论（数字、表格、图）
- [ ] 代码 < 200 行，有详细注释

## 与章节的对应

每章 .md 文件中的「代码示例」段落会指向对应 `experiments/` 中的实验。

---

<!-- 实验索引, 2026-07-20 -->
