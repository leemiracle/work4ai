"""
Lean4 验证作 GRPO 的 reward（pass@k 实验核心）。

reward = 1.0 if Lean4 接受证明 else 0.0（二元 RLVR 标准）
用 LeanDojo-v2 + Pantograph 作 Lean4 RPC。

⚠️ 需 lean-dojo 包 + Lean4 工具链（本机未装，移植到 GPU 环境时安装）。
"""
from typing import Tuple


class Lean4Verifier:
    """
    Lean4 证明验证器（GRPO reward 后端）。

    用法（GRPO 训练时）：
        verifier = Lean4Verifier("04-layers/l2_5-formal-rules/formal-seed")
        reward = 1.0 if verifier.verify(rule_statement, generated_proof) else 0.0

    实现说明：
        真正实现需 LeanDojo-v2 的 Dojo + Pantograph RPC。
        本骨架给出接口；移植时填入 lean_dojo 调用。
    """

    def __init__(self, repo_path: str, lean_version: str = "4.21.0"):
        """
        Args:
            repo_path: Lean4 项目路径（含 lakefile，如 04-layers/l2_5-formal-rules/formal-seed）
            lean_version: Lean 版本（与 SpinlockPreempt v2 一致 = 4.21.0）
        """
        self.repo_path = repo_path
        self.lean_version = lean_version
        # 移植时取消注释：
        # from lean_dojo import LeanGitRepo, Dojo
        # self.repo = LeanGitRepo.of(repo_path)
        # self.dojo = Dojo(self.repo)

    def verify(self, theorem_statement: str, proof: str) -> bool:
        """
        验证 proof 是否证明 theorem_statement。

        Args:
            theorem_statement: Lean4 定理陈述（如 'Inv_preserved_over_trace'）
            proof: LLM 生成的证明文本

        Returns:
            True if Lean4 接受（reward=1.0），False otherwise（reward=0.0）
        """
        # 移植时实现：
        # try:
        #     state = self.dojo.run_tac(theorem_statement, proof)
        #     return state.is_solved
        # except Exception:
        #     return False
        raise NotImplementedError(
            "需 lean_dojo 包（本机未装）。移植到 GPU 环境时：pip install lean-dojo"
        )

    def verify_batch(self, items: list[Tuple[str, str]]) -> list[float]:
        """批量验证（GRPO rollout 用）。返回 reward 列表。"""
        return [1.0 if self.verify(stmt, proof) else 0.0 for stmt, proof in items]


def reward_fn(prompts: list[str], responses: list[str],
              verifier: Lean4Verifier) -> list[float]:
    """
    GRPO 训练的 reward 函数。

    Args:
        prompts: 规则陈述列表（定理 statement）
        responses: LLM 生成的证明列表
        verifier: Lean4Verifier 实例

    Returns:
        rewards: 每个响应的 reward（1.0 = Lean 接受，0.0 = 拒绝）
    """
    return verifier.verify_batch(list(zip(prompts, responses)))


# ============================================================
# pass@k 无偏估计（Chen 2021，HumanEval）
# ============================================================

import numpy as np


def pass_at_k(n: int, c: int, k: int) -> float:
    """
    无偏 pass@k 估计。

    Args:
        n: 总采样次数
        c: 成功次数（证明被 Lean 接受）
        k: pass@k 的 k

    Returns:
        pass@k 概率估计
    """
    if n - c < k:
        return 1.0
    return 1.0 - np.prod(1.0 - k / np.arange(n - c + 1, n + 1))


if __name__ == "__main__":
    print("Lean4Verifier 骨架。需 lean_dojo 包（本机未装）。")
    print("pass_at_k 自测：")
    # 假设 256 次采样，30 次成功
    for k in [1, 8, 32, 128, 256]:
        print(f"  pass@{k:3d} (n=256, c=30) = {pass_at_k(256, 30, k):.4f}")
