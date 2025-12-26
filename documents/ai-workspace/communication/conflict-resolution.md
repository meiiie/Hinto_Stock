# ⚔️ CONFLICT RESOLUTION PROTOCOL

**Document Version:** 1.0
**Last Updated:** 2025-12-22
**Purpose:** Procedures for resolving disagreements between AI agents

---

## 1. CONFLICT TYPES

### Type 1: Technical Disagreement
**Example:** Backend wants SQL, Database prefers NoSQL
**Resolution:** Data-driven analysis, PM decides if tie

### Type 2: Priority Conflict
**Example:** Two features competing for same timeline slot
**Resolution:** PM prioritizes based on business value

### Type 3: Resource Conflict
**Example:** Both FE and BE need same developer time
**Resolution:** PM allocates based on critical path

### Type 4: Architecture Conflict
**Example:** Proposed change breaks existing design
**Resolution:** Architecture review process

---

## 2. RESOLUTION HIERARCHY

```
┌─────────────────────────────────────────────┐
│              RESOLUTION LEVELS              │
├─────────────────────────────────────────────┤
│ Level 1: Direct Discussion                  │
│   Agents discuss, find common ground        │
│   Time limit: 1 session                     │
├─────────────────────────────────────────────┤
│ Level 2: Data-Driven Analysis               │
│   Collect evidence for each position        │
│   Document pros/cons objectively            │
├─────────────────────────────────────────────┤
│ Level 3: PM Arbitration                     │
│   PM reviews evidence, makes decision       │
│   Decision is binding                       │
├─────────────────────────────────────────────┤
│ Level 4: Human Owner Escalation             │
│   For critical/irreversible decisions       │
│   Human has final authority                 │
└─────────────────────────────────────────────┘
```

---

## 3. CONFLICT RESOLUTION PROCESS

### Step 1: Identify Conflict
```markdown
When conflict detected:
1. Pause work on conflicting items
2. Document the conflict:
   - What is the disagreement?
   - Who is involved?
   - What are the options?
3. Notify relevant parties
```

### Step 2: Attempt Direct Resolution
```markdown
Conflicting agents should:
1. State their position clearly
2. Listen to other position
3. Identify common ground
4. Propose compromise if possible

Time limit: 1 working session
```

### Step 3: Document Positions
If not resolved, create conflict document:

```markdown
# Conflict Record: [CONF-XXX]

## Metadata
| Field | Value |
|-------|-------|
| **Date** | [YYYY-MM-DD] |
| **Parties** | [Agent 1], [Agent 2] |
| **Type** | Technical / Priority / Resource / Architecture |
| **Status** | Open / Escalated / Resolved |

## Conflict Description
[What is the disagreement about]

## Position A: [Agent 1]
### Argument
[Their position and reasoning]

### Evidence
- [Data point 1]
- [Data point 2]

### Proposed Solution
[What they want]

## Position B: [Agent 2]
### Argument
[Their position and reasoning]

### Evidence
- [Data point 1]
- [Data point 2]

### Proposed Solution
[What they want]

## Impact Analysis
| Factor | Option A | Option B |
|--------|----------|----------|
| Development time | [X days] | [Y days] |
| Technical debt | [Low/Med/High] | [Low/Med/High] |
| Risk | [Description] | [Description] |
| Alignment with architecture | [Yes/No] | [Yes/No] |

## Resolution
*(To be filled after resolution)*

### Decision
[What was decided]

### Rationale
[Why this option was chosen]

### Decided By
[Who made the decision]

### Date Resolved
[YYYY-MM-DD]
```

### Step 4: Escalate if Needed
```markdown
Escalation triggers:
- No agreement after Step 2
- Critical/irreversible decision
- Significant timeline impact
- Architecture-level change

Escalation path:
1. PM for normal conflicts
2. Human Owner for critical decisions
```

### Step 5: Implement Decision
```markdown
After resolution:
1. Update conflict record with decision
2. Communicate to all affected parties
3. Update relevant documentation
4. Monitor for issues from decision
```

---

## 4. DOMAIN-SPECIFIC AUTHORITY

When agents disagree on domain matters, domain expert has more weight:

| Domain | Authority | Examples |
|--------|-----------|----------|
| API Design | Backend Engineer | Endpoint structure, payload format |
| UI/UX | Frontend Architect | Component design, user flow |
| Data Model | Database Specialist | Schema, indexing, queries |
| Testing | QA Engineer | Test strategy, coverage |
| Priority | Project Manager | Timeline, resource allocation |
| Business Logic | Backend Engineer + PM | Trading rules, risk management |

---

## 5. DECISION DOCUMENTATION

All significant decisions should be recorded in ADR format:

```markdown
# ADR-XXX: [Decision Title]

## Status
Proposed / Accepted / Deprecated / Superseded

## Context
[Why are we making this decision?]

## Decision
[What is the change we're making?]

## Consequences
### Positive
- [Benefit 1]
- [Benefit 2]

### Negative
- [Drawback 1]
- [Drawback 2]

### Neutral
- [Other effects]

## Alternatives Considered
### Option A
[Description and why rejected]

### Option B
[Description and why rejected]
```

---

## 6. CONFLICT PREVENTION

### Best Practices
```markdown
1. Regular sync meetings (via progress updates)
2. Clear domain boundaries
3. Early communication of changes
4. Architecture reviews before major work
5. Shared understanding of constraints (read shared-context/)
6. Explicit API contracts before implementation
```

### Warning Signs
```markdown
Watch for:
- Agents making assumptions about other domains
- Parallel work on same component
- Unclear requirements
- Scope creep
- Communication gaps
```

---

## 7. CONFLICT LOG

Track all conflicts for pattern detection:

| ID | Date | Type | Parties | Resolution | Lesson Learned |
|----|------|------|---------|------------|----------------|
| CONF-001 | [Date] | [Type] | [Agents] | [Outcome] | [What to improve] |

---

## 8. QUICK REFERENCE

```
Conflict Resolution Checklist:
□ Conflict clearly defined
□ All parties heard
□ Evidence documented
□ Options analyzed
□ Decision made
□ Rationale recorded
□ Communicated to team
□ Documentation updated
```
