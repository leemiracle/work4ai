# Increasing Probability Mass on Answer Choices Does Not Always Improve Accuracy
Repository for the EMNLP 2023 paper [*Increasing Probability Mass on Answer Choices Does Not Always Improve Accuracy*](https://aclanthology.org/2023.emnlp-main.522/).

When using this repository, please cite:
```
@inproceedings{wiegreffe-etal-2023-increasing,
    title = "Increasing Probability Mass on Answer Choices Does Not Always Improve Accuracy",
    author = "Wiegreffe, Sarah  and
      Finlayson, Matthew  and
      Tafjord, Oyvind  and
      Clark, Peter  and
      Sabharwal, Ashish",
    editor = "Bouamor, Houda  and
      Pino, Juan  and
      Bali, Kalika",
    booktitle = "Proceedings of the 2023 Conference on Empirical Methods in Natural Language Processing",
    month = dec,
    year = "2023",
    address = "Singapore",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/2023.emnlp-main.522",
    doi = "10.18653/v1/2023.emnlp-main.522",
    pages = "8392--8417",
}
```

# Requirements

`pip install -r requirements.txt`

To query the OpenAI API, you should set the environment variable `OPENAI_API_KEY` to your API key.

Code is formatted with [`black`](https://github.com/psf/black).

# Scripts

The `main.py` script is the entrypoint for obtaining predictions from any model. The script will create both an output file (.csv) of predictions and a logfile (.log) with some stats in the `./data/` directory.

### Required flags
* `--num-primes {0, 1, 2, 4, 8}` to specify number in-context examples
* `--model {"curie", "davinci", "davinci-instruct-beta", "text-davinci-003", "google/flan-t5-xxl", "facebook/opt-30b"}`
* `--dataset {"openbookqa", "commonsense_qa", "mmlu"}`
* `--prompt-format {"no_answer_choices", "string_answer_choices", "enumerated_answer_choices"}`

### Optional flags
* `--outdir {optional string; defaults to "./data/"}` directory where to save output files
* `--random-seed {optional integer; defaults to 10}`
* `--gpus {optional integer; defaults to 2}` to specify number of GPUs to use to T5 model
* `--overwrite` will overwrite the output files if they already exist
* `--complete_existing` if specified, this will re-start and complete partially completed runs, appending to the same output file.
* `--uncontextualized_premise` will compute the predictions using the uncontextualized premise prompt format (denominator in probability normalization equations). Predictions will be stored under `./data/{dataset}/uncontextual_preds/`.

### Example

For example, to run predictions on the OpenbookQA test set using the OpenAI `curie` model with 0 in-context examples and the enumerated prompt, run: ```python main.py --num-primes 0 --model curie --random-seed 10 --dataset openbookqa --prompt-format enumerated_answer_choices```

`run_experiments.sh` gives further examples.

# Plotting and Analysis Files

The `plotting/` and `analysis/` files contain code for plotting and analyzing the results. The `plotting/` files are used to generate the figures in the paper. The `analysis/` files are used to compute the statistics in the paper. See the respective READMEs for more details.
