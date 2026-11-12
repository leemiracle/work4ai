# BeamIbis - Unified Interface for SQL Databases

BeamIbis provides a unified, pandas-like interface for all Ibis clients (BigQuery, SQLite, PostgreSQL, etc.) with lazy execution and pathlib-style navigation. It's designed to follow the same patterns as BeamElastic but adapted for SQL databases.

## Features

### 🚀 **Lazy Execution**
- Queries are built but not executed until explicitly materialized
- Allows for efficient query composition and optimization
- Only executes when calling `as_df()`, `as_dict()`, `count()`, etc.

### 🗂️ **Path-like Interface**
- Navigate databases, tables, and queries like filesystem paths
- Support for different hierarchy levels (root → dataset → table → query)
- Intuitive pathlib-style operations

### 🔗 **Query Composition**
- Combine queries using `&` (AND) and `|` (OR) operators
- Immutable query objects - each operation returns a new instance
- Fluent interface for building complex queries

### 📊 **Multiple Output Formats**
- Pandas DataFrames (`as_df()`)
- Polars DataFrames (`as_pl()`)
- cuDF DataFrames (`as_cudf()`)
- Python dictionaries (`as_dict()`)

### 🔍 **Comprehensive Filtering**
- Term filters (`filter_term`, `filter_terms`)
- Range filters (`filter_gte`, `filter_gt`, `filter_lte`, `filter_lt`)
- Time range filters with smart period parsing
- Fluent `with_filter_*` methods

### 📈 **Aggregations & GroupBy**
- Pandas-like aggregation methods (`sum`, `mean`, `min`, `max`, etc.)
- Comprehensive GroupBy functionality
- Value counts and unique value operations
- Multi-field grouping with multiple aggregations

### 🌐 **Multi-Backend Support**
- SQLite
- BigQuery
- PostgreSQL
- MySQL
- DuckDB
- Any backend supported by Ibis

## Installation

```bash
# Install Ibis with your preferred backend
pip install 'ibis-framework[sqlite]'  # For SQLite
pip install 'ibis-framework[bigquery]'  # For BigQuery
pip install 'ibis-framework[postgres]'  # For PostgreSQL

# For additional output formats
pip install polars  # For Polars support
pip install cudf    # For cuDF support (GPU)
```

## Basic Usage

### Creating BeamIbis Instances

```python
from beam.sql import BeamIbis, beam_ibis

# Method 1: Direct instantiation
db = BeamIbis("/path/to/database.db/table_name", backend='sqlite')

# Method 2: Using URL-like strings
db = beam_ibis("sqlite:///path/to/database.db/table_name")
db = beam_ibis("bigquery://project/dataset/table")
db = beam_ibis("postgresql://user:pass@host:5432/database/table")
```

### Basic Operations

```python
# Check if table exists
print(db.exists())

# Get row count
print(db.count())

# Get schema information
print(db.schema)

# Get first few rows
print(db.head())

# Get table info
print(db.info())
```

## Querying Data

### Column Selection

```python
# Select single column
prices = db['price']

# Select multiple columns
subset = db[['user_id', 'product', 'price']]

# Using select method
subset = db.select('user_id', 'product', 'price')
```

### Filtering

```python
# Simple equality filter
electronics = db.with_filter_term('electronics', 'category')

# Range filters
expensive = db.with_filter_gte(100, 'price')
cheap = db.with_filter_lt(20, 'price')

# Multiple value filter
categories = db.with_filter_terms(['electronics', 'books'], 'category')

# Time range filtering
recent = db.with_filter_time_range(
    field='timestamp',
    start='2024-01-01',
    end='2024-01-31'
)

# Period-based filtering
last_week = db.with_filter_time_range(
    field='timestamp',
    period='7d'  # Last 7 days
)
```

### Query Composition

```python
# Combine filters with AND
expensive_electronics = (db.with_filter_term('electronics', 'category') & 
                        db.with_filter_gte(100, 'price'))

# Combine filters with OR  
high_value = (db.with_filter_gte(100, 'price') | 
              db.with_filter_gte(50, 'quantity'))

# Complex query building
complex_query = (db
                .with_filter_term('electronics', 'category')
                .with_filter_gte(50, 'price')
                .order_by('timestamp')
                .select(['user_id', 'product', 'price']))
```

### Comparison Operators

```python
# When working with single columns
price_col = db['price']
expensive_items = price_col >= 100
cheap_items = price_col < 20
```

## Aggregations

### Basic Aggregations

```python
# Simple aggregations
total_revenue = db.sum('revenue')
avg_price = db.mean('price') 
max_quantity = db.max('quantity')
unique_users = db.nunique('user_id')

# Value counts (pandas-like)
category_counts = db.value_counts('category')
top_products = db.value_counts('product', sort=True)

# Get unique values
unique_categories = db.unique('category')
```

### GroupBy Operations

```python
# Simple groupby
category_stats = db.groupby('category').sum('revenue').mean('price')
results = category_stats.as_df()

# Multiple groupby fields
multi_group = (db.groupby(['category', 'country'])
               .sum('revenue')
               .count()
               .nunique('user_id'))

# Complex aggregations
product_analysis = (db.groupby('product')
                   .sum('revenue')
                   .mean('price')
                   .max('quantity')
                   .nunique('user_id')
                   .first('timestamp')  # First occurrence
                   .last('timestamp'))  # Last occurrence

# Using agg method for multiple aggregations per field
stats = db.groupby('category').agg({
    'revenue': ['sum', 'mean', 'std'],
    'quantity': ['sum', 'max'],
    'user_id': 'nunique'
})
```

## Output Formats

### Pandas DataFrame (Default)

```python
# Execute and get pandas DataFrame
df = db.as_df()
df = db.as_df(limit=1000)  # Limit results

# With additional metadata
df, metadata = db.as_dict(add_metadata=True)
```

### Other Formats

```python
# Polars DataFrame
pl_df = db.as_pl()

# cuDF DataFrame (GPU)
cudf_df = db.as_cudf()

# Python dictionaries
records = db.as_dict()
records = db.as_dict(limit=100)

# Raw SQL query
sql = db.sql()
print(sql)
```

## Advanced Features

### Time Filtering

```python
# Various time period formats
last_day = db.with_filter_time_range(field='timestamp', period='1d')
last_week = db.with_filter_time_range(field='timestamp', period='7d') 
last_month = db.with_filter_time_range(field='timestamp', period='30d')
last_year = db.with_filter_time_range(field='timestamp', period='1y')

# Specific date ranges
date_range = db.with_filter_time_range(
    field='timestamp',
    start='2024-01-01',
    end='2024-01-31'
)

# Relative time references
recent = db.with_filter_time_range(
    field='timestamp',
    start='last_week',
    end='now'
)
```

### Path-like Navigation

```python
# Navigate hierarchy levels
root = BeamIbis("/", backend='sqlite')  # Root level
dataset = BeamIbis("/database.db", backend='sqlite')  # Dataset level  
table = BeamIbis("/database.db/sales", backend='sqlite')  # Table level

# List contents
for table in dataset.iterdir():
    print(f"Table: {table}")
    print(f"Row count: {table.count()}")
```

### LLM Integration

```python
# Ask natural language questions (requires LLM setup)
response = db.ask(
    "What are the top 5 products by revenue?", 
    execute=True,
    answer=True
)

print(response.query)  # Generated SQL
print(response.df)     # Query results
print(response.text_answer)  # Natural language answer
```

### Writing Data

```python
# Write pandas DataFrame to table
import pandas as pd
new_data = pd.DataFrame({...})
db.write(new_data, if_exists='append')

# Create new table
new_table = BeamIbis("/database.db/new_table", backend='sqlite')
new_table.write(new_data, if_exists='replace')
```

## Backend-Specific Examples

### SQLite

```python
from beam.sql import beam_ibis

# Local SQLite file
db = beam_ibis("sqlite:///data/sales.db/transactions")

# In-memory database
db = beam_ibis("sqlite:///:memory:/temp_table")
```

### BigQuery

```python
# BigQuery table
db = beam_ibis("bigquery://my-project/my_dataset/my_table")

# With credentials
db = beam_ibis(
    "bigquery://my-project/my_dataset/my_table",
    backend_kwargs={'credentials_path': '/path/to/credentials.json'}
)
```

### PostgreSQL

```python
# PostgreSQL connection
db = beam_ibis("postgresql://user:password@host:5432/database/table")

# With SSL
db = beam_ibis(
    "postgresql://user:password@host:5432/database/table",
    backend_kwargs={'sslmode': 'require'}
)
```

## Comparison with BeamElastic

| Feature | BeamElastic | BeamIbis |
|---------|-------------|----------|
| **Data Source** | Elasticsearch | SQL Databases (via Ibis) |
| **Query Language** | Elasticsearch DSL / KQL | SQL |
| **Lazy Execution** | ✅ | ✅ |
| **Path Interface** | ✅ | ✅ |
| **Query Composition** | ✅ (`&`, `\|`) | ✅ (`&`, `\|`) |
| **Filtering** | ✅ | ✅ |
| **Aggregations** | ✅ | ✅ |
| **GroupBy** | ✅ | ✅ |
| **Time Filtering** | ✅ | ✅ |
| **Multiple Outputs** | ✅ | ✅ |
| **LLM Integration** | ✅ | ✅ |
| **Backends** | Elasticsearch | SQLite, BigQuery, PostgreSQL, etc. |

## Performance Tips

1. **Use Limits**: Always use `limit` parameter for large datasets during development
2. **Column Selection**: Select only needed columns to reduce data transfer
3. **Filter Early**: Apply filters before aggregations when possible
4. **Backend Optimization**: Each backend has specific optimizations - leverage them
5. **Lazy Evaluation**: Build complex queries before executing for better optimization

## Error Handling

```python
try:
    result = db.with_filter_term('invalid_value', 'category').as_df()
except Exception as e:
    print(f"Query failed: {e}")

# Check existence before operations
if db.exists():
    count = db.count()
else:
    print("Table does not exist")
```

## Best Practices

1. **Use Lazy Evaluation**: Build queries step by step, execute only when needed
2. **Immutable Operations**: Each operation returns a new object, original remains unchanged
3. **Column Selection**: Use `select()` or `[]` to limit columns early in the pipeline
4. **Type Safety**: Check schema before performing operations on fields
5. **Resource Management**: Use context managers for database connections when possible
6. **Error Handling**: Always wrap database operations in try-catch blocks

## Contributing

The BeamIbis implementation follows the same patterns as BeamElastic and integrates seamlessly with the existing Beam ecosystem. Contributions are welcome for:

- Additional backend support
- Enhanced LLM integration
- Performance optimizations
- Additional aggregation functions
- Extended time parsing capabilities

## License

BeamIbis is part of the BeamDS project and follows the same licensing terms. 