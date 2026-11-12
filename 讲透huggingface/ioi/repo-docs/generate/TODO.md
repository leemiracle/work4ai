The tasks is to implement a simple repository for evaluation LLMs on IOI problems.


## Used frameworks
- You should use LiteLLM to call the LLM providers.
- You should use asyncio to run the LLM calls asynchronously.


## Steps for evaluation:
- We have a dataset of IOI 2024 problems here: https://huggingface.co/datasets/open-r1/ioi-2024 with following format:
```
{
    'name': str,
    'id': str,
    'day': str,
    'subtask': str,
    'statement': str,
    'score': str,
    'time_limit': str,
}

- Each problem is split into multiple subtasks (they have same id, but different subtask column). You will iterate over the problems and get their subtasks.

- You will then take a problem and the subtasks and call a subtask sample funciton. Subtask sapmle function takes a problem and the last integer i, and returns the next subtask to solve.

- You will then create a prompt based on subtasks and call the LLM with random seed. Then generate a next subtask and repeat untill you don't have 50 generations.

- This way you will get 50 generations for each problem. And save them as dataset into org_id(arg)/model_id(arg). The resulting dataset will have following format:
```
{
    'problem_id': str,
    'subtask': str,
    'prompt': str,
    'generation': str,
    'code': str,
    'language': str,
    'model_kwargs': dict,
    'metadata': dict,
}
```

Therefore if you have 90 problems and 50 generations for each problem, the resulting dataset will have 4500 samples.