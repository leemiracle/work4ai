<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/SciRIFF · page 6 Configuration System · fetched 2026-10-26 -->

# Configuration System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [sciriff/eval/eleuther_templates/llama2/_default_template.yaml](sciriff/eval/eleuther_templates/llama2/_default_template.yaml)
- [sciriff/eval/eleuther_templates/llama2/utils.py](sciriff/eval/eleuther_templates/llama2/utils.py)

</details>



The Configuration System provides the foundational framework for configuring and managing evaluation tasks across different model architectures within SciRIFF. This system is built around YAML-based evaluation templates that define how models interact with tasks, along with utility functions for dataset filtering and task management. The system enables consistent evaluation across different model families (Llama2, Llama3, etc.) while maintaining task-specific customizations.

For detailed information about the YAML template structure and model-specific configurations, see [Evaluation Templates](#6.1). For utility functions that support dataset processing within templates, see [Template Utilities](#6.2).

## System Architecture

The Configuration System operates as a bridge between the evaluation framework and the underlying Eleuther AI evaluation harness. It translates SciRIFF's scientific tasks into standardized evaluation configurations that can be executed consistently across different models.

### Configuration Flow Diagram

```mermaid
flowchart TD
    subgraph "Template Structure"
        BaseTemplate["_default_template.yaml"]
        ModelDirs["Model Directories<br/>/llama2/<br/>/llama3/"]
        TaskConfigs["Task-specific Configs"]
    end
    
    subgraph "Template Processing"
        EleutherHarness["Eleuther Harness"]
        YAMLParser["YAML Parser"]
        DocFormatter["Document Formatter"]
    end
    
    subgraph "Utility Functions"
        FilterTask["filter_task()"]
        TaskList["eval_tasks[]"]
        DynamicFilters["Generated Filters<br/>filter_bioasq_list_qa()<br/>filter_qasper_abstractive_qa()"]
    end
    
    subgraph "Dataset Processing"
        SciRIFFDataset["SciRIFF Dataset"]
        FilteredInstances["Task-filtered Instances"]
        FormattedPrompts["Formatted Prompts"]
    end
    
    BaseTemplate --> YAMLParser
    ModelDirs --> YAMLParser  
    TaskConfigs --> YAMLParser
    
    YAMLParser --> EleutherHarness
    EleutherHarness --> DocFormatter
    
    TaskList --> DynamicFilters
    FilterTask --> DynamicFilters
    
    SciRIFFDataset --> FilteredInstances
    DynamicFilters --> FilteredInstances
    DocFormatter --> FormattedPrompts
    FilteredInstances --> FormattedPrompts
```

Sources: [sciriff/eval/eleuther_templates/llama2/_default_template.yaml:1-15](), [sciriff/eval/eleuther_templates/llama2/utils.py:1-24]()

## Template Configuration Components

The configuration system consists of several key components that work together to define evaluation behavior:

| Component | Purpose | Location |
|-----------|---------|----------|
| `_default_template.yaml` | Base template configuration | `/eleuther_templates/llama2/` |
| `utils.py` | Task filtering utilities | `/eleuther_templates/llama2/` |
| Model directories | Model-specific template variations | `/eleuther_templates/{model}/` |
| Task filters | Dynamic task isolation functions | Generated from `eval_tasks` list |

### Core Configuration Elements

The base template defines essential configuration parameters:

- **Dataset Configuration**: Points to `allenai/SciRIFF` with specific dataset splits
- **Prompt Formatting**: Defines `doc_to_text` templates for model-specific prompting
- **Output Processing**: Specifies `doc_to_target` and delimiter configurations  
- **Metrics**: Configures evaluation metrics like BLEU with aggregation methods
- **Grouping**: Assigns tasks to evaluation groups like `science_adapt`

### Task Management System

```mermaid
graph TD
    subgraph "Task Registry"
        EvalTasksList["eval_tasks = [<br/>'bioasq_list_qa',<br/>'biored_ner',<br/>'discomat_te',<br/>...]"]
    end
    
    subgraph "Dynamic Function Generation"
        PartialFunc["partial(filter_task, task=eval_task)"]
        GlobalsAssignment["globals()[func_name] = function"]
    end
    
    subgraph "Generated Filter Functions"
        FilterBioASQ["filter_bioasq_list_qa()"]
        FilterBioRED["filter_biored_ner()"]
        FilterDiscomat["filter_discomat_te()"]
        FilterEvidence["filter_evidence_inference()"]
        FilterMulticite["filter_multicite_intent_classification()"]
        FilterMUP["filter_mup_single_document_summarization()"]
        FilterQasper["filter_qasper_abstractive_qa()"]
        FilterSciERC["filter_scierc_ner()"]
        FilterSciFact["filter_scifact_entailment()"]
    end
    
    subgraph "Dataset Filtering"
        InstanceID["_instance_id.split(':')[0]"]
        TaskMatch["task == extracted_task"]
        FilteredDataset["Task-specific Dataset"]
    end
    
    EvalTasksList --> PartialFunc
    PartialFunc --> GlobalsAssignment
    
    GlobalsAssignment --> FilterBioASQ
    GlobalsAssignment --> FilterBioRED  
    GlobalsAssignment --> FilterDiscomat
    GlobalsAssignment --> FilterEvidence
    GlobalsAssignment --> FilterMulticite
    GlobalsAssignment --> FilterMUP
    GlobalsAssignment --> FilterQasper
    GlobalsAssignment --> FilterSciERC
    GlobalsAssignment --> FilterSciFact
    
    FilterBioASQ --> InstanceID
    InstanceID --> TaskMatch
    TaskMatch --> FilteredDataset
```

Sources: [sciriff/eval/eleuther_templates/llama2/utils.py:8-24]()

## Integration with Evaluation Pipeline

The Configuration System serves as the interface between SciRIFF's scientific tasks and the broader evaluation infrastructure. Templates are processed by the Eleuther evaluation harness, which uses the configuration to:

1. **Load Dataset**: Access the SciRIFF dataset from Hugging Face using `dataset_path` and `dataset_name`
2. **Apply Filters**: Use utility functions to isolate specific tasks from the combined dataset
3. **Format Prompts**: Transform raw inputs using `doc_to_text` templates with model-specific formatting
4. **Process Outputs**: Extract targets using `doc_to_target` specifications
5. **Compute Metrics**: Apply configured metrics with specified aggregation methods

The system's modular design allows for easy extension to new model architectures by creating new template directories while maintaining consistent task definitions through the shared utility functions.

Sources: [sciriff/eval/eleuther_templates/llama2/_default_template.yaml:1-15](), [sciriff/eval/eleuther_templates/llama2/utils.py:4-6]()

---

