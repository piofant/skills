---
name: deep-thinking
description: Deep structured thinking before implementation — breaks a task into aspects, runs parallel expert analysis (one named expert per aspect), then synthesizes a design document with recommendations and an implementation plan. Триггеры — «продумай задачу», «deep-thinking», «разложи по экспертам», «design-документ перед кодом», «think it through», /deep-thinking.
argument-hint: "<task or idea to think through>"
model: opus
---

# Structured Thinking

You help think through a task before implementation. Work in three stages.

## Stage 1: Task Breakdown

First, identify **aspects to think through** — parts of the task that need decisions.

Choose a **main expert** for analyzing the task as a whole.

**Output format:**

```
## Understanding the Task

[How you understood the task — 1-2 sentences]

---

### Expert Perspective

> "Analyzing as [Main Expert] because [reason]"
>
> **Principles from 3 experts:**
> 1. [Expert A]: "[principle]"
> 2. [Expert B]: "[principle]"
> 3. [Expert C]: "[principle]"

---

## Aspects to Think Through

| # | Aspect | Why Important | Expert |
|---|--------|---------------|--------|
| 1 | [Name] | [Why needs thinking] | [Who will analyze] |
| 2 | ... | ... | ... |
...
```

Usually 5-10 aspects. No more than 15.

### Expert Table

| Area                   | Expert           | Principles                                                     |
| ---------------------- | ---------------- | -------------------------------------------------------------- |
| React/State            | Dan Abramov      | single responsibility, lift state only when needed, colocation |
| TypeScript types       | Matt Pocock      | infer over explicit, branded types, type narrowing             |
| Testing                | Kent C. Dodds    | test behavior not implementation, avoid test IDs, colocation   |
| Refactoring            | Martin Fowler    | small steps, preserve behavior, extract till you drop          |
| API design             | Theo Browne      | type-safe contracts, fail fast, explicit errors                |
| Database               | Markus Winand    | index-first thinking, avoid N+1, explain analyze               |
| Distributed systems    | Martin Kleppmann | eventual consistency, idempotency, partition tolerance         |
| Architecture           | Sam Newman       | bounded context, single responsibility, loose coupling         |
| Security               | Troy Hunt        | defense in depth, least privilege, validate all inputs         |
| DevOps/K8s             | Kelsey Hightower | declarative config, immutable infrastructure, GitOps           |
| UX/Product             | Nir Eyal         | trigger → action → variable reward → investment                |
| Gamification           | Yu-kai Chou      | core drives, white hat vs black hat motivation                 |

For other areas — find appropriate specialists yourself.

## Stage 2: Project Study

After breakdown, tell the user:

> "Identified N aspects. Now I'll study the project and launch experts for each. 🐙"

Then launch **in parallel** one `general-purpose` agent per aspect. Put **all** Task calls in **ONE message** so they run concurrently.

Give each agent the self-contained prompt below (this is the expert framework inlined — the agent needs no external files). Full reference: [reference/expert-agent.md](reference/expert-agent.md).

```
Task(general-purpose): "
You analyze ONE specific aspect of a task. Study the project, apply expert thinking, propose solution options.

ASPECT: [aspect name]
TASK CONTEXT: [brief context]

WORKFLOW:
1. Project study — use Glob to find related files, Grep for existing patterns, Read to study implementations. If you need current best practices, WebSearch.
2. Pick a MAIN expert for this aspect + 3 supporting experts with relevant principles. Use this table as a starting point (find your own specialist for areas not listed):
   React/State → Dan Abramov; TypeScript → Matt Pocock; Testing → Kent C. Dodds; Refactoring → Martin Fowler; API → Theo Browne; Database → Markus Winand; Distributed systems → Martin Kleppmann; Architecture → Sam Newman; Security → Troy Hunt; DevOps/K8s → Kelsey Hightower; UX/Product → Nir Eyal; Gamification → Yu-kai Chou.
3. Propose 2-4 options. For each: name, essence, ✅ pros, ❌ cons, when it fits.
4. Decide the best option FOR THIS PROJECT on behalf of the main expert, with reasoning + risks.

RETURN in exactly this format:
## Aspect: [aspect name]
### Project Context
[patterns, existing solutions, constraints you found]
### Expert Analysis
> 'Analyzing as [Main Expert] because [reason]'
> Principles from 3 experts:
> 1. [Expert A]: '[principle]'
> 2. [Expert B]: '[principle]'
> 3. [Expert C]: '[principle]'
### Solution Options
**A: [Name]** — essence / ✅ pros / ❌ cons / when
**B: [Name]** ...
**C: [Name]** (if applicable) ...
### Decision from [Main Expert]
**Choice: [Option X]** — [reasoning with project context]
**Risks:** [what to watch during implementation]

Principles: be specific to THIS project (not abstract advice); every option must have honest cons; always state which expert you reason as; account for what already exists.
"
```

**IMPORTANT:** Launch all agents in ONE message in parallel.

## Stage 3: Summary Document

When all agents return results, create a **unified document** in the format:

```markdown
# [Task Name]

> **Status:** Research complete
> **Date:** [date]
> **Goal:** [brief goal description]

---

## Table of Contents

1. [Overview](#overview)
2. [Aspect 1](#1-name)
3. [Aspect 2](#2-name)
...
N. [Implementation Plan](#implementation-plan)

---

## Overview

### Goals

1. **[Goal 1]** — description
2. **[Goal 2]** — description
...

### Key Decisions

| Aspect | Decision |
|--------|----------|
| [Aspect 1] | [Brief decision] |
| [Aspect 2] | [Brief decision] |
...

---

## 1. [Aspect Name]

> **Experts:** [Expert 1], [Expert 2], [Expert 3]

### [Subsection with solution]

[Detailed description of chosen option]

| Aspect | Details |
|--------|---------|
| ... | ... |

### [Code/examples if needed]

\`\`\`typescript
// Example code
\`\`\`

---

## 2. [Next Aspect]
...

---

## Implementation Plan

### Phase 1: MVP

- [ ] Task 1
- [ ] Task 2
...

### Phase 2: ...

---

## Success Metrics

| Metric | Baseline | Target |
|--------|----------|--------|
| ... | — | ... |
```

**Save the document** to `docs/plans/YYYY-MM-DD-[topic]-design.md`

At the end, ask:

> "Summary is ready and saved to `docs/plans/...`. Which aspects would you like to discuss further? Or ready to implement?"

---

## Credits

Adapted from the **think-through** plugin by **Ilia Izmailov** (https://github.com/izmailovilya), originally MIT-licensed. Standalone port: Stage 2 dispatches `general-purpose` agents with the expert framework inlined, instead of the plugin's `think-through:expert` sub-agent, so it runs as a self-contained skill with no plugin dependency. See [LICENSE](LICENSE).
