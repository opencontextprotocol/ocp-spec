---
title: Context Schema
weight: 1
prev: /docs/specs/
next: /docs/specs/tool-schema/
cascade:
  type: docs
---

Schema for OCP context objects carried in the OCP-Session header.

**JSON Schema**: [`/schemas/ocp-context.json`](https://github.com/opencontextprotocol/ocp-spec/blob/main/schemas/ocp-context.json)

## Properties

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `agent_type` | string | Yes | Type of agent creating this context |
| `context_id` | [string](#context_id) | Yes | Unique identifier for this context |
| `created_at` | [string](#created_at) | Yes | When this context was first created |
| `last_updated` | [string](#last_updated) | Yes | When this context was last modified |
| `api_specs` | [object](#api_specs) | No | API specifications for enhanced responses |
| `context_summary` | string? | No | Brief summary of conversation context |
| `current_file` | string? | No | Currently active file |
| `current_goal` | string? | No | Agent's current objective |
| `error_context` | string? | No | Error information for debugging |
| `history` | [array](#history) | No | Chronological record of actions and API calls |
| `recent_changes` | [array](#recent_changes) | No | Recent changes or modifications (max 10) |
| `session` | [object](#session) | No | Session tracking information for this context |
| `user` | string? | No | User identifier |
| `workspace` | string? | No | Current workspace or project |


### `context_id`

**Type:** string

Unique identifier for this context

**Pattern:** `^ocp-[a-f0-9]{8,}$`


### `recent_changes`

**Type:** array

Recent changes or modifications (max 10)

**Default:** `[]`


### `session`

**Type:** object

Session tracking information for this context

#### Properties

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `agent_type` | string | Yes | Type of agent for this session |
| `interaction_count` | [integer](#interaction_count) | Yes | Number of interactions in this session |
| `start_time` | [string](#start_time) | Yes | Session start timestamp |


### `session.start_time`

**Type:** string

Session start timestamp

**Format:** date-time


### `session.interaction_count`

**Type:** integer

Number of interactions in this session

**Minimum:** 0

**Default:** `0`


### `history`

**Type:** array

Chronological record of actions and API calls

**Array items:** object

**Item Properties:**

#### Properties

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `action` | string | Yes | Type of action performed |
| `timestamp` | [string](#timestamp) | Yes | When this action occurred |
| `api_endpoint` | string? | No | API endpoint called if applicable |
| `metadata` | [object](#metadata) | No | Additional contextual data for this action |
| `result` | string? | No | Summary of action result |


### `history.timestamp`

**Type:** string

When this action occurred

**Format:** date-time


### `history.metadata`

**Type:** object

Additional contextual data for this action

**Default:** `{}`


### `api_specs`

**Type:** object

API specifications for enhanced responses


### `api_specs.parameters_pattern`

**Type:** object (dynamic properties)

**Pattern:** Properties matching `^[a-zA-Z0-9_-]+$`

Each property matching this pattern must be:

- **Type:** string

### `created_at`

**Type:** string

When this context was first created

**Format:** date-time


### `last_updated`

**Type:** string

When this context was last modified

**Format:** date-time

