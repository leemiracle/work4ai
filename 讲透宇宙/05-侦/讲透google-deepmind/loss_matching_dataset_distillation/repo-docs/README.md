# Algorithmic Guarantees for Distilling Supervised and Offline RL Datasets

Author: Aaryan Gupta, Rishi Saket, and Aravindan Raghuveer

## Installation

Install the following packages with the versions given below before running the
colabs.

numpy==2.0.2

pandas==2.2.2

scipy==1.15.3

scikit-learn==1.6.1

tensorflow_probability==0.25.0

tensorflow==2.19.0

tf_keras==2.19.0

gymnasium==1.2.2

## Datasets

For the supervised regression case, we use the wine quality, boston housing,
and california housing datasets. Uncomment the get_instance_data() function
to use the boston housing and california housing datasets.

We use the Cartpole, Mountain Car, and Acrobot environments to generate offline
RL data. Uncomment the env_id variable to run experiments for Mountain Car and
Acrobot.

## Usage

For running the supervised learning experiments, run the supervised_lossmatching_datasetdistillation.ipynb colab
and similarly run the offlineRL_lossmatching_datasetdistillation.ipynb colab for the offline RL experiments.

## Citing this work
```
@article{lossmatchingDD,
      title={Algorithmic Guarantees for Distilling Supervised and Offline RL Datasets},
      author={Aaryan Gupta and Rishi Saket and Aravindan Raghuveer},
      year={2025},
}
```

## License and disclaimer

Copyright 2026 Google LLC

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
