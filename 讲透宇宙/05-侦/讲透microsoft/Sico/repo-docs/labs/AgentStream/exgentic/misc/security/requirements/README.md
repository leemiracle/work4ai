# Requirements Files

This directory contains frozen requirements for each virtual environment.

## Directories

Each environment has its own directory with a `requirements.txt` file:

- `core/requirements.txt` - Core environment with all optional dependencies
- `gsm8k/requirements.txt` - GSM8K benchmark environment
- `hotpotqa/requirements.txt` - HotpotQA benchmark environment
- `appworld/requirements.txt` - AppWorld benchmark environment
- `browsecompplus/requirements.txt` - BrowseComp+ benchmark environment
- `swebench/requirements.txt` - SWE-bench benchmark environment
- `tau2/requirements.txt` - TAU-2 benchmark environment

## Usage

To recreate an environment from a requirements file:

```bash
# Create a new virtual environment
uv venv .venv --python 3.11

# Activate it
source .venv/bin/activate

# Install from requirements
uv pip install -r misc/security/requirements/core/requirements.txt
```

## Notes

- These files are generated automatically by `misc/security/setup_environments.sh`
- They represent the exact package versions installed in each environment
- Only PyPI packages are included (no git or local installs)
- Regenerate by re-running the setup script

## Generation Date
