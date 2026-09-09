> 来源: [https://deepwiki.com/deepseek-ai/smallpond/2-core-api](https://deepwiki.com/deepseek-ai/smallpond/2-core-api)
> DeepWiki deepseek-ai/smallpond

# Core API

  Relevant source files 
 - [README.md](https://github.com/deepseek-ai/smallpond/blob/52ecc5e4/README.md?plain=1)
 - [examples/sort_mock_urls_v2.py](https://github.com/deepseek-ai/smallpond/blob/52ecc5e4/examples/sort_mock_urls_v2.py)
 
  The Core API of smallpond provides the primary interfaces that applications use to interact with the framework. It serves as the foundation for data processing operations, enabling users to efficiently work with large-scale datasets without dealing with the complexities of the underlying systems. For detailed information about the implementation of the logical plan system that powers these operations, see [Logical Plan System](https://deepwiki.com/deepseek-ai/smallpond/3-logical-plan-system).

 
## Overview of the Core API

 The smallpond Core API is designed as a layered architecture that provides both high-level, user-friendly interfaces and lower-level components for advanced use cases. It abstracts the complexity of distributed data processing while leveraging the performance capabilities of DuckDB and 3FS.

 
```

```

 Sources: [README.md8-48](https://github.com/deepseek-ai/smallpond/blob/52ecc5e4/README.md?plain=1#L8-L48) [examples/sort_mock_urls_v2.py4-20](https://github.com/deepseek-ai/smallpond/blob/52ecc5e4/examples/sort_mock_urls_v2.py#L4-L20)

 
## Key Components

 
### Session

 The Session is the primary entry point to the smallpond framework. It provides methods for initializing the framework, reading data from various sources, and executing SQL operations.

 
```

```

 Key Session API methods:

 
 - `smallpond.init()`: Initializes a new smallpond session
 - `read_parquet()`: Reads Parquet files into a DataFrame
 - `read_csv()`: Reads CSV files into a DataFrame
 - `partial_sql()`: Executes SQL queries on DataFrames
 
 Sources: [README.md32-42](https://github.com/deepseek-ai/smallpond/blob/52ecc5e4/README.md?plain=1#L32-L42) [examples/sort_mock_urls_v2.py8-9](https://github.com/deepseek-ai/smallpond/blob/52ecc5e4/examples/sort_mock_urls_v2.py#L8-L9) [examples/sort_mock_urls_v2.py29-30](https://github.com/deepseek-ai/smallpond/blob/52ecc5e4/examples/sort_mock_urls_v2.py#L29-L30)

 
### DataFrame

 The DataFrame is the core data abstraction in smallpond, representing a distributed collection of data that can be transformed through various operations.

 
| Operation | Description | Example Usage |
|---|---|---|
| repartition() | Redistributes data into specified number of partitions | df.repartition(3, hash_by="ticker") |
| map() | Applies transformations using SQL expressions | df.map("column1 + column2 as sum") |
| partial_sort() | Sorts data within partitions | df.partial_sort(by=["column1", "column2"]) |
| write_parquet() | Writes DataFrame to Parquet files | df.write_parquet("output/") |
| to_pandas() | Converts DataFrame to pandas DataFrame | df.to_pandas() |

 Sources: [README.md41-47](https://github.com/deepseek-ai/smallpond/blob/52ecc5e4/README.md?plain=1#L41-L47) [examples/sort_mock_urls_v2.py9-19](https://github.com/deepseek-ai/smallpond/blob/52ecc5e4/examples/sort_mock_urls_v2.py#L9-L19)

 
## Data Processing Flow

 The following diagram illustrates the typical flow of data through the smallpond Core API:

 
```

```

 Sources: [README.md32-47](https://github.com/deepseek-ai/smallpond/blob/52ecc5e4/README.md?plain=1#L32-L47) [examples/sort_mock_urls_v2.py8-19](https://github.com/deepseek-ai/smallpond/blob/52ecc5e4/examples/sort_mock_urls_v2.py#L8-L19)

 
## SQL Integration

 A key strength of smallpond is its integration with SQL through the DuckDB engine. This allows users to leverage SQL's power for data transformations while maintaining the distributed processing capabilities of the framework.

 SQL operations can be performed in two primary ways:

 
 - Using `partial_sql()` from the Session object to execute SQL on DataFrames
 - Using `map()` on DataFrames to apply SQL expressions for transformations
 
 
```

```

 Examples of SQL usage:

 
 - Using `partial_sql()`:

 
```
df = sp.partial_sql("SELECT ticker, min(price), max(price) FROM {0} GROUP BY ticker", df)
```
 - Using `map()`:

 
```
urls = dataset.map("""
    split_part(urlstr, '/', 1) as host,
    split_part(urlstr, ' ', 1) as url,
    from_base64(valstr) AS payload
""")
```
 
 Sources: [README.md42](https://github.com/deepseek-ai/smallpond/blob/52ecc5e4/README.md?plain=1#L42-L42) [examples/sort_mock_urls_v2.py10-16](https://github.com/deepseek-ai/smallpond/blob/52ecc5e4/examples/sort_mock_urls_v2.py#L10-L16)

 
## Relationship with Logical Plan System

 The Core API provides a high-level interface that abstracts the underlying Logical Plan system. Every operation performed through the Core API is translated into a logical plan that is then executed by the framework.

 
```

```

 For more details on the Logical Plan system, see [Logical Plan System](https://deepwiki.com/deepseek-ai/smallpond/3-logical-plan-system).

 Sources: [README.md32-47](https://github.com/deepseek-ai/smallpond/blob/52ecc5e4/README.md?plain=1#L32-L47)

 
## Common Usage Patterns

 The Core API is designed to support common data processing patterns in a clean, intuitive way. Here are the most common usage patterns:

 
 - **Basic workflow**: Initialize, read, transform, write

 
```

```
 - **Partitioning and transformation**:

 
```

```
 - **SQL-based analytics**:

 
```

```
 - **Distributed sorting**:

 
```

```
 
 Sources: [README.md32-47](https://github.com/deepseek-ai/smallpond/blob/52ecc5e4/README.md?plain=1#L32-L47) [examples/sort_mock_urls_v2.py8-19](https://github.com/deepseek-ai/smallpond/blob/52ecc5e4/examples/sort_mock_urls_v2.py#L8-L19)

 
## Summary

 The Core API of smallpond provides a user-friendly interface for distributed data processing, built on top of the more advanced Logical Plan system. Through the Session and DataFrame interfaces, users can perform complex data operations with simple, intuitive syntax while leveraging the performance benefits of DuckDB and 3FS.

 Key components include:

 
 - Session: Primary entry point and factory for DataFrames
 - DataFrame: Core data abstraction with transformation operations
 - SQL Integration: Powerful SQL capabilities through DuckDB
 
 For more specific information about each component, refer to:

 
 - [Session API](https://deepwiki.com/deepseek-ai/smallpond/2.1-session-api)
 - [DataFrame Operations](https://deepwiki.com/deepseek-ai/smallpond/2.2-dataframe-operations)
 - [SQL Integration](https://deepwiki.com/deepseek-ai/smallpond/2.3-sql-integration)
 
 Sources: [README.md8-15](https://github.com/deepseek-ai/smallpond/blob/52ecc5e4/README.md?plain=1#L8-L15)
