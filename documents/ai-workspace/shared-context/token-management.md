# 🎫 TOKEN MANAGEMENT GUIDE

**Document Version:** 1.0
**Last Updated:** 2025-12-22
**Purpose:** Guidelines for managing AI context/token limits

---

## 1. OVERVIEW

Khi làm việc với AI agents, context window (token limit) là một constraint quan trọng. Document này hướng dẫn cách quản lý context hiệu quả để duy trì continuity khi đạt tới giới hạn token.

---

## 2. TOKEN BUDGET PER AGENT

### Estimated Token Usage
| Content Type | Est. Tokens | Priority |
|--------------|-------------|----------|
| System Prompt | 2,000 | 🔴 Always include |
| Global Architecture | 1,500 | 🔴 Always include |
| Project Constraints | 1,200 | 🟡 Include on new session |
| Trading Requirements | 1,500 | 🟡 Include when relevant |
| Agent Context Files | 800-1,500 | 🟢 Load as needed |
| Progress Updates | 500-1,000 | 🟢 Latest only |

### Target Distribution
```
┌─────────────────────────────────────────────────────┐
│              CONTEXT WINDOW (128K tokens)           │
├─────────────────────────────────────────────────────┤
│ [System Prompt & Core Context]        10-15K (10%)  │
│ [Current Task Context]                20-30K (20%)  │
│ [Code Being Discussed]                40-50K (40%)  │
│ [Response Generation]                 30-40K (30%)  │
└─────────────────────────────────────────────────────┘
```

---

## 3. CONTEXT LOADING STRATEGY

### Session Start (Fresh)
```markdown
1. MUST LOAD:
   - agents/[role]/system-prompt.md
   - shared-context/global-architecture.md
   
2. SHOULD LOAD:
   - agents/[role]/context/*.md
   - shared-context/project-constraints.md
   
3. OPTIONAL (Load if relevant task):
   - shared-context/trading-requirements.md
   - Latest progress update
```

### Mid-session (Context Getting Full)
```markdown
When approaching token limit:
1. Summarize completed work to progress.md
2. Clear conversation history
3. Restart with fresh context + progress summary
4. Continue from where left off
```

### Session Handoff (Different Agent)
```markdown
When switching agents:
1. Source agent: Update their progress.md
2. Create handoff in communication/agent-handoffs.md
3. Target agent: Load own context + handoff file
```

---

## 4. CONTEXT FILE STRUCTURE

### Keep Files Focused
```markdown
✅ GOOD: Small, focused files
- api-contracts.md (just API specs)
- progress.md (just status)
- design-system.md (just tokens)

❌ BAD: Huge omnibus files
- everything-about-frontend.md (too broad)
- notes.md (unstructured)
```

### Use Sections for Large Topics
```markdown
# File: architecture-current.md

## Quick Summary (100 tokens)
[Brief overview for skimming]

## Component List (500 tokens)
[Structured list for reference]

## Detailed Specs (1000+ tokens)
[Load only when deep-diving]
```

---

## 5. PROGRESS TRACKING PROTOCOL

### Update Frequency
| Trigger | Action |
|---------|--------|
| Major task completed | Update progress.md |
| Before long pause | Update progress.md |
| Before context clear | Update progress.md + handoff |
| End of day | Update all agents' progress.md |

### Progress File Format
```markdown
# Progress Update - [Agent Name]
**Last Updated:** [Timestamp]

## Current Status
[One-line summary of current work]

## Completed This Session
- [Task 1 - with file references]
- [Task 2 - with outcomes]

## In Progress
- [Task being worked on]
- [Blockers if any]

## Next Steps
1. [Immediate next action]
2. [Follow-up action]

## Context References
- Files modified: [list]
- Dependencies: [other agents' work needed]
```

---

## 6. HANDOFF PROTOCOL

### When to Create Handoff
- Switching to different agent
- Requesting work from another agent
- Reporting blocker that needs escalation

### Handoff File Format
```markdown
# Agent Handoff
**From:** [Source Agent]
**To:** [Target Agent]
**Date:** [Timestamp]
**Priority:** 🔴 HIGH | 🟡 MEDIUM | 🟢 LOW

## Context Summary
[What the receiving agent needs to know]

## Request
[Specific ask or information being shared]

## Files to Reference
- [Relevant files with paths]

## Decisions Made
- [Any decisions that affect the target agent]

## Response Needed
- [ ] Yes - Reply in handoff file
- [ ] No - FYI only
```

---

## 7. MINIMIZING TOKEN WASTE

### Do
```markdown
✅ Use code references instead of pasting full files
   "See `SignalGenerator.calculate()` in signal_generator.py"

✅ Summarize long discussions
   "Discussed 3 options for state management, chose Zustand for simplicity"

✅ Use tables for structured data
   | Feature | Status |
   |---------|--------|
   | Login   | ✅ Done |

✅ Reference shared docs
   "Follow constraints in project-constraints.md"
```

### Don't
```markdown
❌ Paste entire files when only discussing small sections

❌ Repeat system prompt information in conversation

❌ Include verbose explanations for trivial changes

❌ Keep outdated context in files (clean up regularly)
```

---

## 8. EMERGENCY RECOVERY

### If Context Lost Mid-task
1. Check `progress.md` for last known state
2. Check `communication/progress-updates/` for recent updates
3. Check `task-board.md` for current assignments
4. Resume from most recent checkpoint

### Checkpoint Recovery Command
When resuming after context loss, start with:
```
"Resume [Agent Role] from last checkpoint.
Context: [Brief summary of what was being done]
Next action: [What needs to happen next]"
```

---

## 9. AUTOMATION HELPERS

### Scripts Available
| Script | Purpose | Usage |
|--------|---------|-------|
| `update-context.sh` | Update progress files | Run at session end |
| `generate-agent-prompt.py` | Create fresh session prompt | Run at session start |
| `validate-architecture.js` | Check doc consistency | Run weekly |

---

## 10. BEST PRACTICES SUMMARY

```markdown
1. START LEAN: Load minimum required context
2. UPDATE OFTEN: Keep progress.md current
3. HANDOFF CLEANLY: Create handoff docs when switching
4. REFERENCE, DON'T COPY: Point to files, don't paste
5. SUMMARIZE: Compress completed work into summaries
6. CLEAN UP: Remove outdated context regularly
```

---

**REMEMBER:** Good token management = Seamless AI collaboration across sessions.
