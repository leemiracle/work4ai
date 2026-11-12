# Model Spec Evals

The Model Spec specifies desired behavior for the models underlying OpenAI's products, including our APIs (see https://github.com/openai/model_spec).
The Model Spec Evals is an evaluation suite consisting of:
- a collection of evaluation prompts that measure a candidate model's adherence to the full Model Spec
- code to run the evaluations using the [Inspect AI framework](https://github.com/UKGovernmentBEIS/inspect_ai).

## Companion dataset repo

This repo expects the prompt dataset from the companion repo: [Model Spec Eval Dataset](https://github.com/openai/model_spec_dataset).
Please check out that repo and point `dataset_dir` at its `dataset/` directory when running evals.

## Local setup

- **Prerequisites**: Python 3.10+ and an OpenAI API key available via the `OPENAI_API_KEY` environment variable.
- **Create a virtual environment**
  - macOS/Linux: `python3 -m venv .venv`
  - Windows (PowerShell): `py -3 -m venv .venv`
- **Activate the environment**:
  - macOS/Linux: `source .venv/bin/activate`
  - Windows (PowerShell): `.venv\Scripts\Activate.ps1`
- **Install dependencies**: `python -m pip install --upgrade pip && pip install -r requirements.txt`

## Run the suite

To run the full suite, run the following command from this directory (replace `/path/to/model_spec_dataset/dataset` with your local path):
```bash
inspect eval src/model_spec_evals/tasks.py --model openai/gpt-4o-mini --display rich -T dataset_dir=/path/to/model_spec_dataset/dataset
```

If Inspect still reports that it cannot find any tasks, double-check that the editable install completed successfully (`pip install -r requirements.txt`) and that you are running inside the activated virtual environment.
Note: without `--display rich`, the default is `--display full` and the TUI is known to crash when there are too many samples.
You will see output after the run like this:
```bash
╭────────────────────────────────────────────────────────────────────────────────────╮
│ model_spec_evals (587 samples): openai/gpt-4o-mini                                 │
╰────────────────────────────────────────────────────────────────────────────────────╯
dataset_dir: ~/code/model_spec_dataset/dataset
total time: 0:39:58
openai/gpt-4o-mini 258,737 tokens [I: 49,788, CW: 0, CR: 0, O: 208,949, R: 0]
openai/gpt-5 33,338,551 tokens [I: 32,778,942, CW: 0, CR: 0, O: 559,609, R: 450,304]

model_graded_spec_section_compliance
style 0.703
chain_of_command 0.667
best_work 0.393
seek_truth 0.667
stay_in_bounds 0.611
all 0.622

Log: logs/2026-02-03T13-11-08-05-00_model-spec-evals_eKyMRnoVdZJYKKxx29eCjQ.eval
```
This reports the compliance rate for each top-level section, as well as `all` which is the compliance rate over the entire spec.
It also reports token usage for both the candidate model (`--model`, here `openai/gpt-4o-mini`) and the grader model (`-T grader_model`, default `openai/gpt-5`), which is why both model names appear.

By default, this only runs a single epoch (sample per candidate model) and a single grader sample.
Increase the number of samples from the candidate model with e.g., `--epochs 10`, which are averaged over.
Increase the number of grader samples (from which we take the median) with e.g., `-T num_grader_samples=5`.
One can also specify a different model to use for the grader, e.g. `-T grader_model=openai/gpt-5`.

You can additionally filter on sections (`-T section_filter=chain_of_command,avoid_errors`) and focus ids (`-T focus_filter=8ep1,adau`).
The standard Inspect CLI argument can be used to filter by prompt id, i.e., `--sample-id 46b7a94e-feb9-440f-bea1-537c474a914f,d7b36bdd-339a-47dd-8999-263acddd61ad,dd9afa72-c9cf-4944-8fe6-3f6e3970c01f,9e9cb7b8-6b1c-4735-95c0-1a87cc8d1937`.

### Reproduce blog post setting

The results reported in our [blog post](https://alignment.openai.com/model-spec-evals/) were obtained by sampling
the target model 20 times on each prompt, and for each target model sample we sample the grader model 5 times and take the median.
Note that the results may not be fully reproducible because some prompts are skipped because the OpenAI API only supports developer
messages for newer models. However, while the absolute scores may not be reproducible, directionality between models should roughly be reproducible.
To reproduce the blog-post setting, use `--epochs 20` and `-T num_grader_samples=5`.
For example, running with `openai/gpt-5`:

```bash
inspect eval src/model_spec_evals/tasks.py \
  --model openai/gpt-5 \
  --display rich \
  --epochs 20 \
  -T dataset_dir=/path/to/model_spec_dataset/dataset \
  -T num_grader_samples=5 \
  -T grader_model=openai/gpt-5
```

## View results in the web viewer

To launch the Inspect log viewer for local results:

```bash
inspect view start
```

The command output will print a URL; open that URL in your browser.
