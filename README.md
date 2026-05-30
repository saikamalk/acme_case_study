# Acme Operations — Agentic Enterprise Assistant

## Overview

A locally runnable agentic enterprise assistant that demonstrates:

- Keycloak authentication and RBAC
- LLM-driven tool selection
- PostgreSQL structured data retrieval
- Redis conversation memory
- MCP server integration
- Reusable escalation summary skill
- Observability and tracing
- Docker Compose deployment

## Architecture

![Architecture Diagram](docs/architecture-diagram.png)
The solution consists of a Streamlit UI, FastAPI-based agent service, Keycloak for authentication and RBAC, Redis for conversation memory, PostgreSQL for structured customer data, and an MCP server exposing enterprise tools. The agent uses an LLM-powered planner to dynamically select tools and invoke reusable skills before generating a final response.

### High-Level Flow

![High Level Flow Diagram](docs/high-level-flow-diagram.png)

## Components

### FastAPI
Main API service exposing chat and protected endpoints.

### PostgreSQL
Durable store for:
- customers
- issues
- issue_updates
- next_actions

### Redis
Stores short-term conversation history and session memory.

### Keycloak
Authentication provider and role management.

### MCP Server
Decouples tool definitions from core agent logic.

## Agent Workflow

1. User submits query.
2. Redis conversation history is loaded.
3. Planner selects tool and response mode.
4. Tool retrieves structured data.
5. Skill generates final response.
6. Traces are recorded.

## Available Tools

### customer_profile_tool
Retrieves customer profile and operational status.

### issue_history_tool
Retrieves issue history and updates.

### create_next_action_tool
Creates recommended next actions for issues.

## Skills

### Escalation Summary Skill

Outputs:

- Executive Summary
- Risk Level
- Recommended Next Action
- Missing Information

## Authentication & RBAC

| Role | Permissions |
|------|-------------|
| sales_user | Read-only customer and issue access |
| support_user | Read and issue workflow access |
| admin | Full access including next actions |

## Redis Usage

Redis is used for short-term memory because conversation history is ephemeral and benefits from low-latency access.

## MCP Usage

MCP provides:

- Tool abstraction
- Separation of concerns
- Reusable integrations
- Easier extensibility

## Observability

Includes:

- Request logs
- Error logs
- Tool execution traces
- Latency tracking

## Running Locally

```bash
GROQ_API_KEY=<input_groq_api_key> docker compose up -d --build
```

Services:

- FastAPI
- PostgreSQL
- Redis
- Keycloak
- MCP Server

## Sample Queries

- What is happening with Globex?
- Show me open issues for Initech.
- Summarise the history of issue 3.
- Create a next action for issue 5.
- How bad is the Initech situation?

## Evaluation

Evaluation covers:

- Tool selection accuracy
- Database grounding
- RBAC validation
- Recommendation quality

Artifacts:

- evals/eval_dataset.json
- evals/results.md

## Trade-offs

Current implementation favors simplicity and local execution:

- In-memory traces
- Seeded enterprise data
- Local container stack

Future improvements:

- JWKS-based JWT verification
- OpenTelemetry integration
- Persistent trace storage
- Expanded tool catalog

## AI Tool Usage

AI tools were used for:

- Boilerplate generation
- Docker scaffolding
- Documentation drafting
- Prompt engineering

All generated code was reviewed, tested, and validated manually before inclusion.

## Repository Structure

```text
app/
keycloak/
mcp_server/
seed/
ui/
docker-compose.yml
README.md
```

## Demo Checklist

- Keycloak login works
- Chat endpoint works
- Tool routing works
- Escalation skill works
- RBAC enforcement works
- Traces visible
- Docker Compose starts entire stack
