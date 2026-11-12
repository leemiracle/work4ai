# Measuring Association Between Labels and Free-Text Rationales

This repository contains code for the EMNLP 2021 paper ["Measuring Association Between Labels and Free-Text Rationales"](https://aclanthology.org/2021.emnlp-main.804.pdf) by Sarah Wiegreffe, Ana Marasović and Noah A. Smith.

When using this code, please cite:
```
@inproceedings{wiegreffe-etal-2021-measuring,
    title = "{M}easuring Association Between Labels and Free-Text Rationales",
    author = "Wiegreffe, Sarah  and
      Marasovi{\'c}, Ana  and
      Smith, Noah A.",
    booktitle = "Proceedings of the 2021 Conference on Empirical Methods in Natural Language Processing",
    month = nov,
    year = "2021",
    address = "Online and Punta Cana, Dominican Republic",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/2021.emnlp-main.804",
    pages = "10266--10284",
    abstract = "In interpretable NLP, we require faithful rationales that reflect the model{'}s decision-making process for an explained instance. While prior work focuses on extractive rationales (a subset of the input words), we investigate their less-studied counterpart: free-text natural language rationales. We demonstrate that *pipelines*, models for faithful rationalization on information-extraction style tasks, do not work as well on {``}reasoning{''} tasks requiring free-text rationales. We turn to models that *jointly* predict and rationalize, a class of widely used high-performance models for free-text rationalization. We investigate the extent to which the labels and rationales predicted by these models are associated, a necessary property of faithful explanation. Via two tests, *robustness equivalence* and *feature importance agreement*, we find that state-of-the-art T5-based joint models exhibit desirable properties for explaining commonsense question-answering and natural language inference, indicating their potential for producing faithful free-text rationales.",
}

```
## Revision to Camera-Ready (August 2022)
In a previous version of the paper, we referred to our rationale quality metric as simulatability, however we realized that simulatability is computed using predicted rather than gold labels, and our implementation uses gold labels. We've submitted a revised version of the PDF to the ACL Anthology and to arXiv to clarify this. `highlighted_revision.pdf` contains this version with changes between the old and new versions highlighted.

Detailed description of revisions:
- The second paragraph under “Evaluation” in Section 2, where the metric is explained, has been updated to clarify this distinction, explain our metric, and why we chose it over simulatability.
- Appendix A.6 has been added to further explain the distinction between our metric and simulatability, and how it may impact our results.
- All references to the term “simulatability” have been changed to the phrase “rationale quality”.
- We added a name to the acknowledgements section in regards to this revision.
- No results have changed.

## Requirements

`pip install -r requirements.txt`
Note: will install Pytorch without any CUDA support; see the requirements file for alternatives.

The code on this branch has been updated from the original codebase to work with upgraded packages, in order to facilitate an easier install process (the original package versions are now too outdated to install easily). If you're looking for the original code (which will exactly reproduce the paper's results), please refer to the `legacy` branch. Relatedly, I can't guarantee the code on this branch will exactly reproduce the paper's results (and in some cases, it may improve them, in part due to improvements in Huggingface's T5 tokenizer).

## Note about Decoding
- To improve results further, you can update the minimum length of the generated sequences to 100 tokens or more (line 135 in custom_args.py). This is not currently done to preserve replicability of the paper's results.

## Joint T5 Models (I-->OR)
- Training + Optional Inference:
`python input_to_label_and_rationale.py --output_dir [where_to_save_models] --task_name [esnli, cos_e] --do_train --num_train_epochs 200 --per_device_train_batch_size 64 --per_device_eval_batch_size 64 --logging_first_step --logging_steps 1 --save_steps 1 --save_total_limit 11 --seed 42 --early_stopping_threshold 10 --version_name [for cos_e, specify v1.0 or v1.11]`
    - evaluation options (can add any combination of these flags) to perform once training is complete: `--do_eval --dev_predict --train_predict --test_predict`
- Inference on a previously-trained model:
`python input_to_label_and_rationale.py --output_dir [where_to_save_models; nothing will be saved here] --task_name [esnli, cos_e] --pretrained_model_file [path to pretrained model directory] --per_device_eval_batch_size 64 --seed 42 --version_name [for cos_e, specify v1.0 or v1.11]`
    - evaluation options (can add any combination of these flags): `--do_eval --dev_predict --train_predict --test_predict`
    - if you already have a file of generations in the pretrained model directory, you can specify that via the flag `---generations_filepath` instead of specifying a `--pretrained_model_file` to load. This will save time by loading the generations from the file rather than having the model re-generate a prediction for each instance in the specified data split(s).
        - The above command changes to: `python input_to_label_and_rationale.py --output_dir [where_to_save_models; nothing will be saved here] --task_name [esnli, cos_e] --generations_filepath [path to pretrained model directory]/checkpoint-[num]/[train/test/validation]_generations.txt --per_device_eval_batch_size 64 --seed 42 --version_name [for cos_e, specify v1.0 or v1.11]`

## Pipeline (I-->R; R-->O) Models

### I-->R model (first)
- same as I-->OR model but with addition of `--rationale_only` flag.

### R-->O model (second)
- Training + Optional Inference:
`python rationale_to_label.py --output_dir [where_to_save_models] --task_name [esnli, cos_e] --do_train --num_train_epochs 200 --per_device_train_batch_size 64 --per_device_eval_batch_size 64 --logging_first_step --logging_steps 1 --save_steps 1 --save_total_limit 11 --seed 42 --early_stopping_threshold 10 --use_dev_real_expls --version_name [for cos_e, specify v1.0 or v1.11]`
    - evaluation options (can add any combination of these flags) to perform once training is complete: `--do_eval --dev_predict --train_predict --test_predict`
    - the model is always trained (and optionally evaluated) on ground-truth (dataset) explanations.

- Inference on a previously-trained model (also for evaluating model-generated explanations):
`python rationale_to_label.py --output_dir [where_to_save_models; nothing will be saved here] --task_name [esnli, cos_e] --pretrained_model_file [path to pretrained model directory] --per_device_eval_batch_size 64 --seed 42 --version_name [for cos_e, specify v1.0 or v1.11]`
    - evaluation options (can add any combination of these flags): `--do_eval --dev_predict --train_predict --test_predict`
    - source of input explanations: specify either `--use_dev_real_expls` to use dataset explanations, or `--predictions_model_file [path_to_pretrained_model_directory/checkpoint_x/train_posthoc_analysis{_1}.txt]` to specify a file of predicted model explanations to use as inputs. Note the train_posthoc_analysis.txt does not have to exist, but the splits you are predicting on do (e.g. {train,test,validation}_posthoc_analysis.txt depending on which evaluation flags (--{train,dev_test}_predict) you've specified). The code will substitute these split names into the filepath passed in.
    - if you already have a file of generations in the pretrained model directory, you can specify that via the flag `---generations_filepath` instead of specifying a `--pretrained_model_file` to load. This will save time by loading the generations from the file rather than having the model re-generate a prediction for each instance in the specified data split(s).
        - The above command changes to: `python rationale_to_label.py --output_dir [where_to_save_models; nothing will be saved here] --task_name [esnli, cos_e] --generations_filepath [path to pretrained model directory]/checkpoint-[num]/[train/test/validation]_generations.txt --per_device_eval_batch_size 64 --seed 42 --version_name [for cos_e, specify v1.0 or v1.11]`

### IR-->O model variant (replaces R-->O)
- same as R-->O model but with addition of ``--include_input`` flag.
- Rationale quality of a set of rationales is computed as IR-->O performance minus I-->O performance using the above "inference on a previously-trained model" command and specifying the set of rationales to pass in using `--predictions_model_file`.

## Baseline (I-->O) Models
- same as I-->OR model but with addition of `--label_only` flag.

## Injecting Noise at Inference Time
- add `--encoder_noise_variance [integer_value]` to the above command for performing inference on a joint model that has already been trained. A new set of noised predictions will be added in a subdirectory of the pretrained model's directory.
    - for example, to produce noised dev set predictions with a Gaussian variance of 5 from a pretrained CommonsenseQA model: `python input_to_label_and_rationale.py --output_dir ./ --task_name cos_e --pretrained_model_file [path to pretrained model directory] --per_device_eval_batch_size 64 --seed 42 --version_name [specify v1.0 or v1.11] --encoder_noise_variance 5 --dev_predict`
    - or to produce noised dev set predictions with a Gaussian variance of 5 from a pretrained SNLI model: `python input_to_label_and_rationale.py --output_dir ./ --task_name esnli --pretrained_model_file [path to pretrained model directory] --per_device_eval_batch_size 64 --seed 42 --encoder_noise_variance 5 --test_predict`

## Computing Gradients
- To compute L1-normalized gradients, run inference on a trained I-->OR model for a specific (or multiple) dataset splits and specify the following flag: `--save_gradients --gradient_method ["raw", "times_input", "smoothgrad", "smoothgrad_squared", "integrated"] [--smoothgrad_stdev 0.1] [--nsamples 10] --combination_method ["sum", "l1"]`. You will need to do this for both the train and test dataset splits in order to retrain models specifically with token-dropped inputs in the next step.
    - To replicate the "winning" gradient method from the paper, specify `--gradient_method raw --combination_method l1`.
    - The `n_samples` flag is only relevant to integrated gradients and the smoothgrad methods. The `smoothgrad_stdev` flag is only relevant to the smoothgrad methods.
    - Gradients will be saved in the checkpoint sub-directory of the trained model's directory, with a filename such as `[cos_e/esnli]_[train/test/validation]_l1_attributions.txt`.

## Performing the ROAR Test
- To train and test a token-drop baseline, use the `--roar_drop_percent [value between 0 and 1]` flag to specify a proportion of tokens to drop.
    - To drop random tokens, specifying this flag alone is enough.
    - To drop tokens based on their gradient importance rank, use the flag `--gradients_filepath [path to gradients computed in previous step for the training split]`.
    - You can always specify the gradients computed for the training split, and the code will grab the gradients file for the correct split at test-time.
- An example:
    - Train and test a T5 I-->OR model on 30% token-dropped (using gradient ranking) e-SNLI inputs: `python input_to_label_and_rationale.py --output_dir [where_to_save_models] --task_name esnli --do_train --num_train_epochs 200 --per_device_train_batch_size 64 --per_device_eval_batch_size 64 --logging_first_step --logging_steps 1 --save_steps 1 --save_total_limit 11 --seed 42 --early_stopping_threshold 10 --roar_drop_percent 0.3 --gradients_filepath [path_to_regularly_trained_ior_model/checkpoint-X/esnli_train_l1_attributions.txt] --test_predict`. Note that because we have called inference on the test set, the `esnli_test_l1_attributions.txt` file must also exist (in the same location as the train attributions) and the code will use it at inference-time to drop tokens from test instances.
    - Train and test a T5 I-->OR model on 30% token-dropped (using random dropping) e-SNLI inputs: `python input_to_label_and_rationale.py --output_dir [where_to_save_models] --task_name esnli --do_train --num_train_epochs 200 --per_device_train_batch_size 64 --per_device_eval_batch_size 64 --logging_first_step --logging_steps 1 --save_steps 1 --save_total_limit 11 --seed 42 --early_stopping_threshold 10 --roar_drop_percent 0.3 --test_predict`. No gradient attributions must be pre-computed for random token dropping.
