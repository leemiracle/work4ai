# MolmoSpaces Policy Zoo

This repo provides plug-and-play integration for running different policies (both from Ai2 and third parties) on [MolmoSpaces](https://github.com/allenai/molmospaces).

## Installation

```bash
pip install -e .
```

Policy dependencies are extras, so those should be specified during installation to use a particular policy. For example, `pip install -e .[molmobot]`. See the policy's documentation for more information.

## Running a policy

See the policy documentation in this repo for detailed instructions. In general, you can run a policy with:

```bash
python -m molmo_spaces.evaluation.eval_main <config_module>:<config_name> --benchmark_dir <benchmark_path>
```

Use `--help` to see additional evaluation options, including disabling wandb, limiting number of trajectories, etc.

To modify different aspects of the evaluation, edit the experiment config.

## Contributing new policies

Contributions adding new policies are welcome! Please see [the MolmoBot implementation](./molmospaces_zoo/molmobot/) as an example. Generally, policy implementations should be self-contained and stored in a subdirectory of `molmospaces_zoo`. A policy's dependencies should be an optional dependency group in the `pyproject.toml`.

### Development

Install with:

```bash
pip install -e .[dev]
```

We use `ruff` to format code, and a CI enforces compliance in PRs. To format the code, run:

```bash
ruff format .
```
