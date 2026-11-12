# Correlational Faithfulness Tests

This is the code accompanying the paper "Verbosity
Tradeoffs and the Impact of Scale on the Faithfulness of LLM Self-Explanations
for Commonsense Tasks".

## Installation

This project requires Docker: https://docs.docker.com/desktop/

Running models locally (as opposed to via API) additionally requires installing
the NVIDIA Container Toolkit:
https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html

If installed properly, you should be able to run `docker run --rm --gpus all
nvidia/cuda:12.9.0-base-ubuntu24.04 nvidia-smi`.

## Usage

To simplify deployment and dependency management, experiments are run in a
Docker container. To build the container image:

```
time docker build -t $USER/corr_faith . \
    --build-arg UID=$(id -u) \
    --build-arg GID=$(id -g)
```

The script `evaluate_faithfulness` measures the faithfulness of LLM explanations
on a classification dataset. For each example from the dataset, the LLM is
prompted to produce a class prediction and explanation. Then, the original
example is perturbed by inserting a random adjective or adverb in a
grammatically appropriate place, and the LLM is prompted again to produce a
class prediction and explanation. If the inserted word changes the model's
prediction, a faithful explanation should be more likely to mention that word
than words which didn't change the model's prediction.

After evaluating all examples, the script prints aggregate statistics, and saves
all results for later analysis. `accuracy.parquet` contains a row for each
original dataset example, `intervention.parquet` contains a row for each
intervention run on each example, and `config.parquet` contains the
configuration options for the run.

### Example Commands

The following command runs with local GPU, evaluating 2 interventions on each of
100 examples from e-SNLI, and saving results locally to `/tmp/corr_faith/`:

```
CONTAINER_HOME=/home/nonroot && \
RESULTS_LOCAL=/tmp/corr_faith/ && \
mkdir -p $RESULTS_LOCAL && \
RESULTS_CONTAINER=$CONTAINER_HOME/results/ && \
HF_CACHE_LOCAL=~/.cache/huggingface/hub/ && \
HF_CACHE_CONTAINER=$CONTAINER_HOME/.cache/huggingface/hub/ && \
echo Running docker run... && \
docker run --rm -it \
    --gpus device=all \
    --mount type=bind,source=$RESULTS_LOCAL,destination=$RESULTS_CONTAINER \
    --mount type=bind,source=$HF_CACHE_LOCAL,destination=$HF_CACHE_CONTAINER \
    $USER/corr_faith \
    -m corr_faith.experiments.scripts.evaluate_faithfulness \
    --config.dataset=esnli \
    --config.eval_start_idx=0 \
    --config.eval_end_idx=100 \
    --config.interventions.n_interventions_per_example=2 \
    --config.model_is_instruction_tuned=True \
    --config.model=Qwen/Qwen2.5-3B-Instruct \
    --experiment_id=0 \
    --worker_id=0
```

The following command runs via the Gemini API, evaluating 2 interventions on
each of 100 examples from e-SNLI, and saving results to Google Cloud Storage
`gs://<BUCKET>/corr_faith/`:

```
GCS_BUCKET=<BUCKET> && \
GEMINI_API_KEY=<GEMINI_API_KEY> && \
CONTAINER_HOME=/home/nonroot && \
GCLOUD_CRED_PATH=.config/gcloud/application_default_credentials.json && \
GCLOUD_CRED_LOCAL=~/$GCLOUD_CRED_PATH && \
GCLOUD_CRED_CONTAINER=$CONTAINER_HOME/$GCLOUD_CRED_PATH && \
echo Running docker run... && \
docker run --rm -it \
    --env GEMINI_API_KEY=$GEMINI_API_KEY \
    --env GOOGLE_CLOUD_PROJECT=$GOOGLE_CLOUD_PROJECT \
    --mount readonly,type=bind,source=$GCLOUD_CRED_LOCAL,destination=$GCLOUD_CRED_CONTAINER \
    $USER/corr_faith \
    -m corr_faith.experiments.scripts.evaluate_faithfulness \
    --config.io.save_results_df_path=gs://$GCS_BUCKET/corr_faith/ \
    --config.dataset=esnli \
    --config.eval_start_idx=0 \
    --config.eval_end_idx=100 \
    --config.interventions.n_interventions_per_example=2 \
    --config.model_is_instruction_tuned=True \
    --config.model=gemini_api/gemini-2.0-flash-lite-001 \
    --experiment_id=1 \
    --worker_id=0
```

### Filtering for Natural Interventions

Inserting random adjectives or adverbs often results in highly unusual
sentences, which may be less representative of the true faithfulness of models
for typical tasks. In our paper, we address this by assessing whether sentences
still make sense with another LLM. We use Qwen/Qwen2.5-72B-Instruct for this
task, as a model with a high level of capability for which we can access token
probabilities. (Note that this can be relatively expensive when only evaluating
the faithfulness of a single hyperparameter configuration. When running larger
sweeps, the cost of filtering interventions once is amortized over the size
of the sweep.)

The following command generates 20 interventions on each of 100 examples from
e-SNLI, and saves the top 5% most natural to `/tmp/corr_faith/`:

```
time docker build -t $USER/corr_faith . \
    --build-arg UID=$(id -u) \
    --build-arg GID=$(id -g) && \
CONTAINER_HOME=/home/nonroot && \
RESULTS_LOCAL=/tmp/corr_faith/ && \
mkdir -p $RESULTS_LOCAL && \
RESULTS_CONTAINER=$CONTAINER_HOME/results/ && \
HF_CACHE_LOCAL=~/.cache/huggingface/hub/ && \
HF_CACHE_CONTAINER=$CONTAINER_HOME/.cache/huggingface/hub/ && \
echo Running docker run... && \
docker run --rm -it \
    --gpus device=all \
    --mount type=bind,source=$RESULTS_LOCAL,destination=$RESULTS_CONTAINER \
    --mount type=bind,source=$HF_CACHE_LOCAL,destination=$HF_CACHE_CONTAINER \
    $USER/corr_faith \
    -m corr_faith.experiments.scripts.generate_and_assess_interventions \
    --config.dataset=esnli \
    --config.eval_start_idx=0 \
    --config.eval_end_idx=100 \
    --config.interventions.n_interventions_per_example=20 \
    --config.interventions.keep_top_frac=0.05 \
    --config.model_is_instruction_tuned=True \
    --config.model=Qwen/Qwen2.5-72B-Instruct \
    --experiment_id=2 \
    --worker_id=0
```

After this, the following command assesses faithfulness of a model on the
filtered interventions:

```
time docker build -t $USER/corr_faith . \
    --build-arg UID=$(id -u) \
    --build-arg GID=$(id -g) && \
CONTAINER_HOME=/home/nonroot && \
RESULTS_LOCAL=/tmp/corr_faith/ && \
mkdir -p $RESULTS_LOCAL && \
RESULTS_CONTAINER=$CONTAINER_HOME/results/ && \
HF_CACHE_LOCAL=~/.cache/huggingface/hub/ && \
HF_CACHE_CONTAINER=$CONTAINER_HOME/.cache/huggingface/hub/ && \
echo Running docker run... && \
docker run --rm -it \
    --gpus device=0 \
    --mount type=bind,source=$RESULTS_LOCAL,destination=$RESULTS_CONTAINER \
    --mount type=bind,source=$HF_CACHE_LOCAL,destination=$HF_CACHE_CONTAINER \
    $USER/corr_faith \
    -m corr_faith.experiments.scripts.evaluate_faithfulness \
    --config.dataset=esnli \
    --config.interventions.load_assessed_interventions_from_path="/home/nonroot/results/2/0/" \
    --config.model_is_instruction_tuned=True \
    --config.model=Qwen/Qwen2.5-3B-Instruct \
    --experiment_id=3 \
    --worker_id=0
```

### Running the Full Paper Sweep

`generate_sweeps.py` produces text files containing the full sweeps used to
produce the paper results. Each line provides a docker command to be run. To
generate these commands:

```
RESULTS_LOCAL=/tmp/corr_faith/ && \
mkdir -p $RESULTS_LOCAL && \
CONTAINER_HOME=/home/nonroot && \
RESULTS_CONTAINER=$CONTAINER_HOME/results/ && \
docker run --rm -it \
    --entrypoint=python \
    --mount type=bind,source=$RESULTS_LOCAL,destination=$RESULTS_CONTAINER \
    $USER/corr_faith \
    -m corr_faith.experiments.scripts.generate_sweeps \
    --intervention_experiment_id=4 \
    --faithfulness_experiment_id=5 \
&& \
head -n3 /tmp/corr_faith/faithfulness_sweep.txt
```

The commands in `intervention_sweep.txt` will generate interventions filtered
for naturalness. The commands in `faithfulness_sweep.txt` will use these
interventions to assess the faithfulness of all models we consider.
