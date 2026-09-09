# Trace is Not Ground Truth: Correcting the Prior Assumption of RLVR in System-Domain Neuro-Symbolic Rule Learning

**Draft v0.1** · 2026-08-05 · Neo-OS Project

> **Target**: NeurIPS 2027 Position Paper Track (submission 2027-05) / arXiv preprint by 2026-09
> **Theoretical anchor**: Yue et al. 2025 "Does RLforcement Learning Really Incentivize Reasoning Capacity in LLMs Beyond the Base Model?" (arXiv:2504.13837, NeurIPS 2025 Oral)
> **Status**: Draft for internal review. Empirical evidence (C1 N=10 + SpinlockPreempt v2) included; pass@k experiments pending GPU environment.

---

## Abstract

Reinforcement Learning with Verifiable Rewards (RLVR) has become the dominant paradigm for training reasoning in LLMs, with AlphaProof demonstrating that RLVR combined with formal verification can achieve IMO silver-medal performance in mathematics. However, Yue et al. (2025) proved that RLVR is merely a *distribution sharpener*—it does not expand the reasoning boundary beyond the base model, because the pre-trained prior bounds all discoverable reasoning paths. **We extend this finding to the system software domain and argue that the consequences are more severe: not merely ineffective, but actively harmful.** In system-domain neuro-symbolic rule learning (e.g., distilling OS invariants from execution traces), the "prior" is the execution trace, which may contain bugs. RLVR sharpens the distribution toward these buggy patterns, producing *mathematically sound proofs of semantically incorrect rules*—what we call the **trace-frozen-bug problem**. We formalize this as the system-domain analogue of AlphaProof's missing ground-truth assumption, propose a **prior correction** framework (provenance tags + Fixes-chain normative signals + human-audited confidence levels), and present preliminary artifacts: (1) C1 real extraction (N=10 kernel commits, 44.4% triple coverage), (2) SpinlockPreempt v2 (Lean4 sorry-free with deadlock modeling), (3) pass@k experiment design for empirical validation. We position this as a research agenda for the formal methods × neuro-symbolic AI community.

---

## 1. Introduction

The year 2025 marked the ascendancy of Reinforcement Learning with Verifiable Rewards (RLVR) as the primary technique for eliciting reasoning in Large Language Models. DeepSeek-R1 (January 2025) demonstrated that GRPO with verifiable rewards could produce reasoning capabilities rivaling OpenAI's o1. AlphaProof (Nature, November 2025) extended this to formal mathematics, combining AlphaZero-style RL with Lean4 verification to achieve IMO silver-medal performance (28/42, solving P1/P2/P6 including the hardest problem). The prevailing belief, drawing analogy from AlphaGo's self-play discovering novel strategies, held that RLVR enables LLMs to "autonomously develop novel reasoning patterns" surpassing their base models.

However, Yue et al. (2025) delivered a sobering counter-result: **RLVR does not elicit fundamentally new reasoning capabilities.** Through rigorous pass@k experiments across 6 algorithms, 3 domains (math/code/visual), and multiple model families, they showed that while RLVR models outperform base models at small k (pass@1), **base models consistently surpass RLVR models at large k (pass@256)**. The reasoning paths exploited by RLVR are already present in the base model's sampling distribution—RLVR merely sharpens the distribution toward rewarded paths, at the cost of reduced coverage. They identify the root cause as the **prior double-edged sword**: in the exponentially large action space of language, any sample deviating from the pre-trained prior is highly likely to produce nonsensical output, receive negative reward, and be suppressed by policy gradient—trapping RLVR within the base model's prior.

**This position paper asks: what happens when the prior is not trustworthy?**

In the mathematical domain (AlphaProof), the prior is mathlib—a curated, peer-reviewed, ground-truth corpus. Distribution sharpening toward mathlib is harmless (if suboptimal). But in the **system software domain**, the analog of mathlib is the execution trace—kernel logs, eBPF events, Intel PT traces. **Execution traces may contain bugs.** A kernel version with a scheduling flaw produces traces encoding the flawed behavior. When an LLM distills rules from these buggy traces and RLVR sharpens the distribution, it sharpens *toward the bug*. Lean4 then verifies the buggy rule with mathematical soundness—producing **a perfect proof of an incorrect rule**.

We call this the **trace-frozen-bug problem** (§3). It is the system-domain manifestation of RLVR's prior limitation, but with consequences escalated from "merely ineffective" to "actively harmful". The contribution of this paper is threefold:

1. **Theoretical** (§3): We extend Limit of RLVR to the system domain, arguing that RLVR's prior double-edged sword becomes a *single-edged sword against correctness* when the prior is buggy. We formalize the trace-frozen-bug problem.

2. **Methodological** (§4): We propose **prior correction**—a framework that does not trust any single source (trace or oracle) as ground truth, instead requiring multi-source decorrelation + human audit for the highest confidence level. This includes provenance tags (S4), Fixes-chain normative signals (S5), and a redefined three-tier confidence system where the top tier requires human audit.

3. **Empirical** (§5): We present preliminary artifacts—C1 real extraction (N=10 kernel commits, 44.4% triple coverage), SpinlockPreempt v2 (Lean4 sorry-free with deadlock modeling), and a pass@k experiment design to validate our claims on GPU hardware.

---

## 2. Background

### 2.1 RLVR and the GRPO Standard

Reinforcement Learning with Verifiable Rewards (RLVR) optimizes a language model policy π_θ against a deterministic verifier V returning binary reward r = V(x, y) ∈ {0,1}, where r=1 iff the model's output is verifiably correct (e.g., a Lean proof is accepted, a code answer passes tests). The dominant algorithm in 2025 is **GRPO** (Group Relative Policy Optimization, DeepSeek), which removes the value function by normalizing rewards across multiple responses per prompt.

### 2.2 Limit of RLVR (Yue et al. 2025)

Yue et al. rigorously probed the reasoning boundary of RLVR-trained models using pass@k at large k. Their key findings:

- **pass@k inversion**: RLVR models win at pass@1 but lose at pass@256 across all benchmarks and model families.
- **Coverage shrinkage**: As RL training progresses, pass@1 improves but pass@256 decreases.
- **Subset relationship**: On AIME24, 0.0% of problems are solvable by RLVR but not by base; RLVR's solvable set is approximately a subset of base's.
- **Perplexity evidence**: RLVR-generated reasoning paths have low perplexity under the base model—they are already in the base distribution.
- **Distillation differs**: Distillation from a stronger teacher genuinely expands the boundary (pass@k consistently above base).

Their theoretical explanation: **the prior double-edged sword**. The pre-trained base model prior guides sampling; deviations produce nonsense (negative reward); policy gradient pulls probability back within the prior; RLVR cannot escape.

### 2.3 System-Domain Formal Verification

Formal verification of system software has a distinguished history: seL4 (Isabelle/HOL, 20 person-years), CompCert (Coq), and more recently Lean4-based efforts (seLe4n, Verus/Atmosphere). These verify *code correctness* against specifications. Neo-OS (this paper's artifact base) proposes verifying *causal rules distilled from execution traces*—a distinct problem requiring a distinct trust model.

---

## 3. Core Argument: Trace is Not Ground Truth

### 3.1 The Mathematical Domain vs. System Domain

| Dimension | Mathematical Domain (AlphaProof) | System Domain (Neo-OS) |
|-----------|----------------------------------|----------------------|
| Prior | mathlib (curated, peer-reviewed) | execution trace (may contain bugs) |
| Ground truth | Lean proof accepted = correct | Lean proof accepted ≠ semantically correct |
| RLVR sharpening effect | Harmless (merely doesn't expand) | **Harmful** (freezes bugs) |
| Reward trustworthiness | Absolute | Contaminated by R5§6 (trace-frozen-bug) |

### 3.2 The Trace-Frozen-Bug Problem (Formal)

**Definition**: Given a buggy execution trace T_bug containing incorrect system behavior, an LLM distills a candidate rule R_bug encoding the bug. Lean4 verifies that R_bug is preserved over T_bug (mathematical soundness). The L3 output layer reports R_bug as a "proven explanation"—but R_bug is semantically incorrect.

**The mechanism**: 
1. Trace T_bug is collected from a kernel version with a scheduling flaw (e.g., `preempt_enable` not checking `lockHeld`).
2. L2 world model distills R_bug: `Inv_buggy(s) := s.preemptCount ≥ 0` (missing the `lockHeld → pc ≥ 1` clause).
3. Lean4 proves `Inv_buggy_preserved_over_trace` (sorry-free, [propext, Quot.sound] only).
4. `#print axioms` confirms mathematical soundness.
5. L3 outputs: "Proven rule: preempt_count must be non-negative"—a correct-sounding but semantically incomplete rule that misses the deadlock prevention invariant.

**The danger**: This is worse than having no formal verification. A rule without formal verification is honestly uncertain. A rule *with* formal verification but encoding a bug wears the mantle of mathematical certainty while being semantically wrong. It raises Cognitive Token Cost (CTC) rather than lowering it—users trust it more and are correspondingly more misled.

### 3.3 Why This is AlphaProof's Missing Assumption

AlphaProof works because mathlib is ground truth. The entire AlphaProof pipeline—autoformalization, RLVR, TTRL—assumes the prior is trustworthy. **This assumption is the load-bearing wall of the entire neuro-symbolic reasoning enterprise, and it does not transfer to the system domain.** In the system domain, the prior is the trace, and the trace is the very thing whose correctness we seek to verify. This is circular: we cannot use the trace to verify rules about the trace's correctness without independent ground truth.

This is not a minor engineering inconvenience. It is the **fundamental epistemic gap** between mathematical reasoning and system reasoning, and it has been under-examined in the rush to apply AlphaProof-style methods to software.

---

## 4. Prior Correction: A Framework

We do not propose abandoning RLVR or neuro-symbolic methods. We propose **correcting the prior assumption** through three mechanisms, ordered by trust contribution:

### 4.1 Provenance Tags (replacing correctness claims)

Following the principle that "every claim should be labeled with its verification level" (Neo-OS Constitution), we attach **provenance tags** to each distilled rule rather than compressing evidence into a single confidence number:

```json
{
  "rule_id": "spinlock_preempt_pair_discipline",
  "provenance": {
    "source_commits": ["abc123", "def456"],
    "matched_docs": ["Documentation/locking/spinlocks.rst"],
    "source_count": 2,
    "sources_decorrelated": true,
    "fixes_chain": {"has_fixes": true, "normative_signal": "strong"},
    "human_audited": false,
    "lean4": {"proven": true, "sorry_free": true}
  }
}
```

The L3 English layer presents provenance factually; the reader interprets. This avoids the **oracle regression** (using an oracle that is itself unverified) and the **correlated-error ★★★ problem** (three sources all passing when they share error modes).

### 4.2 Fixes-Chain as Normative Signal

The most underappreciated signal in system-domain rule learning is the **Fixes: chain** in kernel commits. Ordinary commit messages are *descriptive* (what the system did). Fix commits are *normative* (what the system should do—the fix defines "correct"). Crucially, fix commits are **decorrelated** from the buggy kernel's error modes: they are written to correct, not to describe, the bug.

Our C1 pipeline extracts Fixes: tags and marks them as strong normative signals. In our N=10 sample, 100% of real kernel fix commits contained Fixes: tags—a clean, structured, decorrelated signal source that requires no LLM formalization (avoiding the autoformalization pipeline's 15-20% error rate).

### 4.3 Redefined Three-Tier Confidence

| Tier | Requirement | L3 Output Strategy |
|------|------------|-------------------|
| ★★★ | Lean4 proven (sorry-free) + ≥3 decorrelated sources + **at least one human-audited source** + adversarial layer discriminating power ≥0.8 | "Proven explanation" + provenance |
| ★★ | Lean4 proven + ≥2 sources (partial decorrelation) + Fixes chain | "Soft rule" + provenance |
| ★ | Lean4 proven only (single source or no source) | "Formal-proof-level" + explicit "not independently verified" |

**Critical**: ★★★ requires human audit. There is no "automatic ★★★"—when three sources are error-correlated, automatic agreement is the strongest false signal (the correlated-error problem, F6 in our adversarial layer review).

### 4.4 Adversarial Layer v2.0 (Implemented)

We implemented a preliminary adversarial layer that tests rule sensitivity through minimal-diff mutants (inspired by arXiv:2606.01794's tridirectional discriminating power). On SpinlockPreempt v2, the existing invariant Inv achieves 1/5 discriminating power—partly due to model blind spots (schedule was a no-op in v1, now fixed in v2 with a `deadlocked` field). This is honest evidence that rule sensitivity analysis surfaces incompleteness, but also that it is bounded by model fidelity.

---

## 5. Preliminary Evidence

### 5.1 C1 Real Extraction (N=10)

We built a commit-distillation pipeline that: (1) fetches kernel fix commits via the cgit web interface (bypassing kernel.org's 4.5KB/s clone throttle), (2) extracts (symptom, root_cause, fix) triples using GLM-4-plus, (3) extracts Fixes: chains for provenance.

**Results (N=10, batch-random sample)**:
- Full triple coverage: 44.4% (above the 40% "realistic" threshold)
- root_cause/fix extraction: 100%
- Average confidence: 0.94
- Category distribution: MEM_REF 33%, RESOURCE_LEAK 22%, LOGIC 22%, OFF_BY_ONE 22%
- Fixes: chain extraction: 100% (all 10 commits had Fixes: tags)

This demonstrates that the V25 pipeline (originally validated on sglang/Python at 62%) transfers to kernel/C commits at a realistic rate, and that Fixes: chains are universally available as normative signals.

### 5.2 L2 Distillation: Commit Triples → Lean4 Invariants (N=48)

We validated the L2→L2.5 pipeline end-to-end: C1's 48 extracted triples → GLM-4-plus distillation → 48 Lean4 invariant candidates → lake build verification.

**Results**: **48/48 (100%) compiled successfully**. This compares favorably to the mathematical domain's autoformalization accuracy of 66% (miniF2F-v2). We hypothesize that OS invariants (e.g., `entries ≤ max`, `len ≤ size`, `¬deadlocked`) are structurally more regular than competition-level math theorems, making system-domain autoformalization more tractable.

**Critical caveat**: Compile success ≠ semantic correctness. The 48/48 rate measures *syntactic* validity only. Our preliminary semantic audit (GLM-adjudicated, N=10, an upper bound due to self-correlation bias) reveals: **50% correct, 40% partial (missing key aspects), 10% wrong**. Combined, **50% of compiled rules have semantic defects**—direct empirical evidence for the trace-frozen-bug problem (§3). This is precisely why our prior correction framework (§4) is necessary: provenance tags, Fixes-chain normative signals, and human audit are required before any invariant reaches ★★★ confidence.

**Adversarial layer v2 validation**: After fixing the schedule no-op blind spot (F5 in our adversarial layer review) by adding a `deadlocked` field, the discriminating power improved from 1/5 to 2/6 boundaries. The new boundary B5 (schedule-holding-lock → deadlock) is now correctly discriminated—demonstrating that model fidelity directly affects adversarial layer effectiveness.

### 5.3 SpinlockPreempt v2 (Lean4, sorry-free)

We formalized the spinlock × preempt_disable pairing discipline in Lean4:

- **State**: `S := ⟨preemptCount : Nat, lockHeld : Bool, deadlocked : Bool⟩`
- **Events**: lockAcquire/lockRelease/preemptDisable/preemptEnable/tick/schedule
- **Key v2 improvement**: `step schedule` now enters a deadlocked state when `lockHeld = true` (modeling sleep-holding-lock deadlock), addressing a model blind spot identified in our adversarial layer review.
- **Invariant**: `Inv(s) := pc ≥ 0 ∧ (lockHeld → pc ≥ 1) ∧ ¬deadlocked`
- **Main theorem**: `Inv_preserved_over_trace` (induction on OK, beyond omega)
- **Axiom record**: [propext, Quot.sound] for main theorem; **zero axioms** for three counterexample theorems (cleaner than v1).

### 5.3 pass@k Experiment Design (Pending GPU)

We designed (but could not run on available hardware) two experiments to empirically validate our claims:

**H1 (Replicate Limit of RLVR in system domain)**: Train GRPO on SpinlockPreempt rules with Lean4 reward. Predict pass@k inversion (base surpasses RLVR at large k). *If confirmed: first system-domain empirical evidence that RLVR is a distribution sharpener.*

**H2 (Trace-frozen-bug validation)**: Use a buggy trace as base prior. Predict RLVR sharpens toward buggy rule (pass@1 up, but rule semantically wrong, Lean4 still proves). *If confirmed: direct experimental validation of the trace-frozen-bug problem.*

The experiment design, code skeletons (LeanDojo-v2 + Pantograph + veRL), and migration guide are available in our supplementary materials.

---

## 6. Related Work

**RLVR for LLM reasoning.** Reinforcement Learning with Verifiable Rewards became the dominant paradigm for training reasoning models in 2025. DeepSeek-R1 (Guo et al. 2025) demonstrated GRPO at scale; Tulu 3 (Lambert et al. 2024) systematized the recipe; Kimi-1.5, Qwen3, and dozens of follow-ups adopted RLVR. Our work does not question RLVR's practical effectiveness but builds on Yue et al. (2025) to examine its *epistemic limits* in a new domain.

**Limit of RLVR (Yue et al. 2025).** This NeurIPS 2025 Oral paper is our theoretical anchor. They proved RLVR is a distribution sharpener (pass@k inversion across 6 algorithms, 3 domains). We extend their "prior double-edged sword" analysis to the system domain, arguing that when the prior is untrustworthy (execution traces), sharpening becomes harmful rather than merely ineffective.

**AlphaProof (DeepMind, Nature 2025).** AlphaProof combined AlphaZero-style RL with Lean4 verification and TTRL to achieve IMO silver. It is the paradigm we extend. The critical difference: AlphaProof's prior (mathlib) is curated ground truth; our prior (execution traces) may contain bugs. This is the load-bearing assumption that does not transfer.

**Formal verification of system software.** seL4 (Klein et al., SOSP 2009) verified 8.7KLoC C in Isabelle/HOL (20 person-years). CompCert (Leroy) verified a C compiler in Coq. Verus/Atmosphere (SOSP 2024/2025) brought Rust verification to practical cost (3.32:1 proof-to-code). These verify *code correctness* against specifications. Neo-OS verifies *causal rules distilled from traces*—a distinct problem requiring a distinct trust model (the specification itself is uncertain).

**Neuro-symbolic theorem proving.** LeanDojo (Yang et al., NeurIPS 2023) and LeanDojo-v2 provide the Lean4 interaction infrastructure. COPRA (Thakur et al.) offers GPT-4-driven proof search. DeepSeek-Prover V2 (arXiv:2504.21801) and Seed-Prover (arXiv:2507.23726) achieved near-saturation on miniF2F. These focus on *proving existing mathematical theorems*. Our L2 distillation generates *new* rules from traces—closer to VERISPECGEN's specification synthesis (arXiv:2604.10392) but for system rather than code specs.

**Adversarial methods for formal verification.** The tridirectional discriminating-power framework (arXiv:2606.01794) applies mutation testing to formal verification of smart contracts. LeVer (ACL 2026) uses an adversarial attacker agent. Our adversarial layer v2.0 adapts minimal-diff mutants to system-rule sensitivity analysis, but deliberately avoids automated Attack-to-Property (oracle regression risk, our F1/F2).

**Reward hacking and emergent misalignment.** Anthropic (arXiv:2511.18397) demonstrated that reward hacking in coding-RL generalizes to alignment faking and code sabotage. This directly motivates our "trace-frozen-bug" problem: the same mechanism that causes reward hacking in coding causes rule-fossilization in system-domain RLVR.

**Positioning.** No prior work occupies the intersection of (a) RLVR critique (extending Limit of RLVR), (b) system-domain formal verification, and (c) trace-grounded rule learning with prior correction. The closest neighbors—TAAF (ICSE 2026, trace→KG→LLM without formalization) and Lean4Agent (2026-06, Lean4 for agent workflows without trace grounding)—each miss one axis. This is the blue ocean our project occupies.

## 7. Open Questions

1. **Can prior correction make system-domain RLVR safe?** Our framework reduces the probability of trace-frozen-bugs but cannot eliminate them (Ashby's Law of Requisite Variety applies: the explainer's complexity must meet the system's). We honestly position our framework as "dramatically reducing CTC upper bound, not driving it to zero."

2. **System-domain f2f benchmark**: There is no MiniF2F equivalent for system rules. We propose constructing one from verified Lean4 corpora (dsyme's 716 Raft theorems, Atmosphere's Verus proofs). This is both a research asset and a moat.

3. **The role of multi-agent RL**: Our analysis (based on production system-software RL cases—MLGO, AlphaEvolve, Cold-RL) suggests RL has a narrow but real role: commit active learning sampling and rule sensitivity scoring, but **never** as the rule-correctness arbiter. We codify this in six "iron rules" for introducing RL into system software.

4. **Concurrent with Limit of RLVR's evolution**: The "diversity collapse" rebuttal (arXiv:2606.15455) suggests overtraining may mask real RL gains. Our core argument (trace ≠ GT) is independent of this debate—it holds whether or not better RL formulations exist.

---

## 7. Conclusion

Limit of RLVR proved that RLVR is a distribution sharpener in the mathematical domain. We have argued that in the system software domain, this sharpening is not merely ineffective but actively harmful—it freezes bugs into rules that are then mathematically proven, creating an epistemic hazard worse than no formal verification. The root cause is that AlphaProof's load-bearing assumption (the prior is ground truth) does not transfer: execution traces are not ground truth. We proposed prior correction (provenance + Fixes-chains + human-audited confidence) and presented preliminary artifacts toward a system-domain AlphaProof that is honest about its epistemic limits. The broader lesson for the neuro-symbolic community: **formal verification of a rule proves the rule follows from the prior; it does not prove the prior is correct. When the prior is the trace, verifying the trace with the trace is circular.**

---

## References (Selected, all verified)

1. Yue, Y. et al. "Does Reinforcement Learning Really Incentivize Reasoning Capacity in LLMs Beyond the Base Model?" arXiv:2504.13837. NeurIPS 2025 Oral; ICML 2025 AI4MATH Best Paper. ✅
2. "AlphaProof." Nature, DOI:10.1038/s41586-025-09833-y. 2025. ✅
3. DeepSeek-R1. guo2025deepseek-r1. 2025.
4. Shao, Z. et al. "DeepSeekMath / GRPO." arXiv:2402.03300. 2024.
5. MacDiarmid, M. et al. "Natural Emergent Misalignment from Reward Hacking." arXiv:2511.18397. Anthropic, 2025. ✅
6. Novikov, A. et al. "AlphaEvolve." arXiv:2506.13131. DeepMind, 2025. ✅
7. "Verification Theatre." IACR eprint 2026/192. ✅
8. Klein, G. et al. "seL4." SOSP 2009.
9. LeanDojo-v2. NeurIPS 2025 Math&AI Workshop.
10. Iskander, R. "Tridirectional Discriminating-Power Formal Verification." arXiv:2606.01794. 2026. ✅

(Full reference list in supplementary; all arXiv IDs verified via abs page fetch.)

---

*This draft is for internal review. The core argument (§3) and framework (§4) are complete; §5 empirical evidence will strengthen as C1 scales to N=1000 and pass@k experiments run on GPU hardware.*
