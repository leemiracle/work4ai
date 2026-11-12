# Learning Algorithms for Multiple Instance Regression

Author: Aaryan Gupta and Rishi Saket

To Appear in UAI'25.

## Installation

Install numpy, pandas, scipy, scikit-learn, tensorflow, tensorflow-probability
in a conda environment with versions as given in requirements.txt

Activate the conda environment.

```bash

# optional: clear any previous venv hidden files
rm -rf .venv

# use venv
python --version # make sure you have python 3.12
python3 -m venv .venv
source .venv/bin/activate

# install dependencies
pip install -r requirements.txt
```

## Datasets

There are four folders linearreal, linearsynthetic, linearsyntheticerror,
nnsynthetic corresponding to experiments on a real dataset with
linear regression, linear regression on synthetic data, linear regression
on noisy synthetic data, neural regression on synthetic data.

In the linearreal folder, download the wine quality dataset using this link
(https://archive.ics.uci.edu/dataset/186/wine+quality)
as 'redwine.csv' and 'whitewine.csv'.

Run 'syndata.py', 'errordata.py', 'nndata.py' in the corresponding folders
linearsynthetic, linearsyntheticerror, nnsynthetic to generate synthetic data.
You may modify data hyperparameters using the global variables at the top of
each file.

## Usage

In each folder run the python files 'aggmir.py', 'instancemir.py',
'ouralgorithm.py', 'bpmir.py', 'primemir.py' corresponding to Aggregated MIR,
Instance MIR, our proposed algorithm, BP-MIR, and Prime MIR. The output is the
test loss.

## Citing this work

Add citation details here, usually a pastable BibTeX snippet:

```
@article{miralgorithm,
      title={Learning Algorithms for Multiple Instance Regression},
      author={Aaryan Gupta and Rishi Saket},
      year={2025},
}
```

## License and disclaimer

Copyright 2025 Google LLC

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
