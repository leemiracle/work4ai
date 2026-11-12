# Beneath the Surface Environments

This repository contains the open-source implementations of several environments
from the paper *Beneath the Surface*: Investigating LLMs' Capabilities for
Communicating with Subtext.

## Installation

This repository was tested on Python 3.13. We recommend setting up a virtual
environment using `venv`

```bash
python3 -m venv subtextenv
source subtextenv/bin/activate
```

You can install all the required packages as follows:

```bash
pip install -r requirements.txt
```

## API keys setup

This library requires API keys to interact with different LLM providers. You
need to set up your keys as environment variables:

```bash
# OpenAI API key
export OPENAI_API_KEY="your-openai-api-key"

# Anthropic API key
export ANTHROPIC_API_KEY="your-anthropic-api-key"

# Google API key
export GOOGLE_API_KEY="your-google-api-key"

# Mistral API key
export MISTRAL_API_KEY="your-mistral-api-key"
```

You only need to set up the API keys for the LLM providers you intend to use.
For example, if you're only running game plays that involve Gemini models, you
only need to set up the `GOOGLE_API_KEY`.

### Getting Tell Me A Story Data

Our shared context experiments use stories from
[Tell Me A Story](https://github.com/google-deepmind/tell_me_a_story) Dataset.
You can get the data using the following commands (**Remember to run these from
the head directory of this repo**):

```bash
mkdir -p data/tell_me_a_story
cd data/tell_me_a_story
wget https://storage.googleapis.com/tell-me-a-story/tell-me-a-story-train_encrypted.jsonl
wget https://storage.googleapis.com/tell-me-a-story/tell-me-a-story-validation_encrypted.jsonl
wget https://storage.googleapis.com/tell-me-a-story/tell-me-a-story-test_encrypted.jsonl
wget https://github.com/google-deepmind/tell_me_a_story/raw/refs/heads/main/keys.zip
unzip keys.zip
```

The dataset is encrypted and you will need to decrypt it for using with our
environments, by following the instructions in the original repository.

Note that the decrypted stories should *not* be posted in plaintext online, or
passed to an API that may result in them being used for training models, in
order to avoid contaminating the dataset.

## Running Experiments

### Visual Allusions

**Base Case (No Shared Context)**
```bash
python -m subtext_bench.visual_allusions.main -c "configs/visual_allusions/experiments.json" -e "4p_all_llm"
```

**Running With Shared Context Between 2 Players**
```bash
python -m subtext_bench.visual_allusions.main -c "configs/visual_allusions/experiments.json" -e "4p_2p_shared_context"
```

You can edit [configs/visual_allusions/experiments.json](configs/visual_allusions/experiments.json) to
try out different setups.

## The Aesopian Author

```bash
python -m subtext_bench.aesopian_author.main -c configs/aesopian_author/experiments.json -e flash_author_pro_critic_inquisitor_lh
```

You can edit [configs/aesopian_author/experiments.json](configs/aesopian_author/experiments.json) to try
out different setups.

## Citing this work

If you use this repository, please reference the corresponding paper.

```
@article{ahuja2025beneath,
      title={{Beneath the Surface}: Investigating LLMs' Capabilities for Communicating with Subtext},
      author={Kabir Ahuja and Yuxuan Li and Andrew Lampinen},
      year={2026},
}
```

## License and disclaimer

Copyright 2026 Google LLC

All software is licensed under the Apache License, Version 2.0 (Apache 2.0); you
may not use this file except in compliance with the Apache 2.0 license. You may
obtain a copy of the Apache 2.0 license at:
https://www.apache.org/licenses/LICENSE-2.0

All other materials are licensed under the Creative Commons Attribution 4.0
International License (CC-BY). You may obtain a copy of the CC-BY license at:
https://creativecommons.org/licenses/by/4.0/legalcode

Unless required by applicable law or agreed to in writing, all software and
materials distributed here under the Apache 2.0 or CC-BY licenses are
distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
either express or implied. See the licenses for the specific language governing
permissions and limitations under those licenses.

This is not an official Google product.
