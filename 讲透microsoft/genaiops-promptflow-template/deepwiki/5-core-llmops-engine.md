<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/genaiops-promptflow-template · page 5 Core LLMOps Engine · fetched 2026-10-26 -->

# Core LLMOps Engine

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [llmops/common/common.py](llmops/common/common.py)
- [llmops/common/create_connections.py](llmops/common/create_connections.py)
- [llmops/common/deployment/generate_env_vars.py](llmops/common/deployment/generate_env_vars.py)
- [llmops/common/deployment/kubernetes_deployment.py](llmops/common/deployment/kubernetes_deployment.py)
- [llmops/common/deployment/kubernetes_endpoint.py](llmops/common/deployment/kubernetes_endpoint.py)
- [llmops/common/deployment/provision_deployment.py](llmops/common/deployment/provision_deployment.py)
- [llmops/common/deployment/register_model.py](llmops/common/deployment/register_model.py)
- [llmops/common/deployment/test_model_on_aml.py](llmops/common/deployment/test_model_on_aml.py)
- [llmops/common/deployment/test_model_on_kubernetes.py](llmops/common/deployment/test_model_on_kubernetes.py)
- [llmops/common/experiment.py](llmops/common/experiment.py)
- [llmops/common/get_workspace.py](llmops/common/get_workspace.py)
- [llmops/common/prompt_eval.py](llmops/common/prompt_eval.py)
- [llmops/common/prompt_pipeline.py](llmops/common/prompt_pipeline.py)
- [llmops/common/register_data_asset.py](llmops/common/register_data_asset.py)
- [llmops/config.py](llmops/config.py)

</details>



## Purpose and Scope

The Core LLMOps Engine is the foundational execution system that powers experiment runs, model evaluation, and deployment operations across all Prompt Flow use cases in this template. It provides standardized interfaces and orchestration logic for running bulk experiments, evaluating results, managing Azure ML assets, and deploying models to various compute targets.

This document covers the core modules in `llmops/common/` that handle experiment execution and asset management. For information about specific use case implementations, see [Use Cases and Prompt Flows](#3). For deployment target details, see [Deployment](#6). For CI/CD pipeline integration, see [CI/CD Platforms](#4).

## Engine Architecture Overview

The Core LLMOps Engine consists of four primary functional layers that work together to provide complete experiment-to-deployment automation:

```mermaid
graph TB
    subgraph "Experiment Management Layer"
        ExperimentCloudConfig["ExperimentCloudConfig"]
        load_experiment["load_experiment()"]
        resolve_env_vars["resolve_env_vars()"]
        resolve_flow_type["resolve_flow_type()"]
        create_pf_connections["create_pf_connections()"]
    end
    
    subgraph "Execution Engine Layer"
        prompt_pipeline["prompt_pipeline.py<br/>prepare_and_execute()"]
        VariantsSelector["VariantsSelector"]
        prompt_eval["prompt_eval.py<br/>prepare_and_execute()"]
    end
    
    subgraph "Asset Management Layer"
        register_data_asset["register_data_asset.py<br/>register_data_asset()"]
        register_model["register_model.py<br/>register_model()"]
    end
    
    subgraph "Deployment Engine Layer"
        provision_endpoint["provision_endpoint.py"]
        provision_deployment["provision_deployment.py"]
        kubernetes_deployment["kubernetes_deployment.py"]
        test_model_aml["test_model_on_aml.py"]
        test_model_k8s["test_model_on_kubernetes.py"]
    end
    
    subgraph "External Integrations"
        PFClientLocal["PFClient (Local)"]
        PFClientAzure["PFClient (Azure)"]
        MLClient["MLClient"]
        DefaultAzureCredential["DefaultAzureCredential"]
    end
    
    ExperimentCloudConfig --> load_experiment
    load_experiment --> resolve_flow_type
    load_experiment --> resolve_env_vars
    load_experiment --> create_pf_connections
    
    resolve_flow_type --> prompt_pipeline
    resolve_env_vars --> prompt_pipeline
    create_pf_connections --> prompt_pipeline
    VariantsSelector --> prompt_pipeline
    
    prompt_pipeline --> prompt_eval
    prompt_pipeline --> register_data_asset
    prompt_eval --> register_model
    
    register_model --> provision_endpoint
    provision_endpoint --> provision_deployment
    provision_endpoint --> kubernetes_deployment
    provision_deployment --> test_model_aml
    kubernetes_deployment --> test_model_k8s
    
    prompt_pipeline --> PFClientLocal
    prompt_pipeline --> PFClientAzure
    prompt_eval --> PFClientLocal
    prompt_eval --> PFClientAzure
    register_data_asset --> MLClient
    register_model --> MLClient
    provision_deployment --> MLClient
    kubernetes_deployment --> MLClient
    
    MLClient --> DefaultAzureCredential
    PFClientAzure --> DefaultAzureCredential
```

**Sources:** [llmops/common/prompt_pipeline.py:1-584](), [llmops/common/prompt_eval.py:1-521](), [llmops/common/common.py:1-257](), [llmops/common/deployment/provision_deployment.py:1-309](), [llmops/common/deployment/kubernetes_deployment.py:1-316]()

## Execution Context and Client Management

The engine adapts its behavior based on the execution context defined by `EXECUTION_TYPE` configuration, managing different client objects for local versus cloud execution:

```mermaid
graph LR
    subgraph "Configuration"
        EXECUTION_TYPE["EXECUTION_TYPE<br/>(LOCAL/AZURE)"]
    end
    
    subgraph "Local Execution Path"
        PFClientLocal["PFClient()<br/>local promptflow client"]
        create_pf_connections_local["create_pf_connections()<br/>setup local connections"]
        ObjectWrapper_local["ObjectWrapper(pf=pf)"]
    end
    
    subgraph "Azure Execution Path"
        ExperimentCloudConfig_azure["ExperimentCloudConfig<br/>subscription, rg, workspace"]
        DefaultAzureCredential_azure["DefaultAzureCredential()"]
        MLClient_azure["MLClient<br/>Azure ML workspace client"]
        PFClientAzure_azure["PFClient (Azure)<br/>cloud promptflow client"]
        ObjectWrapper_azure["ObjectWrapper(pf=pf, ml_client=ml_client)"]
    end
    
    EXECUTION_TYPE -->|"LOCAL"| PFClientLocal
    EXECUTION_TYPE -->|"AZURE"| ExperimentCloudConfig_azure
    
    PFClientLocal --> create_pf_connections_local
    create_pf_connections_local --> ObjectWrapper_local
    
    ExperimentCloudConfig_azure --> DefaultAzureCredential_azure
    DefaultAzureCredential_azure --> MLClient_azure
    DefaultAzureCredential_azure --> PFClientAzure_azure
    MLClient_azure --> ObjectWrapper_azure
    PFClientAzure_azure --> ObjectWrapper_azure
```

**Sources:** [llmops/config.py:11](), [llmops/common/prompt_pipeline.py:174-202](), [llmops/common/prompt_eval.py:95-119](), [llmops/common/common.py:30-46]()

## Flow Type Resolution and Parameters

The engine automatically detects and configures different types of Prompt Flows through the `resolve_flow_type()` function:

| Flow Type | Detection Criteria | Configuration Handling |
|-----------|-------------------|----------------------|
| `DAG_FLOW` | `flow.dag.yaml` or `flow.dag.yml` present | Uses YAML node variants configuration |
| `FUNCTION_FLOW` | `flow.flex.yaml` with function entry | No additional parameters |
| `CLASS_FLOW` | `flow.flex.yaml` with class entry | Reads `init.json` for class parameters |
| `NO_FLOW` | No flow files found | Used for custom evaluation scripts |

```mermaid
graph TD
    resolve_flow_type["resolve_flow_type(base_path, flow_path)"]
    
    check_files["Check for flow files:<br/>flow.dag.yaml/yml<br/>flow.flex.yaml/yml"]
    
    dag_flow["DAG_FLOW<br/>Traditional prompt flow"]
    function_flow["FUNCTION_FLOW<br/>Python function entry"]
    class_flow["CLASS_FLOW<br/>Python class entry"]
    no_flow["NO_FLOW<br/>Custom evaluation"]
    
    parse_flex["Parse flow.flex.yaml<br/>entry: file:function_or_class"]
    check_entry_type["Check entry type<br/>ast.FunctionDef vs ast.ClassDef"]
    load_init_json["Load init.json<br/>resolve environment variables"]
    
    resolve_flow_type --> check_files
    check_files -->|"dag file found"| dag_flow
    check_files -->|"flex file found"| parse_flex
    check_files -->|"no files found"| no_flow
    
    parse_flex --> check_entry_type
    check_entry_type -->|"ast.FunctionDef"| function_flow
    check_entry_type -->|"ast.ClassDef"| class_flow
    
    class_flow --> load_init_json
```

**Sources:** [llmops/common/common.py:95-206](), [llmops/common/prompt_pipeline.py:169-170](), [llmops/common/prompt_eval.py:89-91]()

## Experiment Execution Engine

The `prompt_pipeline.py` module orchestrates bulk experiment runs with support for flow variants and multiple datasets:

### Variant Selection Strategy

The `VariantsSelector` class manages which flow variants to execute:

```mermaid
graph LR
    subgraph "Variant Selection Options"
        DEFAULTS_ONLY["DEFAULTS_ONLY<br/>Run only default variants"]
        ALL["ALL<br/>Run all available variants"]
        CUSTOM["CUSTOM<br/>Run specific variants"]
    end
    
    subgraph "Input Processing"
        from_args["VariantsSelector.from_args(variants)"]
        parse_variants["Parse variants string:<br/>'*', 'all', 'defaults',<br/>or comma-separated list"]
    end
    
    subgraph "Variant Execution Logic"
        is_variant_enabled["is_variant_enabled(node, variant)<br/>Check if variant should run"]
        variant_combinations["Generate unique variant<br/>combinations across nodes"]
        check_dictionary_contained["check_dictionary_contained()<br/>Avoid duplicate runs"]
    end
    
    from_args --> parse_variants
    parse_variants --> DEFAULTS_ONLY
    parse_variants --> ALL
    parse_variants --> CUSTOM
    
    DEFAULTS_ONLY --> is_variant_enabled
    ALL --> is_variant_enabled
    CUSTOM --> is_variant_enabled
    
    is_variant_enabled --> variant_combinations
    variant_combinations --> check_dictionary_contained
```

**Sources:** [llmops/common/prompt_pipeline.py:87-136](), [llmops/common/prompt_pipeline.py:222-250](), [llmops/common/prompt_pipeline.py:77-84]()

### Experiment Execution Flow

The main execution loop processes datasets and variants systematically:

```mermaid
sequenceDiagram
    participant prepare_and_execute
    participant ExperimentCloudConfig
    participant load_experiment
    participant PFClient
    participant VariantsSelector
    
    prepare_and_execute->>ExperimentCloudConfig: Initialize cloud config
    prepare_and_execute->>load_experiment: Load experiment.yaml
    prepare_and_execute->>PFClient: Create appropriate client
    
    loop For each dataset
        prepare_and_execute->>VariantsSelector: Check if variants enabled
        alt Variants mode
            loop For each variant combination
                prepare_and_execute->>PFClient: pf.run() with variant string
                PFClient-->>prepare_and_execute: Run details and metrics
            end
        else Default mode
            prepare_and_execute->>PFClient: pf.run() without variants
            PFClient-->>prepare_and_execute: Run details and metrics
        end
        prepare_and_execute->>prepare_and_execute: Save results to CSV/HTML
    end
    
    prepare_and_execute->>prepare_and_execute: Write run IDs to output file
```

**Sources:** [llmops/common/prompt_pipeline.py:138-495](), [llmops/common/prompt_pipeline.py:277-324](), [llmops/common/prompt_pipeline.py:371-410]()

## Evaluation Engine

The `prompt_eval.py` module runs evaluation flows against completed bulk runs:

### Evaluation Dataset Mapping

The evaluation system uses dataset references to link evaluation data with standard runs:

```mermaid
graph TD
    subgraph "Standard Run Processing"
        resolve_run_ids["resolve_run_ids(run_id)<br/>Parse run IDs from string or file"]
        get_run_data["runs[run_id].data<br/>Extract dataset reference"]
        find_dataset["experiment.get_dataset(run_data_name)<br/>Find referenced dataset"]
    end
    
    subgraph "Evaluation Dataset Resolution"
        evaluator_datasets["evaluator.datasets<br/>List of evaluation datasets"]
        find_dataset_with_reference["find_dataset_with_reference(dataset_name)<br/>Match evaluation datasets"]
        column_mapping["dataset_mapping.mappings<br/>Column mapping configuration"]
    end
    
    subgraph "Evaluation Execution"
        create_eval_run["pf.run(flow, data, run=standard_run)<br/>Execute evaluation flow"]
        get_eval_results["pf.get_details() + pf.get_metrics()<br/>Extract evaluation results"]
        combine_results["Combine results with variant info<br/>Generate reports"]
    end
    
    resolve_run_ids --> get_run_data
    get_run_data --> find_dataset
    find_dataset --> evaluator_datasets
    evaluator_datasets --> find_dataset_with_reference
    find_dataset_with_reference --> column_mapping
    column_mapping --> create_eval_run
    create_eval_run --> get_eval_results
    get_eval_results --> combine_results
```

**Sources:** [llmops/common/prompt_eval.py:126-198](), [llmops/common/prompt_eval.py:235-270](), [llmops/common/common.py:235-256]()

### Custom Evaluation Support

For evaluators without flow files (`NO_FLOW` type), the engine supports custom Python evaluation functions:

```mermaid
graph LR
    subgraph "Custom Evaluator Detection"
        check_flow_type["flow_type == FlowTypeOption.NO_FLOW"]
        scan_directory["os.listdir(evaluator.path)<br/>Find eval_*.py files"]
        import_module["importlib.import_module()<br/>Dynamic module loading"]
    end
    
    subgraph "Function Discovery"
        get_functions["inspect.isfunction()<br/>Find all functions in module"]
        filter_eval_functions["function_name.startswith('eval_')<br/>Filter evaluation functions"]
        get_service_function["getattr(module, function_name)<br/>Get function reference"]
    end
    
    subgraph "Function Execution"
        call_eval_function["service_function(<br/>run_name, dataset_path,<br/>mappings, report_dir,<br/>cloud_config)"]
        process_result["Process evaluation results<br/>Generate reports"]
    end
    
    check_flow_type --> scan_directory
    scan_directory --> import_module
    import_module --> get_functions
    get_functions --> filter_eval_functions
    filter_eval_functions --> get_service_function
    get_service_function --> call_eval_function
    call_eval_function --> process_result
```

**Sources:** [llmops/common/prompt_eval.py:344-428](), [llmops/common/prompt_eval.py:370-390]()

## Asset Management System

The engine provides comprehensive asset management for datasets and models in Azure ML:

### Data Asset Registration

The `register_data_asset.py` module handles dataset registration with hash-based change detection:

```mermaid
graph TD
    subgraph "Dataset Discovery"
        load_experiment_datasets["experiment.datasets<br/>Standard datasets"]
        load_evaluator_datasets["evaluator.datasets<br/>Evaluation datasets"]
        merge_datasets["all_datasets = {name: dataset}<br/>Combine all unique datasets"]
    end
    
    subgraph "Hash-Based Registration"
        get_local_source["dataset.get_local_source(base_path)<br/>Get local file path"]
        generate_file_hash["generate_file_hash(file_path)<br/>SHA256 hash of file content"]
        check_existing["ml_client.data.get(name, 'latest')<br/>Check existing dataset"]
        compare_hashes["existing.tags['data_hash'] vs new_hash<br/>Compare for changes"]
    end
    
    subgraph "Registration Process"
        create_aml_dataset["AMLData(path, type=URI_FILE,<br/>tags={'data_hash': hash})<br/>Create dataset object"]
        register_dataset["ml_client.data.create_or_update()<br/>Register in Azure ML"]
        log_version["Log dataset name and version<br/>Update confirmation"]
    end
    
    load_experiment_datasets --> merge_datasets
    load_evaluator_datasets --> merge_datasets
    merge_datasets --> get_local_source
    get_local_source --> generate_file_hash
    generate_file_hash --> check_existing
    check_existing --> compare_hashes
    compare_hashes -->|"hash changed or new"| create_aml_dataset
    create_aml_dataset --> register_dataset
    register_dataset --> log_version
```

**Sources:** [llmops/common/register_data_asset.py:49-117](), [llmops/common/register_data_asset.py:33-46](), [llmops/common/register_data_asset.py:80-111]()

### Model Registration

The `register_model.py` module handles flow model registration with similar hash-based tracking:

```mermaid
graph LR
    subgraph "Model Preparation"
        get_flow_detail["experiment.get_flow_detail(flow_type)<br/>Get flow path"]
        hash_folder["hash_folder(model_path)<br/>SHA256 of entire flow directory"]
        create_model_tags["model_tags = {'model_hash': hash,<br/>'build_id': build_id}"]
    end
    
    subgraph "Model Object Creation"
        create_model["Model(name, path, stage='Production',<br/>properties={'azureml.promptflow.source_flow_id'})<br/>Create model entity"]
        set_description["description = f'{experiment_name} model<br/>registered for prompt flow deployment'"]
    end
    
    subgraph "Registration Logic"
        check_existing_model["ml_client.models.get(name, 'latest')<br/>Check existing model"]
        compare_model_hashes["existing.tags['model_hash'] vs new_hash<br/>Compare for changes"]
        register_model["ml_client.models.create_or_update()<br/>Register model"]
        output_version["Write model version to output_file<br/>For downstream processes"]
    end
    
    get_flow_detail --> hash_folder
    hash_folder --> create_model_tags
    create_model_tags --> create_model
    create_model --> set_description
    set_description --> check_existing_model
    check_existing_model --> compare_model_hashes
    compare_model_hashes -->|"hash changed or new"| register_model
    register_model --> output_version
```

**Sources:** [llmops/common/deployment/register_model.py:55-120](), [llmops/common/deployment/register_model.py:36-52](), [llmops/common/deployment/register_model.py:93-114]()

## Deployment Engine Components

The deployment engine supports multiple compute targets through specialized modules:

### Deployment Configuration Processing

All deployment modules read from `deployment_config.json` to determine target-specific settings:

```mermaid
graph TD
    subgraph "Configuration Loading"
        deployment_config["configs/deployment_config.json<br/>Target-specific configurations"]
        parse_config["json.load(config_file)<br/>Parse configuration"]
        filter_env["elem['ENV_NAME'] == env_name<br/>Filter by environment"]
    end
    
    subgraph "Common Configuration Elements"
        endpoint_name["elem['ENDPOINT_NAME']<br/>Target endpoint name"]
        deployment_name["elem['CURRENT_DEPLOYMENT_NAME']<br/>Blue deployment name"]
        vm_size["elem['DEPLOYMENT_VM_SIZE']<br/>Compute instance type"]
        instance_count["elem['DEPLOYMENT_INSTANCE_COUNT']<br/>Scaling configuration"]
        traffic_allocation["elem['CURRENT_DEPLOYMENT_TRAFFIC_ALLOCATION']<br/>Traffic split percentage"]
        environment_variables["elem['ENVIRONMENT_VARIABLES']<br/>Runtime environment"]
    end
    
    subgraph "Environment Variable Resolution"
        resolve_env_vars_config["resolve_env_vars(experiment.base_path)<br/>Load from env.yaml"]
        merge_env_vars["environment_variables.update()<br/>Merge configurations"]
        add_promptflow_vars["Add PROMPTFLOW_RUN_MODE='serving'<br/>PROMPTFLOW_SERVING_ENGINE='fastapi'"]
    end
    
    deployment_config --> parse_config
    parse_config --> filter_env
    filter_env --> endpoint_name
    filter_env --> deployment_name
    filter_env --> vm_size
    filter_env --> instance_count
    filter_env --> traffic_allocation
    filter_env --> environment_variables
    
    environment_variables --> resolve_env_vars_config
    resolve_env_vars_config --> merge_env_vars
    merge_env_vars --> add_promptflow_vars
```

**Sources:** [llmops/common/deployment/provision_deployment.py:133-190](), [llmops/common/deployment/kubernetes_deployment.py:134-192](), [llmops/common/common.py:48-92]()

## Connection Management

The `create_connections.py` module handles Prompt Flow connection setup for local execution:

```mermaid
graph LR
    subgraph "Connection Type Detection"
        CONNECTION_CLASSES["CONNECTION_CLASSES dict<br/>Maps type strings to classes"]
        connection_type["connection_details.connection_type.lower()<br/>Normalize connection type"]
        get_connection_class["CONNECTION_CLASSES[connection_type]<br/>Get appropriate class"]
    end
    
    subgraph "Custom Connection Handling"
        check_custom["connection_type == 'customconnection'<br/>Special handling"]
        process_configs["connection_details.configs.items()<br/>Process config properties"]
        process_secrets["connection_details.secrets.items()<br/>Process secret properties"] 
        resolve_values["_get_valid_connection_values()<br/>Resolve ${} references"]
    end
    
    subgraph "Standard Connection Handling"
        process_properties["connection_details.connection_properties<br/>Extract properties"]
        filter_connection_type["Skip 'connection_type' property<br/>Handle other properties"]
        create_connection["connection_class(**properties)<br/>Instantiate connection"]
    end
    
    subgraph "Connection Registration"
        pf_create_update["pf.connections.create_or_update()<br/>Register with Prompt Flow"]
        handle_errors["Exception handling<br/>Log and re-raise errors"]
    end
    
    CONNECTION_CLASSES --> connection_type
    connection_type --> get_connection_class
    get_connection_class --> check_custom
    
    check_custom -->|"Yes"| process_configs
    process_configs --> process_secrets
    process_secrets --> resolve_values
    
    check_custom -->|"No"| process_properties
    process_properties --> filter_connection_type
    filter_connection_type --> create_connection
    
    resolve_values --> pf_create_update
    create_connection --> pf_create_update
    pf_create_update --> handle_errors
```

**Sources:** [llmops/common/create_connections.py:22-102](), [llmops/common/create_connections.py:105-118](), [llmops/common/create_connections.py:57-95]()

## Configuration and Environment Management

The `ExperimentCloudConfig` class centralizes Azure resource configuration:

| Configuration Source | Priority | Environment Variables |
|---------------------|----------|----------------------|
| Function parameters | Highest | Direct parameter override |
| Environment variables | Medium | `SUBSCRIPTION_ID`, `RESOURCE_GROUP_NAME`, `WORKSPACE_NAME` |
| Default values | Lowest | Fallback when not specified |

The `resolve_env_vars()` function processes environment configuration from `env.yaml` files with variable substitution support using `${VARIABLE_NAME}` syntax.

**Sources:** [llmops/common/experiment_cloud_config.py](), [llmops/common/common.py:48-92]()

---

