# StarRocks

StarRocks is a high-performance analytical database supported by DB-GPT through
the native connector in `dbgpt_ext.datasource.rdbms.conn_starrocks`.

### Install Dependencies

Install the base dependency set and the StarRocks SQLAlchemy driver required by
your environment.

```bash
uv sync --all-packages \
--extra "base" \
--extra "rag" \
--extra "storage_chromadb" \
--extra "dbgpts"
```

### Prepare StarRocks

Prepare a StarRocks instance and start the DB-GPT webserver:

```bash
uv run dbgpt start webserver --config configs/dbgpt-proxy-openai.toml
```

### StarRocks Configuration

Use the datasource UI or configuration fields for:

- host
- port
- user
- password
- database
- driver (`starrocks`)

The StarRocks connector is implemented in:

- `packages/dbgpt-ext/src/dbgpt_ext/datasource/rdbms/conn_starrocks.py`
