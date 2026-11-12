# MySQL

MySQL is a widely used open-source relational database system. DB-GPT includes a
native MySQL datasource connector in `dbgpt_ext.datasource.rdbms.conn_mysql`.

### Install Dependencies

First, install the MySQL datasource dependency set.

```bash
uv sync --all-packages \
--extra "base" \
--extra "datasource_mysql" \
--extra "rag" \
--extra "storage_chromadb" \
--extra "dbgpts"
```

### Prepare MySQL

Prepare a MySQL service and database, then start the DB-GPT webserver:

```bash
uv run dbgpt start webserver --config configs/dbgpt-proxy-openai.toml
```

Optionally:

```bash
uv run python packages/dbgpt-app/src/dbgpt_app/dbgpt_server.py --config configs/dbgpt-proxy-openai.toml
```

### MySQL Configuration

Use the datasource UI or configuration fields for:

- host
- port
- user
- password
- database
- driver (`mysql+pymysql`)

The MySQL connector is implemented in:

- `packages/dbgpt-ext/src/dbgpt_ext/datasource/rdbms/conn_mysql.py`
