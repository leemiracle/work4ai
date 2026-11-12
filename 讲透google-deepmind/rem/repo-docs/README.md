
# Redirection for Erasing Memory (REM): Towards a universal unlearning method for corrupted data [ICLR 2026]
*[Stefan Schoepf](https://if-loops.github.io/) (2)°, [Michael Curtis Mozer](https://home.cs.colorado.edu/~mozer/index.php) (1), [Nicole Elyse Mitchell](https://nicolemitchell.github.io/) (3), [Alexandra Brintrup](https://www.ifm.eng.cam.ac.uk/people/ab702/) (2), [Georgios Kaissis](https://www.g-k.ai/) (1), [Peter Kairouz](https://kairouzp.github.io/) (3), [Eleni Triantafillou](https://elenitriantafillou.github.io/) (1)*
°Work done during the author’s internship at (1) Google DeepMind; (2) University of Cambridge; (3) Google Research
> Machine unlearning is studied for a multitude of tasks, but specialization of
> unlearning methods to particular tasks has made their systematic comparison
> challenging. To address this issue, we propose a conceptual space to
> characterize diverse corrupted data unlearning tasks in vision classifiers.
> This space is described by two dimensions, the discovery rate (the fraction of
> the corrupted data that are known at unlearning time) and the statistical
> regularity of the corrupted data (from random exemplars to shared concepts).
> Methods proposed previously have been targeted at portions of this space and,
> we show, fail predictably outside these regions. We propose a novel method,
> Redirection for Erasing Memory (REM), whose key feature is that corrupted data
> are redirected to dedicated neurons introduced at unlearning time and then
> discarded or deactivated to suppress the influence of corrupted data. REM
> performs strongly across the space of tasks, in contrast to prior SOTA methods
> that fail outside the regions for which they were designed.
## Usage
You can run the paper experiments with Experiments_run.sh and set the models,
ETD variants, corruptions sizes, etc. in this file.
To achieve additional modifications that deviate from the paper benchmarks,
use the CONFIG.py and opts.py files.
New methods should be added in src/methods.py (method code),
src/opts.py (as selectable method), and in src/main.py (passing data loaders).
Conda dependencies for virtual environment setup are provided in myenv.yml.
Running the default experiments set in experiments.sh on a single A100 (40GB)
takes roughly one working week.
```
conda env create --file=myenv.yaml # create virtual environment
```
```
python ./experiments_run.sh
```
The plots are automatically generated at the end of experiments_run.sh
as well as LateX formatted tables.
If desired, plotting.py and tables.py can be called manually.
## Prior work and code
The code in this repo builds upon the repo of [Goel et al. ("Corrective Unlearning")](https://github.com/drimpossible/corrective-unlearning-bench)(GNU GENERAL PUBLIC LICENSE) with modifications only made where necessary to enable additional functionality (e.g., adding ETD training and additional methods such as REM and Gradient Ascent) or to improve user experience (e.g., Experiments_run.sh which allows quick adjustment of experiments instead of the original hardcoded experiment list).
Additional method implementations are taken from the respective original author repositories where available (e.g., [ETD](https://github.com/pratyushmaini/localizing-memorization), [Potion](https://github.com/if-loops/towards_poison_unlearning), ...)
## Citing this work

ICLR 2026: [OpenReview](https://openreview.net/forum?id=xG0mQ4Xsfm)
```
@inproceedings{
schoepf2026redirection,
title={Redirection for Erasing Memory ({REM}): Towards a universal unlearning method for corrupted data},
author={Stefan Schoepf and Michael Curtis Mozer and Nicole Elyse Mitchell and Alexandra Brintrup and Georgios Kaissis and Peter Kairouz and Eleni Triantafillou}},
booktitle={The Fourteenth International Conference on Learning Representations},
year={2026},
url={https://openreview.net/forum?id=xG0mQ4Xsfm}
}
```

Preprint: [ArXiv](https://arxiv.org/abs/2505.17730)
```
@misc{schoepf2025remunlearning,
      title={Redirection for Erasing Memory (REM): Towards a universal unlearning method for corrupted data},
      author={Stefan Schoepf and Michael Curtis Mozer and Nicole Elyse Mitchell and Alexandra Brintrup and Georgios Kaissis and Peter Kairouz and Eleni Triantafillou},
      year={2025},
      eprint={2505.17730},
      archivePrefix={arXiv},
      primaryClass={cs.LG},
      url={https://arxiv.org/abs/2505.17730}}
```

## License and disclaimer
Copyright 2025 Google LLC
All software is distributed under the terms of the GNU GENERAL PUBLIC LICENSE,
version 3.
All other materials are licensed under the Creative Commons Attribution 4.0
International License (CC-BY). You may obtain a copy of the CC-BY license at:
https://creativecommons.org/licenses/by/4.0/legalcode
Unless required by applicable law or agreed to in writing, all software and
materials distributed here under the GNU GENERAL PUBLIC LICENSE or CC-BY
licenses are distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS
OF ANY KIND, either express or implied. See the licenses for the specific
language governing permissions and limitations under those licenses.
This is not an official Google product.
