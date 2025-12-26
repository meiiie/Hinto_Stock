# 🚀 FEATURE DEVELOPMENT WORKFLOW

**Document Version:** 1.0
**Last Updated:** 2025-12-22
**Purpose:** Standard workflow for developing new features

---

## 1. OVERVIEW

This workflow ensures features are developed consistently across all agents with proper handoffs and quality gates.

```
┌──────────────────┐
│  1. INTAKE       │ ← PM receives feature request
└────────┬─────────┘
         │
┌────────▼─────────┐
│  2. PLANNING     │ ← Agents analyze requirements
└────────┬─────────┘
         │
┌────────▼─────────┐
│  3. DESIGN       │ ← Architecture/API/UI design
└────────┬─────────┘
         │
┌────────▼─────────┐
│  4. IMPLEMENT    │ ← Agents build in parallel
└────────┬─────────┘
         │
┌────────▼─────────┐
│  5. INTEGRATE    │ ← Connect frontend + backend
└────────┬─────────┘
         │
┌────────▼─────────┐
│  6. TEST         │ ← QA verifies
└────────┬─────────┘
         │
┌────────▼─────────┐
│  7. RELEASE      │ ← Deploy to users
└──────────────────┘
```

---

## 2. PHASE 1: INTAKE

**Owner:** Project Manager

### Input
- Feature request from Human Owner
- User story or problem statement

### Activities
1. Parse and clarify requirements
2. Assess priority and timeline
3. Create task in task-board.md
4. Assign to planning phase

### Output
```markdown
## Feature Ticket: [FEAT-XXX]

### Title
[Feature name]

### Description
[What the feature does]

### User Story
As a [user type]
I want [capability]
So that [benefit]

### Acceptance Criteria
- [ ] AC1
- [ ] AC2
- [ ] AC3

### Priority
🔴 Critical / 🟡 High / 🟢 Normal

### Target Sprint
[Sprint number]
```

---

## 3. PHASE 2: PLANNING

**Owner:** All relevant agents

### Activities

#### PM Actions
1. Kick off planning session
2. Share feature ticket with all agents
3. Facilitate requirement clarification

#### Backend Engineer
1. Review business logic requirements
2. Identify domain entities needed
3. Draft API contract outline

#### Frontend Architect
1. Review UI requirements
2. Sketch component hierarchy
3. Identify state management needs

#### Database Specialist
1. Review data requirements
2. Identify schema changes
3. Assess query patterns

#### QA Engineer
1. Review testability
2. Identify test scenarios
3. Flag quality risks

### Output
- Shared understanding document
- Initial effort estimates
- Risk assessment

---

## 4. PHASE 3: DESIGN

**Owner:** Each agent for their domain

### Backend Design
```markdown
### API Design
| Endpoint | Method | Request | Response |
|----------|--------|---------|----------|
| /api/v1/[resource] | [METHOD] | [Schema] | [Schema] |

### Domain Model
[Entity diagrams or descriptions]

### Business Rules
1. [Rule 1]
2. [Rule 2]
```

### Frontend Design
```markdown
### Component Hierarchy
```
PageComponent
├── HeaderSection
├── MainContent
│   ├── DataDisplay
│   └── ActionPanel
└── Footer
```

### State Design
| Store | Data | Updates |
|-------|------|---------|
| [Name] | [Shape] | [Triggers] |

### UI Mockup Reference
[Link to mockup if available]
```

### Database Design
```markdown
### Schema Changes
[SQL or entity definitions]

### Migration Plan
1. [Migration step 1]
2. [Migration step 2]

### Query Patterns
[Key queries and indexes needed]
```

### QA Test Plan
```markdown
### Test Scenarios
| ID | Scenario | Type | Priority |
|----|----------|------|----------|
| T1 | [Description] | Unit/E2E | High |

### Coverage Goals
[Specific coverage targets]
```

### Design Review Checklist
- [ ] All agents reviewed relevant designs
- [ ] API contract agreed
- [ ] No architecture violations
- [ ] Tests planned
- [ ] PM approved proceed

---

## 5. PHASE 4: IMPLEMENT

**Owner:** Backend Engineer + Frontend Architect (parallel)

### Backend Implementation
```markdown
Order of work:
1. Domain entities
2. Repository interfaces
3. Use cases / services
4. API endpoints
5. Infrastructure implementations

### Progress Tracking
- [ ] Entities created
- [ ] Services implemented
- [ ] API endpoints ready
- [ ] Unit tests written
```

### Frontend Implementation
```markdown
Order of work:
1. Component scaffolding
2. State store setup
3. API service integration
4. UI implementation
5. Component tests

### Progress Tracking
- [ ] Components created
- [ ] State wired
- [ ] API connected (can use mocks)
- [ ] UI polished
```

### Database Implementation
```markdown
- [ ] Migration created
- [ ] Migration tested on copy
- [ ] Indexes added
- [ ] Migration applied
```

### Implementation Sync Points
| Checkpoint | Trigger | Participants |
|------------|---------|--------------|
| API Ready | Backend completes endpoints | FE + BE |
| Schema Ready | DB migration done | BE + DB |
| Integration Start | All parts ready | All |

---

## 6. PHASE 5: INTEGRATE

**Owner:** Frontend + Backend collaboration

### Integration Steps
1. Backend provides real API (not mocks)
2. Frontend connects to real API
3. End-to-end data flow tested
4. Edge cases handled

### Integration Checklist
- [ ] API returns expected data
- [ ] Error states handled in UI
- [ ] Loading states work
- [ ] Real-time updates work (if applicable)
- [ ] No console errors

---

## 7. PHASE 6: TEST

**Owner:** QA Engineer

### Testing Phases
```markdown
#### Unit Tests (All developers)
- [ ] Domain logic tests pass
- [ ] Component tests pass
- [ ] Coverage meets threshold

#### Integration Tests
- [ ] API integration tests pass
- [ ] Database integration tests pass

#### E2E Tests
- [ ] Happy path automated
- [ ] Error paths automated
- [ ] Manual exploratory testing done

#### Performance Tests (if applicable)
- [ ] Latency within limits
- [ ] Memory usage acceptable
```

### Bug Handling
- Critical bugs → Block release, immediate fix
- High bugs → Fix before release
- Medium bugs → Fix in next sprint
- Low bugs → Backlog

### QA Approval
```markdown
## QA Sign-off: [FEAT-XXX]

**Date:** [YYYY-MM-DD]
**QA Engineer:** QA Agent

### Test Summary
| Type | Pass | Fail | Skip |
|------|------|------|------|
| Unit | [X] | [Y] | [Z] |
| Integration | [X] | [Y] | [Z] |
| E2E | [X] | [Y] | [Z] |

### Open Issues
- [None / List of known issues]

### Recommendation
✅ Approved for release
⚠️ Approved with conditions: [conditions]
❌ Not approved: [reasons]
```

---

## 8. PHASE 7: RELEASE

**Owner:** Project Manager

### Pre-release Checklist
- [ ] All tests pass
- [ ] QA approved
- [ ] Documentation updated
- [ ] Release notes prepared
- [ ] Rollback plan ready

### Release Actions
1. Tag release version
2. Build production artifacts
3. Deploy to production
4. Monitor for issues
5. Update task-board.md

### Post-release
- [ ] Feature marked complete in task-board
- [ ] Progress updates sent to stakeholders
- [ ] Retrospective notes added

---

## 9. QUICK REFERENCE

```
Feature Development Checklist:
□ Intake complete, ticket created
□ All agents planning complete
□ Designs reviewed and approved
□ Implementation done
□ Integration tested
□ QA approved
□ Released
□ Post-release monitoring done
```
