# Table of Contents
* [Introduction](#nvidia-ai-workbench-introduction-)
* [Project Description](#project-description)
  * [Sizing Guide](#sizing-guide)
* [Quickstart](#quickstart)
   * [Prerequisites](#prerequisites)
   * [Tutorial (Desktop App)](#tutorial-desktop-app)
   * [Tutorial (CLI-Only)](#tutorial-cli)
* [License](#license)

# NVIDIA AI Workbench: Introduction [![Open In AI Workbench](https://img.shields.io/badge/Open_In-AI_Workbench-76B900)](https://ngc.nvidia.com/open-ai-workbench/aHR0cHM6Ly9naXRodWIuY29tL05WSURJQS93b3JrYmVuY2gtZXhhbXBsZS1rYWdnbGUtYW55d2hlcmU=)

<!-- Banner Image -->
<img src="https://developer-blogs.nvidia.com/wp-content/uploads/2024/07/rag-representation.jpg" width="100%">

<!-- Links -->
<p align="center"> 
  <a href="https://www.nvidia.com/en-us/deep-learning-ai/solutions/data-science/workbench/" style="color: #76B900;">:arrow_down: Download AI Workbench</a> •
  <a href="https://docs.nvidia.com/ai-workbench/" style="color: #76B900;">:book: Read the Docs</a> •
  <a href="https://docs.nvidia.com/ai-workbench/user-guide/latest/quickstart/example-projects.html" style="color: #76B900;">:open_file_folder: Explore Example Projects</a> •
  <a href="https://forums.developer.nvidia.com/t/support-workbench-example-project-competition-kernel/309399" style="color: #76B900;">:rotating_light: Facing Issues? Let Us Know!</a>
</p>

# Project Description
This is an [NVIDIA AI Workbench](https://www.nvidia.com/en-us/deep-learning-ai/solutions/data-science/workbench/) project for bringing your own instance to Kaggle competitions. Users can use the Kaggle API to connect, download datasets from, and submit results to the Kaggle platform, providing a new way to seamlessly work locally on hardware of the user's choice, free from the limitations of cloud-based platforms like Google Colab and the Kaggle Kernel. 

| :warning: Heads Up             |
| :----------------------------- |
| This project is compatible with Kaggle competitions that are reachable for submission via the Kaggle API. This project will **not** submit properly for competition formats that restrict users to the platform for a balanced hardware allowance requirement (like the "code" competition format). More details [here](https://www.kaggle.com/docs/competitions#competition-formats). |

This project builds out a mirrored Kaggle environment and consists of the following notebooks to provide a seamless integration into the Kaggle competition platform:
* ``01-data.ipynb``: This notebook walks the user through downloading competition datasets directly from the Kaggle platform. Simply type the competition name and get started!
* ``02-code.ipynb``: This notebook walks through sample code for solving the end-to-end example competition started in ``01-data.ipynb`` and compiles a submission file.
* ``03-submit.ipynb``: This notebook submits your outputs to the Kaggle competition. See how you stack up on the leaderboard! 

In addition to providing a seamless local experience for working with Kaggle competitions, AI Workbench also provides the following to users:
* Easy version control and tracking of code via Github/Gitlab - say goodbye to manual versioning or CI/CD pipelines.
* Get the advantages of using a local, dedicated IDE: robust debugging, intelligent code completion, and downloadable extensions.
* Automatically set up and customize your local environment in minutes. 
* Plug into and access existing data sources locally without needing to upload them to third parties. 
* No Internet? No problem. Develop while offline!

| :memo: Remember             |
| :---------------------------|
| This project is meant as an example workflow and a starting point; you are free to swap out the example competition, add new datasets and models, rearrange the interface, or edit the source code as you see fit! |

## Sizing Guide

| GPU VRAM | Example Hardware | Compatible? |
| -------- | ------- | ------- |
| N/A | CPU-only | Y |
| <16 GB | RTX 3080, RTX 3500 Ada | Y |
| 16 GB | RTX 4080 16GB, RTX A4000 | Y |
| 24 GB | RTX 3090/4090, RTX A5000/5500, A10/30 | Y |
| 32 GB | RTX 5000 Ada  | Y |
| 40 GB | A100-40GB | Y |
| 48 GB | RTX 6000 Ada, L40/L40S, A40 | Y |
| 80+ GB | A100-80GB | Y |

# Quickstart

## Prerequisites
AI Workbench will prompt you to provide a few pieces of information before running any apps in this project. Ensure you have this information ready. 

   * A Kaggle Username. You can find this in ``kaggle.json`` when you click "Create New Token" [here](https://www.kaggle.com/settings).
   * A Kaggle API Key. You can find this in ``kaggle.json`` when you click "Create New Token" [here](https://www.kaggle.com/settings).

Alternatively, if you prefer working directly with the ``kaggle.json`` credential file, you can delete the above secrets and add your ``kaggle.json`` file directly at the top level of this project repository. However, you may need to run a ``chmod 600 /path/to/kaggle.json`` to prevent other users from reading your file. 

## Tutorial (Desktop App)

If you do not NVIDIA AI Workbench installed, first complete the installation for AI Workbench [here](https://www.nvidia.com/en-us/deep-learning-ai/solutions/data-science/workbench/). 

| :bulb: Tip              |
| :-----------------------|
| Working in the AI Workbench command-line interface (CLI)? Skip to the [next section](#tutorial-cli) for a CLI-only tutorial! |

Let's get started! 

1. Fork this Project to your own GitHub namespace and copy the link

   ```
   https://github.com/[your_namespace]/<project_name>
   ```
   
2. Open the NVIDIA AI Workbench App. Select a location to work in. 
   
3. Clone this Project onto your desired machine by selecting **Clone Project** and providing the GitHub link.
   
4. Wait for the project to build. You can expand the bottom **Building** indicator to view real-time build logs. 
   
5. When the build completes, set the following configurations.

   * `Environment` &rarr; `Secrets` &rarr; `Configure`. Specify the Kaggle Username and Kaggle API Key as project secrets.

6. On the top right of the AI Workbench window, select **Open Jupyterlab**. A frontend user interface should automatically open in a new browser tab.

7. Open ``kaggle/working/01-data.ipynb`` and get started. It's that easy!

    * You may see a ``PermissionError: [Errno 13] Permission denied: '/tmp/kaggle.log'`` message as you are using the Kaggle API. This is expected and does not affect any results. 

## Tutorial (CLI)

<details>
<summary>
<b>Working in the CLI? Expand this for the CLI-only Tutorial!</b>
</summary>

Some users may choose to use the **CLI tool only** instead of the Desktop App. If you do not NVIDIA AI Workbench installed, first complete the installation for AI Workbench [here](https://www.nvidia.com/en-us/deep-learning-ai/solutions/data-science/workbench/). Then, 
1. Fork this Project to your own GitHub namespace and copying the link

   ```
   https://github.com/[your_namespace]/<project_name>
   ```
   
2. Open a shell and activating the Context you want to clone into by

   ```
   $ nvwb list contexts
   
   $ nvwb activate <desired_context>
   ```

   | :bulb: Tip                  |
   | :---------------------------|
   | Use ```nvwb help``` to see a full list of  AI Workbench commands. |
   
3. Clone this Project onto your desired machine by running

   ```
   $ nvwb clone project <your_project_link>
   ```
   
4. Open the Project by

   ```
   $ nvwb list projects
   
   $ nvwb open <project_name>
   ```

5. Start **Open Jupyterlab** by

   ```
   $ nvwb start jupyterlab
   ```

   * Specify the Kaggle Username and Kaggle API Key as project secrets.

6. A frontend user interface should automatically open in a new browser tab. 

7. Open ``kaggle/working/01-data.ipynb`` and get started. It's that easy!

</details>

# License
This NVIDIA AI Workbench example project is under the [Apache 2.0 License](https://github.com/NVIDIA/workbench-example-competition-kernel/blob/main/LICENSE.txt)

This project may utilize additional third-party open source software projects. Review the license terms of these open source projects before use. Third party components used as part of this project are subject to their separate legal notices or terms that accompany the components. You are responsible for confirming compliance with third-party component license terms and requirements. 

| :question: Have Questions?  |
| :---------------------------|
| Please direct any issues, fixes, suggestions, and discussion on this project to the DevZone Members Only Forum thread [here](https://forums.developer.nvidia.com/t/support-workbench-example-project-competition-kernel/309399) |
