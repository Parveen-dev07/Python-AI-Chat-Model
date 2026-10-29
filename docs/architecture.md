# Architecture

## Overview

The platform separates **customer-facing UI** (embeddable widget), **AI orchestration** (FastAPI service), and **customer data** (PostgreSQL accessed with read-only credentials).

```mermaid
flowchart TB
  subgraph client [Customer website]
    W[Embeddable widget]
  end
  subgraph platform [AI Chat Platform]
    API[FastAPI ai-service]
    TR[Tenant resolver]
    CS[Chat service]
    PV[Provider factory]
    DBI[PostgreSQL connector]
    QV[Query validator]
  end
  subgraph external [External systems]
    OLL[Ollama / OpenAI]
    PG[(Customer PostgreSQL)]
  end
  W -->|HTTPS + API key| API
  API --> TR
  TR --> CS
  CS --> PV
  PV --> OLL
  CS --> QV
  CS --> DBI
  DBI --> PG
```

## Request flow

```mermaid
sequenceDiagram
  participant U as User
  participant W as Widget
  participant A as ai-service
  participant T as Tenant resolver
  participant M as AI provider
  participant V as Query validator
  participant D as PostgreSQL

  U->>W: Natural language question
  W->>A: POST /api/v1/chat
  A->>T: Resolve widget_id
  T-->>A: Server-side DB config
  A->>M: Question + schema context
  M-->>A: Tool call run_readonly_sql
  A->>V: Validate SELECT
  V-->>A: Approved SQL
  A->>D: Read-only query
  D-->>A: Rows
  A->>M: Query results
  M-->>A: Natural language answer
  A-->>W: answer + request_id
```

## Design principles

- **Never trust the browser** for database URLs or tenant secrets.
- **Validate SQL in application code** before execution.
- **Pluggable AI providers** via a shared interface and factory.
- **Pluggable database connectors** starting with PostgreSQL.
