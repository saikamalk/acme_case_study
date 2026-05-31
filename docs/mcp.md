# MCP Integration
## What is MCP?
Model Context Protocol (MCP) provides a standardized way for AI agents to discover and invoke tools.
Instead of embedding tool implementations directly into agent logic, MCP exposes tools through a separate interface.
---
## Why MCP Was Used
The assessment explicitly requires at least one MCP server.
This project uses a dedicated MCP server to expose enterprise tools and separate tool implementation from agent orchestration.
Benefits:
- Separation of concerns
- Independent tool lifecycle
- Easier extensibility
- Cleaner architecture
- Reduced coupling
---
## Architecture
![MCP FLow](img.png)

---
## Available MCP Tools
### customer_profile_tool
Retrieves:
- Customer information
- Customer health
- Open issues
### issue_history_tool
Retrieves:
- Issue details
- Issue updates
- Historical activity


---
## Why MCP Improves Enterprise Systems
Enterprise environments often integrate with:
- Databases
- CRMs
- Ticketing systems
- Internal APIs
Using MCP allows these integrations to evolve independently from the agent.
This makes the architecture easier to maintain and extend.