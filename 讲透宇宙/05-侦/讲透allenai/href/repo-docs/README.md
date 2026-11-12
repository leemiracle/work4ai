# HREF: Human Response Guided Evaluation for Instruction Following

[![made-with-python](https://img.shields.io/badge/Made%20with-Python-red.svg)](#python)

<div align="center">

📑 [Paper](https://arxiv.org/abs/2412.15524) | 🤗 [Leaderboard](https://huggingface.co/spaces/allenai/href) | 🤗 [Development Set](https://huggingface.co/datasets/allenai/href) | 🤗 [Human Agreement Set](https://huggingface.co/datasets/allenai/href_preference)

 <img src="assets/Ai2_logo_pink_RGB.png" alt="HREF logo" height="50"/>
</div>

### Announcement
* **12/20/2024**: 🌟We officially publish the paper [HREF paper](https://arxiv.org/abs/2412.15524), along with this codebase, the [HREF leaderboard](https://huggingface.co/spaces/allenai/href), [the development set](https://huggingface.co/datasets/allenai/href), and [the human agreement set](https://huggingface.co/datasets/allenai/href_preference)! 🌟

### Citation
```
@article{lyu2024href,
      title={HREF: Human Response-Guided Evaluation of Instruction Following in Language Models}, 
      author={Xinxi Lyu and Yizhong Wang and Hannaneh Hajishirzi and Pradeep Dasigi},
      journal={arXiv preprint arXiv:2412.15524},
      year={2024} 
}
```

## Install
Make a new Python 3.10 environment and install the `href` package.

```bash
# (optional)create the conda environment
conda create -n href python=3.10
conda activate href
# install the href package
pip install -e .
```

## Quick Start 🏃 
To evaluate a supported model on href development set (See a list under `href/generation/configs`), run:
```bash
href_evaluate \
    --model_name Llama-3.1-8B-Instruct \
    --annotator href
```


## Evaluation on HREF 🔗
### Evaluate a supported model
To evaluate a supported model (See a list under `href/generation/configs`) beginning from generating its output using a supported annotator, run:
```bash
href_evaluate \
    --model_name Llama-3.1-8B-Instruct \
    --annotator llama3.1-70b_basic_w_reference \
    --use_human_reference
```
<details>
<summary> General arguments </summary>

- `--model_name`❗: the model name that corresponds to the name of the yaml configuration file under `generation_config_dir` (exclude `.yaml`).
- `--generation_config_dir`: the directory that contains the model generation configuration files.
- `--dataset`: the huggingface dataset name or the path to a local file to use for evaluation. Default to use the development set of HREF.
- `--split`: the split to use in `dataset`. Default to be `dev`.
- `--nr_cateogry`: categories in the HREF to include. Default to use all 8 categories.
- `--seed`: random seed.
- `--save_dir`: directory to save all results.
- `--cache_dir`: the directory to store downloaded datasets, models, and intermmediate annotation files
</details>

<details>
<summary> Evaluation arguments </summary>

- `annotator`❗: name of the evaluation methods. It has to be one the three following: 1. a basic annotator defined in `evaluation/evaluators.DEFINED_ANNOTATORS`. 2. a configuration name for llm_as_a_judge that corresponds to a directory in `llm_as_a_judge`. 3. a suite of the above two types of unit evaluators defined in `evaluation/evaluators.DEFINED_ANNOTATOR_SUITE_DICT`. Default to be suite `href` that we defined in our paper.
- `--config_dir`: the directory to contain configures for llm_as_a_judge evaluators.
- `--use_human_reference`❗: whether of not `annotator` needs to use the human responses. No need to specify if `annotator` specifies a evaluator suite. 
</details>


### Evaluate a custom model
There are several ways to evaluate your own model/tokenizer on the development set:

<!-- - `--response_dir`: the directory that contains pre-generated model outputs. If specified, we will skip output generation and jump directly into evaluation. -->

#### Option 1: if your model supports the [huggingface transformers interface](https://huggingface.co/docs/transformers/index):
Create a generation configuration for your model (examples can be found under `generation/configs`), see the dropdown below to see a discription for each configurable argument in the yaml file: 
<details>
<summary> Generation arguments </summary>

- `model_name_or_path`❗: the huggingface model name or the path to a local directory that contains the model.
- `tokenizer_name_or_path`❗: the huggingface tokenizer name or the path to a local directory that contains the tokenizer
- `use_vllm`: if given, we will use vLLM to generate the responses.
- `use_slow_tokenizer`: if given, we will use the slow tokenizer.
- `max_new_tokens`: maximum number of new tokens to generate.
- `temperature`❗: the temperature we use for model generation.
- `batch_size`: batch size for generation.
- `load_in_8bit`: load model in 8bit mode, which will reduce memory and speed up inference.
- `gptq`: if given, we're evaluating a 4-bit quantized GPTQ model.
- `format`❗: a string that must contain the placeholder `{prompt}` will be applied to every input for the model generation; designed for applying chat format; will call the tokenizer's `apply_chat_template` if set to the string `default`; remove this paratmer if no template needed to be applied.
</details>

Now run:
```bash
href_evaluate \
    --model_name <your configuration file name> \
    --annotator href \ 
    --generation_config_dir < directory cotaining your file>
```

#### Option 2: if you only have generated responses
1. Generate model responses to the `instruction` field of the data in your own way.
2. Make sure to save responses in the following structure
```
📂 <your response directory>
 ┣ 📂 Brainstorm
 ┃ ┗ 📜 responses.jsonl
 ┣ 📂 Open QA
 ┃ ┗ 📜 responses.jsonl
 ┣ ...
 ┃ ...
 ┣ 📂 Multi-Document Sythesis
 ┃ ┗ 📜 responses.jsonl
```
where each data point in responses.jsonl contains the fields: `instruction`, `output`, `generator`.

3. Now run with `--response_dir` specified:
```bash
href_evaluate \
    --model_name <any custom model name> \
    --response_dir <your response directory> \
    --annotator href 
``` 

#### Option 3: add an API model other than OpenAI
Please follow the logic how we implement OpenAI API in `href/generation/generate.py` to add your own API model, which is relatively straightforward.

### Build local leaderboard
To build the leaderboard using the evaluation results, run:
```bash
python scripts/build_leaderboard.py \
    --models <model_1> <model_2> ... <model_n> \
    --result_dir <path to directory that contains results>
```
<details>
<summary> Full arguments </summary>

- `--models`: name of the models to build the leaderboard
- `--annotator`: name of the evaluator that generated the annotation results.
- `--nr_category`: categories in the HREF to include.
- `--result_dir`: path to the dir that contains the annotation files. 
- `--save_dir`: directory to save all results. 
 
</details>



### Submit to HREF Leaderboard 🚀
To submit your custom model / change the configuration of your model to be evaluated on HREF's evaluation set and posted on the [leaderboard](), create a Github issue or directly email us at xxxATallenaiDOTorg with either the model generation configuration you have created in Option 1 in **Evaluate a custom model**.

## Human Agreement Analysis
To calculate the human agreement rate of an evaluation method on HREF human agreement set (Section 3 and 4 in the paper), run:
```bash
href_calculate_agreement \
    --annotator llama3.1-70b_basic_w_reference \
    --use_human_reference
```
<details>
<summary> General arguments </summary>

- `--dataset`: the huggingface dataset name or the path to a local file to use for analysis. Default to use the human agreement set of HREF.
- `--split`: the split to use in `dataset`.
- `--nr_cateogry`: categories in the HREF to include. Default to use all 8 categories.
- `--seed`: random seed.
- `--save_dir`: directory to save all results.
- `--cache_dir`: the directory to store downloaded datasets, models, and intermmediate annotation files
</details>

<details>
<summary> Evaluation arguments </summary>

- `annotator`❗: name of the evaluation methods. It has to be one the three following: 1. a basic annotator defined in `evaluation/evaluators.DEFINED_ANNOTATORS`. 2. a configuration name for llm_as_a_judge that corresponds to a directory in `llm_as_a_judge`. 3. a suite of the above two types of unit evaluators defined in `evaluation/evaluators.DEFINED_ANNOTATOR_SUITE_DICT`. Default to be suite `href` that we defined in our paper.
- `--config_dir`: the directory to contain configures for llm_as_a_judge evaluators.
- `--use_human_reference`❗: whether of not `annotator` needs to use the human responses. No need to specify if `annotator` specifies a evaluator suite. 
</details>


## Add a New Evaluator
For this section, we give instructions on how to add a new evaluator `<new_evaluator>` that can be passed as the argument following `--annotator` for all commands. 

### Add a Non-LLM-based evaluator
1. Create a function for your evaluator in `href/evaluation/evaluators.py`.
2. Add the name `<new_evaluator>` to `href.evaluation.evaluators.DEFINED_ANNOTATORS`.
3. Run: 
```bash
href_calculate_agreement \
    --annotator <new_evaluator> \
    --use_human_reference
```

### Add an LLM-based evaluator
To use llm_as_a_judge, we use a external package: a [modified version](https://github.com/tatsu-lab/alpaca_eval) of [AlpacaEval](https://github.com/tatsu-lab/alpaca_eval). To create a new llm_as_a_judge evaluator, we modify the configuration with the following steps:

#### 1. (Optional) Create a new prompt template 
* Create a new prompt template `<new_template>.txt` under `href/llm_as_a_judge/prompt_templates`. 
* Note that besides the text, there are many placeholders of models' special tokens for different models to fit in, do not change their names. 
* Refer to the existing template to write new templates.

#### 2. Add a new evaluator configuration
* This step is to specify the configuration of your evaluator both in generation and in modifying the base prompt template (due to different special tokens / system prompt for different models).
* Add the configuration for `<new_evaluator>` under `href/llm_as_a_judge/model_settings.json`. 
* The dictionary `template_kwargs` contains keys that corresponds to the placeholders in the prompt templates, please fill the values with the corresponding special token of your model.
* `fn_completions` and `completions_kwargs` are the configurations for the judge models. You can refer to the existing configurations for most of the desired setting. Please refer to [AlpacaEval](https://github.com/tatsu-lab/alpaca_eval) for more advanced settings.

#### 3. Create the configuration file 
To create the configuration file using the configurations from the previous two steps, run:
```bash
href_create_config \
    --model_config_name <new_evaluator> \
    --template_name <new_template> 
```
<details>
<summary> Required Arguments </summary>

- `--model_config_name`❗: the name of the model configuration used as the judge defined in `href/llm_as_a_judge/model_settings.json`.
- `--template_name`❗: the name of the template file in `href/llm_as_a_judge/prompt_templates` (without the suffix).
</details>

<details>
<summary> Optional Arguments </summary>

- `--config_dir`: the directory to save the resulting configuration.
- `--no_exmple`: if specified, remove the demonstration examples in the prompt.
- `--temperature`: the temperature for the judge model.
</details>

This will create a configuration directory with the name `<new_evaluator>_<new_template>` under `config_dir` (default to be `href/llm_as_a_judge/configs`), which contains a configuration yaml file and a resulting prompt template. Now run:
```bash
href_calculate_agreement \
    --annotator `<new_evaluator>_<new_template>` \
    --use_human_reference
```
### Add an Evaluator suite
To create a evaluator suite where different unit evaluators are used for different categories, append to `href/evaluation/evaluators.py/ANNOTATOR_SUITE_DICT` where you specify the unit annotator with `annotator` and whether each annotator uses human responses with `use_human_reference` for each category. Then run:
```bash
href_calculate_agreement --annotator `<new_evaluator_suite>`
```

*Note that you should optionally pass in `--use_human_reference` according to whether your evaluator need to utilize the human responses unless your are specifying a evaluator suite.*

### Comparing Evaluators
To compare the human agreement rates among different annotators, run:
```bash
python scripts/compare_annotators.py \
    --annotators <evaluator_1> <evaluator_2> ... <evaluator_n>  \
    --result_dir <path to directory that contains results>
```
<details>
<summary> Full arguments </summary>

- `--annotors`: names of the evaluation methods. Each has to be one the three following: 1. a basic annotator defined in evaluation/evaluators.DEFINED_ANNOTATORS. 2. a configuration name for llm_as_a_judge that corresponds to a directory in llm_as_a_judge. 3. a suite of the above two types of unit evaluators defined in evaluation/evaluators.DEFINED_ANNOTATOR_SUITE_DICT`.
- `--dataset`: the huggingface dataset name or the path to a local file to use for analysis. Default to use the human agreement set of HREF.
- `--split`: the split to use in `dataset`.
- `--nr_cateogry`: categories in the HREF to include. Default to use all 8 categories.
- `--seed`: random seed.
- `--save_dir`: directory to save all results.
- `--cache_dir`: the directory to store downloaded datasets, models, and intermmediate annotation files
</details>
