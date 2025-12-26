# 🐛 BUG TRACKING - Hinto Stock

**Last Updated:** 2025-12-22
**Owner:** QA Engineer

---

## ACTIVE BUGS

| ID | Title | Severity | Assignee | Status |
|----|-------|----------|----------|--------|
| BUG-001 | Signal Panel not updating | 🟠 High | Backend | Open |

---

## BUG DETAILS

### BUG-001: Signal Panel Not Updating

**Severity:** 🟠 High
**Status:** Open
**Reported:** 2025-12-22
**Assignee:** Backend Engineer

#### Description
Signal panel in the UI does not display new signals in real-time. User has to refresh to see signals.

#### Steps to Reproduce
1. Open trading dashboard
2. Wait for signal generation
3. Observe signal panel does not update

#### Expected
Signal panel updates automatically when new signal generated

#### Actual
Panel remains static, no new signals appear

#### Root Cause Analysis
- Pending investigation
- Suspected: EventBus → WebSocket → UI connection broken

#### Notes
- Related to desktop app migration
- May be WebSocket reconnection issue

---

## RESOLVED BUGS (Recent)

| ID | Title | Severity | Resolved |
|----|-------|----------|----------|
| - | None yet | - | - |

---

## BUG TRENDS

### By Severity (Active)
| Severity | Count |
|----------|-------|
| 🔴 Critical | 0 |
| 🟠 High | 1 |
| 🟡 Medium | 0 |
| 🟢 Low | 0 |

### By Component (Active)
| Component | Count |
|-----------|-------|
| Backend | 1 |
| Frontend | 0 |
| Database | 0 |

---

## REGRESSION TESTS NEEDED

| Bug ID | Test Description | Status |
|--------|------------------|--------|
| BUG-001 | Signal WebSocket delivery test | ⏳ Pending |

---

## BUG SUBMISSION TEMPLATE

```markdown
## Bug Report: [BUG-XXX]

### Summary
[One line description]

### Environment
- App Version:
- OS:
- Browser/Electron version:

### Severity
🔴 Critical / 🟠 High / 🟡 Medium / 🟢 Low

### Steps to Reproduce
1. 
2. 
3. 

### Expected Result

### Actual Result

### Evidence
- Screenshots:
- Logs:
- Screen recording:

### Workaround
[If any]
```

---

**Last Review:** 2025-12-22
