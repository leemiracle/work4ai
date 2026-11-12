<!--
SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
SPDX-License-Identifier: Apache-2.0

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
-->

# Configuration Files

The federation configuration file is the central artifact for federation code. It defines:

- The federation API (available operations)
- Mapping of operations to runtime components (adapters)
- The distributed architecture of the federation

The configuration system is inspired by OpenAPI and uses JSON Schema for type definitions and references.

:::{note}
Configuration files must use the `.dfm.yaml` extension to be recognized by the system.
:::

## Basic Structure

A DFM configuration file is a YAML file that follows the `FederationObject` model. The root object must include these required fields:

```yaml
dfm: "1.0.0"  # Version of the DFM configuration format
info:
  api-version: "2.1.0"  # Version of your API
  code-package: "my_package"  # Python package name for generated code
  description: "Optional description of your federation"
```

## Reference System

The configuration system supports two reference types (both use JSON Pointers to specify locations):

- **Single Object Reference** — references a single object used as the value
- **Dictionary Merge Reference** — references a dictionary whose contents are merged into the current dictionary

### JSON Pointers

JSON pointers are used to reference specific parts of a JSON/YAML document. They start with `#` and use `/` to navigate through the document structure. Here are examples of different pointer types:

```yaml
# Local pointer (within the same file)
$ref: "#/operations/users.GreetMe"  # Points to the 'GreetMe' operation in the current file

# File pointer (points to a specific path in another file)
$ref: "operations.yaml#/operations/users.GreetMe"  # Points to the 'GreetMe' operation in operations.yaml

# URL pointer (points to a specific path in a remote file)
$ref: "https://example.com/api/operations.yaml#/operations/users.GreetMe"  # Points to the 'GreetMe' operation in a remote file
```

The pointer syntax follows these rules:
- `#` indicates the start of a pointer
- `/` separates path segments
- Each segment after `/` represents a key in the JSON/YAML structure
- The pointer can traverse nested objects and arrays

For example, in this YAML:
```yaml
operations:
  users.GreetMe:
    parameters:
      name:
        type: string
```

The pointer `#/operations/users.GreetMe/parameters/name/type` would point to the value `"string"`.

### Single Object Reference

Use this to reference a single object from another file. Specify the reference with a `$ref` key:

```yaml
# Reference a single operation
operations:
  users.GreetMe:
    $ref: "operations.yaml#/operations/users.GreetMe"

# Reference a single schema
schemas:
  user:
    $ref: "schemas.yaml#/schemas/user"
```

### Dictionary Merge Reference

Use this to merge all entries from a dictionary in another file. Specify a `$ref` key in the dictionary:

```yaml
# Merge all operations from operations.yaml and other_operations.yaml
operations:
  $ref: 
    - "operations.yaml#/operations"
    - "other_operations.yaml#/operations"

# Merge all schemas from schemas.yaml
schemas:
  $ref:
    - "schemas.yaml#/schemas"
```

## API Configuration

The API Configuration defines the public interface of your federation in terms of operations and their parameters. This is the contract that sites can implement.

### Schemas

Schemas define the data structures used in your federation. They use JSON Schema format:

```yaml
schemas:
  user:
    type: object
    properties:
      name:
        type: string
      age:
        type: integer
```

### Operations

Operations define the available operations in your federation. Each operation must specify its parameters and return type:

```yaml
operations:
  users.GreetMe:
    type: object
    description: "Greets a user with a customizable message"  # Optional description of the operation
    parameters:
      name:
        type: string
        description: "Name to greet"
        accepts-literal-input: true    # Default: true. Adds the specified json schema as an option
        accepts-node-input: true       # Default: true. Adds the NodeParam as a type option
        accepts-place-input: true      # Default: true. Adds the PlaceParam as a type option
        discoverable: true             # Default: true. If true, adds Advise as a type option
      greeting:
        $ref: "#/schemas/greeting"     # Reference to a schema defined in the schemas section
        description: "Greeting message"
        accepts-literal-input: true
        accepts-node-input: false      # This parameter doesn't accept node input
        accepts-place-input: true
        discoverable: true
      custom_datatype:
        type: some.package.MyPydanticModel           # Can be used to accept custom Pydantic models
        description: "Custom Pydantic model"
        accepts-literal-input: true
        accepts-node-input: true
        accepts-place-input: true
        discoverable: true
    returns: "string"
```

Each parameter can be configured with the following options:
- `description`: A description of the parameter
- `type`: Can be either a JSON Schema type ("string", "number", "integer", "boolean", "array", "object", "null") or the fully qualified class name of a custom Pydantic model (must contain at least one `.`) for accepting any Python Pydantic model. If non-pydantic Python objects need to be passed, they need to be wrapped inside a `dfm.api.PickledObject`, which is a Pydantic model (that is, you'd declare `type: dfm.api.PickledObject` and wrap your non-pydantic object at runtime)
- `$ref`: If `$ref` references a schema defined in the schemas section, this exact schema will be used. If the reference does not point to a model in the schemas section, the JSON object to which `$ref` points to will be inlined in-place (possibly duplicating the type)
- `accepts-literal-input`: Whether the parameter accepts direct values (default: true)
- `accepts-node-input`: Whether the parameter accepts node references (default: true)
- `accepts-place-input`: Whether the parameter accepts place references (default: true)
- `discoverable`: Whether the parameter can be discovered and advised (default: true)

## Site Configuration

Site configuration defines how a site implements the public API. It specifies:

- Which operations the site offers (through site and provider interfaces)
- How each operation is implemented (through adapters)
- The source of values for each adapter parameter

### Sites

Sites represent different locations or services in your federation. They can have their own interface and providers:

```yaml
sites:
  central:
    info:
      description: "Central site"
    interface:
      "#/operations/users.GreetMe":
        adapter: "my_package.adapters.GreetAdapter"
        description: "Greeting adapter for central site"
        returns: "string"
        args:
          name:
            from-param: "name"
          greeting:
            const: "Hello"
```

### Providers

Providers group together related interface operations that share common functionality or implementation details. They help organize and manage sets of operations that work together:

```yaml
sites:
  central:
    providers:
      greeter:
        info:
          description: "Provider for greeting-related operations"
        interface:
          "#/operations/users.GreetMe":
            adapter: "my_package.adapters.GreetProviderAdapter"
            description: "Provider adapter for greeting"
            returns: "string"
            args:
              name:
                from-param: "name"
              greeting:
                from-provider: "greeter.default_greeting"
          "#/operations/users.Farewell":
            adapter: "my_package.adapters.FarewellProviderAdapter"
            description: "Provider adapter for farewell"
            returns: "string"
            args:
              name:
                from-param: "name"
              message:
                from-provider: "greeter.default_farewell"
```

In this example, the `greeter` provider groups greeting-related operations (`GreetMe` and `Farewell`) that share common configuration. This keeps related operations together and lets them share settings and resources.

## Adapter Arguments

Adapters receive arguments in two ways:

- **Direct Operation Parameters** — set `args: "from-operation"` to pass all operation parameters directly to the adapter
- **Custom Argument Mapping** — define a dictionary that maps adapter parameters to their sources

### Direct Operation Parameters

When using `from-operation`, all operation parameters are passed directly to the adapter:

```yaml
adapter: "my_package.adapters.SimpleAdapter"
args: "from-operation"  # All operation parameters are passed directly to the adapter
```

### Custom Argument Mapping

With a dictionary, map adapter arguments to these sources:

- **Operation Parameters** — `from-param` references a parameter from the operation
- **Secrets** — `from-secrets` references a value from the secrets vault
- **Constants** — `const` specifies a constant value
- **Provider Properties** — `from-provider` references a property from a provider
- **Site Properties** — `from-site` references a property from a site

Example:

```yaml
adapter: "my_package.adapters.ComplexAdapter"
args:
  name:
    from-param: "name"
  api_key:
    from-secrets: "api_key"
  greeting:
    const: "Hello"
  base_url:
    from-provider: "api.base_url"
  site_id:
    from-site: "site_id"
```

## Field Exposure

Adapter arguments (except those using `from-param`) can be exposed in the site's public API using `expose-as`. This makes the adapter parameter available as a public API parameter:

```yaml
args:
  api_key:
    from-secrets: "api_key"
    expose-as: "api_key"  # Makes this parameter available in the site's public API
  greeting:
    const: "Hello"
    expose-as: "greeting"  # Makes this parameter available in the site's public API
  base_url:
    from-provider: "api.base_url"
    expose-as: "base_url"  # Makes this parameter available in the site's public API
  site_id:
    from-site: "site_id"
    expose-as: "site_id"  # Makes this parameter available in the site's public API
```

In this example, all adapter arguments (except `from-param`) are exposed. Site users can provide values for these parameters while sensitive data (like API keys) remains secure.