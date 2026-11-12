<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/scibert · page 6 Data Processing · fetched 2026-10-26 -->

# Data Processing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [data/text_classification/chemprot/dev.txt](data/text_classification/chemprot/dev.txt)
- [data/text_classification/chemprot/test.txt](data/text_classification/chemprot/test.txt)
- [data/text_classification/chemprot/train.txt](data/text_classification/chemprot/train.txt)
- [scripts/chemprot_to_relation.py](scripts/chemprot_to_relation.py)
- [scripts/fix_format_pico_conll2003.py](scripts/fix_format_pico_conll2003.py)
- [scripts/sciie_to_relations.py](scripts/sciie_to_relations.py)

</details>



## Purpose and Scope

The data processing system handles format conversion and preprocessing of scientific NLP datasets for fine-tuning SciBERT models. This includes converting various dataset formats to standardized formats compatible with AllenNLP dataset readers, adding entity markers for relation extraction tasks, and preparing data for specific downstream tasks like named entity recognition, PICO extraction, and text classification.

For information about model training and fine-tuning workflows, see [Fine-tuning Guide](#3). For dataset readers that consume the processed data, see [Dataset Readers](#4.2).

## Data Processing Pipeline

The data processing system consists of format conversion scripts that transform raw scientific datasets into standardized formats suitable for model training.

```mermaid
graph TD
    subgraph "Raw Datasets"
        A["PICO/EBMNLP Files<br/>📄 Token + Tag format"]
        B["SciIE Dataset<br/>📄 JSON with entities/relations"]
        C["ChemProt Dataset<br/>📄 XML format"]
    end
    
    subgraph "Processing Scripts"
        D["fix_format_pico_conll2003.py<br/>🔧 PICO to CoNLL2003 converter"]
        E["sciie_to_relations.py<br/>🔧 SciIE relation extractor"]
        F["chemprot_to_relation.py<br/>🔧 ChemProt relation extractor"]
    end
    
    subgraph "Processed Output"
        G["CoNLL2003 Format<br/>📋 4-column: Token POS Chunk Label"]
        H["Relation JSON Lines<br/>📋 text + label + metadata"]
        I["ChemProt JSON Lines<br/>📋 text + label + entity markers"]
    end
    
    subgraph "Dataset Readers"
        J["CoNLL2003DatasetReader<br/>📖 NER tasks"]
        K["ClassificationDatasetReader<br/>📖 Relation classification"]
    end
    
    A --> D
    B --> E
    C --> F
    D --> G
    E --> H
    F --> I
    G --> J
    H --> K
    I --> K
```

**Sources:** [scripts/fix_format_pico_conll2003.py:1-50](), [scripts/sciie_to_relations.py:1-52](), [scripts/chemprot_to_relation.py:1-68]()

## Format Conversion Scripts

### PICO to CoNLL2003 Converter

The `fix_format_pico_conll2003.py` script addresses three formatting issues with PICO/EBMNLP data:

1. **Column Format**: Converts 2-column (Token, Tag) to 4-column CoNLL2003 format
2. **File Consolidation**: Merges separate per-paper files into single train/dev/test files
3. **Sentence Segmentation**: Adds sentence breaks at periods to prevent BERT truncation issues

```mermaid
graph LR
    subgraph "Input: PICO Files"
        A["paper1.txt<br/>Token Tag"]
        B["paper2.txt<br/>Token Tag"]
        C["paper3.txt<br/>Token Tag"]
    end
    
    subgraph "fix_format_pico_conll2003.py"
        D["Add DOCSTART markers<br/>-DOCSTART- (paper_id)"]
        E["Convert to 4-column<br/>Token NN O Label"]
        F["Add sentence breaks<br/>Split on periods"]
    end
    
    subgraph "Output: CoNLL2003"
        G["train.txt<br/>4-column format<br/>Multiple papers"]
    end
    
    A --> D
    B --> D
    C --> D
    D --> E
    E --> F
    F --> G
```

Key implementation details:
- Adds placeholder `NN` for POS tags and `O` for chunk labels at [scripts/fix_format_pico_conll2003.py:43]()
- Inserts sentence breaks when encountering periods with `O` labels at [scripts/fix_format_pico_conll2003.py:46-47]()
- Paper IDs extracted from filenames and used in DOCSTART markers at [scripts/fix_format_pico_conll2003.py:34-36]()

**Sources:** [scripts/fix_format_pico_conll2003.py:1-50]()

### SciIE Relation Extractor

The `sciie_to_relations.py` script extracts relation information from the SciIE dataset and optionally adds entity markers for relation classification tasks.

```mermaid
graph TD
    subgraph "SciIE Input"
        A["JSON Lines<br/>sentences + relations arrays"]
    end
    
    subgraph "sciie_to_relations.py"
        B["Extract Relations<br/>e1_from, e1_to, e2_from, e2_to, rel_type"]
        C["Add Entity Markers<br/>[[ entity1 ]] << entity2 >>"]
        D["Adjust Offsets<br/>Account for sentence boundaries"]
    end
    
    subgraph "Output"
        E["JSON Lines<br/>text + label + metadata"]
    end
    
    A --> B
    B --> C
    C --> D
    D --> E
```

Entity marker placement logic handles overlapping entities by inserting markers in the correct order at [scripts/sciie_to_relations.py:35-45](). The script adjusts character offsets relative to sentence boundaries at [scripts/sciie_to_relations.py:31-34]().

**Sources:** [scripts/sciie_to_relations.py:1-52]()

### ChemProt Relation Extractor

The `chemprot_to_relation.py` script processes ChemProt XML data to extract chemical-protein relations with entity highlighting.

```mermaid
graph TD
    subgraph "ChemProt XML"
        A["XML Documents<br/>sentences + entities + interactions"]
    end
    
    subgraph "chemprot_to_relation.py"
        B["Parse XML<br/>Extract entities and relations"]
        C["Filter Relations<br/>13 valid relation types"]
        D["Add Entity Markers<br/><< chem >> [[ protein ]]"]
        E["Order Entities<br/>Based on character positions"]
    end
    
    subgraph "Output"
        F["JSON Lines<br/>Chemical-protein relations"]
    end
    
    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
```

The script filters for specific relation types defined at [scripts/chemprot_to_relation.py:42-45]() and handles entity ordering based on character positions at [scripts/chemprot_to_relation.py:47-62]().

**Sources:** [scripts/chemprot_to_relation.py:1-68]()

## Output Data Formats

### CoNLL2003 Format

The processed PICO data follows the standard CoNLL2003 4-column format:

| Column | Content | Example |
|--------|---------|---------|
| Token | Word/token | `patients` |
| POS | Part-of-speech | `NN` |
| Chunk | Chunk label | `O` |
| NER | Named entity | `B-Population` |

Document boundaries are marked with `-DOCSTART- (paper_id)` lines, and sentence boundaries are indicated by blank lines.

### Relation Classification Format

Both SciIE and ChemProt outputs use JSON Lines format with entity markers:

```json
{
  "text": "<< Epidermal growth factor receptor >> inhibitors include [[ gefitinib ]]",
  "label": "INHIBITOR", 
  "metadata": []
}
```

Entity markers distinguish between the two entities in each relation:
- `<< entity1 >>` - First entity (typically chemical/drug)
- `[[ entity2 ]]` - Second entity (typically protein/gene)

**Sources:** [data/text_classification/chemprot/train.txt:1-10](), [data/text_classification/chemprot/dev.txt:1-10](), [data/text_classification/chemprot/test.txt:1-10]()

## Integration with Training Pipeline

The processed datasets integrate with the AllenNLP-based fine-tuning system through specific dataset readers:

```mermaid
graph LR
    subgraph "Processed Data"
        A["CoNLL2003 Files<br/>PICO NER data"]
        B["JSON Lines<br/>Relation data"]
    end
    
    subgraph "Dataset Readers"
        C["Conll2003DatasetReader<br/>Reads 4-column format"]
        D["ClassificationDatasetReader<br/>Reads JSON format"]
    end
    
    subgraph "Model Training"
        E["BertCrfTagger<br/>NER models"]
        F["BertTextClassifier<br/>Relation models"]
    end
    
    A --> C
    B --> D
    C --> E
    D --> F
```

The data processing scripts ensure compatibility with AllenNLP's expected input formats, enabling seamless integration with the model training pipeline described in the fine-tuning configurations.

**Sources:** [scripts/fix_format_pico_conll2003.py:1-50](), [scripts/sciie_to_relations.py:1-52](), [scripts/chemprot_to_relation.py:1-68]()

---

