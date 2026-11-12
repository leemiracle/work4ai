<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/NVFlare · page 13 Examples and Tutorials · fetched 2026-10-26 -->

# Examples and Tutorials

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/example_applications_algorithms.rst](docs/example_applications_algorithms.rst)
- [docs/examples/federated_statistics_overview.rst](docs/examples/federated_statistics_overview.rst)
- [docs/examples/fl_algorithms.rst](docs/examples/fl_algorithms.rst)
- [docs/examples/hello_world_examples.rst](docs/examples/hello_world_examples.rst)
- [docs/examples/medical_image_analysis.rst](docs/examples/medical_image_analysis.rst)
- [docs/examples/tutorial_notebooks.rst](docs/examples/tutorial_notebooks.rst)
- [docs/programming_guide/controllers/cross_site_model_evaluation.rst](docs/programming_guide/controllers/cross_site_model_evaluation.rst)
- [docs/programming_guide/controllers/cyclic_workflow.rst](docs/programming_guide/controllers/cyclic_workflow.rst)
- [docs/programming_guide/controllers/scatter_and_gather_workflow.rst](docs/programming_guide/controllers/scatter_and_gather_workflow.rst)
- [docs/release_notes/flare_220.rst](docs/release_notes/flare_220.rst)
- [docs/release_notes/flare_240.rst](docs/release_notes/flare_240.rst)
- [docs/release_notes/flare_250.rst](docs/release_notes/flare_250.rst)
- [docs/whats_new.rst](docs/whats_new.rst)
- [examples/README.md](examples/README.md)
- [examples/advanced/README.md](examples/advanced/README.md)
- [examples/advanced/finance/README.md](examples/advanced/finance/README.md)
- [examples/advanced/job_api/tf/README.md](examples/advanced/job_api/tf/README.md)
- [examples/advanced/job_api/tf/run_jobs.sh](examples/advanced/job_api/tf/run_jobs.sh)
- [examples/advanced/monitoring/README.md](examples/advanced/monitoring/README.md)
- [examples/advanced/monitoring/jobs/README.md](examples/advanced/monitoring/jobs/README.md)
- [examples/advanced/sklearn-kmeans/sklearn_kmeans_iris.ipynb](examples/advanced/sklearn-kmeans/sklearn_kmeans_iris.ipynb)
- [examples/advanced/sklearn-linear/sklearn_linear_higgs.ipynb](examples/advanced/sklearn-linear/sklearn_linear_higgs.ipynb)
- [examples/advanced/sklearn-svm/sklearn_svm_cancer.ipynb](examples/advanced/sklearn-svm/sklearn_svm_cancer.ipynb)
- [examples/hello-world/README.md](examples/hello-world/README.md)
- [examples/hello-world/hello-lightning/hello_lightning.ipynb](examples/hello-world/hello-lightning/hello_lightning.ipynb)
- [examples/hello-world/hello-pt/requirements.txt](examples/hello-world/hello-pt/requirements.txt)
- [examples/hello-world/hello_world.ipynb](examples/hello-world/hello_world.ipynb)
- [examples/hello-world/hw_pre_start.sh](examples/hello-world/hw_pre_start.sh)
- [examples/tutorials/README.md](examples/tutorials/README.md)
- [examples/tutorials/flare_api.ipynb](examples/tutorials/flare_api.ipynb)
- [examples/tutorials/flare_simulator.ipynb](examples/tutorials/flare_simulator.ipynb)
- [examples/tutorials/setup_poc.ipynb](examples/tutorials/setup_poc.ipynb)

</details>



## Purpose and Scope

This page provides a comprehensive guide to the examples and tutorials available in NVIDIA FLARE. These resources help users learn federated learning concepts and master the FLARE platform through hands-on practice, ranging from beginner-friendly "Hello World" examples to advanced domain-specific applications and published research implementations. The materials include over 100 notebooks and production-ready example implementations [examples/README.md:1-12]().

For information about the FL Simulator used to run many of these examples, see [Simulator Architecture](#3.5). For details on using the Job CLI to create jobs from templates, see [Job CLI](#7.4). For system deployment modes, see [Deployment Modes](#1.3).

## Learning Path Overview

The NVIDIA FLARE learning resources are organized to support users at different experience levels, from complete beginners to advanced practitioners implementing complex federated learning systems.

**Learning Path Progression**
```mermaid
graph TB
    subgraph "Beginner_Level"
        [HelloWorld] --> [Tutorials]
    end
    
    subgraph "Intermediate_Level"
        [Tutorials] --> [SelfPaced]
        [SelfPaced] --> [AlgoExamples]
    end
    
    subgraph "Advanced_Level"
        [AlgoExamples] --> [DomainApps]
        [AlgoExamples] --> [Privacy]
        [AlgoExamples] --> [Custom]
    end
    
    [DomainApps] --> [Production]
    [Privacy] --> [Production]
    [Custom] --> [Production]

    [HelloWorld]["Hello World Examples<br/>hello-world/"]
    [Tutorials]["Tutorial Notebooks<br/>tutorials/*.ipynb"]
    [SelfPaced]["Self-Paced Training<br/>12 chapters, 100+ notebooks"]
    [AlgoExamples]["FL Algorithms<br/>FedAvg, FedProx, SCAFFOLD"]
    [DomainApps]["Domain Applications<br/>Medical, Finance, NLP"]
    [Privacy]["Privacy & Security<br/>HE, DP, Filters"]
    [Custom]["Custom Workflows<br/>Swarm, Cyclic, Split"]
    [Production]["Production Deployment"]
```

Sources: [examples/README.md:1-12](), [docs/example_applications_algorithms.rst:1-43]()

## Self-Paced Training Course

The self-paced training course provides structured learning with 5 parts, 12 chapters, and over 100 notebooks. Each notebook is self-contained but sequential learning is recommended [examples/tutorials/README.md:22-26](). For details, see [Self-Paced Training Course](#13.2).

**Course Architecture and Content**
```mermaid
graph LR
    [Part1] --> [Part2]
    [Part2] --> [Part3]
    [Part3] --> [Part4]
    [Part4] --> [Part5]
    
    [Part1] -.-> [Content1]
    [Part2] -.-> [Content2]
    [Part3] -.-> [Content3]
    [Part4] -.-> [Content4]
    [Part5] -.-> [Content5]

    [Part1]["Part 1: Introduction<br/>Chapters 1-2"]
    [Part2]["Part 2: System<br/>Chapters 3-4"]
    [Part3]["Part 3: Security<br/>Chapters 5-6"]
    [Part4]["Part 4: Advanced<br/>Chapters 7-10"]
    [Part5]["Part 5: Industry<br/>Chapters 11-12"]
    
    [Content1]["PyTorch, TF, Lightning<br/>Client API, Statistics"]
    [Content2]["Architecture, POC<br/>Admin API, CLI"]
    [Content3]["DP, HE, PSI<br/>Auth, RBAC, Audit"]
    [Content4]["FedProx, Cyclic, Swarm<br/>NeMo, Secure XGBoost"]
    [Content5]["Medical Imaging<br/>Fraud Detection"]
```

### Course Breakdown

| Part | Focus | Key Content |
|:---|:---|:---|
| **Part 1** | Introduction | Running and developing FL applications; PyTorch and Client API [examples/tutorials/README.md:24-25]() |
| **Part 2** | FL System | Platform architecture, setup, and simulation; Admin console and CLI [examples/tutorials/README.md:9-16]() |
| **Part 3** | Security & Privacy | Risks, attacks, and protections (DP, HE, Secure Aggregation) [docs/examples/federated_statistics_overview.rst:84-105]() |
| **Part 4** | Advanced Topics | Algorithms (FedOpt, FedProx), LLMs, and Experiment Tracking [docs/examples/fl_algorithms.rst:14-31]() |
| **Part 5** | Industry | Real-world use cases in Healthcare (MONAI), Life Sciences, and Finance [docs/example_applications_algorithms.rst:69-72]() |

Sources: [docs/example_applications_algorithms.rst:1-105](), [examples/README.md:75-95](), [examples/tutorials/README.md:1-26]()

## Hello World Examples

Entry-level examples demonstrating core FLARE functionality. The **Client API** introduced in v2.4 allows converting existing ML code with minimal changes using `flare.init()`, `flare.receive()`, and `flare.send()` [docs/release_notes/flare_240.rst:8-48](). Modern versions emphasize the **Job Recipe API** for simplified job creation using the `nvflare job` CLI [docs/release_notes/flare_240.rst:58-68]().

**Client API and Recipe Integration**
```mermaid
graph TB
    subgraph "nvflare.client"
        [flare.init]
        [flare.receive]
        [flare.send]
        [FLModel]
    end
    
    subgraph "Recipe_Orchestration"
        [FedAvgRecipe]
        [SimEnv]
        [ProdEnv]
    end
    
    subgraph "Framework_Examples"
        [HelloPT]
        [HelloTF]
        [HelloNP]
    end
    
    [HelloPT] --> [flare.init]
    [HelloPT] --> [FedAvgRecipe]
    [FedAvgRecipe] --> [SimEnv]
    [FedAvgRecipe] --> [ProdEnv]
    [flare.receive] --> [FLModel]
    [FLModel] --> [flare.send]

    [flare.init]["flare.init()"]
    [flare.receive]["flare.receive()"]
    [flare.send]["flare.send()"]
    [FLModel]["FLModel class<br/>nvflare/app_common/abstract/fl_model.py"]
    [FedAvgRecipe]["FedAvgRecipe<br/>nvflare.app_opt.pt.recipes.fedavg.FedAvgRecipe"]
    [SimEnv]["SimEnv environment"]
    [ProdEnv]["ProdEnv environment"]
    [HelloPT]["Hello PyTorch<br/>examples/hello-world/hello-pt"]
    [HelloTF]["Hello TensorFlow<br/>examples/hello-world/hello-tf"]
    [HelloNP]["Hello NumPy<br/>examples/hello-world/hello-numpy"]
```

| Example | Framework | Summary |
|:---|:---|:---|
| Hello NumPy | NumPy | Basic FedAvg with Recipe API [examples/README.md:79-79]() |
| Hello PyTorch | PyTorch | Image classifier with FedAvg [examples/README.md:84-84]() |
| Hello TensorFlow | TensorFlow | Image classifier with FedAvg [examples/README.md:85-85]() |
| Hello Cyclic | PyTorch | `CyclicController` workflow implementation [examples/README.md:82-82]() |
| Hello JAX | JAX | MNIST classifier using FedAvg [examples/README.md:83-83]() |
| Hello Collab | NumPy | Workflow using the Collab API [examples/README.md:80-80]() |
| Hello HuggingFace | Transformers | Qwen SFT/PEFT with `nvflare.client.hf` [examples/hello-world/README.md:181-195]() |
| Hello Flower | Flower | Run Flower applications on FLARE infrastructure [examples/hello-world/README.md:230-243]() |

Sources: [examples/README.md:75-85](), [docs/example_applications_algorithms.rst:9-33](), [docs/release_notes/flare_240.rst:8-98](), [examples/hello-world/README.md:1-250]()

## Tutorial Notebooks

Interactive notebooks demonstrating specific FLARE features, located in `examples/tutorials/`:

| Notebook | File | Focus |
|:---|:---|:---|
| FL Simulator | `flare_simulator.ipynb` | Local simulation for rapid prototyping [examples/tutorials/flare_simulator.ipynb:8-13]() |
| FLARE API | `flare_api.ipynb` | Syntax and usage of `flare_api` [examples/tutorials/flare_api.ipynb:8-16]() |
| POC Mode | `setup_poc.ipynb` | Single machine full FLARE deployment [examples/tutorials/setup_poc.ipynb:8-13]() |
| Job CLI | `nvflare_cli.ipynb` | Commands for recipes, jobs, and provisioning [examples/tutorials/README.md:15-16]() |
| Job Recipe | `job_recipe.ipynb` | High-level API for job creation [examples/tutorials/README.md:17-18]() |
| FLARE Logging | `logging.ipynb` | Configuration for different use cases [examples/tutorials/README.md:19-20]() |

Sources: [examples/README.md:87-95](), [examples/tutorials/README.md:1-21](), [docs/example_applications_algorithms.rst:35-43]()

## Federated Learning Algorithms

Examples demonstrating various FL algorithms. For details, see [Federated Learning Algorithms Examples](#13.3).

| Algorithm | Implementation Detail | Example Location |
|:---|:---|:---|
| **FedAvg** | `ScatterAndGather` workflow [docs/programming_guide/controllers/scatter_and_gather_workflow.rst:8-12]() | `examples/hello-world/hello-numpy` |
| **FedProx** | `PTFedProxLoss` penalty term [docs/examples/fl_algorithms.rst:14-18]() | `examples/advanced/cifar10` |
| **FedOpt** | `PTFedOptModelShareableGenerator` [docs/examples/fl_algorithms.rst:20-24]() | `examples/advanced/cifar10` |
| **SCAFFOLD** | `CIFAR10ScaffoldLearner` drift correction [docs/examples/fl_algorithms.rst:26-30]() | `examples/advanced/cifar10` |
| **Swarm Learning** | Client-side controlled evaluation [docs/example_applications_algorithms.rst:25-25]() | `examples/advanced/swarm_learning` |
| **Cyclic Weight** | `CyclicController` workflow [docs/programming_guide/controllers/cyclic_workflow.rst:1-10]() | `examples/hello-world/hello-cyclic` |

Sources: [docs/examples/fl_algorithms.rst:1-57](), [docs/example_applications_algorithms.rst:45-53]()

## Traditional ML and Domain Examples

NVIDIA FLARE supports traditional ML libraries like Scikit-learn and XGBoost, alongside medical imaging and LLM applications.

| Category | Framework/Task | Summary |
|:---|:---|:---|
| Scikit-learn | Linear, K-Means, SVM | Federated versions of popular algorithms [docs/example_applications_algorithms.rst:63-66]() |
| XGBoost | Horizontal/Vertical | Histogram-based, bagging, and cyclic approaches [docs/examples/fl_algorithms.rst:32-50]() |
| Medical Imaging | MONAI | 3D medical image analysis using FedAvg [docs/example_applications_algorithms.rst:71-72]() |
| Statistics | Tabular/Image | Federated histograms and summary stats [docs/examples/federated_statistics_overview.rst:31-83]() |
| LLMs | MedGemma, Qwen | QLoRA fine-tuning and multimodal support [examples/advanced/README.md:41-42]() |

Sources: [docs/example_applications_algorithms.rst:60-72](), [docs/examples/fl_algorithms.rst:32-57](), [examples/advanced/README.md:1-89]()

## Federated Statistics

NVIDIA FLARE provides built-in operators to generate global statistics (count, sum, mean, std_dev, histogram) based on local client statistics [docs/examples/federated_statistics_overview.rst:8-13](). For details, see [Federated Statistics](#13.7).

**Statistics Workflow and Code Entities**
```mermaid
graph TB
    [Controller] --> [StatisticsSpec]
    [DFStatsCore] -- "implements" --> [StatisticsSpec]
    [ImageStats] -- "implements" --> [StatisticsSpec]
    [Controller] --> [PrivacyFilters]

    [Controller]["StatisticsController<br/>nvflare.app_common.workflows.statistics_controller"]
    [DFStatsCore]["DFStatisticsCore<br/>nvflare.app_opt.pandas.pandas_stats_executor"]
    [ImageStats]["ImageStatistics<br/>examples/advanced/federated-statistics/image_stats/client.py"]
    [StatisticsSpec]["Statistics(ABC)<br/>nvflare.app_common.abstract.statistic_spec.Statistics"]
    [PrivacyFilters]["task_result_filters<br/>Data protection"]
```

Sources: [docs/example_applications_algorithms.rst:74-87](), [docs/examples/federated_statistics_overview.rst:1-124]()

## Privacy and Security Examples

NVIDIA FLARE includes implementations for Private Set Intersection (PSI), Differential Privacy (DP), and Homomorphic Encryption (HE).

| Feature | Description | Example Location |
|:---|:---|:---|
| **HE** | Encrypted weights transfer via filters [docs/examples/fl_algorithms.rst:48-48]() | `examples/advanced/cifar10` |
| **PSI** | Vertical FL set matching [docs/examples/fl_algorithms.rst:49-49]() | `examples/advanced/vertical_xgboost` |
| **Privacy Filters** | Site-specific `privacy.json` policies [docs/examples/federated_statistics_overview.rst:89-104]() | `examples/advanced/federated-statistics` |
| **Auth/Audit** | Site policies and secure logging [docs/release_notes/flare_220.rst:95-116]() | `examples/advanced/federated-policies` |
| **Secure XGBoost** | HE-protected gradients for XGBoost [docs/release_notes/flare_250.rst:53-64]() | `examples/advanced/xgboost_secure` |

Sources: [docs/examples/fl_algorithms.rst:55-59](), [docs/examples/federated_statistics_overview.rst:84-124](), [docs/release_notes/flare_220.rst:95-117](), [docs/release_notes/flare_250.rst:53-64]()

## Environment Setup

Setting up a clean Python environment is recommended before running examples [examples/README.md:19-21]().

```bash
# Setup virtual environment
python3 -m pip install --user virtualenv
source ./set_env.sh

# Install NVFLARE
pip install nvflare

# Install example dependencies (run in specific example folder)
pip install -r requirements.txt

# Setup JupyterLab
pip install jupyterlab
python3 -m ipykernel install --user --name="nvflare_example"
jupyter lab .
```

Sources: [examples/README.md:19-73]()

---

