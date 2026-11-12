# OceanBase

OceanBase is a distributed SQL database supported by DB-GPT through the native
connector in `dbgpt_ext.datasource.rdbms.conn_oceanbase`.

### Install Dependencies

OceanBase support is built on the OceanBase-compatible MySQL driver path already
used by the connector.

```bash
uv sync --all-packages \
--extra "base" \
--extra "rag" \
--extra "storage_chromadb" \
--extra "dbgpts"
```

### Prepare OceanBase

Prepare an OceanBase instance and start the DB-GPT webserver:

```bash
uv run dbgpt start webserver --config configs/dbgpt-proxy-openai.toml
```

### OceanBase Configuration

Use the datasource UI or configuration fields for:

- host
- port
- user
- password
- database
- driver (`mysql+ob`)

The OceanBase connector is implemented in:

- `packages/dbgpt-ext/src/dbgpt_ext/datasource/rdbms/conn_oceanbase.py`
