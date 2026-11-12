<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/codescientist · page 5 Knowledge Systems · fetched 2026-10-26 -->

# Knowledge Systems

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [codeblocks/knowledgebase_ConvertConceptNet.py](codeblocks/knowledgebase_ConvertConceptNet.py)
- [codeblocks/knowledgebase_conceptnet.py](codeblocks/knowledgebase_conceptnet.py)
- [codeblocks/knowledgebase_wordnet.py](codeblocks/knowledgebase_wordnet.py)

</details>



## Purpose and Scope

The Knowledge Systems provide structured access to external knowledge bases that enhance agent reasoning capabilities within CodeScientist. This infrastructure enables agents to leverage semantic relationships, word meanings, and conceptual hierarchies when performing scientific discovery tasks.

This document covers the integration and preprocessing of ConceptNet and WordNet knowledge bases. For agent architectures that utilize these knowledge systems, see [Agent Architectures](#3). For the common library utilities that provide the underlying access methods, see [Common Experiment Library](#7.1).

## Architecture Overview

CodeScientist integrates two primary knowledge bases to support agent reasoning: ConceptNet for broad conceptual relationships and WordNet for lexical semantic information. These systems are accessed through a common interface provided by the `experiment_common_library` module.

### Knowledge Base Integration Architecture

```mermaid
graph TB
    subgraph "Knowledge Sources"
        ConceptNetRaw["conceptnet-assertions-5.7.0.csv"]
        WordNetNLTK["WordNet via NLTK"]
    end
    
    subgraph "Preprocessing Layer"
        ConceptNetConverter["knowledgebase_ConvertConceptNet.py"]
        WordNetSetup["setup_wordnet()"]
    end
    
    subgraph "Processed Knowledge Stores"
        ConceptNetJSON["conceptnet-assertions-5.7.0.reduced.lookup.json"]
        WordNetCorpus["NLTK WordNet Corpus"]
    end
    
    subgraph "Access Layer"
        ConceptNetClass["ConceptNet class"]
        WordNetFunctions["WordNet functions"]
        CommonLibrary["experiment_common_library"]
    end
    
    subgraph "Agent Systems"
        ReActAgent["ReAct Agent"]
        MemoryAgent["Memory Agent"]
        KnowledgeScorer["Knowledge Scorer"]
    end
    
    ConceptNetRaw --> ConceptNetConverter
    ConceptNetConverter --> ConceptNetJSON
    WordNetNLTK --> WordNetSetup
    WordNetSetup --> WordNetCorpus
    
    ConceptNetJSON --> ConceptNetClass
    WordNetCorpus --> WordNetFunctions
    ConceptNetClass --> CommonLibrary
    WordNetFunctions --> CommonLibrary
    
    CommonLibrary --> ReActAgent
    CommonLibrary --> MemoryAgent
    CommonLibrary --> KnowledgeScorer
```

Sources: [codeblocks/knowledgebase_ConvertConceptNet.py:1-86](), [codeblocks/knowledgebase_conceptnet.py:8-64](), [codeblocks/knowledgebase_wordnet.py:9-254]()

## ConceptNet Integration

ConceptNet provides a large-scale semantic network with relationships between concepts expressed in natural language. The CodeScientist implementation focuses on the English subset for performance and relevance.

### ConceptNet Data Processing Pipeline

```mermaid
graph LR
    subgraph "Raw Data Processing"
        CSVInput["conceptnet-assertions-5.7.0.csv"]
        LineFilter["Filter /c/en/ lines"]
        FieldExtraction["Extract relation, nodeStart, nodeEnd"]
        PathCleaning["Remove /r/ and /c/en/ prefixes"]
        EnglishFilter["Filter non-English nodes"]
    end
    
    subgraph "Output Formats"
        RelationList["relations array"]
        LookupTable["look_up_table dictionary"]
        InverseRelations["INV_ inverse relations"]
    end
    
    subgraph "JSON Outputs"
        ReducedJSON["conceptnet-assertions-5.7.0.reduced.json"]
        LookupJSON["conceptnet-assertions-5.7.0.reduced.lookup.json"]
    end
    
    CSVInput --> LineFilter
    LineFilter --> FieldExtraction
    FieldExtraction --> PathCleaning
    PathCleaning --> EnglishFilter
    
    EnglishFilter --> RelationList
    EnglishFilter --> LookupTable
    LookupTable --> InverseRelations
    
    RelationList --> ReducedJSON
    LookupTable --> LookupJSON
    InverseRelations --> LookupJSON
```

Sources: [codeblocks/knowledgebase_ConvertConceptNet.py:10-86]()

The preprocessing pipeline transforms ConceptNet's raw CSV format into optimized JSON structures. Key transformations include:

| Processing Step | Purpose | Implementation |
|-----------------|---------|----------------|
| English Filtering | Reduce dataset size | Filter lines containing `/c/en/` [codeblocks/knowledgebase_ConvertConceptNet.py:17-18]() |
| Prefix Removal | Simplify node names | Remove `/r/` and `/c/en/` prefixes [codeblocks/knowledgebase_ConvertConceptNet.py:29-35]() |
| Inverse Relations | Bidirectional lookup | Create `INV_` prefixed relations [codeblocks/knowledgebase_ConvertConceptNet.py:74-76]() |
| Lookup Table | Fast access | Dictionary keyed by subject nodes [codeblocks/knowledgebase_ConvertConceptNet.py:63-82]() |

### ConceptNet Access Interface

The `ConceptNet` class provides methods for querying the processed knowledge base:

```mermaid
graph TB
    subgraph "ConceptNet Class Methods"
        FindNodes["find_nodes(term, strict=False)"]
        GetEdges["get_node_edges(node_name, filter_relation_types=None)"]
        GetRelations["get_all_relations()"]
        GetAllNodes["get_all_nodes()"]
    end
    
    subgraph "Query Types"
        StrictQuery["Strict matching: 'cat' → ['cat/n', 'cat/v/wn/contact']"]
        FuzzyQuery["Fuzzy matching: 'cat' → ['catheterized', 'categorize']"]
        RelationFilter["Filtered relations: ['IsA', 'INV_IsA']"]
        AllRelations["Full relation set: ['Antonym', 'AtLocation', ...]"]
    end
    
    subgraph "Data Structures"
        EdgeFormat["[subject, relation, object]"]
        NodeFormat["node_name strings"]
        RelationFormat["relation_type strings"]
    end
    
    FindNodes --> StrictQuery
    FindNodes --> FuzzyQuery
    GetEdges --> RelationFilter
    GetEdges --> EdgeFormat
    GetRelations --> AllRelations
    GetAllNodes --> NodeFormat
```

Sources: [codeblocks/knowledgebase_conceptnet.py:14-60]()

## WordNet Integration

WordNet provides lexical semantic relationships including synonyms, antonyms, hypernyms, hyponyms, and meronyms. The integration uses NLTK's WordNet interface with setup utilities from the common library.

### WordNet Function Categories

| Function Category | Methods | Return Type | Example |
|-------------------|---------|-------------|---------|
| Synset Operations | `get_synsets()`, `get_synset_definition()`, `get_words_in_synset()` | Synset objects, strings, lists | `car.n.01` synset |
| Synonym/Antonym | `get_synonyms()`, `get_antonyms()` | List of strings | `['car', 'auto', 'automobile']` |
| Hierarchical | `get_direct_hypernyms()`, `get_continuous_hypernyms()` | List of Synset objects | Hypernym chains |
| Part Relations | `get_part_meronyms()` | List of Synset objects | Car parts like `accelerator.n.01` |

Sources: [codeblocks/knowledgebase_wordnet.py:12-254]()

### WordNet Semantic Relationship Mapping

```mermaid
graph TB
    subgraph "WordNet Relationship Types"
        Synonyms["get_synonyms('car')"]
        Antonyms["get_antonyms('good')"]
        DirectHyper["get_direct_hypernyms('car')"]
        ContHyper["get_continuous_hypernyms('car')"]
        DirectHypo["get_direct_hyponyms('car')"]
        ContHypo["get_continuous_hyponyms('car')"]
        PartMero["get_part_meronyms('car')"]
    end
    
    subgraph "Semantic Hierarchy"
        EntityRoot["entity.n.01"]
        VehicleLevel["vehicle.n.01"]
        MotorVehicle["motor_vehicle.n.01"]
        CarLevel["car.n.01"]
        SpecificCars["ambulance.n.01, sports_car.n.01"]
    end
    
    subgraph "Part Relationships"
        CarParts["accelerator.n.01, brake.n.01, steering_wheel.n.01"]
    end
    
    DirectHyper --> MotorVehicle
    ContHyper --> EntityRoot
    ContHyper --> VehicleLevel
    ContHyper --> MotorVehicle
    DirectHypo --> SpecificCars
    ContHypo --> SpecificCars
    PartMero --> CarParts
    
    MotorVehicle --> CarLevel
    CarLevel --> SpecificCars
```

Sources: [codeblocks/knowledgebase_wordnet.py:98-254]()

## Integration with Agent Systems

Knowledge systems are accessed by agents through the `experiment_common_library` module, which provides unified interfaces for both ConceptNet and WordNet. This design allows agents to leverage semantic knowledge without directly managing knowledge base connections.

### Agent Knowledge Access Pattern

```mermaid
graph LR
    subgraph "Agent Layer"
        AgentCode["Agent Implementation"]
        KnowledgeQuery["Knowledge Query Logic"]
    end
    
    subgraph "Common Library Interface"
        ConceptNetImport["from experiment_common_library import ConceptNet"]
        WordNetSetup["from experiment_common_library import setup_wordnet"]
        UnifiedAPI["Unified Knowledge API"]
    end
    
    subgraph "Knowledge Base Layer"
        ConceptNetInstance["ConceptNet() instance"]
        WordNetCorpus["NLTK WordNet corpus"]
    end
    
    subgraph "Processed Data"
        ConceptNetLookup["conceptnet lookup.json"]
        WordNetData["WordNet synsets"]
    end
    
    AgentCode --> KnowledgeQuery
    KnowledgeQuery --> ConceptNetImport
    KnowledgeQuery --> WordNetSetup
    ConceptNetImport --> UnifiedAPI
    WordNetSetup --> UnifiedAPI
    
    UnifiedAPI --> ConceptNetInstance
    UnifiedAPI --> WordNetCorpus
    ConceptNetInstance --> ConceptNetLookup
    WordNetCorpus --> WordNetData
```

Sources: [codeblocks/knowledgebase_conceptnet.py:12](), [codeblocks/knowledgebase_wordnet.py:9]()

The knowledge systems enable agents to perform semantic reasoning by providing access to:

- **Conceptual relationships** through ConceptNet's `IsA`, `PartOf`, `UsedFor`, and other semantic relations
- **Lexical semantics** through WordNet's synonym, hypernym, and meronym relationships  
- **Inverse relationship traversal** via ConceptNet's `INV_` prefixed relations
- **Hierarchical concept navigation** through WordNet's hypernym/hyponym chains

This semantic knowledge enhances agent reasoning capabilities in scientific discovery tasks by providing structured background knowledge about concepts, their relationships, and semantic hierarchies.

---

