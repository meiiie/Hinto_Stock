# 🔀 AGENT HANDOFFS PROTOCOL

**Document Version:** 1.0
**Last Updated:** 2025-12-22
**Purpose:** Standard procedures for transferring work between AI agents

---

## 1. OVERVIEW

Agent handoffs occur when:
- One agent completes work that another agent needs
- Work requires expertise from a different role
- Blockers need to be escalated
- Cross-cutting changes affect multiple domains

---

## 2. HANDOFF TYPES

### Type A: Deliverable Handoff
**When:** Agent completes work that another needs
```
Frontend: "I need the API endpoint ready"
         ↓
Backend: Implements endpoint
         ↓
Backend → Frontend: "Endpoint /api/signals is ready"
```

### Type B: Request Handoff  
**When:** Agent needs something from another
```
Backend: "Need database schema for new entity"
         ↓
Backend → Database: Request entity schema
         ↓
Database: Designs and implements
```

### Type C: Escalation Handoff
**When:** Issue needs higher authority
```
Any Agent: "Conflicting requirements discovered"
           ↓
Agent → PM: Escalate for decision
           ↓
PM: Makes decision and communicates back
```

---

## 3. HANDOFF DOCUMENT TEMPLATE

Store in: `communication/handoffs/[date]-[from]-to-[to].md`

```markdown
# Agent Handoff Document

## Metadata
| Field | Value |
|-------|-------|
| **From** | [Source Agent] |
| **To** | [Target Agent] |
| **Date** | [YYYY-MM-DD HH:MM] |
| **Type** | Deliverable / Request / Escalation |
| **Priority** | 🔴 Critical / 🟡 High / 🟢 Normal |
| **Status** | Open / In Progress / Completed |

---

## Summary
[One paragraph describing what this handoff is about]

---

## Context
[Background information the target agent needs to understand the request]

### Related Files
- `path/to/file1.py` - [Why relevant]
- `path/to/file2.ts` - [Why relevant]

### Related Tasks
- Task ID: [Link to task if exists]
- Sprint: [Sprint number]

---

## Request / Deliverable Details

### What I Need / What I'm Providing
[Specific details]

### Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

### Constraints / Considerations
- [Important constraint 1]
- [Important constraint 2]

---

## Timeline
| Milestone | Date |
|-----------|------|
| Requested | [Date] |
| Expected delivery | [Date] |
| Actual delivery | [To be filled] |

---

## Response Section
*(To be filled by receiving agent)*

### Acknowledgement
- [ ] Request received and understood
- [ ] Questions / Clarifications needed

### Response
[Target agent's response goes here]

### Completion
- [ ] Work completed
- [ ] Tests passing
- [ ] Documentation updated
```

---

## 4. HANDOFF WORKFLOW

### Step 1: Initiator Creates Handoff
```
1. Create handoff document in communication/handoffs/
2. Update own progress.md
3. Reference handoff in task-board.md if applicable
```

### Step 2: PM Monitors (Optional)
```
For critical handoffs:
- PM notified
- PM adds to agent-status.md
- PM may facilitate if needed
```

### Step 3: Receiver Acknowledges
```
1. Read handoff document
2. Add acknowledgement in Response Section
3. Ask clarifying questions if needed
```

### Step 4: Receiver Completes
```
1. Do the work
2. Update Response Section with completion details
3. Change Status to "Completed"
4. Notify initiator (or let them poll)
```

### Step 5: Initiator Confirms
```
1. Verify deliverable meets criteria
2. Continue with own work
3. Archive handoff if needed
```

---

## 5. COMMON HANDOFF SCENARIOS

### Frontend → Backend
```markdown
Common Requests:
- "Need API endpoint for [feature]"
- "Endpoint returns wrong data format"
- "Need WebSocket event for [data]"

Expected Response:
- API contract specification
- Sample request/response
- Error scenarios
```

### Backend → Database
```markdown
Common Requests:
- "Need schema for [entity]"
- "Query is too slow, needs optimization"
- "Need migration for [change]"

Expected Response:
- SQL schema definition
- Index recommendations
- Migration script
```

### Any → QA
```markdown
Common Requests:
- "Feature [X] ready for testing"
- "Fixed bug [Y], please verify"

Expected Response:
- Test results
- Bug report if issues found
- Approval if passed
```

### Any → PM
```markdown
Common Escalations:
- "Requirements conflict"
- "Timeline at risk"
- "Need decision on [options]"

Expected Response:
- Decision with rationale
- Updated priorities
- Communication to affected agents
```

---

## 6. HANDOFF ANTI-PATTERNS

### ❌ Don't
```markdown
- Create handoffs for trivial requests (use direct communication)
- Leave handoffs in "Open" status indefinitely
- Handoff without sufficient context
- Assume handoff is received (verify acknowledgement)
- Create circular handoffs (A→B→A)
```

### ✅ Do
```markdown
- Keep handoffs focused (one topic per handoff)
- Include all necessary context upfront
- Set clear expectations and timelines
- Follow up if no response within reasonable time
- Close/archive completed handoffs
```

---

## 7. HANDOFF TRACKING

### Active Handoffs Dashboard
Maintain in `communication/handoff-status.md`:

```markdown
# Active Handoffs

| ID | From | To | Subject | Priority | Status | Days Open |
|----|------|-----|---------|----------|--------|-----------|
| H001 | BE | DB | User table migration | 🟡 | In Progress | 2 |
| H002 | FE | BE | Signal API endpoint | 🔴 | Open | 1 |
```

---

## 8. QUICK REFERENCE

```
Handoff Checklist:
□ Clear subject line
□ Context provided
□ Specific request/deliverable
□ Acceptance criteria defined
□ Timeline set
□ Stored in correct location
□ Notified receiving agent
```
