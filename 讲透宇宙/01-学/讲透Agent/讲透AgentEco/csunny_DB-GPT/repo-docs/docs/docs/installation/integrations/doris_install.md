# Apache Doris

Apache Doris is a real-time analytical data warehouse supported by DB-GPT through
the native connector in `dbgpt_ext.datasource.rdbms.conn_doris`.

### Install Dependencies

Doris uses the MySQL-compatible driver path.

```bash
uv sync --all-packages \
--extra "base" \
--extra "datasource_mysql" \
--extra "rag" \
--extra "storage_chromadb" \
--extra "dbgpts"
```

### Prepare Apache Doris

Prepare a Doris instance and start the DB-GPT webserver:

```bash
uv run dbgpt start webserver --config configs/dbgpt-proxy-openai.toml
```

### Apache Doris Configuration

Use the datasource UI or configuration fields for:

- host
- port
- user
- password
- database
- driver (`mysql+pymysql`)

The Doris connector is implemented in:

- `packages/dbgpt-ext/src/dbgpt_ext/datasource/rdbms/conn_doris.py`
