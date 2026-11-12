# OlmPool
This repository contains additional code and data for the paper "Cracks in the Foundation: Seemingly Minor Architectural Choices Impact Long Context Extension".

## Accessing models
All OlmPool models were pretrained and context extended with [OLMo-core](https://github.com/allenai/OLMo-core). The original checkpoints are available in OLMo-core format [on Google cloud](https://console.cloud.google.com/storage/browser/olmpool_public). For convenience, we also convert checkpoints to Hugging Face format; you can access those checkpoints from the [allenai/olmpool collection](https://huggingface.co/collections/allenai/olmpool). 

Note that these models are *early in pretraining* with little-to-no instruction-format data, and thus are very poor at most tasks. The final checkpoint for each model is a 7-8B model that has been trained to 150B tokens (140B in pretraining and 10B in context extension).  

## Training configurations
The training configuration for each model's pretraining run is available in `src/configs`. Names here are identical to the names on the Hugging Face Hub for each model. 

To retrain any of these models (or to load these models in OLMo-core), firrst replace the `config.py` in OLMo-core with the provided `configs/config.py` to add the new model classes. 

## Analysis scripts
Scripts to replicate the analysis by running generation through OLMo-core will be released shortly. All evaluations were run through OLMo-core; for exact replications of evals, run generation with the OLMo-core checkpoints. 

## Questions? Want additional information about the models in OlmPool?
We're happy to chat! Please open an issue. 

## Citation
```
@misc{bertsch2026cracks, 
    title={Cracks in the Foundation: Seemingly Minor Architectural Choices Impact Long Context Extension}, 
    author={Amanda Bertsch and Luca Soldaini and Matthew R. Gormley and Graham Neubig and Hanna Hajishirzi and Kyle Lo and Dirk Groeneveld}, 
    year={2026}, 
}
```

 

