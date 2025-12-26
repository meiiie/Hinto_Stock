# HINTO STOCK - AI AGENT SYSTEM v2.1

> AI AGENT: Read this file first to understand your role and context.

---

## YOUR ROLE ASSIGNMENT

When Human Owner tells you which role you are, read the corresponding file:

| If you are... | Read this file | Your folder |
|---------------|--------------|----------------|
| Project Manager | agents/project-manager/system-prompt.md | agents/project-manager/ |
| Frontend Architect | agents/frontend-architect/system-prompt.md | agents/frontend-architect/ |
| Backend Engineer | agents/backend-engineer/system-prompt.md | agents/backend-engineer/ |
| Database Specialist | agents/database-specialist/system-prompt.md | agents/database-specialist/ |
| QA Engineer | agents/qa-engineer/system-prompt.md | agents/qa-engineer/ |
| **Quant Specialist** | **agents/quant-specialist/system-prompt.md** | **agents/quant-specialist/** |

Base Path: e:\Sach\DuAn\Hinto_Stock\documents\

---

## PROJECT OVERVIEW

Project: Hinto Stock - Desktop Trading Application
Type: Cryptocurrency 24/7 short-term futures trading
Strategy: Trend Pullback (VWAP + Bollinger Bands + StochRSI)
Architecture: 3-Layer Signal System

```
Layer 1: Real-time Signals (VWAP/BB/StochRSI) <-- CURRENT FOCUS
Layer 2: Candle Pattern Confirmation
Layer 3: LLM Strategic Planning (future)
```

Detailed architecture: Read shared-context/global-architecture.md

---

## DIRECTORY STRUCTURE

```
documents/
|-- agents/                    # Folder for each AI Agent
|   |-- project-manager/       
|   |   |-- system-prompt.md   # Read to understand PM role
|   |   +-- context/           # Task board, timeline, agent status
|   |-- frontend-architect/    
|   |   |-- system-prompt.md   # Read to understand FE role
|   |   +-- context/           # Architecture, design-system, progress
|   |-- backend-engineer/      
|   |   |-- system-prompt.md   # Read to understand BE role
|   |   +-- context/           # API contracts, business logic, progress
|   |-- database-specialist/   
|   |   |-- system-prompt.md   # Read to understand DB role
|   |   +-- context/           # Schema, optimization notes
|   +-- qa-engineer/           
|       |-- system-prompt.md   # Read to understand QA role
|       +-- context/           # Test strategy, bug tracking
|
|-- shared-context/            # Shared context for ALL agents
|   |-- shared-board.md        # SHARED BOARD - Check this first!
|   |-- decision-log.md        # Architecture Decision Records
|   |-- global-architecture.md # System architecture
|   |-- trading-requirements.md# Trading requirements
|   |-- project-constraints.md # Common constraints
|   +-- prompt-engineering-guide.md # SOTA prompt techniques
|
|-- communication/             # Communication protocols
|   |-- agent-handoffs.md      # Work transfer process
|   +-- conflict-resolution.md # Conflict resolution
|
|-- workflows/                 # Work processes
|   |-- feature-development.md # New feature development
|   |-- bug-fixing.md          # Bug fixing
|   +-- architecture-review.md # Architecture review
|
+-- README.md                  # This file - Entry point
```

---

## MANDATORY WORKFLOW FOR ALL AGENTS

### When starting session:
1. Read this README.md file (done)
2. Read shared-context/shared-board.md for current status
3. Read system-prompt.md for your assigned role
4. Read context/progress.md to know previous work
5. Read shared-context/decision-log.md for past decisions

### After completing each task:
- UPDATE shared-context/shared-board.md with your status
- UPDATE context/progress.md with work completed
- LOG decisions to shared-context/decision-log.md if significant

### When transferring work to another agent:
- CREATE handoff document per communication/agent-handoffs.md

### When deep analysis is needed:
- USE command: ULTRATHINK: [problem]
- OR USE: Think step-by-step

---

## TRIGGER COMMANDS

| Command | Effect |
|---------|--------|
| (Default) | Concise, focused response |
| ULTRATHINK | Multi-dimensional deep analysis |
| Think step-by-step | Step-by-step reasoning (CoT) |
| <thinking> block | Show thought process |

---

## IMPORTANT RULES

1. Stay in role - Do not work outside your domain
2. Update progress - After each task completed
3. Use handoffs - When transferring work
4. Escalate - Contact Human Owner for major decisions
5. Document - Record important decisions

---

## CURRENT STATUS

Phase: Layer 1 Fully Operational ✅
Focus: Strategy optimization & Layer 2 preparation

| Agent | Status | Progress file |
|-------|--------|--------------|
| PM | Ready | agents/project-manager/context/agent-status.md |
| FE | Ready | agents/frontend-architect/context/progress.md |
| BE | Ready | agents/backend-engineer/context/progress.md |
| DB | Ready | agents/database-specialist/context/optimization-notes.md |
| QA | Ready | agents/qa-engineer/context/bug-tracking.md |
| **QS** | **Ready** | **agents/quant-specialist/context/progress.md** |

---

## CHECKLIST AFTER READING THIS FILE

- [ ] You know your assigned role?
- [ ] Read system-prompt.md for your role?
- [ ] Read progress.md to know previous work?
- [ ] Ready to receive commands from Human Owner?

If completed, confirm with Human Owner: "[Role] Agent Ready"

---

Version: 2.2 | Updated: 2025-12-23
