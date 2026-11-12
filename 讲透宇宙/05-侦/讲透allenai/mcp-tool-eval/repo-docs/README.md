# MCP-based Tool-use Evaluations

This repository provides code for running MCP-based tool-use evaluations used for developing Olmo 3, particularly LitQA2 and SimpleQA. It uses vLLM to serve the model and [OpenAI Agents SDK](https://openai.github.io/openai-agents-python)
for running inference with MCP servers. Each evaluation involves
1. running inference on the corresponding dataset with the relevant tools
2. computing metrics using evaluation-specific logic on the trajectories resulting from inference

## Installation

```
conda create -n mcp_eval python=3.12
conda activate mcp_eval
pip install -e .
```

SimpleQA uses the [MCP tools](https://github.com/rlresearch/dr-tulu/tree/main/agent) from the [DR Tulu](https://allenai.org/blog/dr-tulu) project. This server can be installed separately as follows:

```
uv pip install dr_agent
```

## Inference

The script `mcp_tool_eval/inference.py` run an agent loop using Agents SDK with the relevant MCP servers plugged in. If the model being used is a local model or one hosted on HuggingFace, the script also lauches a vLLM server before running the agent loop if the following option is specified: `--model_type vllm`.

Run the following command for the full list of options

```
python mcp_tool_eval/inference.py -h 
```

### Inference for LitQA2

LitQA2 uses the [Asta Scientific Corpus](https://allenai.org/asta/resources/mcp) MCP server. Setting the `S2_API_KEY` environment variable gives you a higher rate limit to use this server. This server runs with `npx` (see `mcp_tool_eval/config.py` for the command) so you may have to install Node.js.

You can use the following command for running inference using a vllm server.

```
python mcp_tool_eval/inference.py --model [model-name] --model_type vllm --tool_call_parser [parser-name] --extra_vllm_args [optional-vllm-args] --mcp_server asta-tools --system_prompt [key-to-system-prompt] --temperature [temperature] --max_turns [max-number-of-tool-calls-per-assistant-turn] --data allenai/litqa2_asta_bench --split test --output data/output.jsonl --max_concurrency 10
```

`--tool_call_parser` can be used to specify the name of the tool call parser to use. See more details [here](https://docs.vllm.ai/en/stable/features/tool_calling). If the parser you want to use is not one of the official ones, you can specify a tool parser plugin using `--extra_vllm_args`. The args should be specified as a dict, i.e.:

```
{'tool-parser-plugin': [path to the pligin]}
```

`--mcp_server` specifies the name of the MCP server to use for inference and `--system_prompt` specifies the name of the system prompt to use. The list of options for these values can be found in `mcp_tool_eval/config.py`. You can add new values there if needed.

`--max_concurrency` specifies the number of concurrent requests to process during inference. Setting this to a value much higher than `10` can make you it the rate limit of the Asta MCP server.

You can use the following command to evaluate an OpenAI model.

```
python mcp_tool_eval/inference.py --model [model-name] --model_type openai --mcp_server asta-tools --system_prompt [key-to-system-prompt] --temperature [temperature] --max_turns [max-number-of-tool-calls-per-assistant-turn] --data allenai/litqa2_asta_bench --split test --output data/output.jsonl --max_concurrency 10
```


### Inference for SimpleQA

SimpleQA uses the following tools from the DR Tulu MCP server:

- `semantic_scholar_snippet_search`
- `serper_google_webpage_search`
- `serper_fetch_webpage_content`

You will need to setup the `S2_API_KEY` and `SERPER_API_KEY` as environment variables to use this MCP server.

You can use the following command to run inference for Simple QA:

```
python /stage/eval/mcp_inference.py --model [model-name] --model_type vllm --tool_call_parser [parser-name] --extra_vllm_args [optional-vllm-args] --mcp_server dr-tulu --system_prompt [key-to-system-prompt] --temperature [temperature] --max_turns [max-number-of-tool-calls-per-assistant-turn] --data allenai/simpleqa_full --split test --output output.jsonl --max_concurrency 10 --read_prompts_from_messages
```

See the section on LitQA2 inference for an explanation of the arguments.


## Evaluation

For evaluating LitQA2 outputs:

```
python mcp_tool_eval/litqa2_eval.py --test_trajectories data/output.jsonl --output data/litqa2_metrics.json
```

For evaluating SimpleQA outputs:

```
python mcp_tool_eval/simpleqa_eval.py --test_trajectories data/output.jsonl --output data/simpleqa_metrics.json
```
