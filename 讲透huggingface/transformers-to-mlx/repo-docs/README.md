# transformers-to-mlx

<h3 align="center">
    <p>Agent Skill to aid in the conversion of transformers models to MLX</p>
</h3>

<img width="2752" height="1536" alt="thumbnail" src="https://github.com/user-attachments/assets/4d91f9cd-e81a-4ab5-b5ac-e9dcd6329d1b" />

</p>

Use this Skill to support conversion of language models from transformers to MLX. It currently works for **LLM models** to be ported to the [`mlx-lm` repo](https://github.com/ml-explore/mlx-lm).

## Installation

```bash
uv run https://raw.githubusercontent.com/huggingface/transformers-to-mlx/main/install_skill.py
uvx hf skills add --claude
```

This installs both the `transformers-to-mlx` Skill and the `hf` one. The former drives the conversion process, the latter is used to interact with the Hub (to find and download models).

Reload your agent configuration after you install the skills.

## Usage

Prompt your agent with something like:

```
Please, convert the `olmo_hybrid` architecture to MLX.
```

^ This is just an example. The Skill knows how to handle stuff such as MoEs, MLA (DeepSeek style), hybrid SSM + attention, GatedDeltaNet linear attention, distributed inference, and more.

The Skill creates a virtual environment where everything happens. It then installs mlx-lm and transformers, performs model discovery, analyzes configuration files and the transformers modeling code, ports the model to MLX and runs several tests.

When the process completes, the Skill will ask for confirmation to open a PR to the mlx-lm codebase as well as a test file manifest for a separate test harness repo.

Please, do not submit PRs before reviewing 🙏, and check that no other PRs are open for the same task. This Skill is intended as a tool, not an automation. Reviewers time is valuable; opening PRs does not help unless they are high quality. Agents will improve, but for now our guidance is to only open the PR if you stand by it and would have come with a similar solution yourself. Be prepared to iterate with the reviewers, and do not use the Skill for back-and-forth discussions with them; it's not designed for that.

You can also use the Skill to learn about the codebases. For example, fork the mlx-lm repo, run and tests your conversions in your fork and compare with the canonical ports in the official codebase.

[Here's an example PR](https://github.com/pcuenca/mlx-lm/pull/5) (opened against a fork) from a previous development version of the Skill.

You can find more info and some context in our [release blog post](https://huggingface.co/blog/transformers-to-mlx).

## The Test Harness

After the conversion takes place, the Skill can open a PR against a separate [test harness repository](https://github.com/pcuenca/mlx-lm-tests). This is a not-agentic collection of tests that can be run independently on the converted model.

These tests provide additional confidence to both the reviewers and the author (results were not hallucinated by the Skill), and allows the community to verify and reproduce results.

You can run these tests yourself, or [ask me](https://github.com/pcuenca) to do it on our infra.

## Bundled Resources

The Skill ships with a few helpers and resources it uses internally during conversion. They could be useful as standalone tools as well. For example, `scripts/` contains tools like the following:

- `compare_predictions.py` — top-k overlap and logit diffs between transformers and MLX for a single forward pass
- `compare_layers.py` — per-layer hidden state + logits comparison via a single forward pass per framework
- `resolve_dtype.py` and `check_dtype.py` — infer a model's expected runtime dtype, based on the config or the safetensors metadata, and verify it from a forward pass

The notes under `references/` cover multiple architecture details that could be useful as background reading material.

## Tips

- If you are converting large models and have several Macs, you can create a [distributed hosts file](https://ml-explore.github.io/mlx/build/html/usage/distributed.html) and tell the Skill about it. It knows how to rsync stuff and run distributed tests.
- Feel free to question results and iterate with the Skill until you are satisfied.

## Known Issues / Roadmap

- VLMs are not supported. If you point the Skill to a VLM, it will convert the LLM portion of it.
- Quantization is tested, but quantized models are not uploaded to the Hub. We think it doesn't make sense to do it before the modeling PR is approved and merged.
- No _thinking_-specific tests have been designed.

