# IOI: Running tests

## Piston
To evaluate, we rely on Piston (https://github.com/engineer-man/piston) to compile and run the code in a secure and fast sandbox environment. See the [piston](piston/README.md) directory for more details.
To run the evaluation code below, spin up Piston workers and copy the `.env.template` file to `.env` and set the piston variables.

## Running the pipeline
Install dependencies:
```bash
pip install -r requirements.txt
```

Once you have piston setup and running, or have made the necessary changes to the `run_submission` function in [scoring.py](scoring.py) (see below for more info), you can run the pipeline with the following command:

```bash
python tests_runner.py [-h] [--local_results_path LOCAL_RESULTS_PATH] [--id_column ID_COLUMN] [--max_concurrent_requests MAX_CONCURRENT_REQUESTS] [--test_batch_size TEST_BATCH_SIZE] [--dry_run] [--override]
                       [--timeout TIMEOUT] [--add_includes] [--add_messages_column]
                       datasets_to_evaluate results_dataset_name
```
### Arguments
- `datasets_to_evaluate`: The datasets to evaluate (HF hub ids), separated by commas. Also accepts wildcards on the dataset part, such as `open-r1/models-*-fix`
- `results_dataset_name`: The name of the dataset to save the results to.
- `local_results_path`: Path for local results cache, so that you can restart if the script dies.
- `id_column`: The column name of the unique identifier for each submission. `uuid` by default
- `max_concurrent_requests`: The maximum number of concurrent requests to make to the Piston API. Should be roughly the number of piston workers you have.
- `test_batch_size`: Batch size for testing submissions. Will test this number at a time and then check if any scored 0.0. If so, the remaining tests are skipped. Increase if you have many more workers than submissions.
- `dry_run`: If true, the script will not make any actual API calls to Piston.
- `override`: If true, the script will override existing results in the results dataset.
- `timeout`: Timeout for the Piston API calls.
- `add_includes`: If true, the script will attempt to fix some basic missing #include directives in the code.
- `add_messages_column`: If true, the script will add the `messages` column to the results dataset formatted for SFT.

### Examples

Running the pipeline on the official contest solutions with 1500 workers:

```bash
python tests_runner.py open-r1/ioi-sample-solutions my_org/ioi-sample-solutions-results --id_column label --max_concurrent_requests 1500
```
Make sure to compare your results (look at the reports for each problem) to the official contest solutions in the [open-r1/ioi-sample-solutions](https://huggingface.co/datasets/open-r1/ioi-sample-solutions) dataset.


Running on a dataset produced by evaluate.py:

```bash
python tests_runner.py my_org/my-dataset my_org/my-dataset-results --max_concurrent_requests 1500
```

Besides the actual results dataset, the script will also generate and upload markdown reports to the dataset's repo under `reports/my-dataset/README.md`



## Evaluating without piston
To evaluate in a different sandbox environment, you should change the `run_submission` function in [scoring.py](scoring.py). It should mount/create the following files inside the sandbox:
- `graders/<problem_id>.cpp`: The submission code.
- `input.txt`: The input for the problem.
- `correct_output.txt`: The expected output for the problem.
- all the files in `grader_files`
Plus the following 2 very important files:
- [`compile`](custom_setup/compile), the command to compile the submission code with all the grader/checker/manager files.
- [`run`](custom_setup/run), the command to orchestrate the execution of the submission code, managers, time limits, output checking, etc.

As `run` handles time limits, if you require a time limit for a sandbox, you can set a hard limit to 2 or 3 additional seconds from the problem's time limit.

You should return a tuple of `(score, feedback)` from the function, where `score` is the execution's stdout, and `feedback` its stderr, and need to handle some special failure scenarios such as (piston example):

```python

if 'compile' in response and response['compile']['code'] != 0:
    return "0", "Compilation error exit code " + str(response['compile']['code']) + "\n" + response['compile']['stderr']

if response['run']['code'] == 1 and "MemoryError" in response['run']['stderr']:
    return "0", "Memory limit exceeded"

# successful result
if response['run']['stdout']:
    return response['run']['stdout'], response['run']['stderr']

# hard time limit exceeded
if response['run']['signal'] == 'SIGKILL':
    return "0", "Time limit exceeded"

return '0', 'Unknown error'
```
