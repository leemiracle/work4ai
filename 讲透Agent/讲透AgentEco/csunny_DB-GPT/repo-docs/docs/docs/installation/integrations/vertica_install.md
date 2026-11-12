# Vertica

Vertica is an analytical SQL data warehouse supported by DB-GPT through the native
connector in `dbgpt_ext.datasource.rdbms.conn_vertica`.

### Install Dependencies

Install the Vertica datasource extra.

```bash
uv sync --all-packages \
--extra "base" \
--extra "datasource_vertica" \
--extra "rag" \
--extra "storage_chromadb" \
--extra "dbgpts"
```

### Prepare Vertica

Prepare a Vertica instance and start the DB-GPT webserver:

```bash
uv run dbgpt start webserver --config configs/dbgpt-proxy-openai.toml
```

### Vertica Configuration

Use the datasource UI or configuration fields for:

- host
- port
- user
- password
- database
- driver (`vertica+vertica_python`)

The Vertica connector is implemented in:

- `packages/dbgpt-ext/src/dbgpt_ext/datasource/rdbms/conn_vertica.py`
