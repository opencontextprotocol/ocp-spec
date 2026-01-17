---
title: Tool Schema
weight: 2
prev: /specs/context-schema/
next: /specs/openapi-extensions-schema/
cascade:
  type: docs
---

Schema for tools generated from OpenAPI specifications.

**JSON Schema**: [`/schemas/ocp-tool.json`](https://github.com/opencontextprotocol/ocp-spec/blob/main/schemas/ocp-tool.json)

## Properties

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `description` | string | Yes | Human-readable description from OpenAPI operation summary/description |
| `method` | [string](#method) | Yes | HTTP method for this operation |
| `name` | [string](#name) | Yes | Deterministic camelCase tool name generated from operationId or method+path |
| `parameters` | [object](#parameters) | Yes | Parameter definitions extracted from OpenAPI specification |
| `path` | [string](#path) | Yes | API endpoint path template with {parameter} placeholders |
| `response_schema` | [object](#response_schema) | Yes | OpenAPI response schema for successful responses (2xx status codes) |
| `deprecated` | [boolean](#deprecated) | No | Whether this operation is marked as deprecated in OpenAPI |
| `operation_id` | string? | No | Original OpenAPI operationId if present |
| `security` | array | No | Security requirements from OpenAPI specification |
| `servers` | [array](#servers) | No | Server information from OpenAPI specification |
| `tags` | array? | No | OpenAPI tags for categorizing and organizing tools |


### `name`

**Type:** string

Deterministic camelCase tool name generated from operationId or method+path

**Pattern:** `^[a-z][a-zA-Z0-9]*$`


### `method`

**Type:** string

HTTP method for this operation

**Allowed values:**

- `GET`
- `POST`
- `PUT`
- `PATCH`
- `DELETE`
- `HEAD`
- `OPTIONS`


### `path`

**Type:** string

API endpoint path template with {parameter} placeholders

**Pattern:** `^/`


### `parameters`

**Type:** object

Parameter definitions extracted from OpenAPI specification


### `parameters.parameters_pattern`

**Type:** object (dynamic properties)

**Pattern:** Properties matching `^[a-zA-Z][a-zA-Z0-9_]*$`

Each property matching this pattern must be an object with:

#### Properties

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `location` | [string](#location) | Yes | Where this parameter should be placed in the HTTP request |
| `required` | boolean | Yes | Whether this parameter is required |
| `type` | [string](#type) | Yes | Parameter data type |
| `default` | any | No | Default value for optional parameters |
| `description` | [string](#description) | No | Human-readable parameter description |
| `enum` | array | No | Allowed values for enumerated parameters |
| `format` | string | No | OpenAPI format specifier (e.g., 'date-time', 'email') |
| `items` | object | No | Schema for array items when type is 'array' |
| `maximum` | number | No | Maximum value for numeric parameters |
| `maxLength` | integer | No | Maximum length for string parameters |
| `minimum` | number | No | Minimum value for numeric parameters |
| `minLength` | integer | No | Minimum length for string parameters |
| `pattern` | string | No | Regular expression pattern for string validation |
| `properties` | object | No | Property schemas when type is 'object' |
| `schema` | object | No | Full OpenAPI schema definition for this parameter |


### `parameters.parameters_pattern.type`

**Type:** string

Parameter data type

**Allowed values:**

- `string`
- `number`
- `integer`
- `boolean`
- `array`
- `object`


### `parameters.parameters_pattern.location`

**Type:** string

Where this parameter should be placed in the HTTP request

**Allowed values:**

- `path`
- `query`
- `header`
- `body`


### `parameters.parameters_pattern.description`

**Type:** string

Human-readable parameter description

**Default:** `""`


### `response_schema`

**Type:** object

OpenAPI response schema for successful responses (2xx status codes)

#### Properties

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `items` | object | No | Array item schema definition |
| `properties` | object | No | Object property definitions |
| `type` | string | No | Response data type |


### `servers`

**Type:** array

Server information from OpenAPI specification

**Array items:** object

**Item Properties:**

#### Properties

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `url` | [string](#url) | Yes | Base URL for this server |
| `description` | string | No | Human-readable description of this server |


### `servers.url`

**Type:** string

Base URL for this server

**Format:** uri


### `deprecated`

**Type:** boolean

Whether this operation is marked as deprecated in OpenAPI

**Default:** `false`

