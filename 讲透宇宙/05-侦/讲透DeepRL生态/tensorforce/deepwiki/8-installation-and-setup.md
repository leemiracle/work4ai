> 来源: [https://deepwiki.com/tensorforce/tensorforce/8-installation-and-setup](https://deepwiki.com/tensorforce/tensorforce/8-installation-and-setup)
> DeepWiki tensorforce/tensorforce | Last indexed: 24 April 2025 (d384bd

# Installation and Setup

  Relevant source files 
 - [.travis.yml](https://github.com/tensorforce/tensorforce/blob/d384bdc8/.travis.yml)
 - [docs/conf.py](https://github.com/tensorforce/tensorforce/blob/d384bdc8/docs/conf.py)
 - [docs/index.rst](https://github.com/tensorforce/tensorforce/blob/d384bdc8/docs/index.rst)
 - [docs/requirements.txt](https://github.com/tensorforce/tensorforce/blob/d384bdc8/docs/requirements.txt)
 - [requirements-all.txt](https://github.com/tensorforce/tensorforce/blob/d384bdc8/requirements-all.txt)
 - [requirements.txt](https://github.com/tensorforce/tensorforce/blob/d384bdc8/requirements.txt)
 - [setup.py](https://github.com/tensorforce/tensorforce/blob/d384bdc8/setup.py)
 - [tensorforce/__init__.py](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/__init__.py)
 - [test/test_environments.py](https://github.com/tensorforce/tensorforce/blob/d384bdc8/test/test_environments.py)
 
  This page provides detailed instructions for installing Tensorforce and setting up your environment to begin working with the framework. For information on how to use Tensorforce after installation, see [Getting Started](https://deepwiki.com/tensorforce/tensorforce/9-getting-started).

 
## System Requirements

 Before installing Tensorforce, ensure your system meets the following requirements:

 
```

```

 
 - **Python**: Version 3.7 or higher is required
 - **Operating Systems**: Compatible with Linux, macOS, and Windows
 - **Hardware**: No specific hardware requirements, though a GPU is recommended for training larger models
 
 Sources: [setup.py144-151](https://github.com/tensorforce/tensorforce/blob/d384bdc8/setup.py#L144-L151) [requirements.txt1-10](https://github.com/tensorforce/tensorforce/blob/d384bdc8/requirements.txt#L1-L10)

 
## Basic Installation

 Tensorforce can be installed using pip or directly from the source code.

 
### Installing with pip

 The simplest way to install Tensorforce is via pip:

 
```

```

 This installs the basic Tensorforce package with core dependencies.

 
### Installing from source

 For the latest version or development purposes, you can install from the GitHub repository:

 
```

```

 Sources: [setup.py1-171](https://github.com/tensorforce/tensorforce/blob/d384bdc8/setup.py#L1-L171)

 
## Dependencies

 
### Core Dependencies

 Tensorforce relies on the following core dependencies:

 
| Dependency | Version | Purpose |
|---|---|---|
| TensorFlow | 2.12.1 | Core ML framework |
| NumPy | ~1.21.5 | Numerical operations |
| gym | >=0.21.0, <0.23 | Reinforcement learning environments |
| h5py | >=3.6.0 | HDF5 file format support |
| matplotlib | >=3.5.1 | Visualization |
| msgpack & msgpack-numpy | >=1.0.3 & >=0.4.7.1 | Serialization |
| Pillow | >=9.0.0 | Image processing |
| tqdm | >=4.62.3 | Progress bars |

 Sources: [requirements.txt1-10](https://github.com/tensorforce/tensorforce/blob/d384bdc8/requirements.txt#L1-L10)

 
### Optional Dependencies and Feature Sets

 Tensorforce organizes optional dependencies into feature sets that can be installed as needed:

 
```

```

 To install with specific feature sets, use:

 
```

```

 Sources: [setup.py153-168](https://github.com/tensorforce/tensorforce/blob/d384bdc8/setup.py#L153-L168) [requirements-all.txt1-22](https://github.com/tensorforce/tensorforce/blob/d384bdc8/requirements-all.txt#L1-L22)

 
## Environment-Specific Setup

 
### OpenAI Gym

 Gym provides a variety of environments for reinforcement learning:

 
```

```

 This installs Gym with Box2D and classic control environments. Tensorforce supports a wide range of Gym environments as shown in the test files.

 Sources: [setup.py161](https://github.com/tensorforce/tensorforce/blob/d384bdc8/setup.py#L161-L161) [test/test_environments.py41-93](https://github.com/tensorforce/tensorforce/blob/d384bdc8/test/test_environments.py#L41-L93)

 
### Arcade Learning Environment (ALE)

 ALE allows you to use Atari games as environments:

 
```

```

 Sources: [setup.py160](https://github.com/tensorforce/tensorforce/blob/d384bdc8/setup.py#L160-L160) [test/test_environments.py27-31](https://github.com/tensorforce/tensorforce/blob/d384bdc8/test/test_environments.py#L27-L31)

 
### OpenAI Retro

 For classic video game environments:

 
```

```

 Sources: [setup.py162](https://github.com/tensorforce/tensorforce/blob/d384bdc8/setup.py#L162-L162) [test/test_environments.py95-99](https://github.com/tensorforce/tensorforce/blob/d384bdc8/test/test_environments.py#L95-L99)

 
### ViZDoom

 For 3D first-person environments based on Doom:

 
```

```

 Note: ViZDoom may require additional system dependencies based on your platform.

 Sources: [setup.py163](https://github.com/tensorforce/tensorforce/blob/d384bdc8/setup.py#L163-L163) [test/test_environments.py116-121](https://github.com/tensorforce/tensorforce/blob/d384bdc8/test/test_environments.py#L116-L121)

 
### CARLA Simulator

 For autonomous driving simulation:

 
```

```

 This installs PyGame and OpenCV which are needed for CARLA integration.

 Sources: [setup.py164](https://github.com/tensorforce/tensorforce/blob/d384bdc8/setup.py#L164-L164)

 
## Advanced Installation Options

 
### Installing All Features

 To install Tensorforce with all optional features:

 
```

```

 Or:

 
```

```

 Sources: [requirements-all.txt1-22](https://github.com/tensorforce/tensorforce/blob/d384bdc8/requirements-all.txt#L1-L22)

 
### Development Installation

 For development purposes, install additional dependencies:

 
```

```

 Sources: [setup.py165-168](https://github.com/tensorforce/tensorforce/blob/d384bdc8/setup.py#L165-L168) [docs/requirements.txt1-9](https://github.com/tensorforce/tensorforce/blob/d384bdc8/docs/requirements.txt#L1-L9)

 
## System Environment Variables

 Tensorforce uses the following environment variables:

 
| Variable | Purpose | Default |
|---|---|---|
| TF_CPP_MIN_LOG_LEVEL | Controls TensorFlow logging verbosity (3=FATAL only) | 3 |

 Sources: [tensorforce/__init__.py19-20](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/__init__.py#L19-L20)

 
## Verification

 After installation, you can verify that Tensorforce is correctly installed:

 
```

```

 This should display the installed version number (e.g., 0.6.5).

 You can also run a simple example to verify the full installation:

 
```

```

 This creates a random agent for the CartPole environment, runs one episode, and verifies that the core functionality works.

 Sources: [tensorforce/__init__.py22-26](https://github.com/tensorforce/tensorforce/blob/d384bdc8/tensorforce/__init__.py#L22-L26) [setup.py45-50](https://github.com/tensorforce/tensorforce/blob/d384bdc8/setup.py#L45-L50)

 
## Troubleshooting

 
### Common Issues

 
 - **TensorFlow version conflicts**: Ensure you're using TensorFlow 2.12.1 as specified in the requirements
 - **Missing system dependencies**: Some environments (like ViZDoom) may require additional system packages
 - **Import errors**: Verify that all dependencies are correctly installed
 
 
### Platform-Specific Notes

 On Linux, you may need to install additional system packages for certain environments:

 
```

```

 Sources: [.travis.yml10](https://github.com/tensorforce/tensorforce/blob/d384bdc8/.travis.yml#L10-L10)
