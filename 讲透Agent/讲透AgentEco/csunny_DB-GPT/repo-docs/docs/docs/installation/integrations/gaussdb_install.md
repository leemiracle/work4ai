# GaussDB

GaussDB is an enterprise-grade relational database supported by DB-GPT through the
native connector in `dbgpt_ext.datasource.rdbms.conn_gaussdb`.

### Install Dependencies

GaussDB uses the PostgreSQL-compatible driver path.

```bash
uv sync --all-packages \
--extra "base" \
--extra "datasource_postgres" \
--extra "rag" \
--extra "storage_chromadb" \
--extra "dbgpts"
```

### Prepare GaussDB

Prepare a GaussDB instance and start the DB-GPT webserver:

```bash
uv run dbgpt start webserver --config configs/dbgpt-proxy-openai.toml
```

### GaussDB Configuration

Use the datasource UI or configuration fields for:

- host
- port
- user
- password
- database
- schema
- driver (`postgresql+psycopg2`)

The GaussDB connector is implemented in:

- `packages/dbgpt-ext/src/dbgpt_ext/datasource/rdbms/conn_gaussdb.py`
