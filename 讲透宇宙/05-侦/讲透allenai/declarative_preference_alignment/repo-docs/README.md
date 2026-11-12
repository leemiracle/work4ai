# Direct preference alignment

Code for verifying theoretical experiments on direct preference
alignment. Adapted from the [SIMPO repo](https://github.com/princeton-nlp/SimPO). 

# Setting up 

Using [**conda**](https://docs.conda.io/projects/miniconda/en/latest), do
the following: 

```shell

conda create -n simpo python=3.10 
conda activate simpo
pip install -r requirements_simpo.txt
```
See `simpo.Dockerfile` for instructions on how to build a Docker
version, and (*internally*) on how to build and upload a docker image
for internal use at AI2. 

# training preference models 

Here is an example evocation of the preference tuning code involving a
small qwen model (further details of specific models are included in `training_configs`)
```bash 

accelerate launch \
    --config_file accelerate_configs/deepspeed_single.yaml \ ## uses deepspeed
    scripts/run_simpo.py \ ## main script
    training_configs/qwen-05b-simpo.yaml \ ## particular model config 
    --output_dir=_runs/qwen_run \ ## where to put model output
    --learning_rate=1e-6 \
    --beta=1.0 \
    --gamma_beta_ratio=0 \ ## simpo hyper, shuts off reference ratio
    --loss_type=cpo \ ## loss function name, in `scripts/simpo_trainer`
    --run_name=my_run \ ## name of run 
    --num_train_epochs=3 \
    --per_device_train_batch_size=2 \
    --sft_weight=0.01 \ ## cross-entropy regularizer 
    --torch_dtype=bfloat16 
    --model_name_or_path=trl-lib/qwen1.5-0.5b-sft ## Huggingface base model 
```

Inside of the training config (`training_configs/qwen-05b-simpo.yaml`)
you will also see [`yakazimir/ultrafeedback_binarized`](https://huggingface.co/datasets/yakazimir/ultrafeedback_binarized) which is the
preference dataset hosted on huggingface under my public account (it is just
the standard [**binarized ultrafeedback**](https://huggingface.co/datasets/HuggingFaceH4/ultrafeedback_binarized?row=22)
with a custom development set). One can swap this to run on other datasets. 

Other things that can be done with the `run_simpo` script: 

- **generating win/lose log probabilities**: This can be down by evoking
  `--generate_during_eval=True` and `--no_training=True` (*switches
  off training*) in the code
  above (to generate train probabilities, you can add
  `--eval_train=True`). This is used to batch compute reference ratios
  for training. 

- **pushing models to hub**:  By evoking `push_to_hub=True` and
  `hub_model_id=[name]` with the trainer, this will push the model to
  the huggingface hub, which is helpful for later using this model for
  inference.  

# running generation and reward inference

Model generation is done via
  [**VLLM**](https://github.com/vllm-project/vllm). Given issues with
  vllm's compatbility with `requirements_simpo.txt` and the original
  SimPO setup, I create a seperate environment for inference based on
  the dependencies in `requirements_vllm.txt`  (see docker in `vllm.Dockerfile`)

Running generation can be down by doing the following: 
```bash
python scripts/run_inference.py \
    --model [PATH_TO_MODEL] \
    --output_dir [LOC_OF_OUTPUT_DIR] \
    --data_dir [OUTPUT_TO_HF_DATA] \ 
    --split [SPLIT_TO_USE] \
    --add_reward "yes" \ ## added reward model to score output 
    --seed [SEED] ## vllm generation seed, typical to run with multiple seeds
```

See inside of script for additional generation hyper-parameters and
settings. 


# ICML experiments 

See `declarative_preference_alignment/scripts/experiment/`. Citation
below: 

```bibtex
@article{richardson2025understanding,
  title={Understanding the Logic of Direct Preference Alignment through Logic},
  author={Richardson, Kyle and Srikumar, Vivek and Sabharwal, Ashish},
  journal={Proceedings of ICML},
  year={2025}
}
```
