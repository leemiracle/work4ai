# Partition Tree Weighting for Non-Stationary Stochastic Bandits: Source Code

## Overview:

This is an implementation of the Partition Tree Weighting based algorithms introduced in [Partition Tree Weighting for Non-Stationary Stochastic Bandits](http://www.arxiv.org/fix_me), as well as some implementations of other popular algorithms designed for the non-stationary Bernoulli stochastic bandit setting, including [Sliding Window UCB][1] and [MALG][2].


## Installation

The software provided compiles to a stand-alone C++ executable, and can be compiled using CMake to generate a build target for the platform of choice. The software has been compiled on recent versions (circa 2025) of gcc/clang/msvc.


Make sure Git and CMake is installed. Then from the command line run:

```
git clone https://github.com/google-deepmind/active_ptw
cd active_ptw
mkdir build
cd build
cmake ..
make
```

which will produce an executable in the build directory.

## Usage

```
ebcr [Arg1=Value1] [Arg2=Value2]...
```

### Arguments:

- _Arms=N_, _N_ is an integer specifying the number of arms in the bandit problem
- _Mode=[text/plot]_
- _Agent=[ActivePTW/UCB/TS/MALG/KLUCB/SWUCB]_ : choice of bandit algorithm
- _CptSchedule=[Geometric/Nasty]_
- _Trials=N_, _N_ specifies the maximum number of arm pulls
- _EnvSeed=N_, _N_ an integer, which determines the pseudo random behaviour of the environment
- _AgentSeed=N_, _N_ an integer, which determines the pseudo random behaviour of the agent (if applicable)
- _PlotRepeats=N_, when in plot mode, how many repeated runs are performed to estimate performance
- _CptRate=F_, _F_ in _[0,1]_, determines the geometric spacing of changepoint intervals
- _SWUCBWindow=N_, _N_ an integer, determines the size of the window used for sliding window UCB

There are two main modes of operation, text and plot.
Text mode runs a given configuration and outputs a textual summary to stdout.
In plot mode, the output to stdout is Python3 source code which can be executed to produce a figure.
The only Python dependencies are matplotlib and numpy, which can be installed via pip.
For example,

```
ebcr CptSchedule=Geometric CptRate=0 Mode=plot Arms=5 Trials=5000 PlotRepeats=400 > tmp.py
python3 tmp.py
```

will create a graph showing the performance on a stationary bandit problem, with 5 arms and 5000 trials, with 95% confidence intervals obtained from 400 repeats.

Other example usages are given below:

```
ebcr Agent=ActivePTW CptSchedule=Nasty Mode=text Arms=10 Trials=10000

ebcr CptSchedule=Geometric CptRate=0.0002 Mode=plot Arms=5 Trials=1000000 PlotRepeats=400
```


## Citing this work

```latex
@article{veness25,
      title={Partition Tree Weighting for Non-Stationary Stochastic Bandits},
      author={Joel Veness, Marcus Hutter, Andras Gyorgy, Jordi Grau},
      journal={arXiv},
      year={2025},
}
```

[1]: https://arxiv.org/abs/0805.3415
[2]: https://arxiv.org/abs/2102.05406


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
