---
name: "writing-plans"
description: "Creates detailed, actionable development plans with clear steps, dependencies, and verification criteria. Invoke when user asks to plan a task or create a roadmap."
---

# Writing Plans Skill

A systematic approach to creating structured, actionable development plans.

## When to Use

- Starting a new project or feature
- Breaking down a complex task
- Planning a multi-step implementation
- Creating a roadmap or timeline
- Organizing work for a team

## Plan Structure

### 1. Overview

Brief summary of what the plan achieves:
- **Goal**: What are we building?
- **Scope**: What's included/excluded?
- **Timeline**: Expected duration
- **Resources**: What's needed?

### 2. Task Decomposition

Break down into actionable items:

```markdown
## Task List

### Phase 1: Foundation
- [ ] Task 1.1: [Description]
  - Dependencies: [What must be done first]
  - Verification: [How to confirm completion]
  
- [ ] Task 1.2: [Description]
  - Dependencies: [Task 1.1]
  - Verification: [How to confirm completion]

### Phase 2: Core Implementation
...
```

### 3. Dependencies

Visualize task relationships:
- Sequential dependencies
- Parallel opportunities
- Critical path identification

### 4. Risk Assessment

Identify potential blockers:
- Technical risks
- Resource constraints
- External dependencies

## Plan Template

```markdown
# Development Plan: [Title]

## 1. Overview
**Goal:** [Clear goal statement]
**Scope:** [What's in/out]
**Timeline:** [Duration estimate]
**Owner:** [Responsible party]

## 2. Tasks

### Phase [N]: [Phase Name]
| Task | Dependencies | Effort | Verification |
|------|--------------|--------|--------------|
| [Task] | [Depends on] | [Est] | [Check] |

## 3. Risks & Mitigations
| Risk | Impact | Mitigation |
|------|--------|------------|
| [Risk] | [H/M/L] | [Plan] |

## 4. Milestones
- [ ] Milestone 1: [Date] - [Goal]
- [ ] Milestone 2: [Date] - [Goal]

## 5. Success Criteria
- [ ] Criterion 1
- [ ] Criterion 2
```

## Best Practices

1. **Be Specific**: Every task should be clearly defined
2. **Include Verification**: How do we know it's done?
3. **Identify Dependencies**: What must come first?
4. **Estimate Realistically**: Account for unknowns
5. **Keep it Reviewable**: Small enough to track progress

## Plan Review Checklist

- [ ] All major tasks are captured
- [ ] Dependencies are correctly identified
- [ ] Each task has verification criteria
- [ ] Risks are identified and mitigated
- [ ] Timeline is realistic
- [ ] Stakeholders are aligned