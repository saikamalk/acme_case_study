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
- user_roles

The application uses PostgreSQL as the source of truth for application-level authorization.

After Keycloak authenticates a user and validates the JWT, the application retrieves the user's roles from the user_roles table and enforces RBAC based on the database role.

This allows application permissions to be managed independently from the identity provider.

### Redis
Stores short-term conversation history and session memory.

### Keycloak
Authentication provider.

The application validates JWT tokens using Keycloak's OpenID Connect discovery endpoint and JWS keys.

Keycloak is responsible for authentication and identity verification.

Application authorization is enforced using roles stored in PostgreSQL.

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

### add_issue_update_tool
Adds operational updates to an existing issue.

Accessible by:
- support_user
- admin

## Skills

### Escalation Summary Skill

Outputs:

- Executive Summary
- Risk Level
- Recommended Next Action
- Missing Information

## Authentication & RBAC

| Role | Permissions                                                   |
|------|---------------------------------------------------------------|
| sales_user | Read-only customer and issue access                           |
| support_user | Read access plus ability to add issue updates                 |
| admin | Full access including issue updates and next actions creation |

Authentication is handled by Keycloak

Authorization is enforced by PostgreSQL user_roles mappings loaded during request processing.

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
- Request ID
- Trace ID
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
- Add update to issue 3 saying vendor confirmed root cause.
- Record that issue 5 has been fixed and validated.

## Evaluation

Evaluation covers:

- Tool selection accuracy
- Database grounding
- RBAC validation
- Recommendation quality

Artifacts:

- [evals/test_cases.json](evals/test_cases.json)
- [evals/results.json](evals/results.json)
- [evals/summary.md](evals/summary.md)

## Trade-offs

Current implementation favors simplicity and local execution:

- In-memory traces
- Seeded enterprise data
- Local container stack

Future improvements:
- OpenTelemetry integration
- Persistent trace storage
- Expanded tool catalog
- Automated evalution pipeline

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
