"""Agent Tools - Tool Registry and Tool Implementations."""

from typing import Dict, Any, List, Optional, Callable
from abc import ABC, abstractmethod
from datetime import datetime
import asyncio
import subprocess
import json
import os
from .config import AISettings


class Tool(ABC):
    """Base Tool class."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    async def execute(self, parameters: Dict[str, Any]) -> Any:
        """Execute the tool with given parameters."""
        pass

    def describe(self) -> Dict[str, Any]:
        """Describe the tool."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.get_parameters()
        }

    @abstractmethod
    def get_parameters(self) -> Dict[str, Any]:
        """Get parameter schema."""
        pass


class ToolRegistry:
    """Registry for managing available tools."""

    def __init__(self):
        self.tools: Dict[str, Tool] = {}

    def register(self, tool: Tool):
        """Register a tool."""
        self.tools[tool.name] = tool

    def get_tool(self, name: str) -> Optional[Tool]:
        """Get a tool by name."""
        return self.tools.get(name)

    def has_tool(self, name: str) -> bool:
        """Check if tool exists."""
        return name in self.tools

    def list_tools(self, category: Optional[str] = None) -> List[str]:
        """List all tools or tools in a category."""
        if category:
            return [name for name, tool in self.tools.items()
                    if hasattr(tool, 'category') and tool.category == category]
        return list(self.tools.keys())

    def get_all_descriptions(self) -> List[Dict[str, Any]]:
        """Get descriptions of all tools."""
        return [tool.describe() for tool in self.tools.values()]


# ============ Tool Implementations ============

class DatabaseQueryTool(Tool):
    """Tool for querying the database."""

    def __init__(self, db_session_factory):
        super().__init__(
            name="database_query",
            description="Query the database with SQL or ORM queries"
        )
        self.db_session_factory = db_session_factory

    async def execute(self, parameters: Dict[str, Any]) -> Any:
        """Execute database query."""
        query = parameters.get("query")
        query_type = parameters.get("type", "sql")  # 'sql' or 'orm'

        if not query:
            raise ValueError("Query is required")

        db = self.db_session_factory()

        try:
            if query_type == "sql":
                # Execute raw SQL
                result = db.execute(query)
                columns = result.keys()
                rows = result.fetchall()
                return {
                    "columns": list(columns),
                    "rows": [dict(row) for row in rows]
                }
            else:
                # ORM query (simplified)
                # In practice, you'd have more sophisticated ORM support
                return {"error": "ORM queries not yet implemented"}

        finally:
            db.close()

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "query": {
                "type": "string",
                "description": "SQL query to execute"
            },
            "type": {
                "type": "string",
                "enum": ["sql", "orm"],
                "description": "Query type"
            }
        }


class APICallTool(Tool):
    """Tool for making HTTP API calls."""

    async def execute(self, parameters: Dict[str, Any]) -> Any:
        """Execute HTTP API call."""
        import httpx

        url = parameters.get("url")
        method = parameters.get("method", "GET").upper()
        headers = parameters.get("headers", {})
        body = parameters.get("body", None)
        timeout = parameters.get("timeout", 30)

        if not url:
            raise ValueError("URL is required")

        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.request(
                method=method,
                url=url,
                headers=headers,
                json=body if method in ["POST", "PUT", "PATCH"] else None
            )

        return {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "body": response.text
        }

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "url": {
                "type": "string",
                "description": "API endpoint URL"
            },
            "method": {
                "type": "string",
                "enum": ["GET", "POST", "PUT", "DELETE", "PATCH"],
                "description": "HTTP method"
            },
            "headers": {
                "type": "object",
                "description": "HTTP headers"
            },
            "body": {
                "type": "object",
                "description": "Request body for POST/PUT/PATCH"
            },
            "timeout": {
                "type": "number",
                "description": "Request timeout in seconds"
            }
        }


class FileReadTool(Tool):
    """Tool for reading files."""

    async def execute(self, parameters: Dict[str, Any]) -> str:
        """Read file content."""
        file_path = parameters.get("file_path")

        if not file_path:
            raise ValueError("file_path is required")

        # Security: prevent directory traversal
        if ".." in file_path or file_path.startswith("/"):
            raise ValueError("Invalid file path")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            return {
                "content": content,
                "file_path": file_path,
                "size": len(content)
            }
        except FileNotFoundError:
            return {"error": "File not found"}
        except Exception as e:
            return {"error": str(e)}

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "file_path": {
                "type": "string",
                "description": "Path to the file to read"
            }
        }


class FileWriteTool(Tool):
    """Tool for writing files."""

    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Write content to file."""
        file_path = parameters.get("file_path")
        content = parameters.get("content")

        if not file_path or content is None:
            raise ValueError("file_path and content are required")

        # Security: prevent directory traversal
        if ".." in file_path or file_path.startswith("/"):
            raise ValueError("Invalid file path")

        try:
            # Create directory if it doesn't exist
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            return {
                "success": True,
                "file_path": file_path,
                "size": len(content)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "file_path": {
                "type": "string",
                "description": "Path to the file to write"
            },
            "content": {
                "type": "string",
                "description": "Content to write to the file"
            }
        }


class CodeExecutionTool(Tool):
    """Tool for executing code."""

    async def execute(self, parameters: Dict[str, Any]) -> Any:
        """Execute code and return result."""
        language = parameters.get("language", "python")
        code = parameters.get("code")
        timeout = parameters.get("timeout", 30)

        if not code:
            raise ValueError("Code is required")

        try:
            if language.lower() == "python":
                return await self._execute_python(code, timeout)
            elif language.lower() == "javascript":
                return await self._execute_javascript(code, timeout)
            else:
                return {"error": f"Language {language} not supported"}
        except Exception as e:
            return {"error": str(e)}

    async def _execute_python(self, code: str, timeout: int) -> Dict[str, Any]:
        """Execute Python code safely."""
        # Note: In production, use a sandboxed environment
        try:
            exec_globals = {
                "__builtins__": {
                    "print": print,
                    "len": len,
                    "range": range,
                    "list": list,
                    "dict": dict,
                    "str": str,
                    "int": int,
                    "float": float,
                }
            }

            exec_locals = {"output": None}

            # Capture output
            exec(f"output = {code}", exec_globals, exec_locals)

            return {
                "success": True,
                "output": exec_locals.get("output"),
                "language": "python"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "language": "python"
            }

    async def _execute_javascript(self, code: str, timeout: int) -> Dict[str, Any]:
        """Execute JavaScript code using Node.js."""
        try:
            process = await asyncio.create_subprocess_exec(
                "node", "-e", code,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )

            return {
                "success": True,
                "stdout": stdout.decode(),
                "stderr": stderr.decode(),
                "language": "javascript"
            }
        except asyncio.TimeoutError:
            process.kill()
            return {
                "success": False,
                "error": "Execution timeout",
                "language": "javascript"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "language": "javascript"
            }

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "language": {
                "type": "string",
                "enum": ["python", "javascript"],
                "description": "Programming language"
            },
            "code": {
                "type": "string",
                "description": "Code to execute"
            },
            "timeout": {
                "type": "number",
                "description": "Execution timeout in seconds"
            }
        }


class VectorSearchTool(Tool):
    """Tool for semantic search."""

    def __init__(self, vector_store):
        super().__init__(
            name="vector_search",
            description="Perform semantic search in vector database"
        )
        self.vector_store = vector_store

    async def execute(self, parameters: Dict[str, Any]) -> Any:
        """Perform vector search."""
        query = parameters.get("query")
        collection_name = parameters.get("collection_name", "notes")
        n_results = parameters.get("n_results", 5)

        if not query:
            raise ValueError("Query is required")

        results = await self.vector_store.search(
            collection_name=collection_name,
            query=query,
            n_results=n_results
        )

        return {
            "query": query,
            "results": results,
            "count": len(results.get("ids", [[]])[0]) if results else 0
        }

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "query": {
                "type": "string",
                "description": "Search query"
            },
            "collection_name": {
                "type": "string",
                "description": "Name of the collection to search"
            },
            "n_results": {
                "type": "number",
                "description": "Number of results to return"
            }
        }


class LLMTool(Tool):
    """Tool for calling LLM."""

    def __init__(self, llm_service):
        super().__init__(
            name="llm_chat",
            description="Call LLM for text generation"
        )
        self.llm_service = llm_service

    async def execute(self, parameters: Dict[str, Any]) -> str:
        """Call LLM."""
        messages = parameters.get("messages", [])
        model = parameters.get("model")
        temperature = parameters.get("temperature")
        max_tokens = parameters.get("max_tokens")

        if not messages:
            raise ValueError("Messages are required")

        response = await self.llm_service.chat(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )

        return {
            "response": response,
            "model": model,
            "tokens_used": self.llm_service.estimate_tokens(response)
        }

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "messages": {
                "type": "array",
                "description": "Array of message objects"
            },
            "model": {
                "type": "string",
                "description": "Model to use"
            },
            "temperature": {
                "type": "number",
                "description": "Sampling temperature"
            },
            "max_tokens": {
                "type": "number",
                "description": "Maximum tokens to generate"
            }
        }


class MemoryStoreTool(Tool):
    """Tool for storing memories."""

    def __init__(self, memory_system):
        super().__init__(
            name="memory_store",
            description="Store information in agent memory"
        )
        self.memory = memory_system

    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Store memory."""
        key = parameters.get("key")
        value = parameters.get("value")
        memory_type = parameters.get("memory_type", "long_term")

        if not key or value is None:
            raise ValueError("key and value are required")

        await self.memory.store(
            key=key,
            value=value,
            memory_type=memory_type
        )

        return {
            "success": True,
            "key": key,
            "memory_type": memory_type
        }

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "key": {
                "type": "string",
                "description": "Memory key"
            },
            "value": {
                "type": "any",
                "description": "Value to store"
            },
            "memory_type": {
                "type": "string",
                "enum": ["short_term", "long_term", "episodic"],
                "description": "Type of memory"
            }
        }


class MemoryRetrieveTool(Tool):
    """Tool for retrieving memories."""

    def __init__(self, memory_system):
        super().__init__(
            name="memory_retrieve",
            description="Retrieve information from agent memory"
        )
        self.memory = memory_system

    async def execute(self, parameters: Dict[str, Any]) -> Any:
        """Retrieve memory."""
        key = parameters.get("key")
        query = parameters.get("query")
        memory_type = parameters.get("memory_type", "long_term")

        if key:
            # Retrieve by key
            value = await self.memory.retrieve(key)
            return {"key": key, "value": value}
        elif query:
            # Semantic search
            results = await self.memory.search(query, memory_type)
            return {"query": query, "results": results}
        else:
            raise ValueError("Either key or query is required")

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "key": {
                "type": "string",
                "description": "Exact memory key to retrieve"
            },
            "query": {
                "type": "string",
                "description": "Query for semantic search"
            },
            "memory_type": {
                "type": "string",
                "enum": ["short_term", "long_term", "episodic"],
                "description": "Type of memory"
            }
        }


class TimeTool(Tool):
    """Tool for time-related operations."""

    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute time operation."""
        operation = parameters.get("operation")

        if operation == "current":
            return {
                "current_time": datetime.utcnow().isoformat(),
                "timestamp": datetime.utcnow().timestamp()
            }
        elif operation == "parse":
            date_str = parameters.get("date_string")
            try:
                dt = datetime.fromisoformat(date_str)
                return {
                    "parsed_time": dt.isoformat(),
                    "timestamp": dt.timestamp()
                }
            except ValueError:
                return {"error": "Invalid date string"}
        else:
            return {"error": f"Unknown operation: {operation}"}

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "operation": {
                "type": "string",
                "enum": ["current", "parse"],
                "description": "Time operation to perform"
            },
            "date_string": {
                "type": "string",
                "description": "Date string to parse (for 'parse' operation)"
            }
        }


def create_default_tool_registry(db_session_factory, vector_store, memory_system, llm_service):
    """Create a tool registry with default tools."""

    registry = ToolRegistry()

    # Register tools
    registry.register(DatabaseQueryTool(db_session_factory))
    registry.register(APICallTool())
    registry.register(FileReadTool())
    registry.register(FileWriteTool())
    registry.register(CodeExecutionTool())
    registry.register(VectorSearchTool(vector_store))
    registry.register(LLMTool(llm_service))
    registry.register(MemoryStoreTool(memory_system))
    registry.register(MemoryRetrieveTool(memory_system))
    registry.register(TimeTool())

    return registry
