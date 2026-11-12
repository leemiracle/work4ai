# GPU-enabled Accelerated Single Cell Analysis Resources

## What is NVIDIA Clara™ for Genomics? 
NVIDIA Clara**™** for Genomics is a suite of GPU-enabled software tools that are designed to provide unprecedented speed and accuracy in precision genomics.

This repository focuses on specific tools that will be valuable for analyzing data related to single cell. It provides resources and education on them, as well as a way to get started and 

[RAPIDS-singlecell](https://rapids-singlecell.readthedocs.io/), developed with [scverse](https://scverse.org/), provides GPU-accelerated single cell analysis with an AnnData-first API. It can be installed through [PyPi](https://pypi.org/project/rapids-singlecell/), [docker](https://rapids-singlecell.readthedocs.io/en/latest/Installation.html#docker), or available through 1-click deployment as an [NVIDIA AI Blueprint](https://build.nvidia.com/nvidia/single-cell-analysis).

For those interested in additional healthcare life science tools related to single cell at NVIDIA, check out the below

| Tool Name | Description |
| :---- | :---- |
| [Parabricks](https://www.nvidia.com/en-us/clara/genomics/) | NVIDIA® Parabricks® is a scalable genomics software suite for secondary analysis that provides GPU-accelerated versions of trusted, open-source tools. Parabricks offers STAR for RNA support, including STARsolo mode. |
| [BioNeMo](https://www.nvidia.com/en-us/clara/biopharma/) | Accelerate drug discovery with NVIDIA BioNeMo™ for biopharma, a collection of frameworks, applications, generative AI solutions, and pretrained models. BioNeMo Framework includes the single-cell data loader for foundational model training (bionemo-scdl), [available via pip install](https://pypi.org/project/bionemo-scdl/). |
| [MONAI](https://docs.nvidia.com/monai/index.html) | MONAI is a freely available, community-supported, PyTorch-based framework for deep learning in healthcare imaging. It provides domain-optimized foundational capabilities for developing healthcare imaging training workflows in a native PyTorch paradigm. Monai includes [VISTA2D](https://catalog.ngc.nvidia.com/orgs/nvidia/teams/monaitoolkit/models/monai_vista2d), a cell segmentation training and inference pipeline for cell imaging. |
| [cuCIM](https://github.com/rapidsai/cucim)  | Open-source, accelerated computer vision and image processing software library for multidimensional images used in biomedical, geospatial, material and life science, and remote sensing use cases. |

Additional NVIDIA libraries related to accelerated data science, data loading, or file I/O that could be utilized for single cell data.
| Tool Name | Description |
| :---- | :---- |
| [cuDF](https://github.com/rapidsai/cudf) (RAPIDS) | cuDF is a GPU DataFrame library for loading, joining, aggregating, filtering, and otherwise manipulating data. |
| [cuML](https://github.com/rapidsai/cuml) (RAPIDS) | cuML is a suite of libraries that implement machine learning algorithms and mathematical primitives functions that share compatible APIs with other RAPIDS projects. |
| [cuVS](https://github.com/rapidsai/cuvs) (RAPIDS) | cuVS is a new library mostly derived from the approximate nearest neighbors and clustering algorithms in the RAPIDS RAFT library of machine learning and data mining primitives. |
| [cuGraph](https://github.com/rapidsai/cugraph) (RAPIDS) | cuGraph is a repo that represents a collection of packages focused on GPU-accelerated graph analytics including support for property graphs and remote (graph as a service) operations. |
| [cuSpatial](https://github.com/rapidsai/cuspatial) (RAPIDS) | cuSpatial accelerates vector geospatial operations through GPU parallelization. |
| [IndeX](https://developer.nvidia.com/index) | NVIDIA IndeX® is a 3D volumetric interactive visualization SDK that allows scientists and researchers to visualize and interact with massive datasets, make real-time modifications, and navigate to the most pertinent parts of the data, all in real time |
| [DALI](https://github.com/NVIDIA/DALI) | The NVIDIA Data Loading Library (DALI) is a GPU-accelerated library for data loading and pre-processing to accelerate deep learning applications. It provides a collection of highly optimized building blocks for loading and processing image, video and audio data. It can be used as a portable drop-in replacement for built in data loaders and data iterators in popular deep learning frameworks. |

Additional Community Resources related to Single Cell

| Tool Name | Description |
| :---- | :---- |
| [Scverse](https://scverse.org/) | Foundational tools for single-cell omics data analysis.  |
| [segger](https://elihei2.github.io/segger_dev/) | segger is a cutting-edge tool for cell segmentation in single-molecule spatial omics datasets. By leveraging graph neural networks (GNNs) and heterogeneous graphs, segger offers unmatched accuracy and scalability. |
| [cz-benchmarks](https://virtualcellmodels.cziscience.com/benchmarks#:~:text=cz-benchmarks%20is%20a%20standardized,to%20expand%20to%20additional%20domains\).) | cz-benchmarks is a standardized evaluation and comparison of machine learning models for biological applications first in the single-cell transcriptomics domain |

 ## Getting Started with RAPIDS-singlecell and NVIDIA RAPIDS

This section will walk users through using Brev.dev, a platform which will provide optimized compute and software environments. 

Please Note: **Brev instances need to be manually shut down when not in use, or you will be charged**

### Creating a Brev.dev account 

The following steps will guide you through setting up your brev.dev account, creating a team, and redeeming credits.

* Create a brev.dev account  
  * The first member of your team should sign up for an account on [brev.nvidia.com](http://brev.nvidia.com/).  
* Create a new organization to share resources with your team  
  * On the brev.dev homepage, click on your profile icon in the top-right corner.  
  * Go to Your Profile.  
  * Click the \+ Create a new organization button.  
  * Give your organization a name (e.g., "Team Omics").  
* Redeeming credits  
  * Note: If you are in a sponsored event, you will receive coupon codes to run on brev.dev. Be mindful of how you manage credits to prevent exhaustion \- close instances, keep it to a closed group.   
  * Go to Billing  
    * Within your newly created organization, navigate to the Billing tab.  
  * Redeem the Code  
    * Under the "Pay For Compute" section, find the "Redeem Code" button.  
  * Enter the Coupon Code  
    * Enter the provided hackathon coupon code.  
  * Click Redeem  
    * Click the Redeem button to apply the credits to your organization.  
* Inviting Team Members  
  * Go to the Team Tab  
    * Navigate to the Team tab within your organization.  
  * Generate Invite Link  
    * Click on the Generate Invite Link button.  
  * Share the Link  
    * Copy the generated invite link and share it with the other members of your team. This link will allow them to join your organization and share the allocated compute credits.

### Setting up the compute environment

#### One-click setup 

For users who want to get started right away, the compute environment can be set up with one click using the [NVIDIA Single Cell Analysis Blueprint](https://build.nvidia.com/nvidia/single-cell-analysis)

#### Advanced setup

For users who want more control over the configuration, try this more hands-on setup. 

Go to [brev homepage](https://brev.nvidia.com/environment/new) 

1. Configure hardware  
   1. Select “Create New Instance”   
   2. Choose L40S GPUs running on the Crusoe platform   
2. Configure the instance  
1. Select “Configure” \> “Docker Compose”   
2. Provide the GitHub link to the [YAML](https://github.com/clara-parabricks-workflows/omics-hackathon/blob/main/rsc-2508-pytorch2.yml) (or upload your own)   
   1. This YAML file pulls the [RAPIDS notebook container](https://catalog.ngc.nvidia.com/orgs/nvidia/teams/rapidsai/containers/notebooks), installs additional packages for single-cell analysis, and exposes ports for JupyterLab.   
3. Select “Validate” to ensure the YAML is parsed correctly   
4. Select “Continue”  
5. Name the instance   
6. Select “Deploy”. In a few moments, the instance will be ready   
7. Launch the instance 

More detailed instructions can be found in this [README.md](https://github.com/NVIDIA-AI-Blueprints/single-cell-analysis-blueprint/blob/main/docs/creating_custom_brev.md). 

## How to Get Help

Many of the tools listed above have a developer community around them, which is a great place to start looking at previously answered questions and to ask new questions. 

* The RAPIDS-GoAi workspace on [Slack](https://rapids-goai.slack.com/join/shared_invite/zt-trnsul8g-Sblci8dk6dIoEeGpoFcFOQ#/shared-invite/email) is a great place to see what questions have already been asked and answered, and to get help from others in the RAPIDS developer community.   
* The scverse hosts a user forum on [Zulip](https://scverse.zulipchat.com/) and is a great starting point for troubleshooting.   
* NVIDIA hosts user forums for [Parabricks](https://forums.developer.nvidia.com/c/healthcare/parabricks/290), [BioNeMo](https://forums.developer.nvidia.com/c/healthcare/bionemo/643), and [MONAI](https://forums.developer.nvidia.com/c/healthcare/monai/647). 

## Learn More

[Single Cell Blog](https://developer.nvidia.com/blog/driving-toward-billion-cell-analysis-and-biological-breakthroughs-with-rapids-singlecell/)  
[Blueprint](https://build.nvidia.com/nvidia/single-cell-analysis)  
[Launchable](https://brev.nvidia.com/launchable/deploy?launchableID=env-2xn8JayrpXlBwGXkKASSomq6gXi)  
[DLI](https://learn.nvidia.com/courses/course-detail?course_id=course-v1:DLI+S-HX-05+V1)
