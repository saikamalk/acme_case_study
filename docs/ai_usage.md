# AI Tool Usage Notes
## Overview
AI-assisted development tools were used throughout the implementation of this assessment.

The objective was to accelerate development while maintaining full understanding and ownership of the final solution.

---
## Tools Used
- ChatGPT
- GitHub Copilot
---
## Tasks Delegated To AI
AI assistance was used for:
- Initial project scaffolding
- Docker Compose configuration
- FastAPI boilerplate
- Pydantic model generation
- Prompt engineering
- Documentation drafting
- Evaluation dataset creation
- OpenTelemetry instrumentation guidance
- Jaeger integration guidance
---
## Human Validation
All AI-generated output was reviewed before inclusion.

Validation activities included:
- Manual code review
- Functional testing
- Docker Compose testing
- Authentication testing
- RBAC testing
- Tool routing verification
- OpenTelemetry trace verification
- Evaluation execution
---
## Errors Identified During Development
Examples of issues identified and corrected:

### Planner Validation Failures
Early planner outputs occasionally omitted required fields.

Validation logic and retry mechanisms were added to ensure structured outputs.

### Tool Routing Issues

Several user prompts initially routed to incorrect tools.

Prompt instructions and examples were refined to improve planner accuracy.

### Authentication Integration

JWT validation and role extraction required multiple iterations before stable integration with Keycloak.

### Skill Routing

Escalation workflows initially produced inconsistent outputs.

Prompt structure was refined to enforce:
- Executive Summary
- Risk Level
- Recommended Action
- Missing Information
---

## What Was Not Delegated To AI

The following activities remained under human control:
- Architectural decisions
- Security decisions
- Authentication design
- RBAC implementation
- Database schema design
- Final testing and validation
---

## Production Considerations

AI-generated code should not be accepted without review.

Particular attention should always be paid to:
- Security-sensitive code
- Authentication logic
- Authorization controls
- Database access patterns
- Infrastructure configuration

Human oversight remains essential for production-grade systems.