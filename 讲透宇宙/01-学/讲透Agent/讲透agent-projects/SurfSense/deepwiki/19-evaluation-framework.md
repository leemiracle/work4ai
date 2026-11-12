<!-- source: DeepWiki mcp.deepwiki.com · repo MODSetter/SurfSense · page 19 Evaluation Framework · fetched 2026-10-29 -->

# Evaluation Framework

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [surfsense_backend/app/agents/chat/runtime/llm_config.py](surfsense_backend/app/agents/chat/runtime/llm_config.py)
- [surfsense_backend/app/indexing_pipeline/__init__.py](surfsense_backend/app/indexing_pipeline/__init__.py)
- [surfsense_backend/app/indexing_pipeline/adapters/__init__.py](surfsense_backend/app/indexing_pipeline/adapters/__init__.py)
- [surfsense_backend/app/indexing_pipeline/adapters/file_upload_adapter.py](surfsense_backend/app/indexing_pipeline/adapters/file_upload_adapter.py)
- [surfsense_backend/app/indexing_pipeline/connector_document.py](surfsense_backend/app/indexing_pipeline/connector_document.py)
- [surfsense_backend/app/indexing_pipeline/document_persistence.py](surfsense_backend/app/indexing_pipeline/document_persistence.py)
- [surfsense_backend/app/indexing_pipeline/indexing_pipeline_service.py](surfsense_backend/app/indexing_pipeline/indexing_pipeline_service.py)
- [surfsense_backend/app/indexing_pipeline/pipeline_logger.py](surfsense_backend/app/indexing_pipeline/pipeline_logger.py)
- [surfsense_backend/app/retriever/chunks_hybrid_search.py](surfsense_backend/app/retriever/chunks_hybrid_search.py)
- [surfsense_backend/app/retriever/documents_hybrid_search.py](surfsense_backend/app/retriever/documents_hybrid_search.py)
- [surfsense_backend/app/services/connector_service.py](surfsense_backend/app/services/connector_service.py)
- [surfsense_backend/app/services/llm_router_service.py](surfsense_backend/app/services/llm_router_service.py)
- [surfsense_backend/app/services/llm_service.py](surfsense_backend/app/services/llm_service.py)
- [surfsense_backend/app/services/task_dispatcher.py](surfsense_backend/app/services/task_dispatcher.py)
- [surfsense_backend/app/services/token_tracking_service.py](surfsense_backend/app/services/token_tracking_service.py)
- [surfsense_backend/app/tasks/chat/streaming/flows/shared/llm_bundle.py](surfsense_backend/app/tasks/chat/streaming/flows/shared/llm_bundle.py)
- [surfsense_backend/tests/conftest.py](surfsense_backend/tests/conftest.py)
- [surfsense_backend/tests/integration/conftest.py](surfsense_backend/tests/integration/conftest.py)
- [surfsense_backend/tests/integration/document_upload/conftest.py](surfsense_backend/tests/integration/document_upload/conftest.py)
- [surfsense_backend/tests/integration/indexing_pipeline/adapters/__init__.py](surfsense_backend/tests/integration/indexing_pipeline/adapters/__init__.py)
- [surfsense_backend/tests/integration/indexing_pipeline/adapters/test_file_upload_adapter.py](surfsense_backend/tests/integration/indexing_pipeline/adapters/test_file_upload_adapter.py)
- [surfsense_backend/tests/integration/indexing_pipeline/test_index_document.py](surfsense_backend/tests/integration/indexing_pipeline/test_index_document.py)
- [surfsense_backend/tests/integration/indexing_pipeline/test_prepare_for_indexing.py](surfsense_backend/tests/integration/indexing_pipeline/test_prepare_for_indexing.py)
- [surfsense_backend/tests/unit/connector_indexers/test_confluence_parallel.py](surfsense_backend/tests/unit/connector_indexers/test_confluence_parallel.py)
- [surfsense_backend/tests/unit/connector_indexers/test_linear_parallel.py](surfsense_backend/tests/unit/connector_indexers/test_linear_parallel.py)
- [surfsense_backend/tests/unit/connector_indexers/test_notion_parallel.py](surfsense_backend/tests/unit/connector_indexers/test_notion_parallel.py)
- [surfsense_backend/tests/unit/indexing_pipeline/conftest.py](surfsense_backend/tests/unit/indexing_pipeline/conftest.py)
- [surfsense_backend/tests/unit/indexing_pipeline/test_connector_document.py](surfsense_backend/tests/unit/indexing_pipeline/test_connector_document.py)
- [surfsense_backend/tests/unit/indexing_pipeline/test_document_chunker.py](surfsense_backend/tests/unit/indexing_pipeline/test_document_chunker.py)
- [surfsense_backend/tests/unit/indexing_pipeline/test_index_batch_parallel.py](surfsense_backend/tests/unit/indexing_pipeline/test_index_batch_parallel.py)
- [surfsense_backend/tests/unit/observability/test_retriever_otel.py](surfsense_backend/tests/unit/observability/test_retriever_otel.py)
- [surfsense_web/components/assistant-ui/token-usage-context.tsx](surfsense_web/components/assistant-ui/token-usage-context.tsx)

</details>



The SurfSense Evaluation Framework, implemented primarily within the `surfsense_evals` harness, provides a standardized environment for benchmarking Retrieval-Augmented Generation (RAG) quality. It allows developers to measure the performance of the system's retrieval and generation pipelines against specialized datasets, such as medical QA and multimodal document benchmarks.

The framework is designed to test different system configurations, including various LLM providers, embedding models, and retrieval strategies (e.g., hybrid search with RRF fusion), to ensure high accuracy and reliability in domain-specific knowledge retrieval.

## System Evaluation Overview

The evaluation framework bridges the gap between raw codebase entities (like search retrievers and indexing services) and high-level performance metrics. It utilizes the same underlying services used in production to ensure benchmarks reflect real-world performance.

### Code to Evaluation Mapping
The following diagram illustrates how core system components are integrated into the evaluation harness.

**Evaluation Data Flow**
```mermaid
graph TD
    subgraph "EvaluationHarness"
        [SuiteRegistry] --> [BenchmarkSuite]
        [BenchmarkSuite] --> [EvalArm]
        [EvalArm] --> [ReportWriter]
    end

    subgraph "surfsense_backend"
        [EvalArm] -- "executes_search" --> [ConnectorService]
        [ConnectorService] -- "calls" --> [ChucksHybridSearchRetriever]
        [ConnectorService] -- "calls" --> [DocumentHybridSearchRetriever]
        [IndexingPipelineService] -- "populates" --> [Chunk_Table]
        [EvalArm] -- "generates_response" --> [LLMRouterService]
    end

    [Chunk_Table] -- "read_by" --> [ChucksHybridSearchRetriever]
```
**Sources:** [surfsense_backend/app/services/connector_service.py:25-30](), [surfsense_backend/app/indexing_pipeline/indexing_pipeline_service.py:82-85](), [surfsense_backend/app/services/llm_router_service.py:104-111]()

## Core Components

The framework relies on several key backend services to execute retrieval and generation tasks during benchmarking:

| Component | Role in Evaluation |
| :--- | :--- |
| `IndexingPipelineService` | Responsible for preparing and indexing benchmark datasets into the test database [surfsense_backend/app/indexing_pipeline/indexing_pipeline_service.py:82-85](). |
| `ConnectorService` | Orchestrates the retrieval flow, combining results from multiple search strategies using RRF via `_combined_rrf_search` [surfsense_backend/app/services/connector_service.py:128-162](). |
| `ChucksHybridSearchRetriever` | Executes vector and full-text search at the chunk level [surfsense_backend/app/services/connector_service.py:28-28](). |
| `LLMRouterService` | Manages LLM calls for the "Generation" phase of RAG evaluation, handling load balancing and failover across providers [surfsense_backend/app/services/llm_router_service.py:104-111](). |
| `TokenTrackingService` | Monitors token consumption and costs (`cost_micros`) during eval runs to calculate benchmark efficiency [surfsense_backend/app/services/token_tracking_service.py:173-187](). |

## Benchmark Scenarios

The framework supports multiple execution "arms" or scenarios to compare performance across different cost and quality profiles:

*   **Head-to-Head:** Direct comparison between two different LLMs or retrieval configurations.
*   **Symmetric-Cheap:** Benchmarking using cost-optimized models to establish a performance baseline.
*   **Cost-Arbitrage:** Evaluating the trade-off between expensive "frontier" models and cheaper models assisted by high-quality retrieval.

## Integration with RAG Pipeline

Evaluations directly exercise the production RAG pipeline, specifically the hybrid search logic found in `_combined_rrf_search` [surfsense_backend/app/services/connector_service.py:128-162](). This ensures that improvements in the codebase—such as better chunking via `chunk_text_hybrid` [surfsense_backend/app/indexing_pipeline/indexing_pipeline_service.py:23-23]() or optimized embedding batches [surfsense_backend/app/indexing_pipeline/indexing_pipeline_service.py:23-23]()—are immediately measurable in the benchmark results.

**Search & Retrieval Architecture**
```mermaid
graph LR
    subgraph "Retrieval_Logic"
        [Query] --> [ConnectorService]
        [ConnectorService] -- "parallel_fetch" --> [ChucksHybridSearchRetriever]
        [ConnectorService] -- "parallel_fetch" --> [DocumentHybridSearchRetriever]
    end

    subgraph "Reciprocal_Rank_Fusion"
        [ChucksHybridSearchRetriever] --> [RRF_Fusion]
        [DocumentHybridSearchRetriever] --> [RRF_Fusion]
    end

    subgraph "Generation_Logic"
        [RRF_Fusion] --> [Context_Assembly]
        [Context_Assembly] --> [LLMRouterService]
        [LLMRouterService] --> [Final_Response]
    end
```
**Sources:** [surfsense_backend/app/services/connector_service.py:137-162](), [surfsense_backend/app/services/llm_router_service.py:131-140]()

---

## Detailed Documentation

For deeper technical specifications, refer to the following sub-pages:

### [Eval Harness Architecture](#19.1)
Details the core infrastructure, including HTTP clients for model interaction, metrics collection (latency, recall, precision), and the `ReportWriter` for generating benchmark summaries. It also covers how `TokenUsage` is tracked to measure cost-per-query [surfsense_backend/app/services/token_tracking_service.py:30-31]().

### [Benchmark Suites](#19.2)
Documentation for specific suites:
*   **Medical:** `medxpertqa`, `mirage`, and `cure` for healthcare-specific RAG.
*   **Multimodal Doc:** `mmlongbench` for testing long-context retrieval across complex document formats.
*   **Adapter Testing:** Integration tests for `UploadDocumentAdapter` ensure that manual uploads meet the same quality standards as connector-indexed data [surfsense_backend/app/indexing_pipeline/adapters/file_upload_adapter.py:9-12]().

---

