# RAG: Building a Database

A database is required in order to perform RAG inferencing. The Game Agent SDK
includes `BuildRag.exe`, a utility that converts a collection of UTF-8 text
files into a lexical (BM25) or semantic (vector) database for use with the
RAG APIs. Source lives at `source/tools/build_rag.cpp` and builds together
with the rest of the SDK; after `build.bat` the binary is at
`_out/BuildRag.exe` (or `bin/BuildRag.exe` when using the SDK release zip).

## Data Preparation Best Practices
Before organizing your data into the required folder structure, follow these 
recommendations to optimize retrieval quality:

1. **Prune irrelevant content** — Remove outdated, deprecated, or off-topic records 
   and fields to reduce noise and improve retrieval precision.

2. **Consolidate scattered information** — Process supplementary data sources 
   (e.g., encyclopedias, wikis, external documentation) that contain information 
   missing or fragmented in primary data files.

3. **Resolve references to human-readable text** — Replace internal keys, IDs, 
   and reference patterns with their actual readable values. Follow foreign key 
   chains and perform reverse lookups as needed.

4. **Translate coded values** — Convert machine-readable formats to natural language:
   - Boolean flags: `1` → `yes`, `0` → `no`
   - Interpolate placeholder values: `%+n` → actual computed values
   - Express relationships as sentences: *"Building 'X' allows recruitment of Unit 'Y'"* 
     instead of *"building_units_allowed: X, Y"*

5. **Enrich records selectively** — Inline related data (e.g., effects, stats, 
   availability) into records, but avoid over-flattening. Excessive duplication 
   across records dilutes semantic distinctiveness and hurts retrieval accuracy. 

6. **Generate supplemental summaries** — Create pre-computed summary records for 
   common reverse-lookup query patterns. For example, if individual records describe 
   one-to-one relationships (e.g., "Building X allows recruitment of Unit A"), create summary records that aggregate the reverse lookup (e.g., "Unit A can be recruited from Buildings X, Y").

   Sample record that shows individual relationship of building - unit recruitment:
   ```
   ##Heading2: Unit A
   ##PARA
   Topic: Building unit recruitment
   Section: Unit A

   Building 'X' allows the recruitment of Unit 'A'
   ---
   ##ENDPARA
   ```

   Sample summary record:
   ```
   ##Heading2: Unit A
   ##PARA
   Topic: Building unit recruitment by unit
   Section: Unit A

   Buildings that allow recruiting Unit 'A' (2 buildings):
     - X
     - Y
   ---
   ##ENDPARA
   ```

## Expected Folder Layout for Building a Database   
The data to be converted into a database must be stored in a folder with the following layout:

   ```C
   folder/
   - doc/
      - main_units.txt
      - building_levels.txt
      - ... 
   - kv/
      - faq.txt
      - ... 
   ```

   **Doc (Document) Folder**

   Place files in the doc/ subdirectory.

   How it works:
   - Content is chunked (by section headers or token count)
   - The entire chunk text is used for both search indexing AND retrieval
   - Supports graph edges for navigating between related sections

   Best for:
   - General documentation, articles, knowledge bases
   - Content where any part of the text could be relevant to a query
   - When you want search across the full content

   **KV (Key-Value) Folder**

   Place files in the kv/ subdirectory using Q:/A: format.

   How it works:
   - Only the key (Q:) is embedded/indexed for search
   - The full Q+A is returned when retrieved
   - No chunking, each Q/A pair is one atomic record

   Best for:
   - Large records where searching the full content would dilute retrieval accuracy
   - Structured data with clear descriptive keys
   - FAQ-style content
   
   Example File `kv/faq.txt`:

   ```
   Q: What is the capital of The United States?
   A: Washington D.C.

   Q: What is the capital of Japan?
   A: Tokyo
   ```

   Example KV Database Output:

   | Key | Value |
   | :--------: | :-------: |
   | What is the capital of The United States? | Q: What is the capital of The United States?<br>  A: Washington D.C.  |
   | What is the capital of The Japan? | Q: What is the capital of Japan?<br>A: Tokyo  |
   
## Command Line Parameters
| Single char | Fullname | Meaning |
| :--------: | :-------: | :-------: |
| -m | --model=<file_path>   | Path to embedding model file e.g. `all-MiniLM-L6-v2.F32.gguf`. Required for both semantic and lexical databases (the model's tokenizer is used for chunking) |
| -d | --data=<folder_path>  | Path to the root folder of your input data that contains a doc folder and optionally a kv folder |
| -o | --output=<folder_path> | Path to the output database folder |
| -b | --bm25 | Build a lexical (BM25) database instead of the default semantic database |
| -s | --sections | Section based / fine-grained chunking (see relevant section below) |

```bash
Usage: BuildRag.exe -m [pathToModel] -d [dataFolder] -o [outputFolderName] 
```
```bash
Command Prompt: BuildRag.exe -m ../data/models/miniLM/all-MiniLM-L6-v2.F32.gguf ^
                  -d ../data/raw-text/poker ^
                  -o ../data/dbs/poker.db 

Powershell: .\BuildRag.exe -m ../data/models/miniLM/all-MiniLM-L6-v2.F32.gguf `
                  -d ../data/raw-text/poker `
                  -o ../data/dbs/poker.db 
```

**Notes:** The BuildRag tool has only been tested with the miniLM models included with the SDK: `all-MiniLM-L6-v2.F32.gguf` and `multilingual-e5-base-Q8_0.gguf`. Using other models is not guaranteed to work and results may be unusable by Game Agent SDK.

**Inputs:** The primary input of the BuildRag tool is a folder that contains a collection of text files to encode. Each text file will be converted to tokens and then placed in a unique entry in the database. If the number of tokens for a text file is greater than the given threshold (currently 1024 tokens), it will be chunked into multiple entries in the database.

**Expected Output:** As the database is constructed, each file that is being encoded will be printed to the console window. If a file's token count is above the threshold of 1024 tokens, that file will be chunked into multiple entries in the database to ensure that each database entry is less than 1024 tokens:

<img src="build-rag-output1.png" style='width: 100%; object-fit: contain; display: block; margin-left: auto; margin-right: auto;' />
<br>

When all processing is finished, the total count of database entries (also called embeddings) will be output to the console window as well as the database's total size on disk (in bytes).

```bash 
Saved 29 embeddings
Saved 39498 bytes of docStore data
Saved 29 embeddings, 118 edges (including 5 KV entries)
```

<img src="build-rag-output2.png" style='width: 100%; object-fit: contain; display: block; margin-left: auto; margin-right: auto;' />
<br>

At this point the database was created successfully and is ready to be used in the RAG feature of the Game Agent SDK. For a semantic database, the output folder should have three files: `data.bin`, `index.bin`, and `graph.bin`.

<img src="semantic-db-output.png" style='width: 100%; object-fit: contain; display: block; margin-left: auto; margin-right: auto;' />
<br>

If a lexical database was created (by specifying `-b` on the BuildRag.exe commandline) then there should only be an `index.bin` file in the output folder:

<img src="lexical-db-output.png" style='width: 100%; object-fit: contain; display: block; margin-left: auto; margin-right: auto;' />
<br>

## Multiple Semantic Database Support
If an Game Agent SDK client wants to load multiple semantic databases that were encoded with the same embedding model, then the embedding model must be loaded twice during initialization (think of there being a 1:1 relationship between a semantic database loaded and an embedding model loaded). This restriction only exists with semantic databases, as a lexical database does not utilize an embedding model to perform lexical searches. See the `Samples` doc for further details on how to load multiple databases.

## Section Based Chunking

In addition to splitting large text files into 1024 token chunks, it is possible to split up a text file into multiple chunks based on certain marker strings that can be found in the input text file. Use the `-s` command line parameter to enable section based chunking.

##PARA, ##ENDPARA are expected for any txt file

Supported tags: ##Heading1, ##Heading2, ##METADATA, ##PARA, ##ENDPARA. Text between ##PARA and ##ENDPARA is considered as the content.
- ##Heading1 (optional): Topic (at the top per txt file)
- ##Heading2 (optional / required for section based chunking): Section (per section in a txt file)
- ##METADATA (optional): Related section(s) to ##Heading2 that creates graph edges
- ##PARA (required): Start of content
- ##ENDPARA (required): End of content

**Example 1** (with graph edge generation)
```
##Heading1: Poker Overview
##Heading2: Poker Introduction (poker_introduction)
##METADATA: Basic Idea (poker_basic_idea), Popular Variants (poker_popular_variants)
##PARA
Poker is a **card game** that combines **strategy, skill, and a bit of luck**, where players compete to win chips or money by forming the best hand or by convincing    others to fold (give up).

---
##ENDPARA

##Heading2: Basic Idea (poker_basic_idea)
##PARA
Basic Idea:
- Players are dealt a set of cards.
- They **bet** based on how good they think their hand is (or how well they can bluff).
- The player with the **best hand** (or the last one left after others fold) **wins the pot** (all the chips/money bet in that round).

---
##ENDPARA

##Heading2: Popular Variants (poker_popular_variants)
##PARA
Popular Variants:
- **Texas Hold'em** (most popular)
- **Omaha**
- **Seven Card Stud**
- **Five Card Draw**

Each has different rules for how cards are dealt and how hands are formed, but the core principles remain the same.

---
##ENDPARA
```

Expected graph edges
- poker_introduction -> poker_basic_idea
- poker_introduction -> poker_popular_variants

When using token count based chunking (default)
- Only the content between ##PARA and ##ENDPARA are honored. 

When using section based chunking (-s flag)
- Three chunks will be generated (poker_introduction, poker_basic_idea, poker_popular_variants)


**Example 2** (if there's no need for graph edge generation nor section based chunking)
```
##PARA
Poker is a **card game** that combines **strategy, skill, and a bit of luck**, where players compete to win chips or money by forming the best hand or by convincing    others to fold (give up).

### Basic Idea:
- Players are dealt a set of cards.
- They **bet** based on how good they think their hand is (or how well they can bluff).
- The player with the **best hand** (or the last one left after others fold) **wins the pot** (all the chips/money bet in that round).

---

### Popular Variants:
- **Texas Hold'em** (most popular)
- **Omaha**
- **Seven Card Stud**
- **Five Card Draw**

Each has different rules for how cards are dealt and how hands are formed, but the core principles remain the same.

---

##ENDPARA
```

## Multilingual Support

The BuildRAG tool can generate semantic databases in languages other than English. To build a semantic database in a language other than English, launch the BuildRAG tool with the `-m` parameter set to an appropriate multilingual embedding model. An example multilingual model is included with the Game Agent SDK package, located at `data/models/multilingual/multilingual-e5-base-Q8_0.gguf`.
