<!-- source: DeepWiki mcp.deepwiki.com · repo langchain-ai/rag-from-scratch · page 2 RAG Architecture · fetched 2026-10-26 -->

# RAG Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [rag_from_scratch_1_to_4.ipynb](rag_from_scratch_1_to_4.ipynb)

</details>



## Purpose and Scope

This document provides a comprehensive technical overview of the Retrieval-Augmented Generation (RAG) architecture implemented in the `rag-from-scratch` repository. It details the core components, their interactions, and the data flow through the system as LLMs are grounded with external data sources [README.md:1-6](). For detailed implementation of specific components, see the dedicated pages on [Document Processing and Indexing](#2.1), [Retrieval Mechanisms](#2.2), and [Query Augmentation and Generation](#2.3).

## High-Level RAG Architecture

The architecture follows a modular design pattern consisting of two primary phases: offline processing (indexing) and online processing (retrieval and generation).

### Core RAG Pipeline Architecture

```mermaid
flowchart TD
    subgraph "RAG_Pipeline"
        subgraph "Indexing_Offline"
            A["WebBaseLoader"] --> B["RecursiveCharacterTextSplitter"]
            B --> C["OpenAIEmbeddings"]
            C --> D["Chroma_VectorStore"]
        end
        
        subgraph "Retrieval_and_Generation_Online"
            E["User_Query"] --> F["hub.pull_rlm-rag-prompt"]
            F --> G["Chroma.as_retriever"]
            D -.-> G
            G --> H["format_docs_Function"]
            H --> I["ChatOpenAI_LLM"]
            I --> J["StrOutputParser"]
            J --> K["Final_Response"]
            E -.-> H
        end
    end
```
Sources: [rag_from_scratch_1_to_4.ipynb:42-55](), [rag_from_scratch_1_to_4.ipynb:114-125](), [rag_from_scratch_1_to_4.ipynb:206-225]()

The architecture separates concerns between document preparation and query handling:

1. **Offline Processing (Indexing)**: Documents are loaded via `WebBaseLoader`, split into chunks using `RecursiveCharacterTextSplitter`, embedded, and stored in a `Chroma` vector database [rag_from_scratch_1_to_4.ipynb:42-55]().
2. **Online Processing (Retrieval & Generation)**: Relevant chunks are fetched by a `retriever`, formatted, and passed to an LLM like `ChatOpenAI` using a specific prompt template (e.g., `rlm-rag-prompt`) [rag_from_scratch_1_to_4.ipynb:206-225]().

## Core RAG Components

### Document Processing and Indexing Components

```mermaid
classDiagram
    class WebBaseLoader {
        +load() List[Document]
    }

    class RecursiveCharacterTextSplitter {
        +split_documents(docs) List[Document]
    }

    class OpenAIEmbeddings {
        +embed_documents(texts) List[List[float]]
        +embed_query(text) List[float]
    }

    class Chroma {
        +from_documents(docs, embedding)
        +as_retriever() Retriever
    }

    WebBaseLoader --> RecursiveCharacterTextSplitter : provides raw docs
    RecursiveCharacterTextSplitter --> OpenAIEmbeddings : provides text chunks
    OpenAIEmbeddings --> Chroma : provides vectors
```
Sources: [rag_from_scratch_1_to_4.ipynb:42-55](), [rag_from_scratch_1_to_4.ipynb:114-125]()

### Retrieval and Generation Components

```mermaid
classDiagram
    class ChatOpenAI {
        +invoke(prompt) AIMessage
    }

    class StrOutputParser {
        +parse(text) String
    }

    class PromptTemplate {
        +format(context, question) String
    }

    class Retriever {
        +get_relevant_documents(query) List[Document]
    }

    Retriever --> PromptTemplate : provides context
    PromptTemplate --> ChatOpenAI : provides formatted prompt
    ChatOpenAI --> StrOutputParser : provides raw response
```
Sources: [rag_from_scratch_1_to_4.ipynb:206-225]()

## RAG Data Flow

The following sequence diagram illustrates the data flow using the LCEL (LangChain Expression Language) chain implemented in the repository [rag_from_scratch_1_to_4.ipynb:218-220]():

```mermaid
sequenceDiagram
    participant User
    participant Retriever as Chroma_Retriever
    participant Formatter as format_docs
    participant Prompt as RAG_Prompt_Hub
    participant LLM as ChatOpenAI
    participant Parser as StrOutputParser
    
    User->>Retriever: invoke(query)
    Retriever-->>Formatter: retrieved_chunks
    Formatter-->>Prompt: context_string
    User->>Prompt: question
    Prompt->>LLM: formatted_prompt
    LLM->>Parser: raw_completion
    Parser-->>User: final_answer_string
```
Sources: [rag_from_scratch_1_to_4.ipynb:206-225]()

## Implementation Evolution

The RAG architecture is implemented across multiple notebooks, evolving from basic retrieval to complex multi-step reasoning:

1.  **Basic RAG (Notebooks 1-4)**: Foundation of indexing, retrieval, and generation using `Chroma` and `OpenAI` [rag_from_scratch_1_to_4.ipynb:1-5](). For details, see [Document Processing and Indexing](#2.1).
2.  **Advanced RAG (Notebooks 5-9)**: Introduction of Query Translation techniques like Multi-query, RAG-Fusion, and Decomposition. For details, see [Retrieval Mechanisms](#2.2).
3.  **Extensions (Notebooks 10-11)**: Implementation of Routing (Logical and Semantic) and Query Construction for structured data.
4.  **Refinements (Notebooks 12-14)**: Indexing optimizations like Multi-vector retrievers and ColBERT, and Re-ranking strategies. For details, see [Query Augmentation and Generation](#2.3).
5.  **Production Implementation (Notebooks 15-18)**: Advanced "Corrective RAG" (CRAG) and Self-RAG using `LangGraph` for stateful orchestration.

## Key Implementation Considerations

The RAG architecture in this repository addresses several critical implementation concerns:

1.  **Context Management**: Using `format_docs` to join document contents into a single string for the prompt [rag_from_scratch_1_to_4.ipynb:211-213]().
2.  **Modularity**: Leveraging LangChain's LCEL to pipe components like `retriever | prompt | llm | parser` [rag_from_scratch_1_to_4.ipynb:218-220]().
3.  **External Knowledge**: Mitigating LLM limitations regarding private or recent information [README.md:3-4]().

The subsequent pages will explore specific components in greater detail, including document processing ([Document Processing and Indexing](#2.1)), retrieval mechanisms ([Retrieval Mechanisms](#2.2)), and query augmentation and generation ([Query Augmentation and Generation](#2.3)).

---

