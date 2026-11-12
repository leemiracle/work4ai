---
sidebar_position: 1
title: Chat
---

# Chat

DB-GPT provides multiple chat modes through its Web UI — each tailored for a different use case.

## Chat modes

| Mode | Description | Requirements |
|---|---|---|
| **Chat Normal** | General conversation with the LLM | LLM configured |
| **Chat Data** | Natural language queries on SQL databases (Text2SQL) | Database connected |
| **Chat Excel** | Upload and query Excel/CSV files | LLM configured |
| **Chat Knowledge** | RAG conversations over documents | Knowledge base created |

## Starting a chat

1. Open the Web UI at **[http://localhost:5670](http://localhost:5670)**
2. Click **Chat** in the sidebar
3. Select a chat mode from the dropdown or create a new conversation
4. Type your message and press Enter

:::tip Quick test
Start with **Chat Normal** to verify your LLM is working correctly, then try other modes.
:::

## Chat Normal

The default mode — a direct conversation with the configured LLM.

**Features:**
- Multi-turn conversation with context retention
- Markdown rendering for formatted responses
- Code syntax highlighting
- Streaming responses

## Chat Data (Text2SQL)

Query your connected databases using natural language. DB-GPT converts your question into SQL, executes it, and presents the results.

**How to use:**

1. First, connect a database in the **Database** section of the sidebar
2. Start a new **Chat Data** conversation
3. Select the target database from the dropdown
4. Ask your question in natural language

**Example:**

```
User: Show me the top 10 customers by total order amount
DB-GPT: [generates SQL, executes, and displays results in a table]
```

:::info Supported databases
MySQL, PostgreSQL, SQLite, ClickHouse, DuckDB, MSSQL, Oracle, and more. See [Data Sources](/docs/getting-started/concepts/data-sources) for the full list.
:::

## Chat Excel

Upload an Excel or CSV file and query it with natural language.

**How to use:**

1. Start a new **Chat Excel** conversation
2. Upload your file (`.xlsx`, `.xls`, or `.csv`)
3. Ask questions about the data

**Example:**

```
User: What is the average sales amount per region?
DB-GPT: [analyzes the file and presents results]
```

## Chat Knowledge

Conversational RAG — ask questions and get answers grounded in your uploaded documents.

**How to use:**

1. First, create a knowledge base and upload documents (see [Knowledge Base](/docs/getting-started/web-ui/knowledge-base))
2. Start a new **Chat Knowledge** conversation
3. Select the knowledge base from the dropdown
4. Ask your questions

**Features:**
- Answers cite source documents
- Supports multiple file formats (PDF, Word, Markdown, TXT, etc.)
- Combines vector search with LLM generation

## Conversation management

- **History** — Previous conversations are saved in the sidebar
- **Delete** — Right-click a conversation to delete it
- **Export** — Copy conversation content from the chat window

## Next steps

| Topic | Link |
|---|---|
| Set up knowledge base for Chat Knowledge | [Knowledge Base](/docs/getting-started/web-ui/knowledge-base) |
| Connect databases for Chat Data | [Data Sources](/docs/getting-started/concepts/data-sources) |
| Build custom chat workflows | [AWEL Flow](/docs/getting-started/tools/awel-flow) |
