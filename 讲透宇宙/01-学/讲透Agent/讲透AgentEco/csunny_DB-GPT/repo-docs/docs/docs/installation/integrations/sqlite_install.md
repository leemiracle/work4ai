# SQLite

SQLite is a lightweight embedded relational database. DB-GPT includes a native
SQLite connector in `dbgpt_ext.datasource.rdbms.conn_sqlite`.

### Install Dependencies

SQLite support is available in the base installation and does not require an
additional datasource extra.

```bash
uv sync --all-packages \
--extra "base" \
--extra "rag" \
--extra "storage_chromadb" \
--extra "dbgpts"
```

### Prepare SQLite

Prepare a SQLite database file path such as `./data/demo.db`, then start the server:

```bash
uv run dbgpt start webserver --config configs/dbgpt-proxy-openai.toml
```

### SQLite Configuration

Use the datasource UI or configuration fields for:

- path
- check_same_thread
- driver (`sqlite`)

The SQLite connector is implemented in:

- `packages/dbgpt-ext/src/dbgpt_ext/datasource/rdbms/conn_sqlite.py`
