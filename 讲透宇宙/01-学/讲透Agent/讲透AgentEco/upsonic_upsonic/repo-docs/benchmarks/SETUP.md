# Benchmark Setup Guide

This guide contains the setup steps required to run Upsonic benchmarks.

## ✅ Quick Start

```bash
# 1. Navigate to benchmarks directory
cd /path/to/Upsonic/benchmarks

# 2. Create virtual environment (first time only)
uv venv

# 3. Activate it
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate  # Windows

# 4. Install dependencies (first time only)
uv pip install pydantic python-dotenv pympler anthropic
uv pip install -e ..

# 5. Create environment file (in main directory)
cd ..
echo "OPENAI_API_KEY=your-key-here" > .env
echo "ANTHROPIC_API_KEY=your-key-here" >> .env  # Optional

# 6. Run benchmark
cd benchmarks
python -m overhead_analysis.benchmark --list-tests
```

## 📦 Installed Packages

The virtual environment includes:

### Benchmark Specific
- `pydantic` - For structured output
- `python-dotenv` - Environment variables
- `pympler` - Deep memory profiling (optional)
- `anthropic` - Anthropic API client

### Framework
- `upsonic` - Main framework (editable mode)
- `openai` - LLM provider
- `rich` - Terminal UI
- And other dependencies...

## 🔧 Troubleshooting

### ImportError: No module named 'X'

```bash
# Check if virtual environment is active
which python  # Should show .venv/bin/python

# If not, activate it
source .venv/bin/activate

# Install package
uv pip install <package-name>
```

### ModuleNotFoundError: No module named 'upsonic'

```bash
# Install Upsonic in editable mode
uv pip install -e ..
```

### API Key error

```bash
# Create .env file in main directory
cd /path/to/Upsonic
echo "OPENAI_API_KEY=your-actual-key" > .env
```

### Anthropic API credit balance error

If you see "Your credit balance is too low to access the Anthropic API":

1. Go to [Anthropic Console](https://console.anthropic.com)
2. Navigate to Billing section
3. Add credits to your account
4. Retry the benchmark

## 🎯 Every Time

Before running benchmarks:

```bash
cd benchmarks
source .venv/bin/activate  # Activate virtual env
python -m overhead_analysis.benchmark  # Run benchmark
```

## 📁 File Structure

```
benchmarks/
├── .venv/                  # Virtual environment (in gitignore)
├── .gitignore              # Python, venv, etc.
├── __init__.py
├── utils.py                # Shared utilities
├── README.md               # Main README
├── SETUP.md               # This file
├── Makefile               # Automation commands
│
└── overhead_analysis/      # First benchmark project
    ├── __init__.py
    ├── benchmark.py
    ├── test_cases.py
    ├── README.md
    └── results/
```

## 🚀 For New Benchmark Projects

```bash
# Virtual environment already exists, just activate it
source .venv/bin/activate

# Create new project directory
mkdir -p your_benchmark/results

# Write code and run
python -m your_benchmark.benchmark
```

## 💡 Tips

1. **Activate virtual env in every terminal session**
2. **For package updates**: `uv pip install --upgrade package-name`
3. **To see all packages**: `uv pip list`
4. **Benchmark results**: Stored in `overhead_analysis/results/` directory
   - JSON files contain raw data
   - Markdown files contain formatted reports with comparison table and sample outputs
5. **Using Makefile**: Run `make help` to see all available commands

## 🎨 Makefile Commands

```bash
make setup          # Create venv and install dependencies
make install        # Install dependencies only
make run            # Run default benchmark
make run-all        # Run all test cases
make run-compare    # Compare OpenAI and Anthropic models
make clean          # Clean Python cache
make clean-all      # Clean everything including venv
make help           # Show all commands
```
