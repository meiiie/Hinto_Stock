# DECISION LOG - Architecture Decision Records

Version: 1.0 | Updated: 2025-12-22

This file records significant architectural and technical decisions.
All agents should reference this before making changes that could conflict with past decisions.

---

## Decision Template

```markdown
## ADR-XXX: [Title]

Date: YYYY-MM-DD
Status: Proposed | Accepted | Deprecated | Superseded
Deciders: [Who made this decision]

### Context
[What is the issue or situation that requires a decision?]

### Decision
[What is the decision that was made?]

### Consequences
[What are the positive and negative outcomes?]

### Alternatives Considered
[What other options were evaluated?]
```

---

## Accepted Decisions

### ADR-001: 3-Layer Signal Architecture

Date: 2025-12-22
Status: Accepted
Deciders: Human Owner

#### Context
Need a robust signal generation system that combines real-time indicators with pattern recognition and strategic planning.

#### Decision
Implement a 3-layer architecture:
- Layer 1: Real-time signals (VWAP + BB + StochRSI)
- Layer 2: Candle pattern confirmation
- Layer 3: LLM strategic planning (future)

#### Consequences
Positive:
- Modular, each layer can be developed independently
- Multiple confirmation improves signal quality
- Scalable to add more layers

Negative:
- More complex than single-layer approach
- Requires coordination between layers

#### Alternatives Considered
- Single indicator approach: Too simple, low accuracy
- Pure ML approach: Requires extensive training data

---

### ADR-002: Clean Architecture for Backend

Date: 2025-12-22
Status: Accepted
Deciders: Human Owner

#### Context
Backend needs clear separation of concerns for maintainability and testability.

#### Decision
Adopt Clean Architecture with 4 layers:
- Presentation (API, WebSocket)
- Application (Use Cases)
- Domain (Entities, Services)
- Infrastructure (DB, Exchange API)

#### Consequences
Positive:
- Domain logic isolated from infrastructure
- Easy to test
- Easy to swap infrastructure

Negative:
- More boilerplate code
- Learning curve

---

### ADR-003: SOTA Prompt Engineering v2.1

Date: 2025-12-22
Status: Accepted
Deciders: Human Owner + PM

#### Context
Need effective AI agent prompts for consistent behavior.

#### Decision
Adopt SOTA 2025 techniques:
- XML tag structuring (Anthropic style)
- ReAct pattern for reasoning
- Chain-of-Thought prompting
- No emojis (professional standard)
- PTCF framework (Persona-Task-Context-Format)

#### Consequences
Positive:
- Consistent agent behavior
- Clear reasoning traces
- Professional output

Negative:
- Longer prompts
- Requires training to use effectively

---

### ADR-004: SQLite for Desktop, Future PostgreSQL

Date: 2025-12-22
Status: Accepted
Deciders: DB Specialist

#### Context
Need database for desktop application with future scaling option.

#### Decision
Use SQLite for desktop deployment, design schema to be PostgreSQL-compatible for future migration.

#### Consequences
Positive:
- No separate database server needed
- Easy deployment
- Migration path exists

Negative:
- Limited concurrent writes
- No built-in replication

---

## Pending Decisions

[None currently]

---

## Superseded Decisions

[None currently]
