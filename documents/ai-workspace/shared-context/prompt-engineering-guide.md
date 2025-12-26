# PROMPT ENGINEERING GUIDE - SOTA Techniques 2025

Version: 2.1 | Updated: 2025-12-22

---

## 1. Core Principles (2025)

### 1.1 Context Engineering (Anthropic 2025)
Beyond prompt engineering - manage the ENTIRE information environment available to the LLM.

Key aspects:
- Curate optimal tokens at each inference step
- Manage context across multi-turn agent conversations
- Dynamic context loading based on task requirements

### 1.2 Clarity, Specificity, Conciseness
- State exactly what is desired
- Include format, purpose, and boundaries
- Summarize your prompt in one sentence for accuracy
- Avoid ambiguity that leads to irrelevant responses

### 1.3 Structured Outputs
Explicitly define output format to reduce hallucination:
```
Output format: JSON with fields {signal, confidence, entry, stop_loss, take_profit}
```

---

## 2. Advanced Techniques

### 2.1 Chain-of-Thought (CoT)

Trigger phrases:
- "Think step-by-step"
- "Let's break this down"
- "Reason through this carefully"
- "Before answering, analyze each component"

Example:
```
Think step-by-step about this signal:
1. Analyze trend direction (price vs VWAP)
2. Check pullback quality (distance to BB)
3. Confirm momentum (StochRSI cross)
4. Validate volume
5. Conclude with signal recommendation
```

Best for: Logic-based tasks, multi-step problems, arithmetic, symbolic reasoning
Note: More effective with larger models (100B+ parameters)

### 2.2 ReAct (Reasoning + Acting)

Structure:
```xml
<thought>Analyze current situation and plan next step</thought>
<action>Execute specific action or tool call</action>
<observation>Process and interpret results</observation>
<thought>Decide next step based on observation</thought>
```

Benefits:
- Makes reasoning and actions explicit
- Aids in debugging
- Important for tasks requiring tool invocations

### 2.3 Tree of Thoughts (ToT)

Advanced form of CoT that branches to weigh multiple options:
```
Consider three approaches:
Approach A: [description] - Pros: [...] Cons: [...]
Approach B: [description] - Pros: [...] Cons: [...]
Approach C: [description] - Pros: [...] Cons: [...]

Evaluate and select the optimal approach.
```

Best for: Tasks requiring consideration of various scenarios

### 2.4 Recursive Self-Improvement Prompting (RSIP)

Process:
1. Generate initial output
2. Critically evaluate against specific criteria
3. Generate improved version
4. Repeat until quality threshold met

Example:
```
Generate a solution. Then critique it for:
- Correctness
- Completeness
- Edge cases
- Performance

Provide an improved version addressing the critique.
```

### 2.5 Few-Shot Prompting

Include 2-5 high-quality, diverse examples:
```
Example 1:
Input: [example input]
Output: [example output]

Example 2:
Input: [example input]
Output: [example output]

Now process:
Input: [actual input]
```

80% more efficient than zero-shot for complex tasks

---

## 3. Multi-Agent Prompt Engineering (2025)

### 3.1 Agent Identification
Explicitly name and identify agents:
```
Agent: Backend Engineer
Sequence: After Frontend completes API contract review
Inputs: API specification from Frontend
Outputs: Implemented endpoints with tests
```

### 3.2 Agent Sequencing
Define clear workflow:
```
1. Frontend Agent: Define API contract
2. Backend Agent: Implement endpoints
3. Database Agent: Optimize queries
4. QA Agent: Validate implementation
```

### 3.3 Structured Inter-Agent Communication
Force structured data between agents:
```python
# Handoff schema
{
  "from_agent": "frontend",
  "to_agent": "backend",
  "task": "implement_endpoint",
  "context": {...},
  "acceptance_criteria": [...]
}
```

---

## 4. Trigger Commands

| Command | Mode | Effect |
|---------|------|--------|
| (Default) | Standard | Concise, focused response |
| ULTRATHINK | Deep Analysis | Multi-dimensional exhaustive analysis |
| Think step-by-step | CoT | Step-by-step reasoning |
| <thinking> block | Internal | Show explicit thought process |
| Critique and improve | RSIP | Self-improvement iteration |

---

## 5. Prompt Structure Template

```
<system>
ROLE: [Specific persona with expertise level]
DOMAIN: [Project/domain context]
CONSTRAINTS: [Boundaries and limitations]
</system>

<task>
[Clear, specific task description]
</task>

<context>
[Relevant background information]
[Current state and previous work]
</context>

<requirements>
- [Specific requirement 1]
- [Specific requirement 2]
</requirements>

<output_format>
[Explicit format specification]
</output_format>

<examples>
[2-5 diverse examples if needed]
</examples>
```

---

## 6. Anti-Patterns to Avoid

| Anti-Pattern | Why Avoid | Better Alternative |
|--------------|-----------|-------------------|
| Vague instructions | Leads to irrelevant output | Be specific with exact requirements |
| Emojis in prompts | Affects professional tone, can trigger unintended behavior | Use plain text markers |
| Negative prompting | Can cause unintended behavior | State what TO do, not what NOT to do |
| Overly long prompts | Token waste, context dilution | Summarize, use references |
| No output format | Inconsistent results | Always specify format |

---

## 7. Framework Comparison (2025)

| Framework | Best For | Key Feature |
|-----------|----------|-------------|
| CrewAI | Team workflows | Role-based collaboration protocols |
| LangGraph | Complex branching | Graph-based state machine |
| OpenAI Agents SDK | Managed runtime | First-party tools integration |
| Google ADK | Gemini optimization | Code-first approach |

---

## 8. Quality Checklist

Before finalizing a prompt:
- [ ] Clear role and expertise defined?
- [ ] Task is specific and unambiguous?
- [ ] Output format explicitly stated?
- [ ] Relevant context provided?
- [ ] Constraints and boundaries set?
- [ ] Examples included for complex tasks?
- [ ] No emojis or informal language?
- [ ] Testable and verifiable?

---

## References

- Anthropic Context Engineering (2025)
- CrewAI Multi-Agent Patterns
- LangGraph State Machine Design
- Google ADK Code-First Agents
- Recursive Self-Improvement Prompting Research
