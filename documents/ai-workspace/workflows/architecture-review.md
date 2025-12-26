# 🏛️ ARCHITECTURE REVIEW WORKFLOW

**Document Version:** 1.0
**Last Updated:** 2025-12-22
**Purpose:** Process for reviewing and approving architectural changes

---

## 1. OVERVIEW

Architecture reviews ensure significant changes:
- Align with system vision
- Don't introduce technical debt
- Are properly documented
- Have consensus from affected parties

```
┌──────────────────┐
│  1. PROPOSAL     │ ← Agent proposes change
└────────┬─────────┘
         │
┌────────▼─────────┐
│  2. REVIEW       │ ← All agents evaluate
└────────┬─────────┘
         │
┌────────▼─────────┐
│  3. DECISION     │ ← Accept / Reject / Modify
└────────┬─────────┘
         │
┌────────▼─────────┐
│  4. DOCUMENT     │ ← Record in ADR
└────────┬─────────┘
         │
┌────────▼─────────┐
│  5. IMPLEMENT    │ ← Execute approved change
└──────────────────┘
```

---

## 2. WHEN IS REVIEW REQUIRED?

### Always Required (🔴)
- New external dependency
- New service/component
- Database schema redesign
- API breaking changes
- Security-related changes
- Performance-critical paths

### Sometimes Required (🟡)
- Significant refactoring
- New design pattern adoption
- Cross-cutting concerns
- Large file restructuring

### Not Required (🟢)
- Bug fixes (unless architectural)
- Minor refactoring
- Documentation updates
- Test additions
- Style/formatting changes

---

## 3. PHASE 1: PROPOSAL

**Owner:** Any Agent

### Architecture Change Proposal (ACP)
```markdown
# Architecture Change Proposal: [ACP-XXX]

## Metadata
| Field | Value |
|-------|-------|
| **Author** | [Agent Name] |
| **Date** | [YYYY-MM-DD] |
| **Status** | Draft / In Review / Approved / Rejected |
| **Category** | [New Component / Dependency / Schema / API / Other] |

## Summary
[One paragraph describing the proposed change]

## Motivation
### Problem Statement
[What problem does this solve?]

### Current State
[How things work now and why that's insufficient]

### Goals
- [Goal 1]
- [Goal 2]

## Proposed Solution

### High-Level Design
[Description of the proposed architecture]

### Diagrams
```mermaid
[Architecture diagram if helpful]
```

### Key Changes
| Component | Current | Proposed |
|-----------|---------|----------|
| [Component] | [Current state] | [New state] |

### New Dependencies (if any)
| Dependency | Version | Purpose | License |
|------------|---------|---------|---------|
| [name] | [ver] | [why needed] | [license] |

## Impact Analysis

### Affected Components
- [Component 1]: [How affected]
- [Component 2]: [How affected]

### Migration Required
- [ ] Yes: [Migration steps]
- [ ] No

### Breaking Changes
- [ ] Yes: [What breaks]
- [ ] No

### Performance Impact
[Expected performance implications]

### Security Impact
[Security considerations]

## Alternatives Considered

### Option A: [Name]
**Description:** [Brief description]
**Pros:** [Benefits]
**Cons:** [Drawbacks]
**Why Not:** [Reason rejected]

### Option B: [Name]
[Same format]

## Implementation Plan

### Phases
1. [Phase 1]: [Description]
2. [Phase 2]: [Description]

### Estimated Effort
| Agent | Effort |
|-------|--------|
| Backend | [X days] |
| Frontend | [Y days] |
| Database | [Z days] |

### Rollback Strategy
[How to undo if needed]

## Open Questions
1. [Question 1]
2. [Question 2]
```

---

## 4. PHASE 2: REVIEW

**Owner:** All Affected Agents + PM

### Review Process
1. Proposal shared with all agents
2. Each agent reviews from their perspective
3. Questions/concerns documented
4. Discussion to resolve issues

### Review Checklist

#### Project Manager
- [ ] Aligns with project goals
- [ ] Timeline realistic
- [ ] Resources available
- [ ] Risk acceptable

#### Backend Engineer
- [ ] Clean architecture maintained
- [ ] Domain logic not compromised
- [ ] API design sound
- [ ] Performance acceptable

#### Frontend Architect
- [ ] UI impact understood
- [ ] State management considered
- [ ] User experience not degraded
- [ ] Implementation feasible

#### Database Specialist
- [ ] Data model sound
- [ ] Query patterns efficient
- [ ] Migration plan complete
- [ ] Data integrity preserved

#### QA Engineer
- [ ] Testable design
- [ ] Test strategy clear
- [ ] Risk areas identified
- [ ] Coverage achievable

### Review Comments
```markdown
## Review: [ACP-XXX]

### Reviewer: [Agent Name]
**Date:** [YYYY-MM-DD]

### Overall Assessment
✅ Approve
⚠️ Approve with conditions
❌ Reject
🔄 Needs more information

### Comments

#### Strengths
- [Positive point 1]
- [Positive point 2]

#### Concerns
- [Concern 1]: [Suggested resolution]
- [Concern 2]: [Suggested resolution]

#### Questions
1. [Question 1]
2. [Question 2]

#### Conditions (if conditional approval)
- [ ] [Condition 1]
- [ ] [Condition 2]
```

---

## 5. PHASE 3: DECISION

**Owner:** Project Manager

### Decision Criteria
| Criterion | Weight |
|-----------|--------|
| Alignment with goals | 25% |
| Technical soundness | 25% |
| Implementation feasibility | 20% |
| Risk level | 15% |
| Effort vs benefit | 15% |

### Decision Options

#### ✅ Approved
- All reviewers approve or conditionally approve
- Conditions are acceptable
- Proceed to documentation

#### ⚠️ Approved with Modifications
- Minor changes required
- Author updates proposal
- Quick re-review of changes
- Proceed when updated

#### 🔄 Deferred
- Not enough information
- More analysis needed
- Revisit after X days/weeks

#### ❌ Rejected
- Fundamental issues identified
- Doesn't align with goals
- Better alternatives exist
- Document rejection reason

### Decision Record
```markdown
## Decision: [ACP-XXX]

**Decision:** Approved / Modified / Deferred / Rejected
**Decided By:** Project Manager
**Date:** [YYYY-MM-DD]

### Rationale
[Why this decision was made]

### Conditions (if any)
- [Condition 1]
- [Condition 2]

### Next Steps
1. [Step 1]
2. [Step 2]
```

---

## 6. PHASE 4: DOCUMENT

**Owner:** Proposal Author

### Architecture Decision Record (ADR)
Store in: `documents/architecture/decisions/ADR-XXX.md`

```markdown
# ADR-XXX: [Decision Title]

## Status
Accepted

## Date
[YYYY-MM-DD]

## Context
[Summary of the problem and motivation]

## Decision
[What was decided and why]

## Consequences

### Positive
- [Benefit 1]
- [Benefit 2]

### Negative
- [Drawback 1]
- [Drawback 2]

### Risks
- [Risk 1]: [Mitigation]

## Implementation Notes
[Any important implementation details]

## Related
- ACP: [ACP-XXX]
- Related ADRs: [ADR-YYY]
```

### Update Architecture Docs
- [ ] Update global-architecture.md if needed
- [ ] Update affected agent context files
- [ ] Update project-constraints.md if new constraints

---

## 7. PHASE 5: IMPLEMENT

**Owner:** As per implementation plan

### Implementation Tracking
- Break into tasks in task-board.md
- Follow feature-development.md workflow
- Regular progress updates

### Post-Implementation Review
After implementation complete:
1. Verify architecture matches ADR
2. Update documentation with actual state
3. Note any deviations and reasons
4. Lessons learned for future

---

## 8. QUICK REFERENCE

```
Architecture Review Checklist:
□ Change requires review (see criteria)
□ ACP created with all sections
□ All affected agents reviewed
□ Comments addressed
□ Decision made and recorded
□ ADR created
□ Architecture docs updated
□ Implementation complete and verified
```
