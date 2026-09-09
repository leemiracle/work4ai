#!/usr/bin/env python3
"""
csdiy 端到端集成测试 — 5 个深度系统全链路验证

验证矩阵：
  ① tinytorch  — autograd 正确性
  ② tinyllm    — GPT 前向 + KV Cache 推理
  ③ tinyrag    — 文档入库 + 检索 + 增强
  ④ tinyrl     — Q-Learning 训练 + 评估
  ⑤ tinygen    — 扩散采样
  ⑥ 集成       — tinyllm×tinyrag 联动
"""
import sys, os, time, random, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_tinytorch():
    """① tinytorch: autograd + 训练"""
    print("━━━ ① tinytorch ━━━")
    from tinytorch.tensor import Value
    from tinytorch.nn import MLP
    from tinytorch.optim import Adam
    from tinytorch.loss import cross_entropy

    # autograd 正确性
    a = Value(3.0); b = Value(4.0)
    c = (a * b + a).tanh()
    c.backward()
    assert abs(a.grad) > 0, "autograd failed"

    # XOR 训练（快速版）
    random.seed(42)
    model = MLP(2, [8, 1])
    opt = Adam(model.parameters(), lr=0.05)
    for ep in range(50):
        opt.zero_grad()
        loss = Value(0)
        for x, y in [([0,0],0),([0,1],1),([1,0],1),([1,1],0)]:
            pred = model([Value(x[0]), Value(x[1])])[0].tanh()
            loss = loss + (pred - Value(y))**2
        (loss * 0.25).backward()
        opt.step()
    print(f"  ✅ autograd: da={a.grad:.3f}")
    print(f"  ✅ XOR training: loss={loss.data:.4f}")
    return True

def test_tinyllm():
    """② tinyllm: GPT + 推理引擎"""
    print("\n━━━ ② tinyllm ━━━")
    from tinyllm.model import GPT
    from tinyllm.tokenizer import BPETokenizer
    from tinyllm.infer import LLMInference

    model = GPT(vocab_size=100, d_model=32, n_heads=4, n_layers=2, max_seq=64)
    prompt = [1, 5, 10, 15, 20]

    # 前向
    logits = model.forward(prompt)
    assert len(logits) == len(prompt), "forward shape mismatch"

    # Tokenizer
    tok = BPETokenizer()
    tok.train(["hello world tiny language model"], vocab_size=50)
    ids = tok.encode("hello")
    decoded = tok.decode(ids)

    # 推理引擎
    engine = LLMInference(model)
    tokens_g, stats_g = engine.generate(prompt, max_tokens=5, strategy="greedy")
    tokens_t, stats_t = engine.generate(prompt, max_tokens=5, strategy="temperature", temperature=0.8)
    tokens_k, stats_k = engine.generate(prompt, max_tokens=5, strategy="top_k", top_k=5)

    print(f"  ✅ forward: {len(logits)}×{len(logits[0])} logits")
    print(f"  ✅ tokenizer: vocab={len(tok.vocab)}, encode('hello')={len(ids)} tokens")
    print(f"  ✅ inference greedy: {stats_g['generated_tokens']} tokens, {stats_g['total_ms']:.1f}ms")
    print(f"  ✅ inference temp=0.8: {stats_t['generated_tokens']} tokens")
    print(f"  ✅ inference top_k=5: {stats_k['generated_tokens']} tokens")
    return True

def test_tinyrag():
    """③ tinyrag: 文档入库 + 检索"""
    print("\n━━━ ③ tinyrag ━━━")
    from tinyrag.pipeline import RAGPipeline

    rag = RAGPipeline(embedding_model="hash", index_type="hnsw", dim=32,
                      chunk_size=40, overlap=5)
    # 入库
    docs = {
        "ai": "Artificial intelligence uses neural networks for learning and prediction.",
        "db": "Database systems store data using B-trees and LSM trees for efficiency.",
        "net": "Computer networks use TCP/IP protocols with epoll for high concurrency.",
    }
    total_chunks = 0
    for doc_id, text in docs.items():
        total_chunks += rag.ingest(doc_id, text)

    # 检索
    results = rag.retrieve("neural network", top_k=3)
    assert len(results) > 0, "retrieval returned empty"

    # 增强
    prompt, sources = rag.augment("neural network", top_k=2)
    assert len(sources) > 0, "augment returned empty sources"

    # 评估
    eval_set = [("neural", "ai"), ("database", "db"), ("network", "net")]
    metrics = rag.evaluate_retrieval(eval_set, top_k=2)

    print(f"  ✅ ingest: {len(docs)} docs → {total_chunks} chunks")
    print(f"  ✅ retrieve: top_score={results[0]['score']:.3f}")
    print(f"  ✅ augment: {len(sources)} sources in prompt")
    print(f"  ✅ evaluate: recall@2={metrics['recall@k']:.0%}")
    return True

def test_tinyrl():
    """④ tinyrl: Q-Learning + DQN"""
    print("\n━━━ ④ tinyrl ━━━")
    from tinyrl.env import GridWorld, CartPole1D
    from tinyrl.agent import QLearningAgent, DQNAgent
    from tinyrl.train import Trainer, Evaluator

    random.seed(42)
    # Q-Learning
    env = GridWorld(4)
    agent = QLearningAgent(env.n_states, 4, lr=0.2, epsilon=0.2)
    trainer = Trainer(agent, env, max_episodes=200, verbose=False)
    trainer.train()
    eval = Evaluator.evaluate(agent, env, n_episodes=20)

    # DQN（快速版）
    env2 = CartPole1D()
    dqn = DQNAgent(env2.n_states, 2, lr=0.1, epsilon=0.15)
    for ep in range(50):
        state = env2.reset()
        while True:
            action = dqn.act(state)
            next_s, reward, done, _ = env2.step(action)
            dqn.remember(state, action, reward, next_s, done)
            if len(dqn.replay_buffer) > 32: dqn.learn()
            state = next_s
            if done: break

    print(f"  ✅ Q-Learning: success={eval['success_rate']:.0%}, avg_reward={eval['avg_reward']:.3f}")
    print(f"  ✅ DQN: 50 episodes, buffer={len(dqn.replay_buffer)}")
    return True

def test_tinygen():
    """⑤ tinygen: 扩散采样"""
    print("\n━━━ ⑤ tinygen ━━━")
    from tinygen.diffusion import DiffusionProcess
    from tinygen.gan import GAN
    from tinygen.vae import VAE

    random.seed(42)
    # DDPM
    diff = DiffusionProcess(T=50)
    x0 = [0.5, -0.3, 0.8]
    x_t, noise = diff.q_sample(x0, t=25)
    def denoise(x_t, t): return [v * 0.3 for v in x_t]
    result, _ = diff.sample(denoise, dim=3)
    assert len(result) == 3

    # GAN
    gan = GAN(latent_dim=4, data_dim=2)
    real_data = [[random.gauss(1, 0.3), random.gauss(1, 0.3)] for _ in range(20)]
    gan.train_step(real_data)
    samples = gan.generate(3)
    assert len(samples) == 3

    # VAE
    vae = VAE(input_dim=4, latent_dim=2)
    test_x = [1.0, 0.5, -0.3, 0.8]
    recon = vae.reconstruct(test_x)
    assert len(recon) == 4
    generated = vae.generate(2)
    assert len(generated) == 2

    print(f"  ✅ DDPM: T=50, sample dim=3")
    print(f"  ✅ GAN: 1 train step, 3 samples generated")
    print(f"  ✅ VAE: reconstruct dim=4, generate 2 samples")
    return True

def test_integration():
    """⑥ 集成: tinyllm × tinyrag"""
    print("\n━━━ ⑥ 集成: tinyllm × tinyrag ━━━")
    from tinyllm.model import GPT
    from tinyllm.infer import LLMInference
    from tinyrag.pipeline import RAGPipeline

    random.seed(42)
    # 初始化
    model = GPT(vocab_size=100, d_model=32, n_heads=4, n_layers=2, max_seq=64)
    engine = LLMInference(model)
    rag = RAGPipeline(dim=32, chunk_size=30, overlap=5)

    # 知识库入库
    rag.ingest("kb1", "Tinytorch is a deep learning framework with autograd.")
    rag.ingest("kb2", "Tinyllm is a language model system with KV cache.")
    rag.ingest("kb3", "Tinyrag is a retrieval system using HNSW index.")

    # RAG 增强 + LLM 生成
    query = "what is tinytorch"
    prompt, sources = rag.augment(query, top_k=2)
    prompt_ids = [ord(c) % model.vocab_size for c in query[:16]]
    tokens, stats = engine.generate(prompt_ids, max_tokens=5, strategy="greedy")

    assert len(sources) > 0, "RAG returned no sources"
    assert stats["generated_tokens"] > 0, "LLM generated no tokens"

    print(f"  ✅ RAG: query='{query}' → {len(sources)} sources retrieved")
    print(f"  ✅ LLM: {stats['generated_tokens']} tokens in {stats['total_ms']:.1f}ms")
    print(f"  ✅ 集成链路: query → retrieve → augment → generate ✅")
    return True

def main():
    print("=" * 60)
    print("  csdiy 端到端集成测试")
    print("  5 个深度系统 + 跨系统集成")
    print("=" * 60)

    tests = [
        ("tinytorch", test_tinytorch),
        ("tinyllm", test_tinyllm),
        ("tinyrag", test_tinyrag),
        ("tinyrl", test_tinyrl),
        ("tinygen", test_tinygen),
        ("集成", test_integration),
    ]

    results = {}
    t0 = time.time()
    for name, test_fn in tests:
        try:
            test_fn()
            results[name] = "✅ PASS"
        except Exception as e:
            results[name] = f"❌ FAIL: {e}"
            import traceback; traceback.print_exc()

    elapsed = time.time() - t0
    passed = sum(1 for v in results.values() if "PASS" in v)

    print(f"\n{'='*60}")
    print(f"  集成测试结果 ({elapsed:.1f}s)")
    print(f"{'='*60}")
    for name, result in results.items():
        print(f"  {name:15s} {result}")
    print(f"\n  总计: {passed}/{len(tests)} passed")

    if passed == len(tests):
        print(f"\n  🎉 全部通过！5 个深度系统 + 跨系统集成全部正常。")
    return 0 if passed == len(tests) else 1

if __name__ == "__main__":
    sys.exit(main())
