## Generate generate `rick_science`


### Generation the questions

```
export OPENAI_API_KEY=your_openai_api_key
python generate_questions.py > questions.txt
```

### Generation the answers

```
python generate_answers.py
```

Results will be saved in `dataset.jsonl`.

### Push the dataset

```python
from datasets import load_dataset

dataset = load_dataset("json", data_files='dataset.jsonl')
dataset.push_to_hub("qgallouedec/rick-science")
```

