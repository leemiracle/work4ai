# DFM Startup Kit

This folder contains minimum essential configuration required to start developing DFM adapters and DFM applications, as well as test locally federation deployment. 

### Directory Structure

| Directory Item          | Description                                  |
| ----------------------- | -------------------------------------------- |
| `your_package/apps/`    | Location of your DFM application             |
| `your_package/lib/`     | Implementation of your DFM adapters          |
| `your_package/configs/` | Configuration files for your DFM and NVFlare |
| `.dfm-cli.conf.yaml`    | Default DFM CLI configuration                |
| `federation.yaml`       | List of setup federations                    |
| `pyproject.toml`        | Package installation configuration           |
| `README.md`             | Startup documentation                        |

## Introduction

In order to familiarize yourself with DFM, its key concepts and workflow, we recommend first going through [DFM Developer Guide](https://nvidia.github.io/data-federation-mesh/). 

### Development with DFM

There are two types of development that can happen within DFM:

- Building pipelines: designing and implementing user applications (that is, digital twins) that build functional DFM pipelines for execution by the federation. Your pipelines access federation functionality using API operations, which are a public interface that are mapped into corresponding adapters. This development requires you to have access to the site ["startup kit"](https://nvidia.github.io/data-federation-mesh/userguide/about/key_concepts.html) distributed by site administrator. 

- Adapters development: designing and writing scripts and libraries that implement federation functionality. This includes writing modules that stream data from a weather web service, or process data into an internal federation format, or start jobs on a computational site. Adapters are usually developed and tested separately from the DFM applications. They are maintained without disturbing development of your work. You can access adapter functionality using API operations. See more [here](https://nvidia.github.io/data-federation-mesh/userguide/development/adapters.html).

This repository mainly targets the second group: it enables minimum functionality for writing custom adapters and testing them with local federation deployment (that is NVIDIA Flare POC mode).

### Managing Federation

Maintaining your own federation (locally or distributed on a cloud) requires following:

- Side/federation management: creating configuration that enables sites/federation functionality for users. Here, decisions need to be made on how developed adapters should be exposed to users via public operation API and how to set up specific federation sites for that. See details on creating configuration files [here](https://nvidia.github.io/data-federation-mesh/userguide/development/federation_configuration.html). 

- Provisioning: generating executable code (a Python package) for each site and federation out of provided configuration files. Distribution of the packages over sites. Sending packages to users of each site. Provisioning is performed by NVIDIA Flare, however DFM multiple provides [CLI tools](https://nvidia.github.io/data-federation-mesh/userguide/cli/index.html) to facilitate the both provisioning of NVIDIA Flare "startup kit" and generating API code out of configurations files. See also [NVIDIA Flare Provisioning guide](https://nvflare.readthedocs.io/en/2.6.2/real_world_fl/overview.html) for details.

Startup kits created upon provisioning should contain all essential scripts and packages that are required to start development of DFM applications and pipelines. Specifically, it includes packages (per site) located in `your_package/fed/` folder, as well as deployment scripts from `workspace/my_federation/` folder. 

### DFM Configuration

The key part of DFM is federation config - a YAML file with extension `dfm.yaml` that contains description and definitions of all operations and sites available within federation, as well as how to map those operations into their actual implementations, that is adapters. Detailed description of configuration files is provided [here](https://nvidia.github.io/data-federation-mesh/userguide/development/federation_configuration.html).

### Flare Sites Configuration

Running DFM in POC mode or cloud-deployed mode requires configuring NVIDIA Flare. This is done in `configs/project.yaml` file.

- All the sites listed in `configs/federation.dfm.yaml` must also be described in the  participant section of `project.yaml` file (these are workers in NV Flare terminology).
- You must list additional participants called `server` and `admin`.

Refer to [NVIDIA Flare `project.yaml` examples](https://nvflare.readthedocs.io/en/2.6.2/programming_guide/provisioning_system.html#id2).

### Generated Folders and Files

We recommend placing implementation of adapters, that is adapters library, in `your_package/lib/` folder. 

Upon running code generation, DFM produces additional folders and files **solely based on configuration specified in YAML file**. These files are located in `your_package/fed/` folder and corresponding sub-folders:

 - `your_package/fed/api/`: sub-package with the classes corresponding to all public operations defined in `operation` section of config file: class per operation (for example, `concierge_example.fed.api.users.GreetMe` - a corresponding pydantic model).

 - `your_package/fed/sites/`: contains sub-packages for each site with the corresponding pydantic models for operations (as defined in `interface`) available at that site. It inherits what is implemented in `your_package/fed/api/` with the new parameters as given in `interface`. For example, `concierge_example.fed.site.concierge.users.GreetMe` or `concierge_example.fed.site.reception.users.GreetMe`. The name of the file matches the name of the package for operation (for example, `users`), the name of the class matches operation name (e.g `GreetMe`).

 - `your-package/fed/runtime/`: contains sub-packages corresponding to each site that are intended to be run on the site itself. Here public API is mapped into adapter corresponding to `_this_site`. It is an implementation of the operations described in `interface` and their mapping of parameters and functionality into corresponding adapter. It instantiates instances of each adapter (hence can keep their state) and implements methods corresponding to defined operations. Each method calls corresponding adapter body.

**Important:** `your_package/fed/` is an autogenerated folder, all the file namings there are hardcoded and cannot be changed. Also, user is not recommended to change content of any of the generated file, since it will be lost after re-generation.

## Getting Started

### Setting up DFM
1. Install DFM. Follow [Installation instructions]() for details.
2. Configure federation. There are two option to do it:
    - Option 1: using CLI command and specifying federation name and paths to corresponding config files: 
        ```bash
        dfm fed config set my_federation \
            --federation-dir /path/to/fed \
            --config-path configs/federation.dfm.yaml \
            --project-path None
        ``` 
    - Option 2: manually adding information about your federation (federation name and paths to config files) into `federation.yaml` Note, if you rename or change location on `federation.yaml`, you need to adjust `.dfm-cli.conf.yaml` respectively.

    NOTE: if you are using distributed deployment, you need also to provide path to `project.yaml` with Flare configuration.
    
To list all the configured federations run: 
```bash
dfm fed config list-all
```

To show configuration of specific federation run: 
```bash
dfm fed config show my_federation
```

### Creating Adapters and Building DFM Pipeline
Place adapters implementation in `lib/`. 
When adapters are ready, use CLI to generate API and runtime code.

### Generating API and Runtime Code
Adjust `federation.dfm.yaml` to ensure that all operation APIs (representing adapters) are listed there and their interfaces are mapped into the implemented adapters. Consult [this documentation](https://nvidia.github.io/data-federation-mesh/userguide/development/federation_configuration.html) for explanation and examples.

To generate API run: 
```bash
dfm fed gen code my_federation
``` 

Consult [CLI documentation](https://nvidia.github.io/data-federation-mesh/userguide/cli/index.html) for more information, and command parameters and options. 

Generated code will be placed in `your_package/fed`. Use this path to import adapters when build pipeline (see [example](./concierge_example/apps/concierge.py))

After generating code, you may need to run package installation again to update reference to new generated code.

Write your application that creates and submits DFM pipelines using operations API described in `federation.dfm.yaml`.

### Run Pipeline Locally (no Flare): 
```
python your_package/apps/your_app.py --target local [APP_PARAMETERS]
```

### Using Local Flare Deployment (POC mode)

The above instructions allow for running DFM pipeline as one process on a local machine. 
To test locally a cloud deployment of the federation, use NVIDIA Flare POC mode. 
To manage DFM POC mode using CLI, use `dfm poc [COMMAND]` (see [CLI documentation](https://nvidia.github.io/data-federation-mesh/userguide/cli/index.html) for details)

1. Start Flare: 
    ```bash
    dfm poc start --federation my_federation_poc
    ```
    This will create additional directories in `./your_workspace/` (that is `federation-path`)

2. Run pipeline: 
    ```bash
    python your_package/apps/your_app.py --target flare --federation-path ./your_workspace/my_federation_poc/your_package/ [APP_PARAMETERS]
    ```

3. Stop Flare after finishing: 
    ```bash
    dfm poc stop
    ``` 

Alternatively, one can use DFM CLI to submit pipeline:
```bash
dfm fed submit my_federation script your_package/apps/your_run_script.sh
```
(see [CLI documentation](https://nvidia.github.io/data-federation-mesh/userguide/cli/index.html))

