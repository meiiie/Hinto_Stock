# 🐛 BUG FIXING WORKFLOW

**Document Version:** 1.0
**Last Updated:** 2025-12-22
**Purpose:** Standard workflow for fixing bugs

---

## 1. OVERVIEW

```
┌──────────────────┐
│  1. REPORT       │ ← Bug discovered/reported
└────────┬─────────┘
         │
┌────────▼─────────┐
│  2. TRIAGE       │ ← PM/QA assesses severity
└────────┬─────────┘
         │
┌────────▼─────────┐
│  3. ASSIGN       │ ← Route to correct agent
└────────┬─────────┘
         │
┌────────▼─────────┐
│  4. INVESTIGATE  │ ← Find root cause
└────────┬─────────┘
         │
┌────────▼─────────┐
│  5. FIX          │ ← Implement solution
└────────┬─────────┘
         │
┌────────▼─────────┐
│  6. VERIFY       │ ← QA confirms fix
└────────┬─────────┘
         │
┌────────▼─────────┐
│  7. CLOSE        │ ← Document and close
└──────────────────┘
```

---

## 2. PHASE 1: REPORT

### Bug Report Template
```markdown
## Bug Report: [BUG-XXX]

### Summary
[One-line description]

### Environment
| Field | Value |
|-------|-------|
| App Version | [version] |
| OS | [Windows/macOS/Linux] |
| Symbol | [If trading-related] |
| Market State | [Trending/Sideways/Volatile] |

### Severity
- 🔴 **Critical:** System crash, data loss, wrong trade
- 🟠 **High:** Major feature broken
- 🟡 **Medium:** Feature works but with issues
- 🟢 **Low:** Minor/cosmetic issue

### Steps to Reproduce
1. [Step 1]
2. [Step 2]
3. [Step 3]

### Expected Behavior
[What should happen]

### Actual Behavior
[What actually happens]

### Evidence
- Screenshots: [attached]
- Logs: [relevant lines]
- Screen recording: [if applicable]

### Workaround
[If any workaround exists]

### Reporter
[Who found the bug]
**Date:** [YYYY-MM-DD]
```

---

## 3. PHASE 2: TRIAGE

**Owner:** Project Manager + QA Engineer

### Severity Classification

| Severity | Response Time | Fix Timeline |
|----------|---------------|--------------|
| 🔴 Critical | Immediate | Same day |
| 🟠 High | < 4 hours | < 24 hours |
| 🟡 Medium | < 24 hours | Next sprint |
| 🟢 Low | < 48 hours | Backlog |

### Triage Questions
1. Can user work around this?
2. How many users affected?
3. Data integrity at risk?
4. Revenue/trading impact?
5. Regression from recent change?

### Triage Output
```markdown
## Triage: [BUG-XXX]

**Triaged By:** [PM/QA]
**Date:** [YYYY-MM-DD]

### Assessment
- **Confirmed:** Yes/No
- **Severity:** [Level]
- **Impact:** [Users/Features affected]
- **Likely Cause:** [Frontend/Backend/Database/Other]

### Assignment
- **Assigned To:** [Agent]
- **Due By:** [Date/Time]
- **Priority:** [In queue position]
```

---

## 4. PHASE 3: ASSIGN

**Owner:** Project Manager

### Assignment Rules

| Symptom | Assign To |
|---------|-----------|
| UI not rendering/displaying | Frontend |
| API returns wrong data | Backend |
| API errors/timeouts | Backend |
| Data missing/corrupted | Database |
| Slow performance | Start with Backend |
| Trade execution issue | Backend (Critical) |

### Cross-cutting Bugs
If unclear ownership:
1. Assign to Backend for investigation
2. Backend routes to correct agent after analysis

---

## 5. PHASE 4: INVESTIGATE

**Owner:** Assigned Agent

### Investigation Steps
```markdown
1. REPRODUCE
   - Confirm bug can be reproduced
   - Document exact steps
   - Note any variations

2. ISOLATE
   - Identify component(s) involved
   - Check recent changes (git log)
   - Review related code

3. ROOT CAUSE
   - Find actual cause, not just symptom
   - Understand why it happened
   - Identify other affected areas

4. IMPACT ANALYSIS
   - What else might this fix affect?
   - Any regression risks?
   - Test coverage for area?
```

### Investigation Report
```markdown
## Investigation: [BUG-XXX]

**Investigator:** [Agent]
**Date:** [YYYY-MM-DD]

### Reproduction
- Reproduced: Yes/No
- Consistency: Always/Sometimes/Rare

### Root Cause
[Explanation of why the bug occurs]

### Affected Code
- File: [path/to/file]
- Function: [function name]
- Lines: [line numbers]

### Related Areas
- [Other components that might be affected]

### Proposed Fix
[High-level description of fix approach]

### Estimated Effort
[Time estimate]

### Risks
- [Risk 1]
- [Risk 2]
```

---

## 6. PHASE 5: FIX

**Owner:** Assigned Agent

### Fix Guidelines
```markdown
1. MINIMAL CHANGE
   - Fix only what's broken
   - Avoid "while I'm here" changes
   - Keep scope contained

2. TEST FIRST (if possible)
   - Write test that fails with bug
   - Fix should make test pass
   - Confirms fix works, prevents regression

3. DOCUMENT
   - Comment non-obvious fixes
   - Update related documentation
   - Reference bug ID in commit

4. REVIEW
   - Self-review before marking ready
   - Consider edge cases
   - Check for similar issues elsewhere
```

### Fix Documentation
```markdown
## Fix: [BUG-XXX]

**Fixed By:** [Agent]
**Date:** [YYYY-MM-DD]

### Changes Made
| File | Change |
|------|--------|
| [path] | [Description] |

### Test Added
- [Test file and description]

### Verification Steps
1. [How to verify the fix]
2. [Step 2]

### Regression Risk
- Low/Medium/High
- [Areas to check]

### Ready for QA
- [ ] Fix complete
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Self-reviewed
```

---

## 7. PHASE 6: VERIFY

**Owner:** QA Engineer

### Verification Checklist
```markdown
## Verification: [BUG-XXX]

**Verified By:** QA Agent
**Date:** [YYYY-MM-DD]

### Bug Fix Verification
- [ ] Original bug no longer reproducible
- [ ] New test passes
- [ ] Edge cases tested

### Regression Testing
- [ ] Related features still work
- [ ] Existing tests still pass
- [ ] No new console errors

### Verification Result
✅ **PASSED** - Bug is fixed
⚠️ **PARTIAL** - Partially fixed, [details]
❌ **FAILED** - Bug still present, [details]

### Notes
[Any observations or concerns]
```

### If Verification Fails
1. Return to assigned agent with details
2. Repeat Fix → Verify cycle
3. Escalate if multiple failures

---

## 8. PHASE 7: CLOSE

**Owner:** Project Manager

### Closure Checklist
- [ ] Fix verified by QA
- [ ] Bug report updated with resolution
- [ ] Related tickets updated
- [ ] Release notes updated (if significant)
- [ ] Monitoring in place (if needed)

### Bug Resolution
```markdown
## Resolution: [BUG-XXX]

**Status:** Closed
**Resolution Date:** [YYYY-MM-DD]

### Summary
[What was wrong and how it was fixed]

### Lessons Learned
[Any process improvements identified]

### Related
- Commits: [commit hashes]
- Tests: [new tests added]
- Docs: [documentation updated]
```

---

## 9. SPECIAL CASES

### Critical Production Bug
```
1. STOP - Assess if trading should pause
2. COMMUNICATE - Alert Human Owner immediately
3. HOTFIX - Apply minimal fix
4. VERIFY - Quick verification
5. DEPLOY - Emergency deploy
6. POSTMORTEM - Full analysis after stabilization
```

### Cannot Reproduce
```
1. Request more information
2. Review logs extensively
3. Add logging and wait for recurrence
4. Close as "Cannot Reproduce" if no progress after 3 attempts
```

---

## 10. QUICK REFERENCE

```
Bug Fixing Checklist:
□ Bug reported with all details
□ Triaged and assigned
□ Root cause identified
□ Fix implemented and tested
□ QA verified fix
□ Bug closed and documented
```
