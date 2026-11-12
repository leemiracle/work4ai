# hybrid_rnns_reward_learning

This code fits "hybrid RNNs" to behavioral datasets. Behavioral datasets will
usually be bandit tasks performed by humans.

## Interactive Usage

The Colab train_models.ipynb provides a simple example of running this code
interactively.

## Installation

To install the code and requirements, please run the following command:
```bash
git clone https://github.com/deepmind/hybrid_rnns_reward_learning.git
python3 -m venv hybrnn_venv
source hybrnn_venv/bin/activate
pip install --upgrade pip
pip install -r ./requirements.txt
```

### Demo

The Colab train_models.ipynb provides a demo for training a model on a given
dataset. In short:
config = rnn_config.get_config()
fit_hyb_rnn.train(config)

### Instructions for Use

Please follow the following steps:
1. Adapt the config. The config file will specify the training procedure. You
can set the number of training steps, batch size, and size of the hidden layer
in the model. You can also set the parameters of the cognitive models,
including basic parameters such as learning rate, forgetting, decision
temperature, etc.; and also the parameters specific to the hybrid models, such
as the type of recurrence (e.g., context versus memory).
2. Point the code to the right data directory. If you use our provided
example dataset, use the following link:
'/path/to/dataset/openSourceHumDataset.csv'
If you use our provided full-size dataset, use this link:
'/path/to/dataset/openSourceHumDataset.csv'
3. Run the training loop. This will print a simple training update every few
hundred steps to check the training is progressing. In 2024 and using standard
assignment of resources on a Google Colab, training a single instance of the
full model on the full dataset until convergence will typically require a few
hours. Training a smaller model on a smaller dataset and/or for fewer timesteps
will require a few minutes.

## Citing this work

If you use this code, please cite the following paper:

```latex
@article{eckstein_summerfield_daw_miller_2024,
 title={Hybrid Neural-Cognitive Models Reveal How Memory Shapes Human Reward Learning},
 url={osf.io/preprints/psyarxiv/u9ks4},
 DOI={10.31234/osf.io/u9ks4},
 publisher={PsyArXiv},
 author={Eckstein, Maria and Summerfield, Christopher and Daw, Nathaniel and Miller, Kevin J},
 year={2024},
 month={Jul}
}
```

## License and disclaimer

Copyright 2024 DeepMind Technologies Limited

All software is licensed under the Apache License, Version 2.0 (Apache 2.0);
you may not use this file except in compliance with the Apache 2.0 license.
You may obtain a copy of the Apache 2.0 license at:
https://www.apache.org/licenses/LICENSE-2.0

All other materials are licensed under the Creative Commons Attribution 4.0
International License (CC-BY). You may obtain a copy of the CC-BY license at:
https://creativecommons.org/licenses/by/4.0/legalcode

Unless required by applicable law or agreed to in writing, all software and
materials distributed here under the Apache 2.0 or CC-BY licenses are
distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
either express or implied. See the licenses for the specific language governing
permissions and limitations under those licenses.

This is not an official Google product.
