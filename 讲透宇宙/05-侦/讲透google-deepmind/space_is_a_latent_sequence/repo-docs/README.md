# space_is_a_latent_sequence

This repository provides the code for the paper, ["Space is a latent sequence:
A theory of the hippocampus."](https://www.science.org/doi/10.1126/sciadv.adm8470)

It includes the implementation of the paper's underlying model, the CSCG,
and example notebooks to reproduce a few results from the paper.

## Installation

Create virtual environment and install packages

```
# git clone repository
git clone https://github.com/google-deepmind/space_is_a_latent_sequence.git
cd space_is_a_latent_sequence

# create virtual environment
python3 -m venv venv
source venv/bin/activate

# install packages
pip install -r requirements.txt
pip install -e .
```
On a GPU or TPU machine, install jax for corresponding hardware.
See https://jax.readthedocs.io/en/latest/installation.html.

Install jupyter notebook to run the experiment notebooks using the following
steps:

```
# With the virtual env activated, install jupyter using:
pip install jupyter

# This package is needed to connect your venv to jupyter:
pip install ipykernel

# Add the venv to jupyter kernels:
python -m ipykernel install --user --name=venv

# Open jupyter notebook
jupyter notebook
```

Select the `venv` kernel when running the notebooks.

## Usage

The core logic for the CSCG model resides in the `cscg` folder.
Utilities for tasks like visualizing the transition graph or plotting place
fields are also included in this folder.

To get started, we recommend exploring the example notebooks in the
`experiment_notebooks` folder. These provide examples of how to train a CSCG
and use it for further analysis, such as computing place fields.

### Downloading the dataset for the Transitive-learning experiment
To download the random walk dataset for the transitive learning experiment, you
will need the gcloud CLI. You can install this by following the [instructions
here](https://cloud.google.com/sdk/docs/install).

To download the dataset, use the following:

```
gcloud storage cp -r gs://space_is_a_latent_sequence /path/to/data
```

## Citing this work

```
@article{raju2024space,
  title={Space is a latent sequence: A theory of the hippocampus},
  author={Raju, Rajkumar Vasudeva and Guntupalli, J Swaroop and Zhou, Guangyao and Wendelken, Carter and L{\'a}zaro-Gredilla, Miguel and George, Dileep},
  journal={Science Advances},
  volume={10},
  number={31},
  pages={eadm8470},
  year={2024},
  publisher={American Association for the Advancement of Science}
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
